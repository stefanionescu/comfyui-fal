"""Image: Generate, the paid node for every fal model that makes images."""

from typing import override
from comfy_api.latest import io
from .endpoint import EndpointNode
from ..config.namespace import MENUS, SOCKET_TYPES


class ImageGenerate(EndpointNode):
    """Generate, edit, upscale, or cut out images with any fal image model."""

    kind = "image"
    outputs = (
        io.Image.Output("images", display_name="images", is_output_list=True),
        io.Mask.Output("masks", display_name="masks", is_output_list=True),
        io.Custom(SOCKET_TYPES["FILES"]).Output("files", display_name="files"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and the shared inputs."""
        return cls.build_schema(
            display_name="Image: Generate",
            category=MENUS["IMAGE"],
            description="Generate, edit, upscale, or cut out images with any fal image model.",
        )


__all__ = ["ImageGenerate"]
