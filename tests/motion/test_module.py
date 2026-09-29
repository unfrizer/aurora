"""Manifest tests for the Motion Runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.motion import MOTION_MANIFEST


def test_motion_manifest_has_the_canonical_identity() -> None:
    assert MOTION_MANIFEST.module_id == ModuleId("motion.core")
    assert MOTION_MANIFEST.runtime_layer is RuntimeLayer.L4_MOTION
    assert MOTION_MANIFEST.depends_on == ()
    assert MOTION_MANIFEST.provides == (ServiceId("motion.core"),)
    assert MOTION_MANIFEST.version == "1.0.0"


def test_motion_manifest_is_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        MOTION_MANIFEST.version = "2.0.0"  # type: ignore[misc]
