"""Contract tests for the Theme Runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from src.kernel.contracts.runtime import RuntimeContract
from src.theme.contracts import ThemeContract, ThemeDefinition, ThemeSnapshot


def test_theme_models_are_frozen_dataclasses() -> None:
    definition = ThemeDefinition(
        theme_id="aurora",
        display_name="Aurora",
        tokens=(("color.primary", "#ff00ff"),),
    )
    snapshot = ThemeSnapshot(revision=0, theme=definition)

    assert is_dataclass(definition)
    assert is_dataclass(snapshot)
    with pytest.raises(FrozenInstanceError):
        definition.theme_id = "other"  # type: ignore[misc]


def test_theme_contract_is_abstract_runtime_contract() -> None:
    assert issubclass(ThemeContract, RuntimeContract)
    assert ThemeContract.__abstractmethods__ == {
        "clear",
        "get",
        "health",
        "initialize",
        "runtime_layer",
        "runtime_name",
        "set",
        "shutdown",
        "snapshot",
        "start",
        "stop",
    }
