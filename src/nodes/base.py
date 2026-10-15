"""Share the cache key and the run-number input across the paid nodes."""

from typing import ClassVar
from comfy_api.latest import io
from collections.abc import Callable, Awaitable


class PaidNode(io.ComfyNode):
    """Own the run-number input every paid node shares.

    Attributes:
        send: Typed entry point that receives every saved input except the run number.

    """

    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]


__all__ = ["PaidNode"]
