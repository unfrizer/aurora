"""Strict, atomic persistence for one application preferences document."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from contextlib import suppress
from dataclasses import asdict
from pathlib import Path
from typing import cast

from src.preferences.models import PreferencesError, UserPreferences

_MAX_BYTES = 64 * 1024
_FIELDS = frozenset(
    {"schema_version", "language", "general_model", "image_model", "onboarding_completed"}
)
_REPARSE = cast(int, getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _directory(path: Path) -> None:
    for item in (path, *path.parents):
        try:
            details = item.lstat()
            if (
                not stat.S_ISDIR(details.st_mode)
                or item.is_symlink()
                or item.is_junction()
                or cast(int, getattr(details, "st_file_attributes", 0)) & _REPARSE
            ):
                raise PreferencesError("Unsafe preferences location.")
        except OSError:
            raise PreferencesError("Preferences location unavailable.") from None


def _regular_file(path: Path) -> int | None:
    try:
        details = path.lstat()
    except FileNotFoundError:
        return None
    except OSError:
        raise PreferencesError("Preferences unavailable.") from None
    if (
        not stat.S_ISREG(details.st_mode)
        or details.st_nlink != 1
        or path.is_symlink()
        or path.is_junction()
        or cast(int, getattr(details, "st_file_attributes", 0)) & _REPARSE
    ):
        raise PreferencesError("Unsafe preferences file.")
    if details.st_size > _MAX_BYTES:
        raise PreferencesError("Invalid user preferences.")
    return details.st_size


def _unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise PreferencesError("Invalid user preferences.")
        result[name] = value
    return result


def _decode(raw: bytes) -> UserPreferences:
    try:
        value = cast(object, json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_fields))
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise PreferencesError("Invalid user preferences.") from None
    if not isinstance(value, dict) or value.keys() != _FIELDS:
        raise PreferencesError("Invalid user preferences.")
    fields = cast(dict[str, object], value)
    if (
        type(fields["schema_version"]) is not int
        or fields["schema_version"] != 1
        or (
            fields["language"] is not None
            and (type(fields["language"]) is not str or fields["language"] not in ("ru", "en"))
        )
        or type(fields["general_model"]) is not str
        or type(fields["image_model"]) is not str
        or type(fields["onboarding_completed"]) is not bool
    ):
        raise PreferencesError("Invalid user preferences.")
    return UserPreferences(
        schema_version=1,
        language=fields["language"],
        general_model=fields["general_model"],
        image_model=fields["image_model"],
        onboarding_completed=fields["onboarding_completed"],
    )


def default_preferences_path() -> Path:
    """Resolve the fixed Windows settings path without creating it."""
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        raise PreferencesError("Preferences location unavailable.")
    path = Path(base)
    if not path.is_absolute() or ".." in path.parts:
        raise PreferencesError("Preferences location unavailable.")
    _directory(path)
    return path / "AURORA" / "settings.json"


class PreferencesStore:
    """Read and replace one exact settings document at an injected location."""

    def __init__(self, path: Path) -> None:
        if not path.is_absolute() or ".." in path.parts or path.name != "settings.json":
            raise PreferencesError("Preferences location unavailable.")
        self._path = path

    def _parent(self, *, create: bool) -> bool:
        parent = self._path.parent
        _directory(parent.parent)
        try:
            parent.lstat()
        except FileNotFoundError:
            if not create:
                return False
            try:
                parent.mkdir()
            except OSError:
                raise PreferencesError("Preferences location unavailable.") from None
        except OSError:
            raise PreferencesError("Preferences location unavailable.") from None
        _directory(parent)
        return True

    def load(self) -> UserPreferences:
        if not self._parent(create=False):
            return UserPreferences()
        size = _regular_file(self._path)
        if size is None:
            return UserPreferences()
        try:
            with self._path.open("rb") as file:
                raw = file.read(_MAX_BYTES + 1)
        except OSError:
            raise PreferencesError("Preferences unavailable.") from None
        if len(raw) != size:
            raise PreferencesError("Invalid user preferences.")
        return _decode(raw)

    def save(self, preferences: UserPreferences) -> None:
        if type(preferences) is not UserPreferences:
            raise PreferencesError("Invalid user preferences.")
        validated = UserPreferences(**asdict(preferences))
        try:
            raw = json.dumps(
                asdict(validated), ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        except (TypeError, ValueError, UnicodeError):
            raise PreferencesError("Invalid user preferences.") from None
        if len(raw) > _MAX_BYTES:
            raise PreferencesError("Invalid user preferences.")
        self._parent(create=True)
        self.load()  # A damaged existing document must never be replaced.
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "wb", dir=self._path.parent, prefix=".aurora-settings-", delete=False
            ) as file:
                temporary = Path(file.name)
                file.write(raw)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self._path)
        except OSError:
            raise PreferencesError("Preferences unavailable.") from None
        finally:
            if temporary is not None:
                with suppress(OSError):
                    temporary.unlink(missing_ok=True)


__all__ = ["PreferencesStore", "default_preferences_path"]
