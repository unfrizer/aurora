from __future__ import annotations

from src.core.types import HealthStatus
from src.kernel.runtime.bootstrap import BootstrapRuntime


async def test_wave_one_runtime_health_is_available_after_build() -> None:
    runtime = await BootstrapRuntime().build()
    assert runtime.health() is HealthStatus.OK
