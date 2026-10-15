"""Send a request to fal's queue and record it once fal accepts it, then wait for it and collect what it made.

When the person cancels a run, the pack asks fal to cancel the request. A request still queued is removed and never
billed; one that started may finish, and its record stays.
"""

from __future__ import annotations

import re
import time
import asyncio
from yarl import URL
from contextlib import aclosing
from typing import TYPE_CHECKING
from ..models import read_fal_model
from ..failures import build_failure
from pydantic import ValidationError
from ..arguments import build_arguments
from ...config.media import INLINE_PREFIX
from ..options import build_request_headers
from ..operation import validate_upload_size
from datetime import UTC, datetime, timedelta
from ...config.execution import PROGRESS_STEPS
from ...types.errors import ErrorCode, FalError
from ...types.files import FalFile, EncodedFile
from ...config.patterns import REQUEST_ID_PATTERN
from ...config.messages.run import REPLY_UNREADABLE
from ...types.replies import QueueReply, StatusReply
from ...config.fal import QUEUE_URL, QUEUE_HOST, DASHBOARD_URLS
from ...types.queue import OutputFile, RequestRecord, RequestResult
from ..outputs import list_output_files, choose_output_text, decode_inline_file
from ..transport import send_json, send_cancel, send_lookup, download_output, read_status_stream
from ...config.messages.queue import WAIT_LIMIT, REQUEST_GONE, ADDRESS_REFUSED, REQUEST_UNRECORDED
from ...config.queue import (
    STATUSES,
    STATUS_QUERY,
    RECORD_VERSION,
    STREAM_SEGMENT,
    CANCELLABLE_STATUS,
    STREAM_REOPEN_SECONDS,
    RECORD_RETENTION_SECONDS,
)

if TYPE_CHECKING:
    from ...types import Json
    from ..operation import Progress
    from ..uploads import UploadStore
    from .records import RequestStore
    from ...types.models import MediaKind
    from ...types.queue import QueuedRequest
    from collections.abc import Mapping, Callable
    from ...types.files import FieldValue, ArgumentValue
    from ...types.settings import Settings, Configuration

_REQUEST_ID = re.compile(REQUEST_ID_PATTERN)
# A failed result read whose code is one of these is the request's own outcome: reading again gives the same answer.
_OUTCOME_CODES = frozenset({ErrorCode.INVALID_INPUT, ErrorCode.REFUSED, ErrorCode.TIMEOUT, ErrorCode.UNAVAILABLE})


async def _wait_settled[T](task: asyncio.Task[T]) -> bool:
    """Wait until the asyncio task ends, however often a cancel arrives, and report whether one arrived.

    A cancel stops only the wait, never the asyncio task it waits for, so a second cancel cannot cut it off either.
    """
    is_cancelled = False
    while not task.done():
        try:
            await asyncio.wait({task})
        except asyncio.CancelledError:
            is_cancelled = True
    return is_cancelled


async def _send_cancel(
    record: RequestRecord, requests: RequestStore, configuration: Configuration, last_status: str | None
) -> None:
    """Ask fal to cancel the request, and delete its record only when it was still queued and fal accepted.

    The person asked to stop, so a failed cancel is not raised. A request that started may still finish and bill, so
    its record stays for Request: Download.
    """
    try:
        is_accepted = await send_cancel(record.cancel_url, configuration)
    except FalError:
        return
    if is_accepted and last_status == CANCELLABLE_STATUS:
        await asyncio.to_thread(requests.delete, record.request_id)


def _parse_status(document: Json) -> StatusReply:
    """Read one status; a status read bills nothing, so an unreadable one is a transport error and the record stays."""
    try:
        return StatusReply.model_validate(document)
    except ValidationError:
        raise FalError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


def _read_queue_reply(document: Json) -> QueueReply:
    """Read the submit's reply; it came with a success status, so the request may run even when it cannot be read.

    Each address must be an https address on fal's queue host, since status reads and the cancel carry the key.
    """
    try:
        reply = QueueReply.model_validate(document)
    except ValidationError:
        raise FalError(ErrorCode.UNCERTAIN, REQUEST_UNRECORDED.format(**DASHBOARD_URLS)) from None
    if _REQUEST_ID.match(reply.request_id) is None:
        raise FalError(ErrorCode.UNCERTAIN, REQUEST_UNRECORDED.format(**DASHBOARD_URLS))
    for address in (URL(reply.status_url), URL(reply.response_url), URL(reply.cancel_url)):
        if address.scheme != "https" or address.host != QUEUE_HOST:
            raise FalError(ErrorCode.UNCERTAIN, ADDRESS_REFUSED.format(**DASHBOARD_URLS))
    return reply


def _list_encoded(values: Mapping[str, ArgumentValue]) -> list[EncodedFile]:
    """List every encoded file of a request input, in field and item order."""
    files: list[EncodedFile] = []
    for value in values.values():
        items = value if isinstance(value, tuple) else (value,)
        files.extend(item for item in items if isinstance(item, EncodedFile))
    return files


async def _download_file(file: FalFile, settings: Settings) -> bytes:
    """Read one output file: a data URI in place, any other link with one keyless download."""
    url = file.url or ""
    if url.startswith(INLINE_PREFIX):
        return decode_inline_file(url, settings)
    return await download_output(url, settings)


class CollectOperation:
    """Wait for one recorded request, read its result, and download what the node decodes; none of it bills."""

    def __init__(
        self,
        record: RequestRecord,
        requests: RequestStore,
        input_names: frozenset[str],
        download_kinds: frozenset[MediaKind],
        last_status: str | None = None,
    ) -> None:
        """Keep the record, the store that deletes it, what the result is read for, and the last status seen.

        Only a request this run sent starts with a known status, queued, and only that one is cancelled when the run is;
        one Request: Download collects runs on whatever the person does.
        """
        self.record = record
        self.requests = requests
        self.input_names = input_names
        self.download_kinds = download_kinds
        self.is_cancellable = last_status is not None
        self.last_status = last_status

    async def _set_status(self, status: StatusReply, progress: Progress | None) -> None:
        """Keep the status, and move the progress bar once when the model starts."""
        is_started = status.status == STATUSES["RUNNING"] and self.last_status != STATUSES["RUNNING"]
        self.last_status = status.status
        if is_started and progress is not None:
            await progress(PROGRESS_STEPS["RUNNING"])

    async def _read_stream(
        self, configuration: Configuration, seconds: float, progress: Progress | None
    ) -> StatusReply | None:
        """Follow the status stream until it ends; the completed status, or None when it ended first.

        A dropped stream, or one that fails to connect, ends the read without an error, since reading again is free.
        """
        url = str(URL(self.record.status_url) / STREAM_SEGMENT % STATUS_QUERY)
        try:
            async with aclosing(read_status_stream(url, configuration, seconds)) as events:
                async for event in events:
                    status = _parse_status(event)
                    await self._set_status(status, progress)
                    if status.status == STATUSES["DONE"]:
                        return status
        except FalError as error:
            if error.code is not ErrorCode.TRANSPORT:
                raise
        return None

    async def _read_status(
        self, url: str, configuration: Configuration, progress: Progress | None
    ) -> StatusReply | None:
        """Read the status once; None when fal could not be reached, since reading again is free."""
        try:
            status = _parse_status(await send_lookup(url, configuration.settings, configuration.credential))
        except FalError as error:
            if error.code is not ErrorCode.TRANSPORT:
                raise
            return None
        await self._set_status(status, progress)
        return status

    async def _wait_for_status(self, configuration: Configuration, progress: Progress | None) -> StatusReply:
        """Wait with the status stream, and one status read after each stream ends, until the request completes.

        At the request timeout nothing is cancelled, since the request may still start, and the record stays.
        """
        seconds = configuration.settings.request_timeout_seconds
        deadline = time.monotonic() + seconds
        url = str(URL(self.record.status_url) % STATUS_QUERY)
        while (remaining := deadline - time.monotonic()) > 0:
            status = await self._read_stream(configuration, remaining, progress)
            status = status or await self._read_status(url, configuration, progress)
            if status is not None and status.status == STATUSES["DONE"]:
                return status
            await asyncio.sleep(STREAM_REOPEN_SECONDS)
        raise FalError(ErrorCode.TIMEOUT, WAIT_LIMIT.format(seconds=seconds))

    async def _read_result(self, configuration: Configuration) -> dict[str, Json]:
        """Read the completed request's result.

        A refused input shows only here, as a 400 or 422 with nothing billed, so a failure that is the request's own
        outcome deletes the record; a key, credit, rate, or transport failure leaves it for Request: Download.
        """
        record = self.record
        try:
            result = await send_lookup(record.response_url, configuration.settings, configuration.credential)
        except FalError as error:
            if error.code not in _OUTCOME_CODES:
                raise
            await asyncio.to_thread(self.requests.delete, record.request_id)
            if error.code is ErrorCode.UNAVAILABLE:
                raise FalError(ErrorCode.UNAVAILABLE, REQUEST_GONE) from None
            raise
        if not isinstance(result, dict):
            raise FalError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        return result

    async def _download_files(self, result: Mapping[str, Json], settings: Settings) -> tuple[OutputFile, ...]:
        """Download, one after another in result order, only the files whose kind the node decodes."""
        outputs: list[OutputFile] = []
        for file in list_output_files(result):
            content = await _download_file(file, settings) if file.kind in self.download_kinds else None
            outputs.append(OutputFile(file, content))
        return tuple(outputs)

    def validate(self, settings: Settings) -> None:
        """Accept every record; there is nothing to refuse before reading its status."""

    async def send(self, configuration: Configuration, progress: Progress | None) -> RequestResult:
        """Wait for the request, read its result, and download what the node decodes, then delete the record.

        A cancel asks fal to cancel a request this run sent. The record goes only after every download, so a failed
        download can be collected again.
        """
        record = self.record
        if datetime.now(UTC) >= datetime.fromisoformat(record.submitted_at) + timedelta(
            seconds=RECORD_RETENTION_SECONDS
        ):
            await asyncio.to_thread(self.requests.delete, record.request_id)
            raise FalError(ErrorCode.UNAVAILABLE, REQUEST_GONE)
        try:
            status = await self._wait_for_status(configuration, progress)
        except asyncio.CancelledError:
            if self.is_cancellable:
                cancel = _send_cancel(record, self.requests, configuration, self.last_status)
                await _wait_settled(asyncio.create_task(cancel))
            raise
        except FalError as error:
            if error.code is not ErrorCode.UNAVAILABLE:
                raise
            await asyncio.to_thread(self.requests.delete, record.request_id)
            raise FalError(ErrorCode.UNAVAILABLE, REQUEST_GONE) from None
        if status.error is not None or status.error_type is not None:
            await asyncio.to_thread(self.requests.delete, record.request_id)
            raise build_failure(None, status.error_type, status.error or "")
        result = await self._read_result(configuration)
        files = await self._download_files(result, configuration.settings)
        if progress is not None:
            await progress(PROGRESS_STEPS["DOWNLOADED"])
        await asyncio.to_thread(self.requests.delete, record.request_id)
        return RequestResult(record, result, files, choose_output_text(result, self.input_names))


class QueueOperation:
    """One request to a fal model, sent once and recorded as soon as fal accepts it."""

    def __init__(
        self,
        request: QueuedRequest,
        requests: RequestStore,
        uploads: UploadStore,
        encode_file: Callable[[FalFile], EncodedFile],
    ) -> None:
        """Keep the request, the stores it is recorded and uploaded with, and the encoder of local files.

        The encoder is ComfyUI's, passed in by the node, since this package may not import ComfyUI.
        """
        self.request = request
        self.requests = requests
        self.uploads = uploads
        self.encode_file = encode_file

    def _encode_values(self, values: Mapping[str, FieldValue]) -> dict[str, ArgumentValue]:
        """Encode each local file and put each link file's link in its place, keeping each field's order and shape."""
        encoded: dict[str, ArgumentValue] = {}
        for name, value in values.items():
            if isinstance(value, tuple):
                encoded[name] = tuple(file.url or self.encode_file(file) for file in value)
            else:
                encoded[name] = (value.url or self.encode_file(value)) if isinstance(value, FalFile) else value
        return encoded

    async def _build_body(self, values: Mapping[str, FieldValue], configuration: Configuration) -> dict[str, Json]:
        """Encode the local files in a worker thread, refuse one above the upload limit, and upload each once."""
        encoded = await asyncio.to_thread(self._encode_values, values)
        validate_upload_size(_list_encoded(encoded), configuration.settings)
        return await self.uploads.send_files(encoded, configuration)

    async def _create_record(
        self, endpoint_id: str, body: Mapping[str, Json], headers: Mapping[str, str], configuration: Configuration
    ) -> RequestRecord:
        """Send the submit once, and record the request before anything waits for it."""
        submitted_at = datetime.now(UTC).isoformat()
        reply = _read_queue_reply(await send_json(f"{QUEUE_URL}/{endpoint_id}", body, headers, configuration))
        record = RequestRecord(
            version=RECORD_VERSION,
            request_id=reply.request_id,
            endpoint_id=endpoint_id,
            kind=self.request.kind,
            status_url=reply.status_url,
            response_url=reply.response_url,
            cancel_url=reply.cancel_url,
            submitted_at=submitted_at,
        )
        await asyncio.to_thread(self.requests.save, record)
        return record

    def validate(self, settings: Settings) -> None:
        """Accept every request: each check needs the model, which send reads with the configuration."""

    async def send(self, configuration: Configuration, progress: Progress | None) -> RequestResult:
        """Read and check the model, upload the files, send the request once, record it, and wait for it.

        Every refusal comes before anything leaves the computer. A cancel during the submit waits for fal's answer, so
        a request it created is recorded and then cancelled while still queued, rather than left running unrecorded.
        """
        request = self.request
        model = await read_fal_model(request.model_id, request.kind, configuration.settings, configuration.credential)
        values = build_arguments(model, request.prompt, request.arguments, request.files)
        headers = build_request_headers(request.options)
        body = await self._build_body(values, configuration)
        if progress is not None:
            await progress(PROGRESS_STEPS["UPLOADED"])
        submitting = asyncio.create_task(self._create_record(model.model_id, body, headers, configuration))
        is_cancelled = await _wait_settled(submitting)
        record = submitting.result()
        if is_cancelled:
            await _wait_settled(
                asyncio.create_task(_send_cancel(record, self.requests, configuration, CANCELLABLE_STATUS))
            )
            raise asyncio.CancelledError
        if progress is not None:
            await progress(PROGRESS_STEPS["QUEUED"])
        names = frozenset(field.name for field in model.fields)
        return await CollectOperation(record, self.requests, names, request.download_kinds, CANCELLABLE_STATUS).send(
            configuration, progress
        )


__all__ = ["CollectOperation", "QueueOperation"]
