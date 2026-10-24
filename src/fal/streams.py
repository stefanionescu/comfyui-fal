"""Read the server-sent events of fal's status stream."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..config.fal import REPLY_BYTES
from ..config.units import BYTES_PER_MEGABYTE
from ..state.errors import FalError, ErrorCode
from ..state.parsing import parse_json
from ..config.messages.run import DOWNLOAD_LIMIT, REPLY_UNREADABLE

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import aiohttp

    from ..state import Json


async def _read_lines(response: aiohttp.ClientResponse, max_bytes: int) -> AsyncIterator[bytes]:
    """Split the reply into lines of any length, within the download limit."""
    buffer = bytearray()
    total = 0
    async for chunk in response.content.iter_chunked(REPLY_BYTES['CHUNK']):
        total += len(chunk)
        if total > max_bytes:
            raise FalError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=max_bytes // BYTES_PER_MEGABYTE))
        buffer.extend(chunk)
        while (end := buffer.find(b'\n')) >= 0:
            yield bytes(buffer[:end])
            del buffer[: end + 1]
    if buffer:
        yield bytes(buffer)


async def read_events(response: aiohttp.ClientResponse, max_bytes: int) -> AsyncIterator[Json]:
    """Yield each data event until fal closes the stream, and skip other lines, such as comments.

    A failed request is an ordinary completed status that names its error, so this function reads no event as a failure.
    """
    async for line in _read_lines(response, max_bytes):
        try:
            text = line.decode('utf-8').strip()
        except UnicodeError:
            raise FalError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if not text.startswith('data:'):
            continue
        try:
            event = parse_json(text.removeprefix('data:').strip(), max_bytes=max_bytes)
        except FalError:
            raise FalError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        yield event


__all__ = ['read_events']
