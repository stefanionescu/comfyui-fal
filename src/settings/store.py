"""Own private settings and API key changes outside ComfyUI's public storage."""

import json
import hashlib
from pathlib import Path
import secrets
import threading
from dataclasses import asdict, fields

from ..state import Json
from .schema import DEFAULT_SETTINGS, parse_settings
from ..state.errors import FalError, ErrorCode
from ..state.parsing import parse_json, validate_fields
from ..storage.files import read_file, save_file
from ..config.storage import FILE_NAMES, MAX_FILE_BYTES
from ..state.settings import Settings, Configuration
from ..config.security import GENERATION_TOKEN_BYTES, MAX_CREDENTIAL_CHARACTERS
from ..config.settings import SETTING_RANGES
from ..state.credentials import Credential
from ..storage.credentials import read_credential, parse_credential, read_credential_source
from ..config.messages.settings import SETTINGS_CHANGED, SETTING_READ_ONLY, SETTINGS_UNREADABLE

EDITABLE_SETTINGS = frozenset(item.name for item in fields(Settings))


class ConfigurationStore:
    """Serialize local changes across server and executor threads."""

    def __init__(self, directory: Path) -> None:
        """Select private storage and own the lock for settings and API key changes."""
        self.directory = directory
        self.lock = threading.Lock()
        # The last snapshot; None after the store deletes a key or cannot read the configuration.
        self._previous: Configuration | None = None

    def _build_configuration(self, settings: Settings, credential: Credential) -> Configuration:
        """Return settings and the API key with a cache token renewed only when the key changes.

        No setting changes a successful result, and ComfyUI never caches a failed run, so a settings change needs
        no new token.
        """
        previous = self._previous
        generation = previous.generation if previous is not None else secrets.token_hex(GENERATION_TOKEN_BYTES)
        if previous is not None and previous.credential != credential:
            generation = secrets.token_hex(GENERATION_TOKEN_BYTES)
        self._previous = Configuration(settings, credential, generation)
        return self._previous

    def _read_settings(self) -> tuple[Settings, str]:
        """Read settings and their revision without creating files or directories.

        A save replaces the file whole, so this read needs no lock. The revision identifies these non-secret settings,
        so a stale window cannot overwrite newer changes.
        """
        path = self.directory / FILE_NAMES['SETTINGS']
        settings = DEFAULT_SETTINGS
        if path.exists():
            content = read_file(path, max_bytes=MAX_FILE_BYTES['SETTINGS']).decode()
            settings = parse_settings(validate_fields(parse_json(content)))
        encoded = json.dumps(asdict(settings), sort_keys=True, separators=(',', ':')).encode()
        return settings, hashlib.sha256(encoded).hexdigest()

    def read_configuration(self) -> Configuration:
        """Read effective values together and invalidate unreadable configuration."""
        with self.lock:
            try:
                settings, _revision = self._read_settings()
                credential = read_credential(self.directory)
            except FalError:
                self._previous = None
                raise
            except (OSError, UnicodeError):
                self._previous = None
                raise FalError(ErrorCode.CONFIGURATION, SETTINGS_UNREADABLE) from None
            return self._build_configuration(settings, credential)

    def read_listing_access(self) -> tuple[Settings, Credential | None]:
        """Read the settings, and the key when one exists, for the free model reads that need no key.

        A missing key is no refusal here: the listing is free, and the key only raises fal's rate limit.
        """
        with self.lock:
            try:
                settings, _revision = self._read_settings()
            except (OSError, UnicodeError):
                raise FalError(ErrorCode.CONFIGURATION, SETTINGS_UNREADABLE) from None
            try:
                credential = read_credential(self.directory)
            except FalError as error:
                if error.code is not ErrorCode.AUTHENTICATION:
                    raise
                credential = None
        return settings, credential

    def read_status(self) -> dict[str, Json]:
        """Describe effective settings and API key presence without returning the key."""
        with self.lock:
            settings, revision = self._read_settings()
            source = read_credential_source(self.directory)
        return {
            'settings': asdict(settings),
            'setting_ranges': {
                name: {'minimum': definition['minimum'], 'maximum': definition['maximum']}
                for name, definition in SETTING_RANGES.items()
            },
            'credential_limit': MAX_CREDENTIAL_CHARACTERS,
            'revision': revision,
            'credential': {'source': source},
        }

    def save_settings(self, changes: dict[str, Json], revision: str) -> dict[str, Json]:
        """Apply a validated patch only to the version the editor actually read."""
        if changes.keys() - EDITABLE_SETTINGS:
            raise FalError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current, current_revision = self._read_settings()
            if revision != current_revision:
                raise FalError(ErrorCode.CONFLICT, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            save_file(self.directory / FILE_NAMES['SETTINGS'], (json.dumps(asdict(updated), indent=2) + '\n').encode())
        return self.read_status()

    def save_credential(self, value: str) -> dict[str, Json]:
        """Save a validated API key and return only the effective source."""
        credential = parse_credential(value)
        with self.lock:
            save_file(self.directory / FILE_NAMES['CREDENTIAL'], credential.value.encode('utf-8'))
            previous = self._previous
            # A key saved again unchanged keeps the cache, so it causes no second billed request.
            if (
                read_credential_source(self.directory) != 'environment'
                and previous
                and previous.credential != credential
            ):
                self._previous = None
        return self.read_status()

    def delete_credential(self) -> dict[str, Json]:
        """Remove only the saved API key; the server environment takes precedence."""
        with self.lock:
            (self.directory / FILE_NAMES['CREDENTIAL']).unlink(missing_ok=True)
            if read_credential_source(self.directory) != 'environment':
                self._previous = None
        return self.read_status()


__all__ = ['ConfigurationStore']
