"""Find the files and the text in a fal result, and read a file fal returned inside its reply."""

from __future__ import annotations

import base64
import binascii
from ..types.files import FalFile
from pathlib import PurePosixPath
from urllib.parse import urlsplit
from typing import TYPE_CHECKING, cast
from ..config.units import BYTES_PER_MEGABYTE
from ..types.errors import ErrorCode, FalError
from ..config.messages.run import DOWNLOAD_LIMIT
from ..config.messages.media import INLINE_UNREADABLE
from ..config.media import OUTPUT_KINDS, INLINE_PREFIX

if TYPE_CHECKING:
    from ..types import Json
    from ..types.files import FileKind
    from ..types.settings import Settings
    from collections.abc import Mapping, Collection

# The kind of an output file by its exact content type, by the start of it, and by its link's extension.
_TYPE_KINDS = cast("Mapping[str, FileKind]", OUTPUT_KINDS["TYPES"])
_PREFIX_KINDS = cast("tuple[tuple[str, FileKind], ...]", OUTPUT_KINDS["PREFIXES"])
_EXTENSION_KINDS = cast("Mapping[str, FileKind]", OUTPUT_KINDS["EXTENSIONS"])
# A text value that starts with one of these is a link, not the model's text.
_LINK_PREFIXES = ("http://", "https://", INLINE_PREFIX)


def _choose_content_type(item: Mapping[str, Json], url: str) -> str | None:
    """Take the file object's content type, or for a data URI the type it names; None when neither has one."""
    content_type = item.get("content_type")
    if isinstance(content_type, str) and content_type:
        return content_type
    if url.startswith(INLINE_PREFIX):
        named = url.removeprefix(INLINE_PREFIX).split(",", 1)[0].split(";", 1)[0]
        return named or None
    return None


def _choose_kind(content_type: str | None, url: str) -> FileKind:
    """Sort a file by its exact content type, then the start of it, then its link's extension; other when none fits."""
    if content_type:
        exact = _TYPE_KINDS.get(content_type.lower())
        if exact is not None:
            return exact
        for prefix, kind in _PREFIX_KINDS:
            if content_type.lower().startswith(prefix):
                return kind
    extension = PurePosixPath(urlsplit(url).path).suffix.lower()
    return _EXTENSION_KINDS.get(extension) or "other"


def _list_files(value: Json, files: list[FalFile], urls: set[str]) -> None:
    """Walk one value depth first, adding each file object once, in the order fal sent it."""
    if isinstance(value, list):
        for item in value:
            _list_files(item, files, urls)
        return
    if not isinstance(value, dict):
        return
    url = value.get("url")
    if not isinstance(url, str) or not url:
        for item in value.values():
            _list_files(item, files, urls)
        return
    if url not in urls:
        urls.add(url)
        content_type = _choose_content_type(value, url)
        files.append(FalFile(_choose_kind(content_type, url), url, None, "output", content_type, None))


def list_output_files(result: Mapping[str, Json]) -> tuple[FalFile, ...]:
    """List every file in a result: each object with a string url, at any depth, in fal's order.

    The walk does not look inside a file object, and a link already listed is skipped, so the same file under two
    fields is listed once. A file given as a bare link string is not listed; it stays in the result.
    """
    files: list[FalFile] = []
    _list_files(dict(result), files, set())
    return tuple(files)


def choose_output_text(result: Mapping[str, Json], input_names: Collection[str]) -> str | None:
    """Choose the result's text: its first top-level non-empty string that is not an input's echo and not a link."""
    for name, value in result.items():
        if name in input_names or not isinstance(value, str) or not value.strip():
            continue
        if not value.startswith(_LINK_PREFIXES):
            return value
    return None


def decode_inline_file(url: str, settings: Settings) -> bytes:
    """Read a base64 data URI fal returned in place of a link, within the maximum download size."""
    header, separator, text = url.partition(",")
    if not separator or not header.endswith(";base64"):
        raise FalError(ErrorCode.MEDIA, INLINE_UNREADABLE)
    maximum = settings.max_download_megabytes
    if len(text) * 3 // 4 > maximum * BYTES_PER_MEGABYTE:
        raise FalError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=maximum))
    try:
        return base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError):
        raise FalError(ErrorCode.MEDIA, INLINE_UNREADABLE) from None


__all__ = ["choose_output_text", "decode_inline_file", "list_output_files"]
