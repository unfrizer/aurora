"""Persistence boundary smoke without real user settings or projects."""

from __future__ import annotations

from pathlib import Path

from src.preferences import PreferencesStore, UserPreferences


def test_reopen_preferences_without_touching_sibling_projects(tmp_path: Path) -> None:
    app_root = tmp_path / "local"
    app_root.mkdir()
    projects = app_root / "Projects"
    projects.mkdir()
    project_marker = projects / "project.json"
    project_marker.write_text('{"untouched":true}', encoding="utf-8")
    path = app_root / "AURORA" / "settings.json"

    first = PreferencesStore(path)
    first.save(UserPreferences(language="ru", onboarding_completed=True))
    reopened = PreferencesStore(path)
    assert reopened.load() == UserPreferences(language="ru", onboarding_completed=True)
    reopened.save(UserPreferences(language="en", general_model="next-model"))
    assert first.load() == UserPreferences(language="en", general_model="next-model")
    assert project_marker.read_text("utf-8") == '{"untouched":true}'
