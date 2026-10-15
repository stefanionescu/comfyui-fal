"""The choices of Request Options and the fal headers they set."""

# fal's queue priorities; normal is fal's default, so it sends nothing.
QUEUE_PRIORITIES = ("normal", "low")

# The headers a queue submit may carry, spelled as fal's docs spell them; only the submit sends them.
REQUEST_HEADERS = {
    "QUEUE_PRIORITY": "X-Fal-Queue-Priority",
    "REQUEST_START_TIMEOUT": "X-Fal-Request-Start-Timeout",
    "NO_RETRY": "X-Fal-No-Retry",
    "DISABLE_FALLBACK": "x-app-fal-disable-fallback",
    "OBJECT_LIFECYCLE": "X-Fal-Object-Lifecycle-Preference",
    "STORE_IO": "X-Fal-Store-IO",
}

# The values fal's docs give for turning each switch on or payload storage off.
HEADER_VALUES = {
    "NO_RETRY": "1",
    "DISABLE_FALLBACK": "true",
    "STORE_IO_OFF": "0",
}

# The one field of the lifecycle header the pack sends; outputs are downloaded without the key, so never initial_acl.
LIFECYCLE_FIELD = "expiration_duration_seconds"

__all__ = [
    "HEADER_VALUES",
    "LIFECYCLE_FIELD",
    "QUEUE_PRIORITIES",
    "REQUEST_HEADERS",
]
