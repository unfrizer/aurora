"""Manifest declaration for the Wave 3 Layout Runtime module."""

from __future__ import annotations

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.kernel.contracts.module import RuntimeModuleManifest

LAYOUT_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("layout.core"),
    runtime_layer=RuntimeLayer.L2_LAYOUT,
    depends_on=(),
    provides=(ServiceId("layout.core"),),
    version="1.0.0",
)


__all__ = ["LAYOUT_MANIFEST"]
