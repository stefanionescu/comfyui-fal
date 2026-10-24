"""Regular expression text that its owners compile once."""

# A settings revision, a SHA-256 digest.
REVISION_PATTERN = r'^[a-f0-9]{64}$'

# A fal endpoint ID, two to eight slash-separated segments.
ENDPOINT_ID_PATTERN = r'^[A-Za-z0-9][A-Za-z0-9._-]{0,127}(?:/[A-Za-z0-9._-]{1,128}){1,7}$'

# A fal request ID; also safe as a record's file name and in a URL path.
REQUEST_ID_PATTERN = r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$'

# The name of a file field ends in _url for one link or in _urls for a list.
FILE_FIELD_PATTERN = r'_(url|urls)$'

# The extension shows field descriptions as plain text. A Markdown link keeps its text, HTML tags and emphasis marks go,
# and a star between two words, as in max_images*num_images, stays.
DESCRIPTION_PATTERNS = {
    'LINK': r'\[([^\]]*)\]\([^)]*\)',
    'MARK': r'<[^>]+>|`|(?<!\w)\*+(?=\S)|(?<=\S)\*+(?!\w)',
}

# The extension cleans the reason of a failed reply before a person reads it. Links to the fal documentation and
# dashboard stay, without the scheme. The extension removes other links and key-shaped text. A fal key is a
# universally unique identifier (UUID), a colon, and 32 hexadecimal characters. Other key-shaped text is a UUID, or
# a run of 32 or more letters, digits, and base64 signs that holds both a letter and a digit. `LOCKED` finds a 403
# reason that names the balance, credits, or lock of the account.
REASON_PATTERNS = {
    'FAL_URL': r'https://((?:fal\.ai/(?:docs|dashboard)|docs\.fal\.ai)\S*?)(?=[.,;:]?(?:\s|$))',
    'URL': r'https?://\S+',
    'KEY': (
        r'\b[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}(?::[0-9A-Fa-f]{32})?\b'
        r'|(?<![\w+/=-])(?=[\w+/=]*\d)(?=[\w+/=]*[A-Za-z])[\w+/=]{32,}'
    ),
    'LOCKED': r'(?i)\b(?:balance|credits?|locked)\b',
}

__all__ = [
    'DESCRIPTION_PATTERNS',
    'ENDPOINT_ID_PATTERN',
    'FILE_FIELD_PATTERN',
    'REASON_PATTERNS',
    'REQUEST_ID_PATTERN',
    'REVISION_PATTERN',
]
