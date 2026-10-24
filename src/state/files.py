"""Files fal reads or makes: a link or local media, an encoded upload, and the values a request's fields hold."""

from typing import Literal
from dataclasses import dataclass

from . import Json
from .models import MediaKind

# Every kind of media a field takes, and "other" for an output file that no node decodes: an SVG or an archive, for
# example.
type FileKind = MediaKind | Literal['other']
type FileOrigin = Literal['output', 'link', 'local']


@dataclass(frozen=True, slots=True)
class FalFile:
    """One file a fal field takes or a fal result holds: a link, or ComfyUI media that the extension uploads on send.

    Attributes:
        kind: image, mask, video, audio, mesh, or other.
        url: The https link, or the data URL of an output fal returned inline; None for local media.
        media: The ComfyUI value of local media: one image or mask frame, one audio clip, or a `VIDEO`; None for a link.
        origin: output for a file fal made, link for an address the person gave, or local for ComfyUI media to upload.
        content_type: The file's media type when fal or the link names it; None otherwise.
        field: The fal field File: Add names it for, such as reference_audio_urls; None until File: Add sets one.

    """

    kind: FileKind
    url: str | None
    media: object | None
    origin: FileOrigin
    content_type: str | None
    field: str | None


@dataclass(frozen=True, slots=True)
class EncodedFile:
    """One local file, encoded and ready to upload to fal storage.

    Attributes:
        content: The file's bytes.
        content_type: Its media type, sent as Content-Type.
        file_name: The name fal storage gives it: its kind and the start of its digest.
        digest: The SHA-256 of content in hexadecimal, which finds an earlier upload of the same bytes.

    """

    content: bytes
    content_type: str
    file_name: str
    digest: str


# One field of a request input as the checks build it: a JSON value, one file for a *_url field, or files for *_urls.
type FieldValue = Json | FalFile | tuple[FalFile, ...]
type FileItem = str | EncodedFile
type ArgumentValue = Json | FileItem | tuple[FileItem, ...]

__all__ = ['EncodedFile', 'FalFile']
