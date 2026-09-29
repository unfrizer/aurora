"""Integration test for the Wave 5 Motion Runtime."""

from __future__ import annotations

import pytest

from src.motion import MotionContract, MotionDefinition, MotionRuntime


@pytest.mark.asyncio
async def test_motion_runtime_supports_a_complete_in_memory_lifecycle() -> None:
    runtime: MotionContract = MotionRuntime()
    definition = MotionDefinition(motion_id="enter", duration_ms=250.0)

    await runtime.initialize()
    await runtime.start()
    sample = runtime.sample(definition, 125.0)

    assert sample.progress == 0.5
    assert sample.is_complete is False

    await runtime.stop()
    await runtime.shutdown()
