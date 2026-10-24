"""The cache key, the run number, and the free checks that every paid node shares."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override
import asyncio

from comfy_api.latest import io

from ..fal.models import read_fal_model
from ..state.errors import FalError
from ..comfy.runtime import get_runtime
from ..config.inputs import INPUT_NAMES

if TYPE_CHECKING:
    from collections.abc import Callable, Awaitable

    from ..state import Kind
    from ..state.models import FalModel


class PaidNode(io.ComfyNode):
    """A node that sends a billed request, with the cache key, checks, and run-number input every paid node shares.

    Attributes:
        kind: What the models of the node make; the node refuses a model of another kind before paying.
        check: The free checks of the node against its model, which raise FalError. A value fed by a link is missing
            until the workflow runs, and the node checks it then.
        send: The typed entry point of the node, which receives the ID of the node, or None for a direct call, and every
            saved input except the run number.

    """

    kind: ClassVar[Kind]
    check: ClassVar[Callable[[FalModel, dict[str, object]], None]]
    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]

    @classmethod
    @override
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the API key's token to the cache key, so a new key runs the node again."""
        configuration = await asyncio.to_thread(get_runtime().configuration.read_configuration)
        return configuration.generation

    @classmethod
    @override
    async def validate_inputs(cls, **inputs: object) -> bool | str:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI passes every input by name, the dynamic settings included.
        """Read the model and make the free checks when ComfyUI queues the workflow, before any node runs, and bills.

        ComfyUI hands a validator every dynamic setting, whatever inputs it names, so this one takes every input.
        ComfyUI then skips its own range and choice checks, and fal checks each value itself, free.
        """
        model = inputs.get(INPUT_NAMES['MODEL'])
        if not isinstance(model, str):
            return True
        try:
            settings, credential = await asyncio.to_thread(get_runtime().configuration.read_listing_access)
            cls.check(await read_fal_model(model, cls.kind, settings, credential), inputs)
        except FalError as error:
            return str(error)
        return True

    @classmethod
    @override
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI awaits an async execute with the inputs the schema declares.
        """Drop the run number, which only defeats the cache of ComfyUI, and send.

        ComfyUI sets hidden on the class it runs; a direct call from another pack has no node ID and no progress bar.
        """
        inputs.pop(INPUT_NAMES['RUN_NUMBER'], None)
        node_id = cls.hidden.unique_id if cls.hidden is not None else None  # pyright: ignore[reportUnnecessaryComparison] # reason: a direct call runs the class itself, whose hidden is None.
        return await cls.send(node_id, **inputs)


__all__ = ['PaidNode']
