"""Behavior tests for the Theme Runtime."""

from __future__ import annotations

from typing import cast

import pytest

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.theme import ThemeDefinition, ThemeRuntime, ThemeSnapshot


def _theme(*, tokens: tuple[tuple[str, str], ...] = ()) -> ThemeDefinition:
    return ThemeDefinition(theme_id="aurora", display_name="Aurora", tokens=tokens)


@pytest.mark.asyncio
async def test_identity_lifecycle_and_health_are_deterministic() -> None:
    runtime = ThemeRuntime()

    assert runtime.runtime_name == "theme"
    assert runtime.runtime_layer is RuntimeLayer.L3_THEME
    assert runtime.health() is HealthStatus.OK
    await runtime.initialize()
    await runtime.start()
    await runtime.stop()
    assert runtime.snapshot().revision == 0


def test_set_and_clear_follow_revision_semantics() -> None:
    runtime = ThemeRuntime()
    theme = _theme(tokens=(("color.primary", "#ffffff"),))

    assert runtime.get() is None
    expected = ThemeSnapshot(revision=1, theme=theme)
    assert runtime.set(theme) == runtime.snapshot() == expected
    assert runtime.set(theme).revision == 2
    assert runtime.clear().revision == 3
    assert runtime.get() is None
    assert runtime.clear().revision == 3


@pytest.mark.parametrize(
    "theme",
    [
        ThemeDefinition(theme_id=" ", display_name="Aurora"),
        ThemeDefinition(theme_id="aurora", display_name=" "),
        ThemeDefinition(theme_id="aurora", display_name="Aurora", tokens=(("", "#fff"),)),
        ThemeDefinition(theme_id="aurora", display_name="Aurora", tokens=(("color", " "),)),
        ThemeDefinition(
            theme_id="aurora",
            display_name="Aurora",
            tokens=(("color", "#fff"), ("color", "#000")),
        ),
    ],
)
def test_invalid_themes_are_rejected(theme: ThemeDefinition) -> None:
    with pytest.raises(ValidationError):
        ThemeRuntime().set(theme)


@pytest.mark.parametrize(
    "invalid_theme",
    [
        ThemeDefinition(theme_id=cast(str, None), display_name="Aurora"),
        ThemeDefinition(theme_id="aurora", display_name=cast(str, 123)),
        ThemeDefinition(
            theme_id="aurora",
            display_name="Aurora",
            tokens=cast(tuple[tuple[str, str], ...], [("color", "blue")]),
        ),
        ThemeDefinition(
            theme_id="aurora",
            display_name="Aurora",
            tokens=cast(tuple[tuple[str, str], ...], (["color", "blue"],)),
        ),
    ],
)
def test_invalid_theme_does_not_replace_existing_state(invalid_theme: ThemeDefinition) -> None:
    runtime = ThemeRuntime()
    before = runtime.set(_theme())

    with pytest.raises(ValidationError):
        runtime.set(invalid_theme)

    assert runtime.snapshot() == before


@pytest.mark.asyncio
async def test_shutdown_releases_theme_and_initialize_starts_a_fresh_lifetime() -> None:
    runtime = ThemeRuntime()
    runtime.set(_theme())
    await runtime.shutdown()

    with pytest.raises(RuntimeError):
        runtime.snapshot()

    await runtime.initialize()
    assert runtime.snapshot().revision == 0
    assert runtime.get() is None
