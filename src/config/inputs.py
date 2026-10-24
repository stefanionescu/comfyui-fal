"""Names and tooltips of the inputs every paid node shares."""

# The inputs every paid node shares, in the order of the node: sockets first, then the short text, then the text boxes.
INPUT_NAMES = {
    'FILES': 'files',
    'OPTIONS': 'options',
    'MODEL': 'model',
    'RUN_NUMBER': 'run_number',
    'PROMPT': 'prompt',
    'ARGUMENTS': 'arguments',
}

# The run number's default and range; changing it sends the same request again.
RUN_NUMBER = {'DEFAULT': 0, 'MIN': 0, 'MAX': 2**31 - 1}

# Tooltips of the inputs every paid node shares, in plain words.
TOOLTIPS = {
    'FILES': 'Files for the model, each for the field its File: Add names.',
    'OPTIONS': 'Request options for fal, from Request Options.',
    'MODEL': "The fal model to run: its endpoint ID, from the model's page on fal.ai.",
    'RUN_NUMBER': 'Change it to send the same request again.',
    'PROMPT': (
        "Sent as the model's prompt field. Leave it empty when the model has none or takes its text under another "
        'name, and put that text in arguments.'
    ),
    'ARGUMENTS': (
        'The model\'s other inputs as a JSON object, under the names on its page on fal.ai, such as {"resolution": '
        '"480p"}. Leave it empty to use fal\'s defaults.'
    ),
}

__all__ = [
    'INPUT_NAMES',
    'RUN_NUMBER',
    'TOOLTIPS',
]
