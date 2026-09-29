import pytest

from src.render import RenderContract, RenderNode, RenderRuntime


@pytest.mark.asyncio
async def test_render_lifecycle() -> None:
    runtime: RenderContract = RenderRuntime()
    await runtime.initialize()
    await runtime.start()
    assert runtime.render(RenderNode(node_id="root", kind="document")).root.node_id == "root"
    await runtime.stop()
    await runtime.shutdown()
