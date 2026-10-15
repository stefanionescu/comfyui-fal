"""Register the extension's nodes in menu order."""

from .files import FileAdd
from .model import ModelInfo
from comfy_api.latest import io
from .audio import AudioGenerate
from .image import ImageGenerate

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (ImageGenerate, AudioGenerate, FileAdd, ModelInfo)

__all__ = ["NODE_TYPES"]
