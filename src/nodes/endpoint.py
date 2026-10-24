"""The paid node every kind node is: any fal model of its kind, named by its endpoint ID, and one request."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast, override
import asyncio
from functools import partial

from comfy_api.latest import io

from .base import PaidNode
from .outputs import build_node_outputs
from ..fal.models import read_fal_model
from ..comfy.media import encode_local_file
from ..state.queue import QueuedRequest
from ..config.media import OUTPUT_ID_KINDS
from ..state.errors import FalError
from ..comfy.runtime import get_runtime
from ..config.inputs import TOOLTIPS, RUN_NUMBER, INPUT_NAMES
from ..config.models import DEFAULT_MODELS
from ..fal.arguments import parse_arguments
from ..comfy.execution import send_request
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..fal.queue.operation import QueueOperation

if TYPE_CHECKING:
    from ..state import Kind
    from ..state.files import FalFile
    from ..state.models import MediaKind
    from ..state.options import Options


class EndpointNode(PaidNode):
    """Run one request to any fal model of the kind this node runs and fill the outputs of the node.

    Attributes:
        kind: What the models of the node make; the node refuses a model of another kind before any payment.
        display_name: The name ComfyUI shows for the node.
        description: The description ComfyUI shows for the node.
        outputs: The output sockets of the node in order; build_node_outputs fills them by ID.

    """

    kind: ClassVar[Kind]
    display_name: ClassVar[str]
    description: ClassVar[str]
    outputs: ClassVar[tuple[io.Output, ...]]

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe a kind node: the shared inputs, sockets first and text boxes last, and the kind's outputs."""
        inputs: list[io.Input] = [
            io.Custom(SOCKET_TYPES['FILES']).Input(INPUT_NAMES['FILES'], optional=True, tooltip=TOOLTIPS['FILES']),
            io.Custom(SOCKET_TYPES['OPTIONS']).Input(
                INPUT_NAMES['OPTIONS'], optional=True, tooltip=TOOLTIPS['OPTIONS']
            ),
            io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS[cls.kind], tooltip=TOOLTIPS['MODEL']),
            io.Int.Input(
                INPUT_NAMES['RUN_NUMBER'],
                default=RUN_NUMBER['DEFAULT'],
                min=RUN_NUMBER['MIN'],
                max=RUN_NUMBER['MAX'],
                tooltip=TOOLTIPS['RUN_NUMBER'],
            ),
            io.String.Input(INPUT_NAMES['PROMPT'], default='', multiline=True, tooltip=TOOLTIPS['PROMPT']),
            io.String.Input(INPUT_NAMES['ARGUMENTS'], default='', multiline=True, tooltip=TOOLTIPS['ARGUMENTS']),
        ]
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name=cls.display_name,
            category=MENUS[cls.kind.upper()],
            description=cls.description,
            inputs=inputs,
            outputs=list(cls.outputs),
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def validate_inputs(  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls validate_inputs with the inputs the schema declares.
        cls, model: object = None, prompt: object = None, arguments: object = None
    ) -> bool | str:
        """Make the free checks a typed model allows when ComfyUI queues the workflow: before any node runs or bills.

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
    @override
    async def send(
        cls,
        *,
        model: str,
        prompt: str = '',
        arguments: str = '',
        files: tuple[FalFile, ...] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Send one request and fill the outputs; the operation makes every check again, because a link skips them.

        ComfyUI sets hidden on the class it runs; a direct call from another pack has no node ID and no progress bar.
        """
        node_id = cls.hidden.unique_id if cls.hidden is not None else None  # pyright: ignore[reportUnnecessaryComparison] # reason: ComfyUI types hidden as always set, but a direct call runs the class itself, whose hidden is None.
        output_ids = tuple(output.id for output in cls.outputs if output.id is not None)
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
            cast('frozenset[MediaKind]', download_kinds),
        )
        runtime = get_runtime()
        operation = QueueOperation(request, runtime.requests, runtime.uploads, encode_local_file)
        return await send_request(operation.send, partial(build_node_outputs, output_ids=output_ids), node_id)


__all__ = ['EndpointNode']
