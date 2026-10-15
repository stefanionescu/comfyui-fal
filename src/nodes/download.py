"""Collect a recorded fal request that kept running after a cancel, a restart, or a timeout."""

from __future__ import annotations

import re
import asyncio
from functools import partial
from comfy_api.latest import io
from ..comfy.runtime import get_runtime
from ..fal.models import read_fal_model
from .outputs import build_node_outputs
from ..config.media import OUTPUT_ID_KINDS
from ..types.errors import ErrorCode, FalError
from ..config.patterns import REQUEST_ID_PATTERN
from typing import TYPE_CHECKING, cast, override
from ..fal.queue.operation import CollectOperation
from ..config.messages.queue import REQUEST_UNKNOWN
from ..fal.queue.records import list_request_labels
from ..comfy.execution import send_request, wait_for_request
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES

if TYPE_CHECKING:
    from ..types.queue import RequestRecord
    from ..types.models import FalModel, MediaKind

_REQUEST_ID = re.compile(REQUEST_ID_PATTERN)
# Every output of every kind node, in the order the nodes list them; Request: Download fills whichever the request made.
_OUTPUTS = (
    io.Image.Output("images", display_name="images", is_output_list=True),
    io.Mask.Output("masks", display_name="masks", is_output_list=True),
    io.Video.Output("video", display_name="video", is_output_list=True),
    io.Audio.Output("audio", display_name="audio", is_output_list=True),
    io.String.Output("text", display_name="text"),
    io.File3DAny.Output("model_3d", display_name="model_3d", is_output_list=True),
    io.Custom(SOCKET_TYPES["FILES"]).Output("files", display_name="files"),
    io.String.Output("result", display_name="result"),
)


async def _read_model(record: RequestRecord) -> FalModel | None:
    """Read the request's model from fal's free listing, so the text output reads the model's own text field.

    A model fal no longer lists, or a failed read, gives None: collecting the request must not depend on it.
    """
    settings, credential = await asyncio.to_thread(get_runtime().configuration.read_listing_access)
    try:
        return await read_fal_model(record.endpoint_id, None, settings, credential)
    except FalError:
        return None


async def _download_request(request_id: str, node_id: str | None) -> io.NodeOutput:
    """Read the request's record, wait for it, and download every file any output can show."""
    requests = get_runtime().requests
    record = await asyncio.to_thread(requests.read, request_id)
    model = await _read_model(record)
    kinds: frozenset[MediaKind] = cast("frozenset[MediaKind]", frozenset(OUTPUT_ID_KINDS.values()))
    operation = CollectOperation(record, requests, model, kinds)
    output_ids = tuple(output.id for output in _OUTPUTS)
    return await send_request(operation, partial(build_node_outputs, output_ids=output_ids), node_id)


class RequestDownload(io.ComfyNode):
    """Collect one recorded request of any kind and return everything it made; collecting bills nothing.

    The same request always gives the same outputs, so ComfyUI's cache is correct and this is not a paid node.
    """

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the recorded requests when ComfyUI builds the node definitions; the R key reads them again."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Request: Download",
            category=MENUS["SHARED"],
            description="Collect a fal request that kept running after a cancel, a restart, or a timeout. It bills "
            "nothing.",
            inputs=[
                io.Combo.Input(
                    "request",
                    options=list_request_labels(get_runtime().requests),
                    tooltip="A request recorded on this server. Press R to list requests recorded later.",
                )
            ],
            outputs=list(_OUTPUTS),
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    def validate_inputs(cls, **inputs: object) -> bool | str:
        """Take a request recorded after the node definitions were built, as long as the label starts with its ID.

        ComfyUI skips its own list check only for inputs the validator takes as positional or extra keywords.
        """
        return True if _REQUEST_ID.match(str(inputs.get("request", "")).split(" ", 1)[0]) else REQUEST_UNKNOWN

    @classmethod
    @override
    async def execute(cls, *, request: str = "") -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Collect the chosen request in an owned task, so ComfyUI's cancel stops the wait and keeps the record."""
        request_id = request.split(" ", 1)[0]
        if _REQUEST_ID.match(request_id) is None:
            raise FalError(ErrorCode.INVALID_INPUT, REQUEST_UNKNOWN)
        return await wait_for_request(asyncio.create_task(_download_request(request_id, cls.hidden.unique_id)))


__all__ = ["RequestDownload"]
