"""The paid node every kind node is: any fal model of its kind, named by its endpoint ID, and one request."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast, override
from functools import partial

from comfy_api.latest import io

from .base import PaidNode
from .outputs import build_node_outputs
from ..comfy.media import encode_local_file
from ..state.queue import QueuedRequest
from ..config.media import OUTPUT_ID_KINDS
from ..comfy.runtime import get_runtime
from ..config.inputs import (
    LINES,
    TEXTS,
    CHOICE,
    SWITCH,
    TOOLTIPS,
    RUN_NUMBER,
    INPUT_NAMES,
    TEXT_SETTINGS,
    NUMBER_MINIMUMS,
    NUMBER_SETTINGS,
    SWITCH_SETTINGS,
)
from ..config.models import DEFAULT_MODELS
from ..fal.arguments import parse_arguments
from ..comfy.execution import send_request
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..fal.queue.operation import QueueOperation

if TYPE_CHECKING:
    from ..state import Json, Kind
    from ..state.files import FalFile
    from ..state.models import FalModel, MediaKind
    from ..state.options import Options


def _build_settings(kind: Kind) -> list[io.Input]:
    """Build the named settings: a line per text setting, a dropdown per on/off setting, and a choice per number.

    A number setting at default sends nothing, and custom shows its value.
    """
    inputs: list[io.Input] = [io.String.Input(name, default='', tooltip=TOOLTIPS[name]) for name in TEXT_SETTINGS[kind]]
    inputs += [
        io.Combo.Input(name, options=list(SWITCH.values()), default=SWITCH['DEFAULT'], tooltip=TOOLTIPS[name])
        for name in SWITCH_SETTINGS[kind]
    ]
    for name, start in NUMBER_SETTINGS[kind].items():
        minimum, tooltip = NUMBER_MINIMUMS[name], TOOLTIPS[name]
        value = (
            io.Int.Input(CHOICE['VALUE'], default=start, min=int(minimum), tooltip=tooltip)
            if isinstance(start, int)
            else io.Float.Input(CHOICE['VALUE'], default=start, min=minimum, step=0.1, tooltip=tooltip)
        )
        options = [io.DynamicCombo.Option(CHOICE['DEFAULT'], []), io.DynamicCombo.Option(CHOICE['CUSTOM'], [value])]
        inputs.append(io.DynamicCombo.Input(name, options=options, tooltip=tooltip))
    return inputs


def _read_settings(kind: Kind, values: dict[str, object]) -> dict[str, Json]:
    """Read the named settings the workflow sets; an empty line, default, or no value from a caller sends nothing."""
    settings: dict[str, Json] = {}
    for name in TEXT_SETTINGS[kind]:
        text = values.get(name)
        if isinstance(text, str) and text.strip():
            settings[name] = text.strip()
    for name in SWITCH_SETTINGS[kind]:
        if values.get(name) in {SWITCH['ON'], SWITCH['OFF']}:
            settings[name] = values.get(name) == SWITCH['ON']
    for name in NUMBER_SETTINGS[kind]:
        choice = values.get(name)
        if isinstance(choice, dict) and cast('dict[str, Json]', choice).get(name) == CHOICE['CUSTOM']:
            settings[name] = cast('dict[str, Json]', choice).get(CHOICE['VALUE'])
    return settings


class EndpointNode(PaidNode):
    """Run one request to any fal model of the kind this node runs and fill the outputs of the node.

    Attributes:
        display_name: The name ComfyUI shows for the node.
        description: The description ComfyUI shows for the node.
        outputs: The output sockets of the node in order; build_node_outputs fills them by ID.

    """

    display_name: ClassVar[str]
    description: ClassVar[str]
    outputs: ClassVar[tuple[io.Output, ...]]

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe a kind node: sockets, the model, its named settings, the run number, then the text inputs."""
        lines = [
            io.String.Input(name, default=start, tooltip=TOOLTIPS[name]) for name, start in LINES[cls.kind].items()
        ]
        texts = [io.String.Input(name, default='', multiline=True, tooltip=TOOLTIPS[name]) for name in TEXTS[cls.kind]]
        inputs: list[io.Input] = [
            io.Custom(SOCKET_TYPES['FILES']).Input(INPUT_NAMES['FILES'], optional=True, tooltip=TOOLTIPS['FILES']),
            io.Custom(SOCKET_TYPES['OPTIONS']).Input(
                INPUT_NAMES['OPTIONS'], optional=True, tooltip=TOOLTIPS['OPTIONS']
            ),
            io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS[cls.kind], tooltip=TOOLTIPS['MODEL']),
            *_build_settings(cls.kind),
            io.Int.Input(
                INPUT_NAMES['RUN_NUMBER'],
                default=RUN_NUMBER['DEFAULT'],
                min=RUN_NUMBER['MIN'],
                max=RUN_NUMBER['MAX'],
                tooltip=TOOLTIPS['RUN_NUMBER'],
            ),
            *lines,
            *texts,
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
    def check(cls, model: FalModel, inputs: dict[str, object]) -> None:
        """Check the text inputs, the named settings, and the arguments that the workflow sets, against the model."""
        names = (*LINES[cls.kind], *TEXTS[cls.kind])
        texts = {name: value if isinstance(value := inputs.get(name), str) else None for name in names}
        arguments = inputs.get(INPUT_NAMES['ARGUMENTS'])
        parse_arguments(
            model, texts, _read_settings(cls.kind, inputs), arguments if isinstance(arguments, str) else None
        )

    @classmethod
    @override
    async def send(cls, node_id: str | None, **inputs: object) -> io.NodeOutput:
        """Send one request and fill the outputs; the operation makes every check again, because a link skips them."""
        output_ids = tuple(output.id for output in cls.outputs if output.id is not None)
        download_kinds = frozenset(
            OUTPUT_ID_KINDS[output_id] for output_id in output_ids if output_id in OUTPUT_ID_KINDS
        )
        request = QueuedRequest(
            model_id=str(inputs.get(INPUT_NAMES['MODEL'], DEFAULT_MODELS[cls.kind])).strip(),
            texts={name: str(inputs.get(name) or '') for name in (*LINES[cls.kind], *TEXTS[cls.kind])},
            settings=_read_settings(cls.kind, inputs),
            arguments=str(inputs.get(INPUT_NAMES['ARGUMENTS']) or ''),
            files=cast('tuple[FalFile, ...] | None', inputs.get(INPUT_NAMES['FILES'])) or (),
            options=cast('Options | None', inputs.get(INPUT_NAMES['OPTIONS'])),
            kind=cls.kind,
            download_kinds=cast('frozenset[MediaKind]', download_kinds),
        )
        runtime = get_runtime()
        operation = QueueOperation(request, runtime.requests, runtime.uploads, encode_local_file)
        return await send_request(operation.send, partial(build_node_outputs, output_ids=output_ids), node_id)


__all__ = ['EndpointNode']
