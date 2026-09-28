from __future__ import annotations

from src.core.types import RuntimeLayer
from src.state import SharedStateContract, SharedStateRuntime


async def test_shared_state_runtime_lifecycle_flow_uses_only_its_public_contract() -> None:
    runtime: SharedStateContract = SharedStateRuntime()

    await runtime.initialize()
    await runtime.start()
    first = runtime.set("workspace", {"tabs": ["kernel"]})

    assert runtime.runtime_layer is RuntimeLayer.L1_STATE
    assert runtime.get("workspace") == {"tabs": ["kernel"]}
    assert runtime.snapshot() == first

    await runtime.stop()
    assert runtime.get("workspace") == {"tabs": ["kernel"]}

    await runtime.shutdown()
