"""Queued fal requests: the record kept while one runs, the request to queue, and what it made."""

from .files import FalFile
from typing import Literal
from .options import Options
from .models import MediaKind
from . import Json, Kind, Value
from dataclasses import dataclass
from collections.abc import Mapping


class RequestRecord(Value):
    """One request fal accepted, recorded before the first wait so a request that keeps running can be collected.

    Attributes:
        version: File format version; any other is refused.
        request_id: fal's request ID, which also names the record's file.
        endpoint_id: The endpoint the request ran on.
        kind: The kind of node that sent it.
        status_url: fal's status address for it, as fal returned it.
        response_url: fal's result address for it, as fal returned it.
        cancel_url: fal's cancel address for it, as fal returned it.
        submitted_at: When the submit was sent, in ISO 8601 and UTC.

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
    """One request a paid node asks for, as its inputs came; the model is read and checked when it is sent.

    Attributes:
        model_id: The endpoint ID as typed, stripped.
        prompt: The prompt input.
        arguments: The arguments input's JSON text.
        files: The files chain, each item naming its field.
        options: Request Options, or None.
        kind: The kind of node that sends it.
        download_kinds: The kinds of file the node's outputs decode, which are the only ones downloaded.

    """

    model_id: str
    prompt: str
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


__all__ = ["OutputFile", "QueuedRequest", "RequestRecord", "RequestResult"]
