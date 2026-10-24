"""Execution settings and private configuration snapshot records."""

from dataclasses import field, dataclass

from .credentials import Credential


@dataclass(frozen=True, slots=True)
class Settings:
    """Limits that a workflow cannot raise.

    Attributes:
        request_timeout_seconds: How long one HTTP exchange may take, and the whole wait for a queued request.
        max_upload_megabytes: Largest single file uploaded to fal storage.
        max_download_megabytes: Largest reply body or output file accepted.

    """

    request_timeout_seconds: int
    max_upload_megabytes: int
    max_download_megabytes: int


@dataclass(frozen=True, slots=True)
class Configuration:
    """One private settings and API key snapshot for one request.

    Attributes:
        settings: Effective execution limits.
        credential: Private fal API key excluded from representations.
        generation: Token identifying the API key in ComfyUI's cache.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ['Configuration', 'Settings']
