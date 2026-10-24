"""Send a request to fal's queue and record it once fal accepts it, then collect it.

A cancel during the submit waits for the answer from fal. The operation then records a request that the submit created
and cancels it while it is still in the queue.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
import asyncio
from datetime import UTC, datetime

from yarl import URL
from pydantic import ValidationError

from ..models import read_fal_model
from .collect import CollectOperation, wait_settled, cancel_request
from ..options import build_request_headers
from ..arguments import build_arguments
from ..operation import validate_upload_size
from ..transport import send_json
from ...config.fal import QUEUE_URL, QUEUE_HOST, DASHBOARD_URLS
from ...state.files import FalFile, EncodedFile
from ...state.queue import RequestRecord
from ...config.queue import RECORD_VERSION, CANCELLABLE_STATUS
from ...state.errors import FalError, ErrorCode
from ...state.replies import QueueReply
from ...config.patterns import REQUEST_ID_PATTERN
from ...config.execution import PROGRESS_STEPS
from ...config.messages.queue import ADDRESS_REFUSED, REQUEST_UNRECORDED

if TYPE_CHECKING:
    from collections.abc import Mapping, Callable

    from ...state import Json
    from .records import RequestStore
    from ..uploads import UploadStore
    from ..operation import Progress
    from ...state.files import FieldValue, ArgumentValue
    from ...state.queue import QueuedRequest, RequestResult
    from ...state.settings import Configuration

_REQUEST_ID = re.compile(REQUEST_ID_PATTERN)


def _read_queue_reply(document: Json) -> QueueReply:
    """Read the reply of the submit; it came with a success status, so the request may run even when it is unreadable.

    Each address must be an https address on the fal queue host, because status reads and the cancel carry the key.
    """
    try:
        reply = QueueReply.model_validate(document)
    except ValidationError:
        raise FalError(ErrorCode.UNCERTAIN, REQUEST_UNRECORDED.format(**DASHBOARD_URLS)) from None
    if _REQUEST_ID.match(reply.request_id) is None:
        raise FalError(ErrorCode.UNCERTAIN, REQUEST_UNRECORDED.format(**DASHBOARD_URLS))
    for address in (URL(reply.status_url), URL(reply.response_url), URL(reply.cancel_url)):
        if address.scheme != 'https' or address.host != QUEUE_HOST:
            raise FalError(ErrorCode.UNCERTAIN, ADDRESS_REFUSED.format(**DASHBOARD_URLS))
    return reply


def _list_encoded(values: Mapping[str, ArgumentValue]) -> list[EncodedFile]:
    """List every encoded file of a request input in the order of its fields and items."""
    files: list[EncodedFile] = []
    for value in values.values():
        items = value if isinstance(value, tuple) else (value,)
        files.extend(item for item in items if isinstance(item, EncodedFile))
    return files


class QueueOperation:
    """One request to a fal model, sent once and recorded as soon as fal accepts it."""

    def __init__(
        self,
        request: QueuedRequest,
        requests: RequestStore,
        uploads: UploadStore,
        encode_file: Callable[[FalFile], EncodedFile],
    ) -> None:
        """Keep the request, the stores that record it and upload its files, and the encoder of local files.

        The encoder comes from ComfyUI, and the node passes it in, because this package may not import ComfyUI.
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
        reply = _read_queue_reply(await send_json(f'{QUEUE_URL}/{endpoint_id}', body, headers, configuration))
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

    async def send(self, configuration: Configuration, progress: Progress | None) -> RequestResult:
        """Read and check the model, upload the files, send the request once, record it, and wait for it.

        Every refusal comes before anything leaves the computer. A cancel during the submit waits for the answer from
        fal. The operation then records a request that the submit created and cancels it while it is still in the
        queue, rather than leaving it running without a record.
        """
        request = self.request
        model = await read_fal_model(request.model_id, request.kind, configuration.settings, configuration.credential)
        values = build_arguments(model, request.texts, request.settings, request.arguments, request.files)
        headers = build_request_headers(request.options)
        body = await self._build_body(values, configuration)
        if progress is not None:
            await progress(PROGRESS_STEPS['UPLOADED'])
        submitting = asyncio.create_task(self._create_record(model.model_id, body, headers, configuration))
        is_cancelled = await wait_settled(submitting)
        record = submitting.result()
        if is_cancelled:
            await wait_settled(
                asyncio.create_task(cancel_request(record, self.requests, configuration, CANCELLABLE_STATUS))
            )
            raise asyncio.CancelledError
        if progress is not None:
            await progress(PROGRESS_STEPS['QUEUED'])
        collect = CollectOperation(record, self.requests, model, request.download_kinds, CANCELLABLE_STATUS)
        return await collect.send(configuration, progress)


__all__ = ['QueueOperation']
