from __future__ import annotations

import pytest

from src.platform import PlatformContract, PlatformDescriptor, PlatformRuntime


@pytest.mark.asyncio
async def test_platform_runtime_lifecycle() -> None:
    runtime: PlatformContract = PlatformRuntime()
    await runtime.initialize()
    await runtime.start()
    assert (
        runtime.configure(
            PlatformDescriptor(platform_id="windows", display_name="Windows")
        ).revision
        == 1
    )
    await runtime.stop()
    await runtime.shutdown()
