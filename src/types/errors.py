"""Errors that can be shown without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for the messages a person sees."""

    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    CREDITS = "credits"
    INVALID_INPUT = "invalid_input"
    REFUSED = "refused"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    TRANSPORT = "transport"
    UNCERTAIN = "uncertain"
    INTERRUPTED = "interrupted"
    CONFLICT = "conflict"
    MEDIA = "media"


class FalError(RuntimeError):
    """Show reviewed text; fal's cleaned reason, when there is one, is already part of it."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Store the complete message and its category."""
        super().__init__(message)
        self.code = code


class RetryLaterError(FalError):
    """A refusal that names how long to wait before reading again; only free reads wait for it.

    Attributes:
        seconds: The wait fal asked for in its Retry-After header.

    """

    def __init__(self, code: ErrorCode, message: str, seconds: float) -> None:
        """Store the message, its category, and the wait."""
        super().__init__(code, message)
        self.seconds = seconds


__all__ = ["ErrorCode", "FalError", "RetryLaterError"]
