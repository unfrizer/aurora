from __future__ import annotations

from itertools import pairwise

import pytest

from src.core.exceptions import RuntimeStateError
from src.core.types import HealthStatus, RuntimeLayer, RuntimeStatus
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.state import StateRuntime


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


@pytest.mark.parametrize("source", tuple(RuntimeStatus))
@pytest.mark.parametrize("target", tuple(RuntimeStatus))
def test_state_runtime_accepts_only_the_ab00b_transition_matrix(
    source: RuntimeStatus, target: RuntimeStatus
) -> None:
    normal = (
        RuntimeStatus.CREATED,
        RuntimeStatus.INITIALIZING,
        RuntimeStatus.READY,
        RuntimeStatus.STARTING,
        RuntimeStatus.RUNNING,
        RuntimeStatus.STOPPING,
        RuntimeStatus.STOPPED,
        RuntimeStatus.SHUTTING_DOWN,
        RuntimeStatus.TERMINATED,
    )
    failure_sources = (
        RuntimeStatus.INITIALIZING,
        RuntimeStatus.READY,
        RuntimeStatus.STARTING,
        RuntimeStatus.RUNNING,
        RuntimeStatus.STOPPING,
        RuntimeStatus.SHUTTING_DOWN,
    )
    allowed: set[tuple[RuntimeStatus, RuntimeStatus]] = set(pairwise(normal))
    allowed.update((status, RuntimeStatus.FAILED) for status in failure_sources)
    state = StateRuntime()
    if source is RuntimeStatus.FAILED:
        state.transition(RuntimeStatus.INITIALIZING)
        state.transition(RuntimeStatus.FAILED)
    else:
        for status in normal[1:]:
            if state.current() is source:
                break
            state.transition(status)
    before = state.snapshot()
    assert state.can_transition(target) == ((source, target) in allowed)
    if (source, target) in allowed:
        after = state.transition(target)
        assert after.current is target
        assert after.previous is source
        assert after.transition_count == before.transition_count + 1
    else:
        with pytest.raises(RuntimeStateError):
            state.transition(target)
        assert state.snapshot() == before
