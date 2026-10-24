"""Turn fal's error replies into reviewed messages that carry fal's cleaned reason where it helps."""

from __future__ import annotations

import re
from http import HTTPStatus
import math
from typing import TYPE_CHECKING

from pydantic import ValidationError

from ..config.fal import DASHBOARD_URLS, REASON_ENDINGS, MAX_REASON_CHARACTERS
from ..state.errors import FalError, ErrorCode, RetryLaterError
from ..state.replies import ErrorReply, RefusalItem, RefusalReply, PlatformErrorReply
from ..config.patterns import REASON_PATTERNS
from ..config.messages.run import (
    NO_MEDIA,
    NO_REASON,
    SERVER_BUSY,
    KEY_REJECTED,
    RATE_LIMITED,
    ACCESS_DENIED,
    INPUT_REFUSED,
    MODEL_TIMEOUT,
    SERVER_FAILED,
    START_TIMEOUT,
    ACCOUNT_LOCKED,
    REQUEST_FAILED,
    FILE_UNREADABLE,
    REQUEST_REJECTED,
    REQUEST_CANCELLED,
    ENDPOINT_NOT_FOUND,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

_KEY = re.compile(REASON_PATTERNS['KEY'])
_URL = re.compile(REASON_PATTERNS['URL'])
_FAL_URL = re.compile(REASON_PATTERNS['FAL_URL'])
_LOCKED = re.compile(REASON_PATTERNS['LOCKED'])
# A refusal names at most this many refused values, so a long list does not hide the message.
_MAX_REFUSAL_ITEMS = 3
# The category and message of each error type that fal documents. The status decides every other type of a refused
# input, such as image_too_large, and the reason names the field and the text that fal sent.
_FAILURE_TYPES: dict[str, tuple[ErrorCode, str]] = {
    'content_policy_violation': (ErrorCode.REFUSED, INPUT_REFUSED),
    'no_media_generated': (ErrorCode.INVALID_INPUT, NO_MEDIA),
    'file_download_error': (ErrorCode.INVALID_INPUT, FILE_UNREADABLE),
    'image_load_error': (ErrorCode.INVALID_INPUT, FILE_UNREADABLE),
    'bad_request': (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    'validation_error': (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    'not_found': (ErrorCode.UNAVAILABLE, ENDPOINT_NOT_FOUND),
    'rate_limited': (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    'client_disconnected': (ErrorCode.UNAVAILABLE, REQUEST_CANCELLED),
    'client_cancelled': (ErrorCode.UNAVAILABLE, REQUEST_CANCELLED),
    'request_timeout': (ErrorCode.TIMEOUT, MODEL_TIMEOUT),
    'startup_timeout': (ErrorCode.TIMEOUT, MODEL_TIMEOUT),
    'generation_timeout': (ErrorCode.TIMEOUT, MODEL_TIMEOUT),
    'runner_scheduling_failure': (ErrorCode.TRANSPORT, SERVER_BUSY),
    'runner_connection_timeout': (ErrorCode.TRANSPORT, SERVER_BUSY),
    'runner_connection_refused': (ErrorCode.TRANSPORT, SERVER_BUSY),
    'runner_connection_error': (ErrorCode.TRANSPORT, SERVER_BUSY),
    'runner_disconnected': (ErrorCode.TRANSPORT, SERVER_BUSY),
    'runner_incomplete_response': (ErrorCode.TRANSPORT, SERVER_BUSY),
    'downstream_service_unavailable': (ErrorCode.TRANSPORT, SERVER_BUSY),
    'internal_server_error': (ErrorCode.TRANSPORT, SERVER_FAILED),
    'internal_error': (ErrorCode.TRANSPORT, SERVER_FAILED),
    'runner_server_error': (ErrorCode.TRANSPORT, SERVER_FAILED),
    'downstream_service_error': (ErrorCode.TRANSPORT, SERVER_FAILED),
    'server_error': (ErrorCode.TRANSPORT, SERVER_FAILED),
}
# The statuses that decide a failure whose type is missing or unlisted. For a 403, the reason decides.
_STATUS_FAILURES: dict[int, tuple[ErrorCode, str]] = {
    401: (ErrorCode.AUTHENTICATION, KEY_REJECTED),
    404: (ErrorCode.UNAVAILABLE, ENDPOINT_NOT_FOUND),
    422: (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    429: (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    499: (ErrorCode.UNAVAILABLE, REQUEST_CANCELLED),
}


def _choose_status_failure(status: int | None, message: str) -> tuple[ErrorCode, str]:
    """Choose the category and message of a status when the type names none.

    A request that completed with an error has no status, and its model failed the input. fal documents no type for
    a locked account, so a 403 whose reason names the balance, credits, or a lock is one. A redirect is never
    followed, so it is an unexpected reply.
    """
    if status is None:
        return ErrorCode.INVALID_INPUT, REQUEST_REJECTED
    if status == HTTPStatus.FORBIDDEN:
        is_locked = _LOCKED.search(message) is not None
        return (ErrorCode.CREDITS, ACCOUNT_LOCKED) if is_locked else (ErrorCode.AUTHENTICATION, ACCESS_DENIED)
    if HTTPStatus.BAD_REQUEST <= status < HTTPStatus.INTERNAL_SERVER_ERROR:
        return _STATUS_FAILURES.get(status, (ErrorCode.INVALID_INPUT, REQUEST_REJECTED))
    return ErrorCode.TRANSPORT, SERVER_FAILED if status >= HTTPStatus.INTERNAL_SERVER_ERROR else REQUEST_FAILED


def _sanitize_reason(message: str) -> str:
    """Remove the only private details a reason can carry, then shorten it.

    Links to the fal documentation and dashboard stay, without the scheme. This step removes other links, because file
    links are public to whoever holds them. It removes key-shaped text and request IDs too. The reason ends as a
    sentence, because a message can add its next step after it.
    """
    text = _URL.sub('', _FAL_URL.sub(r'\1', message))
    text = ' '.join(_KEY.sub('', text).split())
    if len(text) > MAX_REASON_CHARACTERS:
        text = text[: MAX_REASON_CHARACTERS - 1].rstrip() + '…'
    if text and not text.endswith(REASON_ENDINGS):
        text += '.'
    return text or NO_REASON


def _describe_refusal(item: RefusalItem) -> str:
    """Name one refused value by its field, without the leading body part, and give fal's text for it."""
    parts = item.loc[1:] if item.loc[:1] == ('body',) else item.loc
    field = '.'.join(str(part) for part in parts)
    text = f'{field}: {item.msg}' if field else item.msg
    if item.type == 'content_policy_violation' and item.categories:
        text += f' ({", ".join(item.categories)})'
    return text


def _read_refusal(body: bytes) -> tuple[str | None, str] | None:
    """Read a 422 list of refused values: the first listed type, and the first few values as the reason."""
    try:
        reply = RefusalReply.model_validate_json(body)
    except ValidationError:
        return None
    error_type = next((item.type for item in reply.detail if item.type in _FAILURE_TYPES), None)
    reason = '; '.join(_describe_refusal(item) for item in reply.detail[:_MAX_REFUSAL_ITEMS])
    return error_type, reason


def _read_reason(body: bytes, headers: Mapping[str, str]) -> tuple[str | None, str]:
    """Read the type and the reason of a failed reply, trying fal's three error shapes in turn.

    A string detail carries its type in the body or in the X-Fal-Error-Type header. The Platform API wraps its error
    in an object of its own.
    """
    refusal = _read_refusal(body)
    if refusal is not None:
        return refusal
    try:
        error = ErrorReply.model_validate_json(body)
    except ValidationError:
        pass
    else:
        return error.error_type or headers.get('X-Fal-Error-Type'), error.detail
    try:
        platform = PlatformErrorReply.model_validate_json(body).error
    except ValidationError:
        return headers.get('X-Fal-Error-Type'), ''
    return platform.type, platform.message


def _read_retry_after(headers: Mapping[str, str]) -> float | None:
    """Read the seconds a 429 asks to wait; a missing or non-numeric value gives none."""
    try:
        seconds = float(headers.get('Retry-After', ''))
    except ValueError:
        return None
    return seconds if math.isfinite(seconds) and seconds >= 0 else None


def build_failure(status: int | None, error_type: str | None, message: str) -> FalError:
    """Build the reviewed error for one fal failure, by its type and then its status, with the cleaned reason.

    The status is None for a request that completed with an error. A template without a reason placeholder drops the
    reason.
    """
    failure = _FAILURE_TYPES.get(error_type) if error_type else None
    category, template = failure if failure is not None else _choose_status_failure(status, message)
    text = template.format(reason=_sanitize_reason(message), status=status, **DASHBOARD_URLS)
    return FalError(category, text)


def read_failure(status: int, body: bytes, headers: Mapping[str, str]) -> FalError:
    """Read a failed reply's error document; a body that is not one gives no type and no reason.

    The header alone identifies a start timeout that the caller set. A 429 that names how long to wait becomes a
    RetryLaterError, which only free reads wait for.
    """
    if status == HTTPStatus.GATEWAY_TIMEOUT and headers.get('X-Fal-Request-Timeout-Type') == 'user':
        return FalError(ErrorCode.TIMEOUT, START_TIMEOUT)
    error_type, reason = _read_reason(body, headers)
    failure = build_failure(status, error_type, reason)
    seconds = _read_retry_after(headers) if status == HTTPStatus.TOO_MANY_REQUESTS else None
    if seconds is None:
        return failure
    return RetryLaterError(failure.code, str(failure), seconds)


__all__ = ['build_failure', 'read_failure']
