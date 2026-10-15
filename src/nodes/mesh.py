"""3D: Generate, the paid node for every fal model that makes a 3D model."""

from typing import override
from comfy_api.latest import io
from .endpoint import EndpointNode
from ..config.namespace import MENUS, SOCKET_TYPES


class MeshGenerate(EndpointNode):
    """Make a 3D model from images or a prompt with any fal 3D model."""

    kind = "mesh"
    outputs = (
        io.File3DAny.Output("model_3d", display_name="model_3d", is_output_list=True),
        io.Custom(SOCKET_TYPES["FILES"]).Output("files", display_name="files"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and the shared inputs."""
        return cls.build_schema(
            display_name="3D: Generate",
            category=MENUS["MESH"],
            description="Make a 3D model from images or a prompt with any fal 3D model.",
        )


__all__ = ["MeshGenerate"]
