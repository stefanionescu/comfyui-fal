"""Register the extension's nodes in menu order."""

from comfy_api.latest import io

NODE_TYPES: tuple[type[io.ComfyNode], ...] = ()

__all__ = ["NODE_TYPES"]
