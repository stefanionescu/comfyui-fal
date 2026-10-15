"""Audio: Generate, the paid node for every fal model that makes audio."""

from typing import override
from comfy_api.latest import io
from .endpoint import EndpointNode
from ..config.namespace import MENUS, SOCKET_TYPES


class AudioGenerate(EndpointNode):
    """Make speech, music, sound effects, or stems with any fal audio model."""

    kind = "audio"
    outputs = (
        io.Audio.Output("audio", display_name="audio", is_output_list=True),
        io.Custom(SOCKET_TYPES["FILES"]).Output("files", display_name="files"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and the shared inputs."""
        return cls.build_schema(
            display_name="Audio: Generate",
            category=MENUS["AUDIO"],
            description="Make speech, music, sound effects, or stems with any fal audio model.",
        )


__all__ = ["AudioGenerate"]
