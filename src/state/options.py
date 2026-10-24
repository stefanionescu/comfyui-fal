"""fal's request headers from a Request Options node."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Options:
    """The headers to add to one queue submit.

    Attributes:
        queue_priority: `low`, or None for fal's default, normal.
        request_start_timeout: Seconds fal waits for a runner before it drops the request unbilled, or None.
        can_retry: True lets fal run the request again after a server error; the extension's default is False.
        can_switch_model: True lets fal send the request to a fallback model; the extension's default is False.
        expiration_duration_seconds: How long the files the request makes stay on fal storage, or None for the
            account's setting.
        can_store_payloads: False asks fal to keep no input and output JSON for the request.

    """

    queue_priority: str | None
    request_start_timeout: int | None
    can_retry: bool
    can_switch_model: bool
    expiration_duration_seconds: int | None
    can_store_payloads: bool


__all__ = ['Options']
