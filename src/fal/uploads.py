"""Upload a request's local files to fal storage, and put each link where the request input needs it.

Each request uploads its own files. Between requests, the store keeps only the storage token in memory, and it writes
nothing to disk.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import UTC, datetime, timedelta
import threading
from dataclasses import field, dataclass

from pydantic import ValidationError

from .transport import send_upload, create_upload_token
from ..config.fal import UPLOAD_TOKEN_MARGIN_SECONDS
from ..state.files import EncodedFile
from ..state.errors import FalError, ErrorCode
from ..state.replies import UploadReply, StorageTokenReply
from ..config.messages.run import UPLOAD_UNREADABLE

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..state import Json
    from ..state.files import FileItem, ArgumentValue
    from ..state.settings import Configuration


@dataclass(slots=True, eq=False)
class UploadStore:
    """Upload each request's local files to fal storage, reusing one storage token while ComfyUI runs."""

    # No token until the first upload; a lock guards it, because several runs may upload at once.
    _token: StorageTokenReply | None = field(default=None, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

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
        if not link.startswith('https://'):
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

        Fields keep their order, and links stay as they are. The store uploads files one after another, and it uploads
        the same file in two fields of one request only once; the next request uploads its files again.
        """
        links: dict[str, str] = {}
        request: dict[str, Json] = {}
        for name, value in arguments.items():
            if isinstance(value, tuple):
                request[name] = [await self._send_item(item, links, configuration) for item in value]
            else:
                request[name] = await self._send_item(value, links, configuration)
        return request


__all__ = ['UploadStore']
