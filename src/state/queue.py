"""Queued fal requests: the record kept while one runs, the request to queue, and what it made."""

from typing import Literal
from dataclasses import dataclass
from collections.abc import Mapping

from . import Json, Kind, Value
from .files import FalFile
from .models import MediaKind
from .options import Options


class RequestRecord(Value):
    """One request fal accepted, saved before the first wait so the extension can collect a request that keeps running.

    Attributes:
        version: File format version; a reader refuses any other.
        request_id: fal's request ID, which also names the record's file.
        endpoint_id: The endpoint the request ran on.
        kind: The kind of node that sent it.
        status_url: fal's status address for it, as fal returned it.
        response_url: fal's result address for it, as fal returned it.
        cancel_url: fal's cancel address for it, as fal returned it.
        submitted_at: When the extension sent the submit, as ISO 8601 text in UTC.

    """

    version: Literal[1]
    request_id: str
    endpoint_id: str
    kind: Kind
    status_url: str
    response_url: str
    cancel_url: str
    submitted_at: str


@dataclass(frozen=True, slots=True)
class QueuedRequest:
    """One request a paid node asks for, as its inputs came; sending it reads and checks the model.

    Attributes:
        model_id: The endpoint ID as typed, stripped.
        texts: The text inputs by fal's field name, such as prompt.
        settings: The named settings set to custom, by fal's field name.
        arguments: The JSON text of the arguments input.
        files: The files chain, each item naming its field.
        options: Request Options, or None.

        kind: The kind of node that sends it.
        download_kinds: The kinds of file the outputs of the node decode, the only kinds the extension downloads.

    """

    model_id: str
    texts: dict[str, str]
    settings: dict[str, Json]
    arguments: str
    files: tuple[FalFile, ...]
    options: Options | None
    kind: Kind
    download_kinds: frozenset[MediaKind]


@dataclass(frozen=True, slots=True)
class OutputFile:
    """One file a request made.

    Attributes:
        file: The file and its link.
        content: The downloaded bytes, or None for a file no output of the node decodes.

    """

    file: FalFile
    content: bytes | None


@dataclass(frozen=True, slots=True)
class RequestResult:
    """What one finished request made.

    Attributes:
        record: The request's record.
        result: fal's whole result.
        files: Every file in the result, in result order.
        text: The result's text, or None.

    """

    record: RequestRecord
    result: Mapping[str, Json]
    files: tuple[OutputFile, ...]
    text: str | None


__all__ = ['OutputFile', 'QueuedRequest', 'RequestRecord', 'RequestResult']
