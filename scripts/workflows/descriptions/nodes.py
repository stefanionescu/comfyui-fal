"""The node IDs the shipped workflows place most, and the model IDs more than one family chooses."""

from src.config.namespace import NODE_PREFIX

IMAGE_GENERATE = f"{NODE_PREFIX}ImageGenerate"
VIDEO_GENERATE = f"{NODE_PREFIX}VideoGenerate"
AUDIO_GENERATE = f"{NODE_PREFIX}AudioGenerate"
FILE_ADD = f"{NODE_PREFIX}FileAdd"
ELEVEN_V4 = "elevenlabs/tts/eleven-v4"

__all__ = ["AUDIO_GENERATE", "ELEVEN_V4", "FILE_ADD", "IMAGE_GENERATE", "VIDEO_GENERATE"]
