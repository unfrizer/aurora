"""Manifest tests for the Accessibility Runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.accessibility import ACCESSIBILITY_MANIFEST
from src.core.types import ModuleId, RuntimeLayer, ServiceId


def test_accessibility_manifest_has_the_canonical_identity() -> None:
    assert ACCESSIBILITY_MANIFEST.module_id == ModuleId("accessibility.core")
    assert ACCESSIBILITY_MANIFEST.runtime_layer is RuntimeLayer.L6_ACCESSIBILITY
    assert ACCESSIBILITY_MANIFEST.depends_on == ()
    assert ACCESSIBILITY_MANIFEST.provides == (ServiceId("accessibility.core"),)
    assert ACCESSIBILITY_MANIFEST.version == "1.0.0"


def test_accessibility_manifest_is_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        ACCESSIBILITY_MANIFEST.version = "2.0.0"  # type: ignore[misc]
