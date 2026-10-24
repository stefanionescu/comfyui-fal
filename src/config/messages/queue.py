"""Messages for a queued request's outcomes."""

ADDRESS_REFUSED = (
    'The reply from fal gave a request address outside queue.fal.run, so the request was not recorded. It may still '
    'run and be billed; check the Usage page at {usage_page}.'
)

REQUEST_GONE = (
    'This request or its result is no longer on fal, so its record was deleted. Run the node that sent it again.'
)

REQUEST_UNKNOWN = (
    'Choose a recorded request in request. A request is recorded when a paid fal node sends it, and leaves the list '
    'once its outputs are collected.'
)

REQUEST_UNRECORDED = (
    "The request's reply from fal could not be read, so the request was not recorded. It may still run and be billed; "
    'check the Usage page at {usage_page} before running again.'
)

WAIT_LIMIT = (
    'The request did not finish on fal within the request timeout of {seconds} seconds in fal Settings. It keeps '
    'running on fal and stays recorded; collect it with Request: Download.'
)

__all__ = [
    'ADDRESS_REFUSED',
    'REQUEST_GONE',
    'REQUEST_UNKNOWN',
    'REQUEST_UNRECORDED',
    'WAIT_LIMIT',
]
