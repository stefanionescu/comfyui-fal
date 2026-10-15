"""The node IDs the shipped workflows place most, and the model IDs more than one family chooses."""

from src.config.namespace import NODE_PREFIX

IMAGE_GENERATE = f"{NODE_PREFIX}ImageGenerate"
FILE_ADD = f"{NODE_PREFIX}FileAdd"

__all__ = ["FILE_ADD", "IMAGE_GENERATE"]
