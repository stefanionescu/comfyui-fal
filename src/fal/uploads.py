"""Upload a request's local files to fal storage, and put each link where the request input needs it.

Each request uploads its own files; only the storage token is kept in memory between requests, and nothing is written
to disk.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING
from pydantic import ValidationError
from ..types.files import EncodedFile
from datetime import UTC, datetime, timedelta
from ..types.errors import ErrorCode, FalError
from ..config.messages.run import UPLOAD_UNREADABLE
from ..config.fal import UPLOAD_TOKEN_MARGIN_SECONDS
from .transport import send_upload, create_upload_token
from ..types.replies import UploadReply, StorageTokenReply

if TYPE_CHECKING:
    from ..types import Json
    from collections.abc import Mapping
    from ..types.settings import Configuration
    from ..types.files import FileItem, ArgumentValue


class UploadStore:
    """Upload each request's local files to fal storage, reusing one storage token while ComfyUI runs."""

    __slots__ = ("_lock", "_token")

    def __init__(self) -> None:
        """Start with no token; a lock guards it, since several runs may upload at once."""
        self._token: StorageTokenReply | None = None
        self._lock = threading.Lock()

    async def _read_token(self, configuration: Configuration) -> StorageTokenReply:
        """Reuse the token in memory until it is about to expire, then ask fal for a new one."""
        with self._lock:
            token = self._token
        deadline = datetime.now(UTC) + timedelta(seconds=UPLOAD_TOKEN_MARGIN_SECONDS)
        if token is not None and token.expires_at > deadline:
            return token
        reply = await create_upload_token(configuration)
        try:
            token = StorageTokenReply.model_validate(reply)
        except ValidationError:
            raise FalError(ErrorCode.TRANSPORT, UPLOAD_UNREADABLE) from None
        with self._lock:
            self._token = token
        return token

    async def _send_file(self, file: EncodedFile, configuration: Configuration) -> str:
        """Upload one file with the storage token, never the key, and return its link."""
        token = await self._read_token(configuration)
        reply = await send_upload(file.content, file.content_type, file.file_name, token, configuration.settings)
        try:
            link = UploadReply.model_validate(reply).access_url
        except ValidationError:
            raise FalError(ErrorCode.TRANSPORT, UPLOAD_UNREADABLE) from None
        if not link.startswith("https://"):
            raise FalError(ErrorCode.TRANSPORT, UPLOAD_UNREADABLE)
        return link

    async def _send_item(self, item: Json | FileItem, links: dict[str, str], configuration: Configuration) -> Json:
        """Upload an encoded file once per request, or pass any other value on unchanged."""
        if not isinstance(item, EncodedFile):
            return item
        if item.digest not in links:
            links[item.digest] = await self._send_file(item, configuration)
        return links[item.digest]

    async def send_files(self, arguments: Mapping[str, ArgumentValue], configuration: Configuration) -> dict[str, Json]:
        """Return the request input with every encoded file replaced by its link and every tuple turned into a list.

        Fields keep their order, and links stay as they are. Files are uploaded one after another, and the same file in
        two fields of one request is uploaded once; the next request uploads its files again.
        """
        links: dict[str, str] = {}
        request: dict[str, Json] = {}
        for name, value in arguments.items():
            if isinstance(value, tuple):
                request[name] = [await self._send_item(item, links, configuration) for item in value]
            else:
                request[name] = await self._send_item(value, links, configuration)
        return request


__all__ = ["UploadStore"]
