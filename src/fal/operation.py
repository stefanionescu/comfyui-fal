"""Define the progress report every request makes, and the upload limit every request shares."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..config.units import BYTES_PER_MEGABYTE
from ..state.errors import FalError, ErrorCode
from ..config.messages.media import UPLOAD_LIMIT

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Awaitable

    from ..state.files import EncodedFile
    from ..state.settings import Settings

type Progress = Callable[[int], Awaitable[None]]


def validate_upload_size(files: Iterable[EncodedFile], settings: Settings) -> None:
    """Refuse the first encoded file larger than the maximum upload size; fal takes each file in its own upload."""
    maximum = settings.max_upload_megabytes
    for file in files:
        if len(file.content) > maximum * BYTES_PER_MEGABYTE:
            shown = math.ceil(len(file.content) * 10 / BYTES_PER_MEGABYTE) / 10
            raise FalError(ErrorCode.INVALID_INPUT, UPLOAD_LIMIT.format(size=shown, maximum=maximum))


__all__ = ['validate_upload_size']
