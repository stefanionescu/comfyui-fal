"""Fill a fal node's outputs from what its request made."""

from __future__ import annotations

import json
from comfy_api.latest import io
from typing import TYPE_CHECKING
from comfy_execution.graph import ExecutionBlocker
from ..comfy.media import decode_mesh, decode_audio, decode_video, decode_images

if TYPE_CHECKING:
    from ..types.files import FalFile
    from collections.abc import Sequence
    from ..types.queue import RequestResult


def _list_contents(result: RequestResult, kind: str) -> list[tuple[FalFile, bytes]]:
    """List the downloaded files of one kind with their bytes, in result order."""
    files = result.files
    contents = [(output.file, output.content) for output in files if output.file.kind == kind]
    return [(file, content) for file, content in contents if content is not None]


def build_node_outputs(result: RequestResult, output_ids: Sequence[str]) -> io.NodeOutput:
    """Return one value per output ID, in the order given, decoding only the files those outputs show.

    An empty list, no text, and no files block the nodes connected to them; result is always filled.
    """
    values: dict[str, object] = {
        "text": result.text,
        "files": tuple(output.file for output in result.files),
        "result": json.dumps(result.result, indent=2, ensure_ascii=False),
    }
    if {"images", "masks"} & set(output_ids):
        images, masks = decode_images([content for _, content in _list_contents(result, "image")])
        values.update(images=list(images), masks=list(masks))
    if "video" in output_ids:
        values["video"] = [decode_video(content) for _, content in _list_contents(result, "video")]
    if "audio" in output_ids:
        values["audio"] = [decode_audio(content) for _, content in _list_contents(result, "audio")]
    if "model_3d" in output_ids:
        values["model_3d"] = [decode_mesh(content, file) for file, content in _list_contents(result, "mesh")]
    return io.NodeOutput(*(values.get(output_id) or ExecutionBlocker(None) for output_id in output_ids))


__all__ = ["build_node_outputs"]
