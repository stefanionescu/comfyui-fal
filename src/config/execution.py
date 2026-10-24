"""How a paid run shows ComfyUI's progress bar and notices its cancel."""

# The progress bar of a paid node: files uploaded, request queued, model running, outputs downloaded, outputs built.
PROGRESS_STEPS = {
    'UPLOADED': 1,
    'QUEUED': 2,
    'RUNNING': 3,
    'DOWNLOADED': 4,
    'TOTAL': 5,
}

# How often a wait checks ComfyUI's cancel, in seconds.
CANCELLATION_POLL_SECONDS = 0.1

__all__ = [
    'CANCELLATION_POLL_SECONDS',
    'PROGRESS_STEPS',
]
