"""Names, tooltips, and ranges of the inputs the paid nodes share, and the named settings of each kind node."""

# The inputs every paid node shares.
INPUT_NAMES = {
    'FILES': 'files',
    'OPTIONS': 'options',
    'MODEL': 'model',
    'RUN_NUMBER': 'run_number',
    'ARGUMENTS': 'arguments',
}

# The run number's default and range; changing it sends the same request again.
RUN_NUMBER = {'DEFAULT': 0, 'MIN': 0, 'MAX': 2**31 - 1}

# The choices of a named setting: default sends nothing, and custom shows a value, which the node sends.
CHOICE = {
    'DEFAULT': 'default',
    'CUSTOM': 'custom',
    'VALUE': 'value',
}

# The named settings of each kind node, in node order, by fal's field name, with the value custom starts at. They are
# the fields most fal models of the kind share. Each goes only to a model with a field of that name; Model: Info shows
# the values a model takes.
SETTINGS: dict[str, dict[str, str | int | float | bool]] = {
    'image': {
        'aspect_ratio': '1:1',
        'resolution': '1K',
        'num_images': 1,
        'output_format': 'png',
        'guidance_scale': 3.5,
        'num_inference_steps': 28,
        'seed': 42,
    },
    'video': {'duration': 5, 'resolution': '720p', 'aspect_ratio': '16:9', 'generate_audio': True, 'seed': 42},
    'audio': {'output_format': 'mp3', 'seed': 42},
    'text': {},
    'mesh': {},
}

# The least value of each named setting that takes a number; fal checks the range of each model itself, free.
NUMBER_MINIMUMS = {
    'num_images': 1,
    'guidance_scale': 0.0,
    'num_inference_steps': 1,
    'duration': 1,
    'seed': 0,
}

# The one-line text inputs of each kind node, by fal's field name, with the text they start with.
LINES: dict[str, dict[str, str]] = {
    'image': {},
    'video': {},
    'audio': {'voice': ''},
    'text': {},
    'mesh': {},
}

# The text boxes of each kind node, in node order, by fal's field name.
TEXTS = {
    'image': ('prompt', 'negative_prompt'),
    'video': ('prompt', 'negative_prompt'),
    'audio': ('prompt', 'text'),
    'text': ('prompt',),
    'mesh': ('prompt',),
}

# Tooltips of the shared inputs, the named settings, and the text inputs, in plain words.
TOOLTIPS = {
    'FILES': 'Files for the model, each for the field its File: Add names.',
    'OPTIONS': 'Request options for fal, from Request Options.',
    'MODEL': 'Any fal model ID, such as fal-ai/flux-2/klein/4b. Copy one from its page on fal.ai.',
    'RUN_NUMBER': 'Change this number to send the same request again.',
    'ARGUMENTS': (
        'The model\'s other fields as a JSON object, under the names Model: Info lists, such as {"resolution": '
        '"480p"}. Leave it empty to use the model\'s defaults.'
    ),
    'aspect_ratio': 'The shape of the result, such as 16:9. Choose custom to send one.',
    'resolution': 'The size of the result, such as 1K or 720p. Choose custom to send one.',
    'num_images': 'How many images to make. Choose custom to send a number.',
    'output_format': 'The file format of the result, such as png. Choose custom to send one.',
    'guidance_scale': 'How closely the image follows the prompt; higher follows it more. Choose custom to send one.',
    'num_inference_steps': (
        'How many steps the model takes; more is slower and often finer. Choose custom to send a number.'
    ),
    'seed': 'Number the model uses to vary its output. Choose custom to send one.',
    'duration': 'The length in seconds. Choose custom to send one.',
    'generate_audio': 'Whether the video has sound. Choose custom to turn it on or off.',
    'prompt': (
        "Sent as the model's prompt field. Leave it empty when the model has none or takes its text under another "
        'name, and put that text in arguments.'
    ),
    'negative_prompt': 'What to leave out. Leave it empty to send nothing.',
    'text': 'The words to speak, for a voice model. Leave it empty to send nothing.',
    'voice': 'The voice, for a voice model, by the name or ID the model lists. Leave it empty to send nothing.',
}

__all__ = [
    'CHOICE',
    'INPUT_NAMES',
    'LINES',
    'NUMBER_MINIMUMS',
    'RUN_NUMBER',
    'SETTINGS',
    'TEXTS',
    'TOOLTIPS',
]
