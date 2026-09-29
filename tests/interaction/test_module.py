"""Manifest tests for the Interaction Runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.interaction import INTERACTION_MANIFEST


def test_interaction_manifest_has_the_canonical_identity() -> None:
    assert INTERACTION_MANIFEST.module_id == ModuleId("interaction.core")
    assert INTERACTION_MANIFEST.runtime_layer is RuntimeLayer.L5_INTERACTION
    assert INTERACTION_MANIFEST.depends_on == ()
    assert INTERACTION_MANIFEST.provides == (ServiceId("interaction.core"),)
    assert INTERACTION_MANIFEST.version == "1.0.0"


def test_interaction_manifest_is_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        INTERACTION_MANIFEST.version = "2.0.0"  # type: ignore[misc]
