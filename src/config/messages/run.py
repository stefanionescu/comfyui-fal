"""Messages for fal failures.

The reason placeholder holds the cleaned reason from fal, ending as a sentence, and the dashboard placeholders take
their values from DASHBOARD_URLS.
"""

ACCESS_DENIED = "This API key may not make this request on fal: {reason} Check the key's permissions at {key_page}."

ACCOUNT_LOCKED = (
    "Your fal account's credit balance is below its lock threshold, so the request was refused: {reason} Add credits "
    'at {billing_page}, then run again.'
)

DOWNLOAD_LIMIT = (
    'A file or reply from fal is larger than the maximum download size of {maximum} MB in fal Settings. Raise it, or '
    'ask for a shorter or smaller output.'
)

ENDPOINT_NOT_FOUND = (
    "No fal model has this endpoint ID, or the API key may not use it: {reason} Copy the endpoint ID from the model's "
    'page on fal.ai into model.'
)

FAL_UNREACHABLE = 'ComfyUI could not reach fal. Check the connection and try again.'

FILE_UNREADABLE = (
    'A file you gave fal could not be read: {reason} A link must open without signing in. Add the media itself with '
    'File: Add instead, or use another link.'
)

INPUT_REFUSED = 'The content check on fal refused an input: {reason} Change the prompt or the media, then run again.'

KEY_REJECTED = (
    'The API key was not accepted by fal. Check the key in fal Settings. A fal key looks like key_id:key_secret, and '
    'you can create one at {key_page}.'
)

MODEL_TIMEOUT = (
    'The model ran out of time on fal: {reason} A timeout is not billed. Run again, or ask for a shorter or smaller '
    'output.'
)

NO_MEDIA = 'The model made nothing from this input: {reason} Change the prompt or the media, then run again.'

NO_REASON = 'no reason given.'

OUTPUT_DOWNLOAD_FAILED = (
    'An output file could not be downloaded from fal: HTTP {status}. The request stays recorded, so Request: Download '
    'can collect it again.'
)

RATE_LIMITED = 'Requests are being limited on fal: {reason} Wait a minute, then try again.'

REPLY_UNREADABLE = (
    'The reply from fal could not be read. The request may still have run; check Usage in the fal dashboard before '
    'running again.'
)

REQUEST_CANCELLED = 'The request was cancelled on fal before it finished: {reason} Run again.'

REQUEST_FAILED = 'The fal API returned HTTP {status}. Try again later.'

REQUEST_REJECTED = 'The request was refused by fal: {reason}'

REQUEST_TIMEOUT = (
    'No answer came from fal within the request timeout of {seconds} seconds in fal Settings. The request may have '
    'been queued and billed; check the Usage page at {usage_page} before running again.'
)

REQUEST_UNCERTAIN = (
    'The connection closed before fal answered. The request may have been queued and billed; check the Usage page at '
    '{usage_page} before running again.'
)

SERVER_BUSY = (
    'The model could not run on fal just now: {reason} This is not billed. Wait a few minutes, then run again.'
)

SERVER_FAILED = 'A server error on fal stopped the request, which is not billed: {reason} Run again.'

START_TIMEOUT = (
    'No fal machine started the request within request_start_timeout in Request Options, so fal dropped it without '
    'billing. Raise the timeout, or run again later.'
)

UPLOAD_FAILED = 'Storage on fal refused an upload: HTTP {status}. Nothing was sent to the model. Try again.'

UPLOAD_UNREADABLE = 'The upload reply from fal storage could not be read. Nothing was sent to the model. Try again.'

__all__ = [
    'ACCESS_DENIED',
    'ACCOUNT_LOCKED',
    'DOWNLOAD_LIMIT',
    'ENDPOINT_NOT_FOUND',
    'FAL_UNREACHABLE',
    'FILE_UNREADABLE',
    'INPUT_REFUSED',
    'KEY_REJECTED',
    'MODEL_TIMEOUT',
    'NO_MEDIA',
    'NO_REASON',
    'OUTPUT_DOWNLOAD_FAILED',
    'RATE_LIMITED',
    'REPLY_UNREADABLE',
    'REQUEST_CANCELLED',
    'REQUEST_FAILED',
    'REQUEST_REJECTED',
    'REQUEST_TIMEOUT',
    'REQUEST_UNCERTAIN',
    'SERVER_BUSY',
    'SERVER_FAILED',
    'START_TIMEOUT',
    'UPLOAD_FAILED',
    'UPLOAD_UNREADABLE',
]
