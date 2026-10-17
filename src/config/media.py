"""How ComfyUI media is encoded for fal storage, and how the files fal returns are sorted by kind."""

# A ComfyUI IMAGE tensor: batch, height, width, and three or four channels.
IMAGE_TENSOR = {
    "DIMENSIONS": 4,
    "RGB_CHANNELS": 3,
    "RGBA_CHANNELS": 4,
}

# A ComfyUI MASK: a batch of height-by-width frames, or one frame alone.
MASK_TENSOR = {
    "DIMENSIONS": 3,
    "FRAME_DIMENSIONS": 2,
}

# What each kind of local media is uploaded as: lossless WebP for images, lossless PNG for masks, 16-bit WAV, and MP4.
ENCODED_FORMATS = {
    "image": {"CONTENT_TYPE": "image/webp", "EXTENSION": "webp"},
    "mask": {"CONTENT_TYPE": "image/png", "EXTENSION": "png"},
    "audio": {"CONTENT_TYPE": "audio/wav", "EXTENSION": "wav"},
    "video": {"CONTENT_TYPE": "video/mp4", "EXTENSION": "mp4"},
}

# How an image is encoded as lossless WebP: the same pixels as a PNG in about a quarter to a third less, which every
# fal model that takes images reads. Method 1 encodes in a fraction of the slowest setting's time within 2% of its size,
# and exact keeps the colors under fully see-through pixels.
WEBP = {"METHOD": 1, "QUALITY": 0}

# The WAV container and codec PyAV writes audio with.
WAV = {
    "FORMAT": "wav",
    "CODEC": "pcm_s16le",
}

# An uploaded file is named by its kind and the start of its SHA-256 digest.
DIGEST_CHARACTERS = 12

# How a file in a fal result is sorted by kind: its exact content type first, then the start of its content type,
# then the extension of its link. Vector images and archives are passed on as links, never decoded.
OUTPUT_KINDS = {
    "TYPES": {
        "image/svg+xml": "other",
        "model/gltf-binary": "mesh",
        "model/gltf+json": "mesh",
        "model/obj": "mesh",
        "model/stl": "mesh",
        "model/vnd.usdz+zip": "mesh",
    },
    "PREFIXES": (
        ("image/", "image"),
        ("video/", "video"),
        ("audio/", "audio"),
    ),
    "EXTENSIONS": {
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".webp": "image",
        ".gif": "image",
        ".bmp": "image",
        ".tif": "image",
        ".tiff": "image",
        ".mp4": "video",
        ".mov": "video",
        ".webm": "video",
        ".mkv": "video",
        ".mp3": "audio",
        ".wav": "audio",
        ".flac": "audio",
        ".ogg": "audio",
        ".opus": "audio",
        ".m4a": "audio",
        ".aac": "audio",
        ".glb": "mesh",
        ".gltf": "mesh",
        ".obj": "mesh",
        ".fbx": "mesh",
        ".stl": "mesh",
        ".usdz": "mesh",
        ".ply": "mesh",
    },
}

# The format word ComfyUI's 3D file type takes, by link extension and then by content type.
MESH_FORMATS = {
    "EXTENSIONS": {
        ".glb": "glb",
        ".gltf": "gltf",
        ".obj": "obj",
        ".fbx": "fbx",
        ".stl": "stl",
        ".usdz": "usdz",
        ".ply": "ply",
    },
    "TYPES": {
        "model/gltf-binary": "glb",
        "model/gltf+json": "gltf",
        "model/obj": "obj",
        "model/stl": "stl",
        "model/vnd.usdz+zip": "usdz",
    },
}

# The node outputs that hold decoded files, and the kind of file each decodes; masks come from the images.
OUTPUT_ID_KINDS = {
    "images": "image",
    "masks": "image",
    "video": "video",
    "audio": "audio",
    "model_3d": "mesh",
}

# A file fal returns inside its reply, when a request sets sync_mode, starts with this.
INLINE_PREFIX = "data:"

# The only scheme File: Add takes; fal reads public and presigned https links.
LINK_SCHEME = "https"

# A typical web address limit; longer text is a paste mistake.
MAX_LINK_CHARACTERS = 2048

__all__ = [
    "DIGEST_CHARACTERS",
    "ENCODED_FORMATS",
    "IMAGE_TENSOR",
    "INLINE_PREFIX",
    "LINK_SCHEME",
    "MASK_TENSOR",
    "MAX_LINK_CHARACTERS",
    "MESH_FORMATS",
    "OUTPUT_ID_KINDS",
    "OUTPUT_KINDS",
    "WAV",
    "WEBP",
]
