"""Share the cache key and the run number of the paid nodes."""

from __future__ import annotations

import asyncio
from comfy_api.latest import io
from ..comfy.runtime import get_runtime
from ..config.inputs import INPUT_NAMES
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Callable, Awaitable


class PaidNode(io.ComfyNode):
    """Own the cache key and the run-number input every paid node shares.

    Attributes:
        send: Typed entry point that receives every saved input except the run number.

    """

    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]

    @classmethod
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the API key's token to the cache key, so a new key runs the node again."""
        snapshot = await asyncio.to_thread(get_runtime().configuration.read_snapshot)
        return snapshot.generation

    @classmethod
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI awaits an async execute.
        """Drop the run number, which ComfyUI uses to invalidate its cache, and send."""
        inputs.pop(INPUT_NAMES["RUN_NUMBER"], None)
        return await cls.send(**inputs)


__all__ = ["PaidNode"]
