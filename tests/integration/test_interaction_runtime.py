"""Integration test for the Wave 6 Interaction Runtime."""

from __future__ import annotations

import pytest

from src.interaction import InteractionContract, InteractionRequest, InteractionRuntime


@pytest.mark.asyncio
async def test_interaction_runtime_supports_a_complete_in_memory_lifecycle() -> None:
    runtime: InteractionContract = InteractionRuntime()
    request = InteractionRequest(interaction_id="select-1", action="select", target_id="hero")

    await runtime.initialize()
    await runtime.start()
    snapshot = runtime.submit(request)

    assert snapshot.revision == 1
    assert runtime.current() == request

    await runtime.stop()
    assert runtime.current() == request
    await runtime.shutdown()
