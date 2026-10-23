"""Report what any fal model takes and makes, from fal's free listing."""

from __future__ import annotations

import re
import json
import asyncio
from comfy_api.latest import io
from ..comfy.runtime import get_runtime
from ..config.inputs import INPUT_NAMES
from ..fal.models import read_fal_model
from typing import TYPE_CHECKING, override
from ..comfy.execution import wait_for_request
from ..types.errors import ErrorCode, FalError
from ..config.namespace import MENUS, NODE_PREFIX
from ..config.patterns import ENDPOINT_ID_PATTERN
from ..config.models import KIND_NODES, DEFAULT_MODELS
from ..config.messages.models import MODEL_REPORT_EMPTY, MODEL_REPORT_UNKNOWN

if TYPE_CHECKING:
    from ..types import Json
    from ..types.models import FalModel, ModelField

_ENDPOINT_ID = re.compile(ENDPOINT_ID_PATTERN)


def _format_bound(value: float | None) -> Json:
    """Show a whole-number bound without a decimal point, as fal's schema writes it."""
    if value is None:
        return None
    return int(value) if value.is_integer() else value


def _describe_input(field: ModelField) -> dict[str, Json]:
    """Describe one input under the keys a paid node's arguments and a File: Add's field use."""
    is_file = field.input == "file"
    media = (field.media or "link") if is_file else None
    return {
        "field": field.name,
        "type": field.schema_type,
        "required": field.required,
        "default": field.default,
        "choices": list(field.choices) or None,
        "minimum": _format_bound(field.minimum),
        "maximum": _format_bound(field.maximum),
        "list": field.is_list,
        "max_items": field.max_items,
        "max_length": field.max_length,
        "file": is_file,
        "media": media,
        "description": field.description or None,
    }


def _format_report(model_id: str, model: FalModel) -> str:
    """Write the model's report as JSON: every key present, and null where fal gives no value."""
    outputs: list[Json] = [
        {
            "field": output.name,
            "type": output.schema_type,
            "list": output.is_list,
            "file": output.is_file,
            "text": output.name == model.text_field,
        }
        for output in model.outputs
    ]
    report: dict[str, Json] = {
        "model": model_id,
        "name": model.display_name,
        "kind": model.kind,
        "node": KIND_NODES[model.kind] if model.kind is not None else None,
        "category": model.category,
        "status": model.status,
        "updated": model.updated_at,
        "docs": model.docs_url,
        "description": model.description or None,
        "inputs": [_describe_input(field) for field in model.fields],
        "outputs": outputs,
    }
    return json.dumps(report, ensure_ascii=False)


async def _read_report(model_id: str) -> io.NodeOutput:
    """Read one model from fal's listing, free and with the key only when one is saved, and report it.

    An ID that cannot be one is refused without a read; one fal does not know is read again next time.
    """
    if not model_id:
        raise FalError(ErrorCode.INVALID_INPUT, MODEL_REPORT_EMPTY)
    if _ENDPOINT_ID.match(model_id) is None:
        raise FalError(ErrorCode.INVALID_INPUT, MODEL_REPORT_UNKNOWN.format(model=model_id))
    settings, credential = await asyncio.to_thread(get_runtime().configuration.read_listing_access)
    try:
        model = await read_fal_model(model_id, None, settings, credential)
    except FalError as error:
        if error.code is not ErrorCode.INVALID_INPUT:
            raise
        raise FalError(ErrorCode.INVALID_INPUT, MODEL_REPORT_UNKNOWN.format(model=model_id)) from None
    return io.NodeOutput(_format_report(model_id, model))


class ModelInfo(io.ComfyNode):
    """Report any fal model's inputs and outputs; it reads fal's free listing, so it needs no key and costs nothing."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the model ID and the JSON the node returns."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Model: Info",
            category=MENUS["SHARED"],
            description="Show the inputs any fal model takes and the files it makes, as JSON. Free, and needs no key.",
            inputs=[
                io.String.Input(
                    INPUT_NAMES["MODEL"],
                    default=DEFAULT_MODELS["image"],
                    tooltip="The model ID, its name on fal, such as alibaba/wan-3.0/reference-to-video. Each model's "
                    "page on fal.ai shows it.",
                )
            ],
            outputs=[io.String.Output("info", display_name="info")],
        )

    @classmethod
    @override
    async def execute(cls, *, model: str) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Read the model in an owned task, so ComfyUI's cancel stops a listing read."""
        return await wait_for_request(asyncio.create_task(_read_report(model.strip())))


__all__ = ["ModelInfo"]
