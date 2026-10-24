"""fal's request statuses, and how the extension records and waits for a queued request."""

# fal's three statuses; fal reports a failed request as COMPLETED with an error.
STATUSES = {
    'QUEUED': 'IN_QUEUE',
    'RUNNING': 'IN_PROGRESS',
    'DONE': 'COMPLETED',
}

# fal removes a request that is still queued when a cancel reaches it, and never runs it.
CANCELLABLE_STATUS = 'IN_QUEUE'

# A status read asks for no logs: they are model text a person cannot act on.
STATUS_QUERY = {'logs': '0'}

# The status stream is the status address with this path segment added.
STREAM_SEGMENT = 'stream'

# The extension opens a dropped status stream again after this pause, so a dead connection does not spin.
STREAM_REOPEN_SECONDS = 2

# The request record format; a reader refuses any other.
RECORD_VERSION = 1

# fal keeps a request's payload 30 days by default, so the extension deletes an older record instead of reading it.
RECORD_RETENTION_SECONDS = 2_592_000

# The label of a recorded request in Request: Download: its ID, its endpoint, and its submit time to the minute,
# in UTC.
REQUEST_LABEL_SEPARATOR = ' · '
REQUEST_TIME_CHARACTERS = 16

__all__ = [
    'CANCELLABLE_STATUS',
    'RECORD_RETENTION_SECONDS',
    'RECORD_VERSION',
    'REQUEST_LABEL_SEPARATOR',
    'REQUEST_TIME_CHARACTERS',
    'STATUSES',
    'STATUS_QUERY',
    'STREAM_REOPEN_SECONDS',
    'STREAM_SEGMENT',
]
