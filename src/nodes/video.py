"""Video: Generate, the paid node for every fal model that makes a video."""

from typing import override
from comfy_api.latest import io
from .endpoint import EndpointNode
from ..config.namespace import MENUS, SOCKET_TYPES


class VideoGenerate(EndpointNode):
    """Make, edit, extend, or upscale a video with any fal video model."""

    kind = "video"
    outputs = (
        io.Video.Output("video", display_name="video", is_output_list=True),
        io.Custom(SOCKET_TYPES["FILES"]).Output("files", display_name="files"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and the shared inputs."""
        return cls.build_schema(
            display_name="Video: Generate",
            category=MENUS["VIDEO"],
            description="Make, edit, extend, or upscale a video with any fal video model.",
        )


__all__ = ["VideoGenerate"]
