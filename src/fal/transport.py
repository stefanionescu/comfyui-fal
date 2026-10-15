"""Open every HTTP session the extension uses, and send the only requests that carry the fal API key.

A submit is sent once and never again. A read that bills nothing fails without a charge, and its caller may read again.
"""

from __future__ import annotations

import math
import aiohttp
from yarl import URL
from http import HTTPStatus
from dataclasses import replace
from .streams import read_events
from typing import TYPE_CHECKING
from .failures import read_failure
from pydantic import ValidationError
from ..types.parsing import parse_json
from ..types.replies import CancelReply
from contextlib import asynccontextmanager
from ..config.units import BYTES_PER_MEGABYTE
from ..types.errors import ErrorCode, FalError
from ..config.fal import KEY_HOSTS, REPLY_BYTES, STORAGE_URLS, STORAGE_TYPE, DASHBOARD_URLS
from ..config.messages.run import (
    UPLOAD_FAILED,
    DOWNLOAD_LIMIT,
    FAL_UNREACHABLE,
    REQUEST_TIMEOUT,
    REPLY_UNREADABLE,
    REQUEST_UNCERTAIN,
    UPLOAD_UNREADABLE,
    OUTPUT_DOWNLOAD_FAILED,
)

if TYPE_CHECKING:
    from ..types import Json
    from ..types.credentials import Credential
    from ..types.replies import StorageTokenReply
    from collections.abc import Mapping, AsyncGenerator
    from ..types.settings import Settings, Configuration

# Every JSON request and reply names its media type.
_JSON_HEADERS = {"Accept": "application/json"}


def _create_session(settings: Settings) -> aiohttp.ClientSession:
    """Open one session for one request, bounded by the request timeout.

    Proxy settings from the environment and cookies are ignored, and every request refuses redirects, so neither the
    key nor a reply can pass through another host. aiohttp sends a GET again when its connection drops, and its only
    switch for that is private, so it is turned off here.
    """
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=settings.request_timeout_seconds),
        trust_env=False,
        cookie_jar=aiohttp.DummyCookieJar(),
    )
    setattr(session, "_retry_connection", False)  # noqa: B010 -- reason: aiohttp offers no public switch for its resend.
    return session


def _build_headers(url: str | URL, credential: Credential | None, headers: Mapping[str, str]) -> dict[str, str]:
    """Add the API key only for an https address on one of fal's API hosts, whatever address a reply named."""
    result = dict(headers)
    address = URL(url)
    if credential is not None and address.scheme == "https" and address.host in KEY_HOSTS:
        result["Authorization"] = f"Key {credential.reveal()}"
    return result


async def _read_body(response: aiohttp.ClientResponse, settings: Settings) -> bytes:
    """Read a reply or a file within the maximum download size."""
    maximum = settings.max_download_megabytes
    content = bytearray()
    async for chunk in response.content.iter_chunked(REPLY_BYTES["CHUNK"]):
        content.extend(chunk)
        if len(content) > maximum * BYTES_PER_MEGABYTE:
            raise FalError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=maximum))
    return bytes(content)


async def _validate_reply(response: aiohttp.ClientResponse) -> None:
    """Refuse a reply that is not a success, reading at most a short error body."""
    if response.status < HTTPStatus.MULTIPLE_CHOICES:
        return
    body = await response.content.read(REPLY_BYTES["MAX_ERROR"])
    raise read_failure(response.status, body, response.headers)


@asynccontextmanager
async def _validate_paid_request(settings: Settings) -> AsyncGenerator[None]:
    """Name what a failed paid request may have cost; nothing retries it."""
    try:
        yield
    except aiohttp.ClientConnectorError:
        # The connection failed before the request was sent, so nothing was billed.
        raise FalError(ErrorCode.TRANSPORT, FAL_UNREACHABLE) from None
    except aiohttp.ClientError:
        raise FalError(ErrorCode.UNCERTAIN, REQUEST_UNCERTAIN.format(**DASHBOARD_URLS)) from None
    except TimeoutError:
        seconds = settings.request_timeout_seconds
        raise FalError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds, **DASHBOARD_URLS)) from None


@asynccontextmanager
async def _send_free_request(
    method: str, url: str | URL, settings: Settings, headers: Mapping[str, str], body: bytes | None = None
) -> AsyncGenerator[aiohttp.ClientResponse]:
    """Send one request that bills nothing, once, and hand over its reply.

    A failure to connect or to read is reported as fal being out of reach, not as a possible charge, because the
    request bills nothing.
    """
    try:
        async with (
            _create_session(settings) as session,
            session.request(method, url, headers=headers, data=body, allow_redirects=False) as response,
        ):
            yield response
    except (aiohttp.ClientError, TimeoutError):
        raise FalError(ErrorCode.TRANSPORT, FAL_UNREACHABLE) from None


def _parse_reply(content: bytes, code: ErrorCode, message: str) -> Json:
    """Read a JSON reply whose size the download limit already bounds.

    The reply came with a success status. The code says what an unreadable reply means: UNCERTAIN when a paid request
    ran and may be billed, or TRANSPORT when a request that bills nothing failed.
    """
    try:
        text = content.decode("utf-8")
        return parse_json(text, max_bytes=len(content) + 1)
    except (UnicodeError, FalError):
        raise FalError(code, message) from None


async def send_json(
    url: str, body: Mapping[str, Json], headers: Mapping[str, str], configuration: Configuration
) -> Json:
    """Send one paid JSON request, with Request Options' headers, and return its parsed JSON reply."""
    sent = _build_headers(url, configuration.credential, {**_JSON_HEADERS, **headers})
    async with (
        _validate_paid_request(configuration.settings),
        _create_session(configuration.settings) as session,
        session.post(url, json=body, headers=sent, allow_redirects=False) as response,
    ):
        await _validate_reply(response)
        content = await _read_body(response, configuration.settings)
    return _parse_reply(content, ErrorCode.UNCERTAIN, REPLY_UNREADABLE)


async def send_lookup(url: str, settings: Settings, credential: Credential | None) -> Json:
    """Send one GET that bills nothing, such as a status read or a listing page, and return its parsed JSON reply.

    The listing is free without a key, so the key is optional; it only raises fal's rate limit.
    """
    headers = _build_headers(url, credential, _JSON_HEADERS)
    async with _send_free_request("GET", url, settings, headers) as response:
        await _validate_reply(response)
        content = await _read_body(response, settings)
    return _parse_reply(content, ErrorCode.TRANSPORT, REPLY_UNREADABLE)


async def read_status_stream(url: str, configuration: Configuration, seconds: float) -> AsyncGenerator[Json]:
    """Yield each status of fal's status stream until it closes or what is left of the wait passes.

    The caller closes the stream once it has the status it needs, which closes the session at once.
    """
    settings = replace(configuration.settings, request_timeout_seconds=max(1, math.ceil(seconds)))
    headers = _build_headers(url, configuration.credential, {"Accept": "text/event-stream"})
    async with _send_free_request("GET", url, settings, headers) as response:
        await _validate_reply(response)
        async for event in read_events(response, settings.max_download_megabytes * BYTES_PER_MEGABYTE):
            yield event


async def send_cancel(url: str, configuration: Configuration) -> bool:
    """Ask fal to cancel one request, and say whether fal accepted.

    A refusal changes nothing: fal refuses a request that already completed or that it does not know. fal's documented
    reply names a status and no success field, so a reply without one counts as accepted.
    """
    headers = _build_headers(url, configuration.credential, _JSON_HEADERS)
    async with _send_free_request("PUT", url, configuration.settings, headers) as response:
        if response.status >= HTTPStatus.MULTIPLE_CHOICES:
            return False
        content = await response.content.read(REPLY_BYTES["MAX_ERROR"])
    try:
        return CancelReply.model_validate_json(content).success
    except ValidationError:
        return True


async def create_upload_token(configuration: Configuration) -> Json:
    """Ask fal for a storage token, the one credential an upload carries."""
    url = URL(STORAGE_URLS["AUTHORIZE"]).with_query({"storage_type": STORAGE_TYPE})
    headers = _build_headers(url, configuration.credential, {**_JSON_HEADERS, "Content-Type": "application/json"})
    async with _send_free_request("POST", url, configuration.settings, headers, b"{}") as response:
        await _validate_reply(response)
        content = await _read_body(response, configuration.settings)
    return _parse_reply(content, ErrorCode.TRANSPORT, UPLOAD_UNREADABLE)


async def send_upload(
    content: bytes, content_type: str, file_name: str, token: StorageTokenReply, settings: Settings
) -> Json:
    """Upload one file to fal storage with the storage token, never the key, and return the parsed reply.

    A storage host's error body is not in fal's API format, so a refusal names only its status.
    """
    headers = {
        **_JSON_HEADERS,
        "Content-Type": content_type,
        "X-Fal-File-Name": file_name,
        "Authorization": f"{token.token_type} {token.token}",
    }
    async with _send_free_request("POST", STORAGE_URLS["UPLOAD"], settings, headers, content) as response:
        if response.status >= HTTPStatus.MULTIPLE_CHOICES:
            raise FalError(ErrorCode.TRANSPORT, UPLOAD_FAILED.format(status=response.status))
        reply = await _read_body(response, settings)
    return _parse_reply(reply, ErrorCode.TRANSPORT, UPLOAD_UNREADABLE)


async def download_output(url: str, settings: Settings) -> bytes:
    """Download one output file, once, without any credential.

    The address may carry its own signature, so it is sent byte for byte. A storage host's error body is not in fal's
    API format, so a failure names only its status. An address that is not https is not an output file, but the paid
    request behind it ran, so its charge is uncertain.
    """
    if not url.startswith("https://"):
        raise FalError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE)
    async with _send_free_request("GET", URL(url, encoded=True), settings, {}) as response:
        if response.status >= HTTPStatus.MULTIPLE_CHOICES:
            raise FalError(ErrorCode.TRANSPORT, OUTPUT_DOWNLOAD_FAILED.format(status=response.status))
        return await _read_body(response, settings)


__all__ = [
    "create_upload_token",
    "download_output",
    "read_status_stream",
    "send_cancel",
    "send_json",
    "send_lookup",
    "send_upload",
]
