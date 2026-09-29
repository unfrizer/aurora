from src.core.types import ModuleId, RuntimeLayer, ServiceId
from src.render import RENDER_MANIFEST


def test_manifest() -> None:
    assert (
        RENDER_MANIFEST.module_id == ModuleId("render.core")
        and RENDER_MANIFEST.runtime_layer is RuntimeLayer.L8_RENDER
    )
    assert RENDER_MANIFEST.provides == (ServiceId("render.core"),)
