"""Register the extension's nodes in menu order."""

from comfy_api.latest import io

from .files import FileAdd
from .model import ModelInfo
from .options import RequestOptions
from .download import RequestDownload
from .generate import MeshGenerate, TextGenerate, AudioGenerate, ImageGenerate, VideoGenerate

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    ImageGenerate,
    VideoGenerate,
    AudioGenerate,
    TextGenerate,
    MeshGenerate,
    FileAdd,
    RequestDownload,
    RequestOptions,
    ModelInfo,
)

__all__ = ['NODE_TYPES']
