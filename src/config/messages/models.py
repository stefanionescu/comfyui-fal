"""Messages about finding a model on fal and whether a node can run it."""

MODEL_EMPTY = "Type a fal model in model: its endpoint ID from the model's page on fal.ai, such as {example}."

MODEL_FORM = (
    'The text "{model}" in model is not an endpoint ID. Copy the ID from the model\'s page on fal.ai, such as '
    "{example}."
)

MODEL_KIND = "The model {model} makes {made}, so it runs in {node}, not in {this}."

MODEL_LEFT_OUT = "The model {model} cannot run in a fal node: {reason}."

MODEL_LISTING_BUSY = (
    "The fal model listing asked to wait {seconds} seconds, longer than the request timeout allows. Try again in a few "
    "minutes."
)

MODEL_LISTING_UNREADABLE = (
    "The fal model listing sent a reply this extension cannot read. Update the extension, or try again later."
)

MODEL_UNKNOWN = "The model {model} is not on fal. Copy its endpoint ID from the model's page on fal.ai."

# What each kind of model makes, as the refusals name it.
KIND_NAMES = {"image": "images", "video": "videos", "audio": "audio", "text": "text", "mesh": "3D models"}

# Why a node cannot run a model, as the refusal and Model: Info say it.
LEFT_OUT_REASONS = {
    "training": "it makes model weights, which no fal node outputs",
    "no_schema": "fal publishes no request schema for it, as for realtime models",
    "no_output": "its result holds nothing a fal node outputs",
}

__all__ = [
    "KIND_NAMES",
    "LEFT_OUT_REASONS",
    "MODEL_EMPTY",
    "MODEL_FORM",
    "MODEL_KIND",
    "MODEL_LEFT_OUT",
    "MODEL_LISTING_BUSY",
    "MODEL_LISTING_UNREADABLE",
    "MODEL_UNKNOWN",
]
