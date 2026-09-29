from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.layout import LAYOUT_MANIFEST
from src.layout.runtime import LayoutRuntime


def test_layout_manifest_matches_the_canonical_module_declaration() -> None:
    assert LAYOUT_MANIFEST.module_id == ModuleId("layout.core")
    assert LAYOUT_MANIFEST.runtime_layer is RuntimeLayer.L2_LAYOUT
    assert LAYOUT_MANIFEST.depends_on == ()
    assert LAYOUT_MANIFEST.provides == (ServiceId("layout.core"),)
    assert LAYOUT_MANIFEST.version == "1.0.0"


def test_layout_manifest_is_immutable_and_does_not_construct_a_runtime() -> None:
    assert not hasattr(LAYOUT_MANIFEST, "runtime")
    with pytest.raises(FrozenInstanceError):
        LAYOUT_MANIFEST.version = "2.0.0"  # type: ignore[misc]
    assert LayoutRuntime().runtime_name == "layout"
