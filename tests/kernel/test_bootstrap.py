from __future__ import annotations

from src.core.types import RuntimeStatus
from src.kernel.runtime.bootstrap import BootstrapRuntime


async def test_bootstrap_builds_and_runs_runtime_graph() -> None:
    runtime = await BootstrapRuntime().build()
    await runtime.initialize()
    await runtime.start()
    assert runtime.status() is RuntimeStatus.RUNNING
    await runtime.stop()
    await runtime.shutdown()
    assert runtime.status() is RuntimeStatus.TERMINATED
