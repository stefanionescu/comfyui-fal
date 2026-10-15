"""Keep a private record of every request fal accepted.

A request that started keeps running after a cancel, a timeout, or a ComfyUI restart, and its record lets Request:
Download collect it.
"""

from __future__ import annotations

import re
import threading
from typing import TYPE_CHECKING
from pydantic import ValidationError
from ...types.queue import RequestRecord
from ...types.errors import ErrorCode, FalError
from ...config.patterns import REQUEST_ID_PATTERN
from ...storage.files import save_file, read_file
from ...config.messages.queue import REQUEST_UNKNOWN
from ...config.storage import REQUEST_FILES, MAX_FILE_BYTES
from ...config.queue import REQUEST_LABEL_SEPARATOR, REQUEST_TIME_CHARACTERS

if TYPE_CHECKING:
    from pathlib import Path

_REQUEST_ID = re.compile(REQUEST_ID_PATTERN)


class RequestStore:
    """Own the request records folder; every method blocks, so callers run it off the event loop."""

    def __init__(self, directory: Path) -> None:
        """Select the private requests folder and the lock its files share across threads."""
        self.directory = directory
        self._lock = threading.Lock()

    def _read_all(self) -> list[RequestRecord]:
        """Read every record; a damaged, oversized, or other-version file is skipped, so it never blocks the rest."""
        if not self.directory.is_dir():
            return []
        records: list[RequestRecord] = []
        for path in sorted(self.directory.glob(f"*{REQUEST_FILES['SUFFIX']}")):
            try:
                records.append(RequestRecord.model_validate_json(read_file(path, max_bytes=MAX_FILE_BYTES["REQUEST"])))
            except (OSError, ValidationError, FalError):
                continue
        return records

    def save(self, record: RequestRecord) -> None:
        """Write one record atomically, named by its request ID."""
        path = self.directory / f"{record.request_id}{REQUEST_FILES['SUFFIX']}"
        with self._lock:
            save_file(path, (record.model_dump_json(indent=2) + "\n").encode())

    def delete(self, request_id: str) -> None:
        """Delete one record; a record already gone needs no removal."""
        path = self.directory / f"{request_id}{REQUEST_FILES['SUFFIX']}"
        with self._lock:
            # reason: Record names are validated request IDs inside the private requests folder.
            # bearer:disable python_lang_path_traversal
            path.unlink(missing_ok=True)

    def list_records(self) -> list[RequestRecord]:
        """List every recorded request, of every kind, newest first: one node collects them all."""
        with self._lock:
            records = self._read_all()
        return sorted(records, key=lambda record: record.submitted_at, reverse=True)

    def read(self, request_id: str) -> RequestRecord:
        """Return the recorded request with this ID; an ID that cannot be one, or has no record, is refused."""
        if _REQUEST_ID.match(request_id) is None:
            raise FalError(ErrorCode.INVALID_INPUT, REQUEST_UNKNOWN)
        with self._lock:
            record = next((record for record in self._read_all() if record.request_id == request_id), None)
        if record is None:
            raise FalError(ErrorCode.INVALID_INPUT, REQUEST_UNKNOWN)
        return record


def list_request_labels(requests: RequestStore) -> list[str]:
    """List the recorded requests as Request: Download shows them: ID, endpoint, and submit time in UTC.

    The submit time is cut to the minute, and fal's own request ID leads, so the node can read it back.
    """
    labels: list[str] = []
    for record in requests.list_records():
        submitted = record.submitted_at[:REQUEST_TIME_CHARACTERS].replace("T", " ")
        labels.append(REQUEST_LABEL_SEPARATOR.join((record.request_id, record.endpoint_id, submitted)))
    return labels


__all__ = ["RequestStore", "list_request_labels"]
