"""Acceptance tests for the isolated P8-001 preferences owner."""

from __future__ import annotations

import json
import os
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import Literal, cast

import pytest

from src.preferences import (
    PreferencesError,
    PreferencesStore,
    UserPreferences,
    default_preferences_path,
)


def test_missing_preferences_are_defaults_without_filesystem_write(tmp_path: Path) -> None:
    path = tmp_path / "AURORA" / "settings.json"
    store = PreferencesStore(path)
    assert store.load() == UserPreferences()
    assert not path.parent.exists()
    assert not path.exists()


def test_default_location_uses_only_patched_localappdata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert default_preferences_path() == tmp_path / "AURORA" / "settings.json"
    assert not (tmp_path / "AURORA").exists()
    monkeypatch.delenv("LOCALAPPDATA")
    with pytest.raises(PreferencesError, match="location unavailable"):
        default_preferences_path()
    monkeypatch.setenv("LOCALAPPDATA", "relative/path")
    with pytest.raises(PreferencesError, match="location unavailable"):
        default_preferences_path()


def test_exact_immutable_snapshot_round_trips_without_secret_fields(tmp_path: Path) -> None:
    store = PreferencesStore(tmp_path / "AURORA" / "settings.json")
    settings = UserPreferences(
        language="ru",
        general_model="future-text",
        image_model="future-image",
        onboarding_completed=True,
    )
    with pytest.raises(FrozenInstanceError):
        settings.general_model = "changed"  # type: ignore[misc]
    store.save(settings)
    assert store.load() == settings
    document = json.loads((tmp_path / "AURORA" / "settings.json").read_text("utf-8"))
    assert document == {
        "schema_version": 1,
        "language": "ru",
        "general_model": "future-text",
        "image_model": "future-image",
        "onboarding_completed": True,
    }
    assert not ({"openai_api_key", "netlify_token", "project_root"} & document.keys())
    assert not list((tmp_path / "AURORA").glob(".aurora-settings-*"))


def test_invalid_public_snapshots_are_rejected() -> None:
    for settings in (
        lambda: UserPreferences(schema_version=cast(Literal[1], True)),
        lambda: UserPreferences(language=cast(Literal["ru", "en"], "fr")),
        lambda: UserPreferences(general_model=" "),
        lambda: UserPreferences(image_model="bad\nmodel"),
        lambda: UserPreferences(image_model="bad\u0085model"),
        lambda: UserPreferences(image_model="\ud800"),
        lambda: UserPreferences(onboarding_completed=cast(bool, 1)),
    ):
        with pytest.raises(PreferencesError, match="Invalid user preferences"):
            settings()


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"{",
        b"\xff",
        b"[]",
        b'{"schema_version":1,"language":null}',
        b'{"schema_version":2,"language":null,"general_model":"m","image_model":"i","onboarding_completed":false}',
        b'{"schema_version":1,"language":null,"general_model":"m","image_model":"i","onboarding_completed":false,"secret":"private"}',
        b'{"schema_version":1,"schema_version":1,"language":null,"general_model":"m","image_model":"i","onboarding_completed":false}',
        b'{"schema_version":true,"language":null,"general_model":"m","image_model":"i","onboarding_completed":false}',
    ],
)
def test_malformed_existing_document_fails_closed(raw: bytes, tmp_path: Path) -> None:
    directory = tmp_path / "AURORA"
    directory.mkdir()
    path = directory / "settings.json"
    path.write_bytes(raw)
    store = PreferencesStore(path)
    with pytest.raises(PreferencesError, match="Invalid user preferences"):
        store.load()
    with pytest.raises(PreferencesError):
        store.save(UserPreferences(language="en"))
    assert path.read_bytes() == raw


def test_oversize_document_and_save_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "AURORA" / "settings.json"
    path.parent.mkdir()
    path.write_bytes(b"x" * (64 * 1024 + 1))
    with pytest.raises(PreferencesError):
        PreferencesStore(path).load()
    path.unlink()
    with pytest.raises(PreferencesError):
        PreferencesStore(path).save(UserPreferences(general_model="x" * (64 * 1024)))
    assert not path.exists()


def test_atomic_replacement_failure_preserves_existing_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "AURORA" / "settings.json"
    store = PreferencesStore(path)
    store.save(UserPreferences(language="en"))
    before = path.read_bytes()

    def failed_replace(_source: Path, _target: Path) -> None:
        raise OSError("private path")

    monkeypatch.setattr(os, "replace", failed_replace)
    with pytest.raises(PreferencesError, match="Preferences unavailable") as error:
        store.save(UserPreferences(language="ru"))
    assert "private path" not in str(error.value)
    assert path.read_bytes() == before
    assert not list(path.parent.glob(".aurora-settings-*"))


def test_unsafe_or_nonregular_settings_location_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "AURORA" / "settings.json"
    path.parent.mkdir()
    path.mkdir()
    with pytest.raises(PreferencesError, match="Unsafe preferences file"):
        PreferencesStore(path).load()
    path.rmdir()
    path.write_text("{}", encoding="utf-8")
    original = Path.is_symlink

    def linked(self: Path) -> bool:
        return self == path or original(self)

    monkeypatch.setattr(Path, "is_symlink", linked)
    with pytest.raises(PreferencesError, match="Unsafe preferences file"):
        PreferencesStore(path).load()
    with pytest.raises(PreferencesError):
        PreferencesStore(path).save(UserPreferences())


def test_hardlinked_settings_file_cannot_be_read_or_overwritten(tmp_path: Path) -> None:
    directory = tmp_path / "AURORA"
    directory.mkdir()
    source = tmp_path / "shared.json"
    source.write_text("private", encoding="utf-8")
    path = directory / "settings.json"
    os.link(source, path)
    store = PreferencesStore(path)
    with pytest.raises(PreferencesError, match="Unsafe preferences file"):
        store.load()
    with pytest.raises(PreferencesError):
        store.save(UserPreferences())
    assert source.read_text("utf-8") == "private"


def test_unsafe_parent_and_invalid_explicit_path_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(PreferencesError):
        PreferencesStore(Path("relative/settings.json"))
    with pytest.raises(PreferencesError):
        PreferencesStore(tmp_path / "other.json")
    parent = tmp_path / "AURORA"
    parent.mkdir()
    original = Path.is_junction

    def junction(self: Path) -> bool:
        return self == parent or original(self)

    monkeypatch.setattr(Path, "is_junction", junction)
    with pytest.raises(PreferencesError, match="Unsafe preferences location"):
        PreferencesStore(parent / "settings.json").load()
    assert not (parent / "settings.json").exists()


def test_no_existing_preferences_are_changed_by_invalid_save(tmp_path: Path) -> None:
    store = PreferencesStore(tmp_path / "AURORA" / "settings.json")
    original = UserPreferences(language="en")
    store.save(original)
    before = (tmp_path / "AURORA" / "settings.json").read_bytes()
    invalid = replace(original, language="ru")
    object.__setattr__(invalid, "general_model", "")
    with pytest.raises(PreferencesError):
        store.save(invalid)
    assert (tmp_path / "AURORA" / "settings.json").read_bytes() == before
