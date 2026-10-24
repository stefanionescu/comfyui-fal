"""Wait for a request fal accepted, read its result, and download what the node decodes; none of it bills.

When the person cancels a run, the pack asks fal to cancel the request. fal removes a request still in the queue and
never bills it; one that started may finish, and its record stays.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
import asyncio
from datetime import UTC, datetime, timedelta
from contextlib import aclosing

from yarl import URL
from pydantic import ValidationError

from ..outputs import list_output_files, choose_output_text, decode_inline_file
from ..failures import build_failure
from ..transport import send_cancel, send_lookup, download_output, read_status_stream
from ...state.queue import OutputFile, RequestResult
from ...config.media import INLINE_PREFIX
from ...config.queue import (
    STATUSES,
    STATUS_QUERY,
    STREAM_SEGMENT,
    CANCELLABLE_STATUS,
    STREAM_REOPEN_SECONDS,
    RECORD_RETENTION_SECONDS,
)
from ...state.errors import FalError, ErrorCode
from ...state.replies import StatusReply
from ...config.execution import PROGRESS_STEPS
from ...config.messages.run import REPLY_UNREADABLE
from ...config.messages.queue import WAIT_LIMIT, REQUEST_GONE

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ...state import Json
    from .records import RequestStore
    from ..operation import Progress
    from ...state.files import FalFile
    from ...state.queue import RequestRecord
    from ...state.models import FalModel, MediaKind
    from ...state.settings import Settings, Configuration

# A failed result read whose code is one of these is the request's own outcome: reading again gives the same answer.
_OUTCOME_CODES = frozenset({ErrorCode.INVALID_INPUT, ErrorCode.REFUSED, ErrorCode.TIMEOUT, ErrorCode.UNAVAILABLE})


async def wait_settled[T](task: asyncio.Task[T]) -> bool:
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


async def cancel_request(
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


async def _download_file(file: FalFile, settings: Settings) -> bytes:
    """Read one output file: decode inline data in place, and fetch any other link with one keyless download."""
    url = file.url or ''
    if url.startswith(INLINE_PREFIX):
        return decode_inline_file(url, settings)
    return await download_output(url, settings)


class CollectOperation:
    """Wait for one recorded request, read its result, and download what the node decodes; none of it bills."""

    def __init__(
        self,
        record: RequestRecord,
        requests: RequestStore,
        model: FalModel | None,
        download_kinds: frozenset[MediaKind],
        last_status: str | None = None,
    ) -> None:
        """Keep the record, the store that deletes it, the model for reading the text, and the last status seen.

        Only a request that this run sent starts with a known status, queued. The operation cancels only that request
        when the person cancels the run. A request that Request: Download collects keeps running whatever the person
        does.
        """
        self.record = record
        self.requests = requests
        self.model = model
        self.download_kinds = download_kinds
        self.is_cancellable = last_status is not None
        self.last_status = last_status

    async def _set_status(self, status: StatusReply, progress: Progress | None) -> None:
        """Keep the status, and move the progress bar once when the model starts."""
        is_started = status.status == STATUSES['RUNNING'] and self.last_status != STATUSES['RUNNING']
        self.last_status = status.status
        if is_started and progress is not None:
            await progress(PROGRESS_STEPS['RUNNING'])

    async def _read_stream(
        self, configuration: Configuration, seconds: float, progress: Progress | None
    ) -> StatusReply | None:
        """Follow the status stream until it ends; the completed status, or None when it ended first.

        A dropped stream, or one that fails to connect, ends the read without an error, because reading again is free.
        """
        url = str(URL(self.record.status_url) / STREAM_SEGMENT % STATUS_QUERY)
        try:
            async with aclosing(read_status_stream(url, configuration, seconds)) as events:
                async for event in events:
                    status = _parse_status(event)
                    await self._set_status(status, progress)
                    if status.status == STATUSES['DONE']:
                        return status
        except FalError as error:
            if error.code is not ErrorCode.TRANSPORT:
                raise
        return None

    async def _read_status(
        self, url: str, configuration: Configuration, progress: Progress | None
    ) -> StatusReply | None:
        """Read the status once; None when fal is out of reach, because reading again is free."""
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

        At the request timeout the wait cancels nothing, because the request may still start, and the record stays.
        """
        seconds = configuration.settings.request_timeout_seconds
        deadline = time.monotonic() + seconds
        url = str(URL(self.record.status_url) % STATUS_QUERY)
        while (remaining := deadline - time.monotonic()) > 0:
            status = await self._read_stream(configuration, remaining, progress)
            status = status or await self._read_status(url, configuration, progress)
            if status is not None and status.status == STATUSES['DONE']:
                return status
            await asyncio.sleep(STREAM_REOPEN_SECONDS)
        raise FalError(ErrorCode.TIMEOUT, WAIT_LIMIT.format(seconds=seconds))

    async def _read_result(self, configuration: Configuration) -> dict[str, Json]:
        """Read the completed request's result.

        A refused input shows only here: fal answers with a 400 or 422 and bills nothing. A failure that is the
        outcome of the request itself therefore deletes the record. A key, credit, rate, or transport failure leaves
        it for Request: Download.
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

    async def send(self, configuration: Configuration, progress: Progress | None) -> RequestResult:
        """Wait for the request, read its result, and download what the node decodes, then delete the record.

        A cancel asks fal to cancel a request this run sent. The record goes only after every download, so the pack
        can collect the request again after a failed download.
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
                cancel = cancel_request(record, self.requests, configuration, self.last_status)
                await wait_settled(asyncio.create_task(cancel))
            raise
        except FalError as error:
            if error.code is not ErrorCode.UNAVAILABLE:
                raise
            await asyncio.to_thread(self.requests.delete, record.request_id)
            raise FalError(ErrorCode.UNAVAILABLE, REQUEST_GONE) from None
        if status.error is not None or status.error_type is not None:
            await asyncio.to_thread(self.requests.delete, record.request_id)
            raise build_failure(None, status.error_type, status.error or '')
        result = await self._read_result(configuration)
        files = await self._download_files(result, configuration.settings)
        if progress is not None:
            await progress(PROGRESS_STEPS['DOWNLOADED'])
        await asyncio.to_thread(self.requests.delete, record.request_id)
        return RequestResult(record, result, files, choose_output_text(result, self.model))


__all__ = ['CollectOperation', 'cancel_request', 'wait_settled']
