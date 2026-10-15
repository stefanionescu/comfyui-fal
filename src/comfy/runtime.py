"""Create the shared stores when ComfyUI loads the extension."""


def create_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""


__all__ = ["create_runtime"]
