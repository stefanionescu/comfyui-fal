"""Messages for private settings, the API key, and state storage."""

KEY_EMPTY = "Enter a fal API key of 1 to {maximum} characters without spaces at either end."

KEY_REQUIRED = "Set your fal API key in fal Settings or in the server's FAL_KEY before running."

KEY_UNREADABLE = "The saved fal API key could not be read. Save the key again in fal Settings."

KEY_WHITESPACE = "Remove spaces and line breaks from the fal API key."

PRIVATE_STATE_LOCATION = "Keep the fal extension's private state outside ComfyUI, its package, and its media folders."

RUNTIME_NOT_READY = "The fal nodes are still loading. Wait for ComfyUI to finish starting, then run again."

SETTINGS_CHANGED = "The settings changed in another window. Reload the settings and try again."

SETTINGS_RANGE = "Choose each fal setting within its range."

SETTINGS_UNREADABLE = "The fal extension's private settings could not be read. Check the state folder's permissions."

SETTINGS_WHOLE_NUMBERS = "Enter whole numbers for the fal settings."

SETTING_READ_ONLY = "That fal setting cannot be changed here."

SETTING_UNKNOWN = "The fal settings file has an unknown setting. Remove it or reset the settings."

STATE_DIRECTORY_ABSOLUTE = "Set FAL_COMFY_STATE_DIRECTORY to an absolute folder path."

STATE_FILE_SIZE = "A fal state file is larger than expected. Check the state folder."

STATE_UNREADABLE = (
    "The fal extension's private state could not be read or written. Check the state folder's permissions."
)

__all__ = [
    "KEY_EMPTY",
    "KEY_REQUIRED",
    "KEY_UNREADABLE",
    "KEY_WHITESPACE",
    "PRIVATE_STATE_LOCATION",
    "RUNTIME_NOT_READY",
    "SETTINGS_CHANGED",
    "SETTINGS_RANGE",
    "SETTINGS_UNREADABLE",
    "SETTINGS_WHOLE_NUMBERS",
    "SETTING_READ_ONLY",
    "SETTING_UNKNOWN",
    "STATE_DIRECTORY_ABSOLUTE",
    "STATE_FILE_SIZE",
    "STATE_UNREADABLE",
]
