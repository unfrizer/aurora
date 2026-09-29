from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.platform import PLATFORM_MANIFEST


def test_manifest_identity() -> None:
    assert PLATFORM_MANIFEST.module_id == ModuleId("platform.core")
    assert PLATFORM_MANIFEST.runtime_layer is RuntimeLayer.L7_PLATFORM
    assert PLATFORM_MANIFEST.depends_on == () and PLATFORM_MANIFEST.provides == (
        ServiceId("platform.core"),
    )


def test_manifest_is_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        PLATFORM_MANIFEST.version = "2.0.0"  # type: ignore[misc]
