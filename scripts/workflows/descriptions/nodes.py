"""The node IDs the shipped workflows place, and the model IDs more than one family chooses."""

from src.config.namespace import NODE_PREFIX

IMAGE_GENERATE = f'{NODE_PREFIX}ImageGenerate'
VIDEO_GENERATE = f'{NODE_PREFIX}VideoGenerate'
AUDIO_GENERATE = f'{NODE_PREFIX}AudioGenerate'
TEXT_GENERATE = f'{NODE_PREFIX}TextGenerate'
MESH_GENERATE = f'{NODE_PREFIX}MeshGenerate'
FILE_ADD = f'{NODE_PREFIX}FileAdd'
MODEL_LOOKUP = f'{NODE_PREFIX}ModelInfo'
REQUEST_OPTIONS = f'{NODE_PREFIX}RequestOptions'
REQUEST_DOWNLOAD = f'{NODE_PREFIX}RequestDownload'
SPEECH_MODEL = 'elevenlabs/tts/eleven-v4'

__all__ = [
    'AUDIO_GENERATE',
    'FILE_ADD',
    'IMAGE_GENERATE',
    'MESH_GENERATE',
    'MODEL_LOOKUP',
    'REQUEST_DOWNLOAD',
    'REQUEST_OPTIONS',
    'SPEECH_MODEL',
    'TEXT_GENERATE',
    'VIDEO_GENERATE',
]
