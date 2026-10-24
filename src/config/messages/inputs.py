"""Refusals of the prompt, arguments, and files of a paid node, which come before any upload or payment."""

ARGUMENTS_INVALID = 'The arguments input is not valid JSON. Write a JSON object, such as {{"resolution": "480p"}}.'

ARGUMENTS_SHAPE = (
    'The arguments input holds {shape}. Write a JSON object of field names and values, such as {{"resolution": '
    '"480p"}}.'
)

ARGUMENT_UNKNOWN = 'The model {model} has no field named {field}. Model: Info lists the fields it takes.'

FIELD_MEDIA = 'The {field} field takes {media}, not {other}. Connect {media} to its File: Add.'

FIELD_NOT_FILE = 'The {field} field of {model} takes no file. Set it in arguments instead.'

FIELD_ONE_FILE = 'The {field} field takes one file, and it has {count}. Keep one.'

FIELD_REQUIRED = 'Set {field} in arguments. The model {model} needs it.'

FIELD_TOO_MANY = 'The {field} field takes at most {maximum} files on {model}, and it has {count}. Remove {extra}.'

FIELD_TWICE = 'The {field} field is set twice, in arguments and by {source}. Remove it from one of them.'

FILE_EMPTY = "Connect an image, a mask, audio, a video, or a fal node's files to File: Add, or type a link into file."

FILE_FIELD_EMPTY = "Type the model's file input into field, such as image_url. Model: Info lists a model's inputs."

FILE_FIELD_MISSING = 'Connect files through File: Add, which names the field each file goes to.'

FILE_FIELD_NAME = (
    'Type a file input into field: its name ends in _url or _urls, such as image_url or reference_audio_urls.'
)

FILE_FIELD_UNKNOWN = (
    'The model {model} has no field named {field}. Change field on that File: Add; Model: Info lists the fields the '
    'model takes.'
)

FILE_LINK = 'Type a public https:// link into file, such as a file on your own storage, or connect the file instead.'

FILE_LINK_LENGTH = 'Use a link of at most {maximum} characters in file.'

FILE_REQUIRED = 'Give the model {model} a file for {field}: connect it through File: Add, or put its link in arguments.'

FILE_SAMPLE = (
    'Give the model {model} a file for {field}: connect it through File: Add, or put its link in arguments. Left '
    'empty, fal would run its own sample file and bill it.'
)

PROMPT_REQUIRED = 'Write a prompt. The model {model} needs one.'

SETTING_UNKNOWN = (
    'The model {model} has no field named {field}. Empty {field} or set it to default, and put the setting in '
    "arguments under the model's own name. Model: Info lists its fields."
)

SINGLE_VALUE = 'Connect one value to {name}, not a list.'

TEXT_NOT_TAKEN = 'The model {model} takes no {field}. Leave {field} empty.'

TEXT_UNUSED = (
    'The model {model} takes no {field}. Leave {field} empty, and put the text in arguments under one of its text '
    'fields: {fields}.'
)

# How a refusal names the media a file field takes and the media it received.
MEDIA_NAMES = {
    'image': 'an image',
    'mask': 'a mask',
    'video': 'a video',
    'audio': 'an audio clip',
    'mesh': 'a 3D model',
}

# How a refusal names a JSON value that is not an object.
JSON_SHAPES = {
    'array': 'a JSON list',
    'string': 'text in double quotes',
    'number': 'a number',
    'boolean': 'true or false',
    'null': 'null',
}

__all__ = [
    'ARGUMENTS_INVALID',
    'ARGUMENTS_SHAPE',
    'ARGUMENT_UNKNOWN',
    'FIELD_MEDIA',
    'FIELD_NOT_FILE',
    'FIELD_ONE_FILE',
    'FIELD_REQUIRED',
    'FIELD_TOO_MANY',
    'FIELD_TWICE',
    'FILE_EMPTY',
    'FILE_FIELD_EMPTY',
    'FILE_FIELD_MISSING',
    'FILE_FIELD_NAME',
    'FILE_FIELD_UNKNOWN',
    'FILE_LINK',
    'FILE_LINK_LENGTH',
    'FILE_REQUIRED',
    'FILE_SAMPLE',
    'JSON_SHAPES',
    'MEDIA_NAMES',
    'PROMPT_REQUIRED',
    'SETTING_UNKNOWN',
    'SINGLE_VALUE',
    'TEXT_NOT_TAKEN',
    'TEXT_UNUSED',
]
