from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.state import SHARED_STATE_MANIFEST


def test_shared_state_manifest_matches_the_canonical_module_declaration() -> None:
    assert SHARED_STATE_MANIFEST.module_id == ModuleId("state.shared")
    assert SHARED_STATE_MANIFEST.runtime_layer is RuntimeLayer.L1_STATE
    assert SHARED_STATE_MANIFEST.depends_on == ()
    assert SHARED_STATE_MANIFEST.provides == (ServiceId("state.shared"),)
    assert SHARED_STATE_MANIFEST.version == "1.0.0"


def test_shared_state_manifest_is_immutable_and_has_no_runtime_side_effect() -> None:
    with pytest.raises(FrozenInstanceError):
        SHARED_STATE_MANIFEST.version = "2.0.0"  # type: ignore[misc]
