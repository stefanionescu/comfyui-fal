"""Text: Generate, the paid node for every fal model that makes text."""

from typing import override
from comfy_api.latest import io
from .endpoint import EndpointNode
from ..config.namespace import MENUS, SOCKET_TYPES


class TextGenerate(EndpointNode):
    """Transcribe speech, describe images and video, or answer with any fal text model."""

    kind = "text"
    outputs = (
        io.String.Output("text", display_name="text"),
        io.Custom(SOCKET_TYPES["FILES"]).Output("files", display_name="files"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and the shared inputs."""
        return cls.build_schema(
            display_name="Text: Generate",
            category=MENUS["TEXT"],
            description="Transcribe speech, describe images and video, or answer with any fal text model.",
        )


__all__ = ["TextGenerate"]
