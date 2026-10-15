"""Regular expression text that its owners compile once."""

# A settings revision, a SHA-256 digest.
REVISION_PATTERN = r"^[a-f0-9]{64}$"

__all__ = ["REVISION_PATTERN"]
