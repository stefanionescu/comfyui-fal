"""The fal addresses, the hosts that receive the API key, the reply limits, and the dashboard pages messages name."""

# Every model call goes through fal's queue; a submit goes to QUEUE_URL plus "/" plus the endpoint ID.
QUEUE_URL = "https://queue.fal.run"

# The host of every status, result, and cancel address fal returns for a queued request.
QUEUE_HOST = "queue.fal.run"

# The model listing, read with or without the key.
PLATFORM_URLS = {
    "MODELS": "https://api.fal.ai/v1/models",
}

# The storage token for uploads, and the upload itself, which takes the token and never the key.
STORAGE_URLS = {
    "AUTHORIZE": "https://rest.fal.ai/storage/auth/token",
    "UPLOAD": "https://v3.fal.media/files/upload",
}

# The storage the token is for, sent as the token request's storage_type query value.
STORAGE_TYPE = "fal-cdn-v3"

# A storage token is renewed this long before it expires, so an upload never starts with a token about to lapse.
UPLOAD_TOKEN_MARGIN_SECONDS = 300

# The only hosts that receive the API key; every one is reached over https.
KEY_HOSTS = ("queue.fal.run", "rest.fal.ai", "api.fal.ai")

# A reply is read in chunks, and a failed one only this far.
REPLY_BYTES = {
    "CHUNK": 65_536,
    "MAX_ERROR": 65_536,
}

# A failed reply's reason is cut to this length.
MAX_REASON_CHARACTERS = 300

# A reason that ends otherwise gets a full stop.
REASON_ENDINGS = (".", "!", "?", "…")

# Dashboard pages messages send the person to, keyed by the placeholder each message uses.
DASHBOARD_URLS = {
    "usage_page": "fal.ai/dashboard/usage-billing",
    "billing_page": "fal.ai/dashboard/billing",
    "key_page": "fal.ai/dashboard/keys",
    "concurrency_page": "fal.ai/dashboard/usage-billing/concurrency",
}

__all__ = [
    "DASHBOARD_URLS",
    "KEY_HOSTS",
    "MAX_REASON_CHARACTERS",
    "PLATFORM_URLS",
    "QUEUE_HOST",
    "QUEUE_URL",
    "REASON_ENDINGS",
    "REPLY_BYTES",
    "STORAGE_TYPE",
    "STORAGE_URLS",
    "UPLOAD_TOKEN_MARGIN_SECONDS",
]
