"""Create the shared stores when ComfyUI loads the extension."""

from ..types.errors import ErrorCode, FalError
from ..settings.store import ConfigurationStore
from ..storage.files import choose_state_directory
from ..config.messages.settings import RUNTIME_NOT_READY


class Runtime:
    """State shared by this extension's nodes and routes across event loops.

    Attributes:
        configuration: Private settings and the API key.

    """

    __slots__ = ("configuration",)

    configuration: ConfigurationStore

    def __init__(self) -> None:
        """Create the shared stores and place their state under one private directory."""
        self.configuration = ConfigurationStore(choose_state_directory())


_runtime: Runtime | None = None


def create_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 -- reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the extension."""
    if _runtime is None:
        raise FalError(ErrorCode.CONFIGURATION, RUNTIME_NOT_READY)
    return _runtime


__all__ = ["Runtime", "create_runtime", "get_runtime"]
