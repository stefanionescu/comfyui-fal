"""The names this extension uses in spaces shared with other packs."""

# Every node identifier is this prefix and the class name.
NODE_PREFIX = 'Fal'

# The menu headings ComfyUI groups the nodes under, in fal's lowercase spelling; 3D nodes are "mesh" in code
# because digits cannot start a name.
MENUS = {
    'SHARED': 'fal',
    'IMAGE': 'fal/Image',
    'VIDEO': 'fal/Video',
    'AUDIO': 'fal/Audio',
    'TEXT': 'fal/Text',
    'MESH': 'fal/3D',
}

# The socket types more than one node shares, prefixed so no other pack's socket of the same name connects.
SOCKET_TYPES = {
    'FILES': 'FAL_FILES',
    'OPTIONS': 'FAL_OPTIONS',
}

__all__ = [
    'MENUS',
    'NODE_PREFIX',
    'SOCKET_TYPES',
]
