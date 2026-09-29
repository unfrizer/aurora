"""Manifest declaration for the Wave 9 Render Runtime."""

from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.kernel.contracts.module import RuntimeModuleManifest

RENDER_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("render.core"),
    runtime_layer=RuntimeLayer.L8_RENDER,
    depends_on=(),
    provides=(ServiceId("render.core"),),
    version="1.0.0",
)
__all__ = ["RENDER_MANIFEST"]
