"""Read one model from fal's live listing before a request is paid, sharing reads and keeping each model.

Each model is kept for the life of the process. The listing is free; the API key, when one is saved, only raises
fal's rate limit.
"""

from __future__ import annotations

import re
import time
import asyncio
import weakref
from yarl import URL
from .schema import parse_model
from typing import TYPE_CHECKING
from .transport import send_lookup
from pydantic import ValidationError
from ..config.fal import PLATFORM_URLS
from ..types.models import ListingReply
from ..config.patterns import ENDPOINT_ID_PATTERN
from ..types.errors import ErrorCode, FalError, RetryLaterError
from ..config.models import KIND_NODES, DEFAULT_MODELS, OPENAPI_EXPAND, PLATFORM_SPACING_SECONDS
from ..config.messages.models import (
    KIND_NAMES,
    MODEL_FORM,
    MODEL_KIND,
    MODEL_EMPTY,
    MODEL_UNKNOWN,
    MODEL_LEFT_OUT,
    LEFT_OUT_REASONS,
    MODEL_LISTING_BUSY,
    MODEL_LISTING_UNREADABLE,
)

if TYPE_CHECKING:
    from ..types import Kind
    from ..types.models import FalModel
    from ..types.settings import Settings
    from ..types.credentials import Credential

_ENDPOINT_ID = re.compile(ENDPOINT_ID_PATTERN)
# Each model is read once per ComfyUI process; an unknown ID is read again, since it may be fixed.
_MODELS: dict[str, FalModel] = {}
# The reads in flight on each event loop, keyed by model ID, which callers asking at the same time share.
_READS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, dict[str, asyncio.Task[FalModel | None]]] = (
    weakref.WeakKeyDictionary()
)


def _delete_read(
    reads: dict[str, asyncio.Task[FalModel | None]], model_id: str, read: asyncio.Task[FalModel | None]
) -> None:
    """Drop a finished read, so a later caller reads the listing again when this one kept nothing.

    Its failure already reached every caller still waiting; taking it here keeps a read whose callers all cancelled
    from failing unseen.
    """
    del reads[model_id]
    if not read.cancelled():
        read.exception()


async def _wait_for_listing(error: FalError, deadline: float) -> None:
    """Wait as long as fal's 429 asks, or the usual spacing when it names no wait, within the request timeout."""
    seconds = error.seconds if isinstance(error, RetryLaterError) else PLATFORM_SPACING_SECONDS
    if time.monotonic() + seconds > deadline:
        raise FalError(ErrorCode.RATE_LIMITED, MODEL_LISTING_BUSY.format(seconds=round(seconds)))
    await asyncio.sleep(seconds)


async def _download_model(model_id: str, settings: Settings, credential: Credential | None) -> FalModel | None:
    """Read one model's listing entry and OpenAPI document; None when fal does not know the ID.

    These reads are free, so a 429 is waited out and read again until the request timeout passes. Any other failure
    stops the run, and nothing is kept.
    """
    url = str(URL(PLATFORM_URLS["MODELS"]).with_query({"endpoint_id": model_id, "expand": OPENAPI_EXPAND}))
    deadline = time.monotonic() + settings.request_timeout_seconds
    while True:
        try:
            reply = await send_lookup(url, settings, credential)
        except FalError as error:
            if error.code is ErrorCode.UNAVAILABLE:
                return None
            if error.code is not ErrorCode.RATE_LIMITED:
                raise
            await _wait_for_listing(error, deadline)
            continue
        try:
            models = ListingReply.model_validate(reply).models
        except ValidationError:
            raise FalError(ErrorCode.TRANSPORT, MODEL_LISTING_UNREADABLE) from None
        return parse_model(models[0]) if models else None


async def _read_listing(model_id: str, settings: Settings, credential: Credential | None) -> FalModel | None:
    """Read one model, sharing the read with every caller that asks for it at the same time.

    A task belongs to its event loop, and ComfyUI runs each prompt on a new one, so the reads in flight are kept per
    loop. A caller's cancel leaves the read running for the others.
    """
    reads = _READS.setdefault(asyncio.get_running_loop(), {})
    task = reads.get(model_id)
    if task is None:
        task = reads[model_id] = asyncio.create_task(_download_model(model_id, settings, credential))
        task.add_done_callback(lambda done: _delete_read(reads, model_id, done))
    return await asyncio.shield(task)


async def read_fal_model(
    model_id: str, kind: Kind | None, settings: Settings, credential: Credential | None
) -> FalModel:
    """Read one model from fal's listing, refusing an ID that cannot be one and one fal does not know.

    A paid node passes its kind, and a model no node runs, or that another node runs, is refused too. Model: Info
    passes no kind.
    """
    example = DEFAULT_MODELS[kind or "image"]
    model_id = model_id.strip()
    if not model_id:
        raise FalError(ErrorCode.INVALID_INPUT, MODEL_EMPTY.format(example=example))
    if not _ENDPOINT_ID.match(model_id):
        raise FalError(ErrorCode.INVALID_INPUT, MODEL_FORM.format(model=model_id, example=example))
    model = _MODELS.get(model_id) or await _read_listing(model_id, settings, credential)
    if model is None:
        raise FalError(ErrorCode.INVALID_INPUT, MODEL_UNKNOWN.format(model=model_id))
    _MODELS[model_id] = model
    if kind is not None and model.left_out is not None:
        reason = LEFT_OUT_REASONS[model.left_out]
        raise FalError(ErrorCode.INVALID_INPUT, MODEL_LEFT_OUT.format(model=model_id, reason=reason))
    if kind is not None and model.kind is not None and model.kind != kind:
        names = {"made": KIND_NAMES[model.kind], "node": KIND_NODES[model.kind], "this": KIND_NODES[kind]}
        raise FalError(ErrorCode.INVALID_INPUT, MODEL_KIND.format(model=model_id, **names))
    return model


__all__ = ["read_fal_model"]
