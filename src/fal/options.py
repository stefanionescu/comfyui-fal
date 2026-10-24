"""Turn Request Options into the queue submit's headers; fal's retries and fallbacks stay off unless allowed."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..config.options import HEADER_VALUES, LIFECYCLE_FIELD, REQUEST_HEADERS

if TYPE_CHECKING:
    from ..state.options import Options


def _build_choice_headers(options: Options) -> dict[str, str]:
    """Build the headers of the choices that send something only when set: priority, start timeout, expiry, storage."""
    headers: dict[str, str] = {}
    if options.queue_priority is not None:
        headers[REQUEST_HEADERS['QUEUE_PRIORITY']] = options.queue_priority
    if options.request_start_timeout is not None:
        headers[REQUEST_HEADERS['REQUEST_START_TIMEOUT']] = str(options.request_start_timeout)
    if options.expiration_duration_seconds is not None:
        lifecycle = {LIFECYCLE_FIELD: options.expiration_duration_seconds}
        headers[REQUEST_HEADERS['OBJECT_LIFECYCLE']] = json.dumps(lifecycle, separators=(',', ':'))
    if not options.can_store_payloads:
        headers[REQUEST_HEADERS['STORE_IO']] = HEADER_VALUES['STORE_IO_OFF']
    return headers


def build_request_headers(options: Options | None) -> dict[str, str]:
    """Build the headers of one queue submit; no Request Options reads as Request Options at its defaults.

    At the defaults, the submit sends only the two headers that keep the fal retries and fallbacks off.
    """
    headers: dict[str, str] = {}
    if options is None or not options.can_retry:
        headers[REQUEST_HEADERS['NO_RETRY']] = HEADER_VALUES['NO_RETRY']
    if options is None or not options.can_switch_model:
        headers[REQUEST_HEADERS['DISABLE_FALLBACK']] = HEADER_VALUES['DISABLE_FALLBACK']
    if options is not None:
        headers.update(_build_choice_headers(options))
    return headers


__all__ = ['build_request_headers']
