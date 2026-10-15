"""Regular expression text that its owners compile once."""

# A settings revision, a SHA-256 digest.
REVISION_PATTERN = r"^[a-f0-9]{64}$"

# A fal endpoint ID, two to eight slash-separated segments.
ENDPOINT_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}(?:/[A-Za-z0-9._-]{1,128}){1,7}$"

# A file field's name ends in _url (one link) or _urls (a list).
FILE_FIELD_PATTERN = r"_(url|urls)$"

# A field description is shown as plain text: a Markdown link keeps its text, and HTML tags and emphasis marks go.
DESCRIPTION_PATTERNS = {
    "LINK": r"\[([^\]]*)\]\([^)]*\)",
    "MARK": r"<[^>]+>|[*`]",
}

# A failed reply's reason is cleaned before a person sees it. fal's own documentation and dashboard links stay, without
# the scheme. Other links and key-shaped text are removed. A fal key is a UUID, a colon, and 32 hexadecimal characters;
# other key-shaped text is a UUID, or a run of 32 or more letters, digits, and base64 signs that holds both a letter
# and a digit. LOCKED finds a 403 reason that names the account's balance, credits, or lock.
REASON_PATTERNS = {
    "FAL_URL": r"https://((?:fal\.ai/(?:docs|dashboard)|docs\.fal\.ai)\S*?)(?=[.,;:]?(?:\s|$))",
    "URL": r"https?://\S+",
    "KEY": (
        r"\b[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}(?::[0-9A-Fa-f]{32})?\b"
        r"|(?<![\w+/=-])(?=[\w+/=]*\d)(?=[\w+/=]*[A-Za-z])[\w+/=]{32,}"
    ),
    "LOCKED": r"(?i)\b(?:balance|credits?|locked)\b",
}

__all__ = [
    "DESCRIPTION_PATTERNS",
    "ENDPOINT_ID_PATTERN",
    "FILE_FIELD_PATTERN",
    "REASON_PATTERNS",
    "REVISION_PATTERN",
]
