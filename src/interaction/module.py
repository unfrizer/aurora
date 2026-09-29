"""Manifest declaration for the Wave 6 Interaction Runtime module."""

from __future__ import annotations

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.kernel.contracts.module import RuntimeModuleManifest

INTERACTION_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("interaction.core"),
    runtime_layer=RuntimeLayer.L5_INTERACTION,
    depends_on=(),
    provides=(ServiceId("interaction.core"),),
    version="1.0.0",
)


__all__ = ["INTERACTION_MANIFEST"]
