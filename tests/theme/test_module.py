"""Manifest tests for the Theme Runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.theme import THEME_MANIFEST


def test_theme_manifest_has_the_canonical_identity() -> None:
    assert THEME_MANIFEST.module_id == ModuleId("theme.core")
    assert THEME_MANIFEST.runtime_layer is RuntimeLayer.L3_THEME
    assert THEME_MANIFEST.depends_on == ()
    assert THEME_MANIFEST.provides == (ServiceId("theme.core"),)
    assert THEME_MANIFEST.version == "1.0.0"


def test_theme_manifest_is_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        THEME_MANIFEST.version = "2.0.0"  # type: ignore[misc]
