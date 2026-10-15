"""Which fal models each paid node runs, and how fal's schemas become fields."""

# The paid nodes, by what their models make, in menu order.
KINDS = ("image", "video", "audio", "text", "mesh")

# The node that runs each kind.
KIND_NODES = {
    "image": "Image: Generate",
    "video": "Video: Generate",
    "audio": "Audio: Generate",
    "text": "Text: Generate",
    "mesh": "3D: Generate",
}

# Each paid node's model when the person changes nothing: current, inexpensive, and needing only a prompt or one file.
DEFAULT_MODELS = {
    "image": "fal-ai/flux-2/klein/4b",
    "video": "fal-ai/ltx-2.3-22b/distilled/text-to-video",
    "audio": "fal-ai/minimax/speech-2.8-turbo",
    "text": "fal-ai/elevenlabs/speech-to-text/scribe-v2",
    "mesh": "fal-ai/trellis-2",
}

# Each fal category's kind, used when a model's output names do not show one; None means the output decides.
CATEGORY_KINDS = {
    "text-to-image": "image",
    "image-to-image": "image",
    "text-to-video": "video",
    "image-to-video": "video",
    "video-to-video": "video",
    "audio-to-video": "video",
    "text-to-audio": "audio",
    "text-to-speech": "audio",
    "audio-to-audio": "audio",
    "video-to-audio": "audio",
    "speech-to-speech": "audio",
    "speech-to-text": "text",
    "audio-to-text": "text",
    "vision": "text",
    "video-to-text": "text",
    "image-to-text": "text",
    "text-to-text": "text",
    "llm": "text",
    "json": "text",
    "image-to-json": "text",
    "text-to-json": "text",
    "image-to-3d": "mesh",
    "text-to-3d": "mesh",
    "3d-to-3d": "mesh",
    "unknown": None,
    "workflow": None,
}

# Categories no node runs: trainers return model weights.
LEFT_OUT_CATEGORIES = ("training",)

# fal's file objects in outputs, by schema name, and the kind each carries; File and MediaFile carry any kind.
OUTPUT_FILE_KINDS = {
    "Image": "image",
    "ImageFile": "image",
    "Video": "video",
    "VideoFile": "video",
    "Audio": "audio",
    "AudioFile": "audio",
}

# Words in an output field's name and the kind each shows, checked in this order.
OUTPUT_KIND_TOKENS = {
    "mesh": ("model", "mesh", "meshes", "glb", "gltf", "obj", "fbx", "usdz", "stl", "ply", "splat"),
    "video": ("video", "videos"),
    "image": ("image", "images", "mask", "masks"),
    "audio": ("audio", "audios", "speech", "vocals", "drums", "bass", "guitar", "piano", "stem", "stems"),
}

# fal's own media hint on a file field (ui.field or _fal_ui_field), and the media kind it gives.
FIELD_HINT_KINDS = {
    "image": "image",
    "video": "video",
    "audio": "audio",
    "file": None,
}

# Words in a file field's name that show a file which is not media, such as weights, documents, or archives.
NON_MEDIA_FIELD_TOKENS = (
    "archive",
    "cache",
    "checkpoint",
    "data",
    "embedding",
    "file",
    "font",
    "lora",
    "pdf",
    "srt",
    "web",
)

# Words in a file field's name and the media kind each shows, checked in this order.
MEDIA_FIELD_TOKENS = {
    "video": ("video",),
    "mask": ("mask",),
    "audio": ("audio", "voice"),
    "mesh": ("mesh", "pointmap"),
    "image": ("image", "images", "img", "frame", "cover"),
}

# Result fields that hold a model's text; the first of them in fal's order is the text output.
TEXT_FIELD_NAMES = (
    "output",
    "text",
    "transcript",
    "transcription",
    "caption",
    "description",
    "answer",
    "response",
    "results",
    "content",
)

# Result fields that hold text that is never the model's answer, such as why it stopped or the language it heard.
NON_TEXT_FIELD_NAMES = ("finish_reason", "stop_reason", "language", "language_code", "error", "status", "request_id")

# The listing call's expand value, which adds each model's OpenAPI document.
OPENAPI_EXPAND = "openapi-3.0"

# Seconds to wait after a 429 that names no wait of its own.
PLATFORM_SPACING_SECONDS = 5

# The model's page on fal.ai, from its endpoint ID.
MODEL_PAGE_URL = "https://fal.ai/models/{model_id}"

__all__ = [
    "CATEGORY_KINDS",
    "DEFAULT_MODELS",
    "FIELD_HINT_KINDS",
    "KINDS",
    "KIND_NODES",
    "LEFT_OUT_CATEGORIES",
    "MEDIA_FIELD_TOKENS",
    "MODEL_PAGE_URL",
    "NON_MEDIA_FIELD_TOKENS",
    "NON_TEXT_FIELD_NAMES",
    "OPENAPI_EXPAND",
    "OUTPUT_FILE_KINDS",
    "OUTPUT_KIND_TOKENS",
    "PLATFORM_SPACING_SECONDS",
    "TEXT_FIELD_NAMES",
]
