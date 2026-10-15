"""The parts of fal's replies the extension reads; unknown fields are ignored."""

from . import Reply
from typing import Literal
from pydantic import AwareDatetime


class RefusalItem(Reply):
    """One item of a 422 refusal's detail list.

    Attributes:
        loc: Where the refused value sits, such as ("body", "prompt").
        msg: fal's text for a person.
        type: fal's machine name for the refusal, such as content_policy_violation.
        categories: The content policy categories a refused input hit.

    """

    loc: tuple[str | int, ...] = ()
    msg: str = ""
    type: str = ""
    categories: tuple[str, ...] = ()


class RefusalReply(Reply):
    """A model's validation refusal: a list of refused values.

    Attributes:
        detail: Every refused value.

    """

    detail: tuple[RefusalItem, ...]


class ErrorReply(Reply):
    """An infrastructure failure, or a refusal whose detail is one string.

    Attributes:
        detail: fal's text for a person.
        error_type: fal's machine name for the failure.

    """

    detail: str = ""
    error_type: str | None = None


class PlatformErrorBody(Reply):
    """The error object of fal's Platform API.

    Attributes:
        type: The Platform API's machine name for the failure.
        message: The Platform API's text for a person.

    """

    type: str | None = None
    message: str = ""


class PlatformErrorReply(Reply):
    """The Platform API's error envelope.

    Attributes:
        error: The error it holds.

    """

    error: PlatformErrorBody


class QueueReply(Reply):
    """What fal answers when it accepts a queued request.

    Attributes:
        request_id: The request's ID.
        status_url: Where the request's status is read.
        response_url: Where its result is read.
        cancel_url: Where it is cancelled.

    """

    request_id: str
    status_url: str
    response_url: str
    cancel_url: str


class StatusReply(Reply):
    """One status of a queued request, from the status stream or a status read.

    Attributes:
        status: Queued, running, or completed; a failed request is completed with an error.
        error: fal's text for a failed request.
        error_type: fal's machine name for the failure.

    """

    status: Literal["IN_QUEUE", "IN_PROGRESS", "COMPLETED"]
    error: str | None = None
    error_type: str | None = None


class CancelReply(Reply):
    """The reply to a cancel; fal's documented body names a status and holds no success field.

    Attributes:
        success: Whether fal accepted the cancel.

    """

    success: bool = True


class StorageTokenReply(Reply):
    """A token for fal storage uploads.

    Attributes:
        token: The token itself.
        token_type: The word the upload's Authorization header starts with.
        base_url: The storage address the token is for.
        expires_at: When the token stops working.

    """

    token: str
    token_type: str
    base_url: str
    expires_at: AwareDatetime


class UploadReply(Reply):
    """What fal storage answers for an upload.

    Attributes:
        access_url: The uploaded file's public link.

    """

    access_url: str


__all__ = [
    "CancelReply",
    "ErrorReply",
    "PlatformErrorBody",
    "PlatformErrorReply",
    "QueueReply",
    "RefusalItem",
    "RefusalReply",
    "StatusReply",
    "StorageTokenReply",
    "UploadReply",
]
