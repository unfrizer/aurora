"""Manifest declaration for the Wave 2 Shared State Runtime module."""

from __future__ import annotations

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.kernel.contracts.module import RuntimeModuleManifest

SHARED_STATE_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("state.shared"),
    runtime_layer=RuntimeLayer.L1_STATE,
    depends_on=(),
    provides=(ServiceId("state.shared"),),
    version="1.0.0",
)


__all__ = ["SHARED_STATE_MANIFEST"]
