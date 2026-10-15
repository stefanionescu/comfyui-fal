"""The paid node every kind node is: any fal model of its kind, named by its endpoint ID, and one request."""

from __future__ import annotations

import asyncio
from .base import PaidNode
from functools import partial
from comfy_api.latest import io
from ..types.errors import FalError
from ..comfy.runtime import get_runtime
from ..fal.models import read_fal_model
from ..types.queue import QueuedRequest
from .outputs import build_node_outputs
from ..comfy.execution import send_request
from ..config.media import OUTPUT_ID_KINDS
from ..config.models import DEFAULT_MODELS
from ..comfy.media import encode_local_file
from ..fal.arguments import parse_arguments
from ..fal.queue.operation import QueueOperation
from ..config.namespace import NODE_PREFIX, SOCKET_TYPES
from typing import TYPE_CHECKING, ClassVar, cast, override
from ..config.inputs import TOOLTIPS, RUN_NUMBER, INPUT_NAMES

if TYPE_CHECKING:
    from ..types import Kind
    from ..types.files import FalFile
    from ..types.options import Options
    from ..types.models import MediaKind


class EndpointNode(PaidNode):
    """Run one request to any fal model of the node's kind and fill the node's outputs.

    Attributes:
        kind: What the node's models make; a model of another kind is refused before paying.
        outputs: The node's output sockets in order; build_node_outputs fills them by ID.

    """

    kind: ClassVar[Kind]
    outputs: ClassVar[tuple[io.Output, ...]]

    @classmethod
    def build_schema(cls, *, display_name: str, category: str, description: str) -> io.Schema:
        """Describe a kind node: the shared inputs, sockets first and text boxes last, and the kind's outputs."""
        node_id = f"{NODE_PREFIX}{cls.__name__}"
        inputs: list[io.Input] = [
            io.Custom(SOCKET_TYPES["FILES"]).Input(INPUT_NAMES["FILES"], optional=True, tooltip=TOOLTIPS["FILES"]),
            io.Custom(SOCKET_TYPES["OPTIONS"]).Input(
                INPUT_NAMES["OPTIONS"], optional=True, tooltip=TOOLTIPS["OPTIONS"]
            ),
            io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS[cls.kind], tooltip=TOOLTIPS["MODEL"]),
            io.Int.Input(
                INPUT_NAMES["RUN_NUMBER"],
                default=RUN_NUMBER["DEFAULT"],
                min=RUN_NUMBER["MIN"],
                max=RUN_NUMBER["MAX"],
                tooltip=TOOLTIPS["RUN_NUMBER"],
            ),
            io.String.Input(INPUT_NAMES["PROMPT"], default="", multiline=True, tooltip=TOOLTIPS["PROMPT"]),
            io.String.Input(INPUT_NAMES["ARGUMENTS"], default="", multiline=True, tooltip=TOOLTIPS["ARGUMENTS"]),
        ]
        return io.Schema(
            node_id=node_id,
            display_name=display_name,
            category=category,
            description=description,
            inputs=inputs,
            outputs=list(cls.outputs),
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def validate_inputs(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, model: object = None, prompt: object = None, arguments: object = None
    ) -> bool | str:
        """Make the free checks a typed model allows when the workflow is queued, before any node runs or bills.

        A value fed by a link is None until the workflow runs, and send makes its checks then. ComfyUI skips its own
        checks only for the inputs named here, so run_number keeps its range check.
        """
        if not isinstance(model, str):
            return True
        try:
            settings, credential = await asyncio.to_thread(get_runtime().configuration.read_listing_access)
            fal_model = await read_fal_model(model, cls.kind, settings, credential)
            texts = (prompt if isinstance(prompt, str) else None, arguments if isinstance(arguments, str) else None)
            parse_arguments(fal_model, *texts)
        except FalError as error:
            return str(error)
        return True

    @classmethod
    async def send(
        cls,
        *,
        model: str,
        prompt: str = "",
        arguments: str = "",
        files: tuple[FalFile, ...] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Send one request and fill the outputs; the operation makes every check again, since a link skips them.

        ComfyUI sets hidden on the class it runs; a direct call from another pack has no node ID and no progress bar.
        """
        node_id = cls.hidden.unique_id if cls.hidden is not None else None  # pyright: ignore[reportUnnecessaryComparison] -- reason: ComfyUI types hidden as always set, but a direct call runs the class itself, whose hidden is None.
        output_ids = tuple(output.id for output in cls.outputs)
        download_kinds = frozenset(
            OUTPUT_ID_KINDS[output_id] for output_id in output_ids if output_id in OUTPUT_ID_KINDS
        )
        request = QueuedRequest(
            model.strip(),
            prompt,
            arguments,
            files or (),
            options,
            cls.kind,
            cast("frozenset[MediaKind]", download_kinds),
        )
        runtime = get_runtime()
        operation = QueueOperation(request, runtime.requests, runtime.uploads, encode_local_file)
        return await send_request(operation, partial(build_node_outputs, output_ids=output_ids), node_id)


__all__ = ["EndpointNode"]
