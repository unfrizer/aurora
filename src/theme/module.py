"""Manifest declaration for the Wave 4 Theme Runtime module."""

from __future__ import annotations

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.kernel.contracts.module import RuntimeModuleManifest

THEME_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("theme.core"),
    runtime_layer=RuntimeLayer.L3_THEME,
    depends_on=(),
    provides=(ServiceId("theme.core"),),
    version="1.0.0",
)


__all__ = ["THEME_MANIFEST"]
