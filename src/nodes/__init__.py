"""Register the extension's nodes in menu order."""

from .files import FileAdd
from .model import ModelInfo
from comfy_api.latest import io
from .image import ImageGenerate

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (ImageGenerate, FileAdd, ModelInfo)

__all__ = ["NODE_TYPES"]
