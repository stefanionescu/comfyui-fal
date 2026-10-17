"""Check ComfyUI media and convert it with ComfyUI's own helpers, to fal storage files and back from fal's files.

Encoding and decoding block, so callers run these functions through wait_for_thread.
"""

from __future__ import annotations

import io
import torch
import hashlib
from pathlib import PurePosixPath
from urllib.parse import urlsplit
from ..types.files import EncodedFile
from typing import TYPE_CHECKING, cast
from comfy_api.latest import Types, InputImpl
from ..types.errors import ErrorCode, FalError
from ..config.media import WAV, WEBP, MASK_TENSOR, IMAGE_TENSOR, MESH_FORMATS, ENCODED_FORMATS, DIGEST_CHARACTERS
from ..config.messages.media import (
    MASK_SHAPE,
    AUDIO_EMPTY,
    IMAGE_PIXELS,
    IMAGE_CHANNELS,
    AUDIO_UNREADABLE,
    AUDIO_UNWRITABLE,
    IMAGE_UNREADABLE,
    VIDEO_UNREADABLE,
    VIDEO_UNWRITABLE,
)
from comfy_api_nodes.util.conversions import (
    tensor_to_pil,
    tensor_to_bytesio,
    bytesio_to_image_tensor,
    audio_ndarray_to_bytesio,
    audio_bytes_to_audio_input,  # pyright: ignore[reportUnknownVariableType] -- reason: ComfyUI types its result as a bare dict.
    audio_tensor_to_contiguous_ndarray,
)

if TYPE_CHECKING:
    from typing import Literal
    from ..types.files import FalFile
    from comfy_api.latest import Input
    from collections.abc import Sequence


def _build_encoded(content: bytes, kind: Literal["image", "mask", "audio", "video"]) -> EncodedFile:
    """Name an encoded file by its kind and the start of its digest, with the content type of its kind."""
    digest = hashlib.sha256(content).hexdigest()
    encoded = ENCODED_FORMATS[kind]
    file_name = f"{kind}-{digest[:DIGEST_CHARACTERS]}.{encoded['EXTENSION']}"
    return EncodedFile(content, encoded["CONTENT_TYPE"], file_name, digest)


def _encode_webp(frame: torch.Tensor) -> bytes:
    """Encode one image as lossless WebP, at its own pixels."""
    buffer = io.BytesIO()
    tensor_to_pil(frame, total_pixels=None).save(
        buffer, format="WEBP", lossless=True, exact=True, method=WEBP["METHOD"], quality=WEBP["QUALITY"]
    )
    return buffer.getvalue()


def _encode_image(image: torch.Tensor) -> tuple[EncodedFile, ...]:
    """Encode every image of a batch as its own lossless WebP, never shrinking it; one fal cannot read is refused."""
    if image.ndim != IMAGE_TENSOR["DIMENSIONS"] or image.shape[-1] not in {
        IMAGE_TENSOR["RGB_CHANNELS"],
        IMAGE_TENSOR["RGBA_CHANNELS"],
    }:
        raise FalError(ErrorCode.INVALID_INPUT, IMAGE_CHANNELS)
    if not bool(torch.isfinite(image).all()):
        raise FalError(ErrorCode.INVALID_INPUT, IMAGE_PIXELS)
    try:
        contents = [_encode_webp(frame.clamp(0, 1)) for frame in image]
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise FalError(ErrorCode.MEDIA, IMAGE_CHANNELS) from None
    return tuple(_build_encoded(content, "image") for content in contents)


def _encode_mask(mask: torch.Tensor) -> tuple[EncodedFile, ...]:
    """Encode every frame of a mask as a one-channel PNG, where a mask value of 1 is white."""
    if mask.ndim == MASK_TENSOR["FRAME_DIMENSIONS"]:
        mask = mask.unsqueeze(0)
    if mask.ndim != MASK_TENSOR["DIMENSIONS"]:
        raise FalError(ErrorCode.INVALID_INPUT, MASK_SHAPE)
    if not bool(torch.isfinite(mask).all()):
        raise FalError(ErrorCode.INVALID_INPUT, IMAGE_PIXELS)
    try:
        contents = [
            tensor_to_bytesio(frame.clamp(0, 1), total_pixels=None, mime_type="image/png").getvalue() for frame in mask
        ]
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise FalError(ErrorCode.MEDIA, MASK_SHAPE) from None
    return tuple(_build_encoded(content, "mask") for content in contents)


def _encode_audio(audio: Input.Audio) -> tuple[EncodedFile, ...]:
    """Encode every clip of an audio batch as its own 16-bit WAV, which keeps every sample."""
    waveform = audio["waveform"]
    if waveform.shape[-1] == 0:
        raise FalError(ErrorCode.INVALID_INPUT, AUDIO_EMPTY)
    try:
        contents = [
            audio_ndarray_to_bytesio(
                audio_tensor_to_contiguous_ndarray(waveform[index : index + 1]),
                audio["sample_rate"],
                container_format=WAV["FORMAT"],
                codec_name=WAV["CODEC"],
            ).getvalue()
            for index in range(waveform.shape[0])
        ]
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise FalError(ErrorCode.MEDIA, AUDIO_UNWRITABLE) from None
    return tuple(_build_encoded(content, "audio") for content in contents)


def _encode_video(video: Input.Video) -> EncodedFile:
    """Write a ComfyUI video as MP4 in memory, keeping an MP4 source's streams as they are."""
    buffer = io.BytesIO()
    try:
        video.save_to(buffer, format=Types.VideoContainer.MP4, codec=Types.VideoCodec.AUTO)  # pyright: ignore[reportUnknownMemberType] -- reason: ComfyUI types its metadata parameter as a bare dict.
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise FalError(ErrorCode.MEDIA, VIDEO_UNWRITABLE) from None
    return _build_encoded(buffer.getvalue(), "video")


def encode_local_file(file: FalFile) -> EncodedFile:
    """Encode one local file of File: Add, which holds one image or mask frame, one audio clip, or one video."""
    media = file.media
    if file.kind == "image":
        return _encode_image(cast("torch.Tensor", media))[0]
    if file.kind == "mask":
        return _encode_mask(cast("torch.Tensor", media))[0]
    if file.kind == "audio":
        return _encode_audio(cast("Input.Audio", media))[0]
    return _encode_video(cast("Input.Video", media))


def decode_images(contents: Sequence[bytes]) -> tuple[tuple[torch.Tensor, ...], tuple[torch.Tensor, ...]]:
    """Read each image as pixels [1, H, W, 3] and its mask [1, H, W], where the mask is 1 minus alpha.

    An opaque image gets a mask of zeros, so the masks pair with the images by index.
    """
    pixels: list[torch.Tensor] = []
    masks: list[torch.Tensor] = []
    for content in contents:
        try:
            image = bytesio_to_image_tensor(io.BytesIO(content))
        except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
            raise FalError(ErrorCode.MEDIA, IMAGE_UNREADABLE) from None
        if image.shape[-1] == IMAGE_TENSOR["RGBA_CHANNELS"]:
            pixels.append(image[..., : IMAGE_TENSOR["RGB_CHANNELS"]].contiguous())
            masks.append(1.0 - image[..., IMAGE_TENSOR["RGB_CHANNELS"]])
        else:
            pixels.append(image)
            masks.append(torch.zeros(image.shape[:3], dtype=image.dtype))
    return tuple(pixels), tuple(masks)


def decode_video(content: bytes) -> Input.Video:
    """Read a video from memory, and its size once, so an unreadable file fails here and not in Save Video."""
    try:
        video = InputImpl.VideoFromFile(io.BytesIO(content))
        video.get_dimensions()
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise FalError(ErrorCode.MEDIA, VIDEO_UNREADABLE) from None
    return video


def decode_audio(content: bytes) -> Input.Audio:
    """Read any common audio container as ComfyUI audio: a waveform [1, C, T] and its sample rate."""
    try:
        audio = cast("Input.Audio", audio_bytes_to_audio_input(content))
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise FalError(ErrorCode.MEDIA, AUDIO_UNREADABLE) from None
    return audio


def decode_mesh(content: bytes, file: FalFile) -> Types.File3D:
    """Wrap a 3D file for ComfyUI's 3D nodes, naming its format by the link's extension, then by its content type."""
    extension = PurePosixPath(urlsplit(file.url or "").path).suffix.lower()
    file_format = MESH_FORMATS["EXTENSIONS"].get(extension) or MESH_FORMATS["TYPES"].get(file.content_type or "", "")
    return Types.File3D(io.BytesIO(content), file_format=file_format)


__all__ = [
    "decode_audio",
    "decode_images",
    "decode_mesh",
    "decode_video",
    "encode_local_file",
]
