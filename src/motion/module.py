"""Manifest declaration for the Wave 5 Motion Runtime module."""

from __future__ import annotations

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.kernel.contracts.module import RuntimeModuleManifest

MOTION_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("motion.core"),
    runtime_layer=RuntimeLayer.L4_MOTION,
    depends_on=(),
    provides=(ServiceId("motion.core"),),
    version="1.0.0",
)


__all__ = ["MOTION_MANIFEST"]
