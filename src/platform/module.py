"""Manifest declaration for the Wave 8 Platform Runtime module."""

from __future__ import annotations

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.kernel.contracts.module import RuntimeModuleManifest

PLATFORM_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("platform.core"),
    runtime_layer=RuntimeLayer.L7_PLATFORM,
    depends_on=(),
    provides=(ServiceId("platform.core"),),
    version="1.0.0",
)
__all__ = ["PLATFORM_MANIFEST"]
