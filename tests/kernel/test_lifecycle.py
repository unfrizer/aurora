from __future__ import annotations

from src.core.types import HealthStatus, RuntimeLayer, RuntimeStatus
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.lifecycle import LifecycleRuntime


class RecordingRuntime(RuntimeContract):
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    @property
    def runtime_name(self) -> str:
        return "recording"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    async def initialize(self) -> None:
        self.calls.append("initialize")

    async def start(self) -> None:
        self.calls.append("start")

    async def stop(self) -> None:
        self.calls.append("stop")

    async def shutdown(self) -> None:
        self.calls.append("shutdown")

    def health(self) -> HealthStatus:
        return HealthStatus.OK


async def test_lifecycle_follows_resolved_transition_sequence() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    lifecycle.register(RecordingRuntime(calls))
    await lifecycle.initialize()
    await lifecycle.start()
    await lifecycle.stop()
    await lifecycle.shutdown()
    assert lifecycle.status is RuntimeStatus.TERMINATED
    assert calls == ["initialize", "start", "stop", "shutdown"]
