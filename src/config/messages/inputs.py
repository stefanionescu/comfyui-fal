"""Refusals of a paid node's prompt, arguments, and files, made before anything is uploaded or paid."""

ARGUMENTS_INVALID = 'The arguments input is not valid JSON. Write a JSON object, such as {{"resolution": "480p"}}.'

ARGUMENTS_SHAPE = (
    'The arguments input holds {shape}. Write a JSON object of field names and values, such as {{"resolution": '
    '"480p"}}.'
)

ARGUMENT_UNKNOWN = "The model {model} has no field named {field}. Model: Info lists the fields it takes."

FIELD_MEDIA = "The {field} field takes {media}, not {other}. Connect {media} to its File: Add."

FIELD_NOT_FILE = "The {field} field of {model} takes no file. Set it in arguments instead."

FIELD_ONE_FILE = "The {field} field takes one file, and it has {count}. Keep one."

FIELD_REQUIRED = "Set {field} in arguments. The model {model} needs it."

FIELD_TOO_MANY = "The {field} field takes at most {maximum} files on {model}, and it has {count}. Remove {extra}."

FIELD_TWICE = "The {field} field is set in arguments and by File: Add. Remove it from one of them."

FILE_FIELD_MISSING = "Connect files through File: Add, which names the field each file goes to."

FILE_FIELD_UNKNOWN = (
    "The model {model} has no field named {field}. Change field on that File: Add; Model: Info lists the fields the "
    "model takes."
)

FILE_REQUIRED = "Give the model {model} a file for {field}: connect it through File: Add, or put its link in arguments."

FILE_SAMPLE = (
    "Give the model {model} a file for {field}: connect it through File: Add, or put its link in arguments. Left "
    "empty, fal would run its own sample file and bill it."
)

PROMPT_NOT_TAKEN = "The model {model} takes no text. Leave prompt empty."

PROMPT_REQUIRED = "Write a prompt. The model {model} needs one."

PROMPT_TWICE = "The prompt input and arguments both set prompt. Remove it from one of them."

PROMPT_UNUSED = (
    "The model {model} takes no prompt. Leave prompt empty, and put the text in arguments under one of its text "
    "fields: {fields}."
)

# How a refusal names the media a file field takes and the media it was given.
MEDIA_NAMES = {
    "image": "an image",
    "mask": "a mask",
    "video": "a video",
    "audio": "an audio clip",
    "mesh": "a 3D model",
}

# How a refusal names a JSON value that is not an object.
JSON_SHAPES = {
    "array": "a JSON list",
    "string": "text in double quotes",
    "number": "a number",
    "boolean": "true or false",
    "null": "null",
}

__all__ = [
    "ARGUMENTS_INVALID",
    "ARGUMENTS_SHAPE",
    "ARGUMENT_UNKNOWN",
    "FIELD_MEDIA",
    "FIELD_NOT_FILE",
    "FIELD_ONE_FILE",
    "FIELD_REQUIRED",
    "FIELD_TOO_MANY",
    "FIELD_TWICE",
    "FILE_FIELD_MISSING",
    "FILE_FIELD_UNKNOWN",
    "FILE_REQUIRED",
    "FILE_SAMPLE",
    "JSON_SHAPES",
    "MEDIA_NAMES",
    "PROMPT_NOT_TAKEN",
    "PROMPT_REQUIRED",
    "PROMPT_TWICE",
    "PROMPT_UNUSED",
]
