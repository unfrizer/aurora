"""Manifest declaration for the Wave 7 Accessibility Runtime module."""

from __future__ import annotations

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.kernel.contracts.module import RuntimeModuleManifest

ACCESSIBILITY_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("accessibility.core"),
    runtime_layer=RuntimeLayer.L6_ACCESSIBILITY,
    depends_on=(),
    provides=(ServiceId("accessibility.core"),),
    version="1.0.0",
)


__all__ = ["ACCESSIBILITY_MANIFEST"]
