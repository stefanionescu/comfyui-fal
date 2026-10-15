"""Define the request every node hands to the run wrapper, and the upload limit every request shares."""

from __future__ import annotations

import math
from typing import Protocol, TYPE_CHECKING
from ..config.units import BYTES_PER_MEGABYTE
from ..types.errors import ErrorCode, FalError
from ..config.messages.media import UPLOAD_LIMIT

if TYPE_CHECKING:
    from ..types.files import EncodedFile
    from ..types.settings import Settings, Configuration
    from collections.abc import Iterable, Callable, Awaitable

type Progress = Callable[[int], Awaitable[None]]


class Operation[Result](Protocol):
    """One fal request, validated before it is sent."""

    def validate(self, settings: Settings) -> None:
        """Refuse inputs the settings do not allow, before anything is sent."""
        raise NotImplementedError(settings)

    async def send(self, configuration: Configuration, progress: Progress | None) -> Result:
        """Send the request, report each step reached, and return its result."""
        raise NotImplementedError(configuration, progress)


def validate_upload_size(files: Iterable[EncodedFile], settings: Settings) -> None:
    """Refuse the first encoded file larger than the maximum upload size; fal takes each file in its own upload."""
    maximum = settings.max_upload_megabytes
    for file in files:
        if len(file.content) > maximum * BYTES_PER_MEGABYTE:
            shown = math.ceil(len(file.content) * 10 / BYTES_PER_MEGABYTE) / 10
            raise FalError(ErrorCode.INVALID_INPUT, UPLOAD_LIMIT.format(size=shown, maximum=maximum))


__all__ = ["Operation", "validate_upload_size"]
