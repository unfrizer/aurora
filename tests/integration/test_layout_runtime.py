from __future__ import annotations

from src.core.types import RuntimeLayer
from src.layout import LayoutContract, LayoutDirection, LayoutNode, LayoutRuntime, LayoutSize


async def test_layout_runtime_public_contract_lifecycle_flow() -> None:
    runtime: LayoutContract = LayoutRuntime()
    root = LayoutNode(
        node_id="root",
        size=LayoutSize(width=100.0, height=100.0),
        direction=LayoutDirection.VERTICAL,
        gap=2.0,
        children=(
            LayoutNode(node_id="child", size=LayoutSize(width=20.0, height=10.0)),
        ),
    )

    await runtime.initialize()
    await runtime.start()
    runtime.validate(root)
    result = runtime.layout(root)

    assert runtime.runtime_layer is RuntimeLayer.L2_LAYOUT
    assert result.children[0].rect.x == 0.0
    assert result.children[0].rect.y == 0.0

    await runtime.stop()
    await runtime.shutdown()
