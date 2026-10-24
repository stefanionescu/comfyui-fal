"""Put links and ComfyUI media into a chain of files, each for a named file input of a fal model."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, cast, override
from dataclasses import replace
from urllib.parse import urlsplit

import torch
from comfy_api.latest import Input, io

from ..state.files import FalFile
from ..config.media import LINK_SCHEME, MASK_TENSOR, IMAGE_TENSOR, MAX_LINK_CHARACTERS
from ..state.errors import FalError, ErrorCode
from ..config.patterns import FILE_FIELD_PATTERN
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..config.messages.inputs import (
    FILE_LINK,
    FILE_EMPTY,
    SINGLE_VALUE,
    FILE_FIELD_NAME,
    FILE_FIELD_EMPTY,
    FILE_LINK_LENGTH,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_FILE_FIELD = re.compile(FILE_FIELD_PATTERN)


def _read_field(values: Sequence[str]) -> str:
    """Read the one field name the files of the node go to, refusing a name no fal file input can have."""
    names = {value.strip() for value in values}
    if len(names) > 1:
        raise FalError(ErrorCode.INVALID_INPUT, SINGLE_VALUE.format(name='field'))
    field = next(iter(names), '')
    if not field:
        raise FalError(ErrorCode.INVALID_INPUT, FILE_FIELD_EMPTY)
    if _FILE_FIELD.search(field) is None or ' ' in field or '.' in field:
        raise FalError(ErrorCode.INVALID_INPUT, FILE_FIELD_NAME)
    return field


def _read_link(text: str, field: str) -> tuple[FalFile, ...]:
    """Read a typed link; blank text adds nothing, and the node takes only an https address with a host."""
    link = text.strip()
    if not link:
        return ()
    if len(link) > MAX_LINK_CHARACTERS:
        raise FalError(ErrorCode.INVALID_INPUT, FILE_LINK_LENGTH.format(maximum=MAX_LINK_CHARACTERS))
    parts = urlsplit(link)
    if parts.scheme != LINK_SCHEME or not parts.netloc:
        raise FalError(ErrorCode.INVALID_INPUT, FILE_LINK)
    return (FalFile('other', link, None, 'link', None, field),)


def _read_media(value: object, field: str) -> tuple[FalFile, ...]:
    """Split connected media into one local file per image or mask frame, per audio clip, or the one video."""
    if isinstance(value, torch.Tensor):
        kind = 'image' if value.ndim == IMAGE_TENSOR['DIMENSIONS'] else 'mask'
        frames = value.unsqueeze(0) if value.ndim == MASK_TENSOR['FRAME_DIMENSIONS'] else value
        return tuple(
            FalFile(kind, None, frames[index : index + 1], 'local', None, field) for index in range(len(frames))
        )
    if isinstance(value, dict) and 'waveform' in value and 'sample_rate' in value:
        audio = cast('Input.Audio', cast('object', value))
        waveform = audio['waveform']
        clips = [
            {'waveform': waveform[index : index + 1], 'sample_rate': audio['sample_rate']}
            for index in range(len(waveform))
        ]
        return tuple(FalFile('audio', None, clip, 'local', None, field) for clip in clips)
    if isinstance(value, Input.Video):
        return (FalFile('video', None, value, 'local', None, field),)
    raise FalError(ErrorCode.INVALID_INPUT, FILE_EMPTY)


def _read_file(value: object, field: str) -> tuple[FalFile, ...]:
    """Turn one connected or typed value into files for the field: a link, the files of a fal node, or local media."""
    if isinstance(value, str):
        return _read_link(value, field)
    if isinstance(value, tuple):
        return tuple(
            replace(item, field=field) for item in cast('tuple[object, ...]', value) if isinstance(item, FalFile)
        )
    return _read_media(value, field)


class FileAdd(io.ComfyNode):
    """Add files for one named file input after the files it receives; it uploads nothing and needs no key."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the earlier files, the field, and the file: a typed link or connected media or fal files."""
        file = io.String.Input(
            'file',
            default='',
            tooltip='The file to add: a public https:// link typed here, or a connected image, mask, audio, video, or '
            "a fal node's files.",
        )
        files_socket = io.Custom(SOCKET_TYPES['FILES'])
        inputs: list[io.Input] = [
            files_socket.Input(
                'files',
                optional=True,
                tooltip='Files from another File: Add. The new files go after them, each keeping its own field.',
            ),
            io.String.Input(
                'field',
                default='',
                tooltip="The model's file input, exactly as fal names it, such as image_url or reference_audio_urls. "
                "Model: Info lists a model's inputs.",
            ),
            io.MultiType.Input(file, types=[io.Image, io.Mask, io.Audio, io.Video, files_socket]),
        ]
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='File: Add',
            category=MENUS['SHARED'],
            description="Add a link, images, masks, audio, a video, or another node's files for one file input of a "
            'fal model, named in field. It uploads nothing until a paid node sends it.',
            inputs=inputs,
            outputs=[files_socket.Output('files', display_name='files')],
            is_input_list=True,
        )

    @classmethod
    @override
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls execute with the inputs the schema declares.
        cls, *, field: list[str], file: list[object], files: list[tuple[FalFile, ...]] | None = None
    ) -> io.NodeOutput:
        """Put the added files after the ones received, each with the field of this node; the chain keeps its order.

        With input lists every input arrives as a list, so an image list from a fal node arrives whole.
        """
        name = _read_field(field)
        earlier = tuple(item for chain in files or () for item in chain)
        added = tuple(item for value in file for item in _read_file(value, name))
        if not added:
            raise FalError(ErrorCode.INVALID_INPUT, FILE_EMPTY)
        return io.NodeOutput((*earlier, *added))


__all__ = ['FileAdd']
