"""The paid kind nodes: Image, Video, Audio, Text, and 3D: Generate, each for every fal model of its kind."""

from __future__ import annotations

from typing import ClassVar

from comfy_api.latest import io

from .endpoint import EndpointNode
from ..config.namespace import SOCKET_TYPES

# The files and the result that every kind node returns after what its kind makes.
_FILES = io.Custom(SOCKET_TYPES['FILES']).Output('files', display_name='files')
_RESULT = io.String.Output('result', display_name='result')


class ImageGenerate(EndpointNode):
    """Generate, edit, upscale, or cut out images with any fal image model."""

    kind = 'image'
    display_name = 'Image: Generate'
    description = 'Generate, edit, upscale, or cut out images with any fal image model.'
    outputs: ClassVar[tuple[io.Output, ...]] = (
        io.Image.Output('images', display_name='images', is_output_list=True),
        io.Mask.Output('masks', display_name='masks', is_output_list=True),
        _FILES,
        _RESULT,
    )


class VideoGenerate(EndpointNode):
    """Make, edit, extend, or upscale a video with any fal video model."""

    kind = 'video'
    display_name = 'Video: Generate'
    description = 'Make, edit, extend, or upscale a video with any fal video model.'
    outputs: ClassVar[tuple[io.Output, ...]] = (
        io.Video.Output('video', display_name='video', is_output_list=True),
        _FILES,
        _RESULT,
    )


class AudioGenerate(EndpointNode):
    """Make speech, music, sound effects, or stems with any fal audio model."""

    kind = 'audio'
    display_name = 'Audio: Generate'
    description = 'Make speech, music, sound effects, or stems with any fal audio model.'
    outputs: ClassVar[tuple[io.Output, ...]] = (
        io.Audio.Output('audio', display_name='audio', is_output_list=True),
        _FILES,
        _RESULT,
    )


class TextGenerate(EndpointNode):
    """Transcribe speech, describe images and video, or answer with any fal text model."""

    kind = 'text'
    display_name = 'Text: Generate'
    description = 'Transcribe speech, describe images and video, or answer with any fal text model.'
    outputs: ClassVar[tuple[io.Output, ...]] = (
        io.String.Output('text', display_name='text'),
        _FILES,
        _RESULT,
    )


class MeshGenerate(EndpointNode):
    """Make a 3D model from images or a prompt with any fal 3D model."""

    kind = 'mesh'
    display_name = '3D: Generate'
    description = 'Make a 3D model from images or a prompt with any fal 3D model.'
    outputs: ClassVar[tuple[io.Output, ...]] = (
        io.File3DAny.Output('model_3d', display_name='model_3d', is_output_list=True),
        _FILES,
        _RESULT,
    )


__all__ = ['AudioGenerate', 'ImageGenerate', 'MeshGenerate', 'TextGenerate', 'VideoGenerate']
