"""Register the extension's nodes in menu order."""

from .files import FileAdd
from .model import ModelInfo
from .text import TextGenerate
from comfy_api.latest import io
from .audio import AudioGenerate
from .image import ImageGenerate
from .video import VideoGenerate
from .options import RequestOptions
from .download import RequestDownload

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    ImageGenerate,
    VideoGenerate,
    AudioGenerate,
    TextGenerate,
    FileAdd,
    RequestDownload,
    RequestOptions,
    ModelInfo,
)

__all__ = ["NODE_TYPES"]
