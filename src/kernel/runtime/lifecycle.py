"""KR-006 lifecycle transition coordinator."""

from __future__ import annotations

from src.core.exceptions import RuntimeInitializationError, RuntimeShutdownError
from src.core.types import HealthStatus, RuntimeLayer, RuntimeStatus
from src.kernel.contracts.lifecycle import LifecycleContract, LifecycleState
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.hooks import HookRuntime, LifecycleHook
from src.kernel.runtime.state import StateRuntime


class LifecycleRuntime(LifecycleContract, RuntimeContract):
    """Coordinate participants while StateRuntime owns status mutation."""

    def __init__(self) -> None:
        self._state = StateRuntime()
        self._hooks = HookRuntime()
        self._runtimes: list[RuntimeContract] = []

    @property
    def runtime_name(self) -> str:
        return "lifecycle"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    @property
    def status(self) -> RuntimeStatus:
        return self._state.current()

    def register(self, runtime: RuntimeContract) -> None:
        if runtime not in self._runtimes:
            self._runtimes.append(runtime)

    def hooks(self) -> HookRuntime:
        return self._hooks

    async def initialize(self) -> None:
        await self.transition(RuntimeStatus.INITIALIZING)
        try:
            await self._hooks.execute(LifecycleHook.BEFORE_INITIALIZE)
            for runtime in self._runtimes:
                await runtime.initialize()
            await self._hooks.execute(LifecycleHook.AFTER_INITIALIZE)
            await self.transition(RuntimeStatus.READY)
        except Exception as exc:
            self._fail()
            raise RuntimeInitializationError("Runtime initialization failed") from exc

    async def start(self) -> None:
        await self.transition(RuntimeStatus.STARTING)
        try:
            await self._hooks.execute(LifecycleHook.BEFORE_START)
            for runtime in self._runtimes:
                await runtime.start()
            await self._hooks.execute(LifecycleHook.AFTER_START)
            await self.transition(RuntimeStatus.RUNNING)
        except Exception as exc:
            self._fail()
            raise RuntimeInitializationError("Runtime startup failed") from exc

    async def stop(self) -> None:
        await self.transition(RuntimeStatus.STOPPING)
        try:
            await self._hooks.execute(LifecycleHook.BEFORE_STOP)
            for runtime in reversed(self._runtimes):
                await runtime.stop()
            await self._hooks.execute(LifecycleHook.AFTER_STOP)
            await self.transition(RuntimeStatus.STOPPED)
        except Exception as exc:
            self._fail()
            raise RuntimeShutdownError("Runtime shutdown failed") from exc

    async def shutdown(self) -> None:
        await self.transition(RuntimeStatus.SHUTTING_DOWN)
        try:
            for runtime in reversed(self._runtimes):
                await runtime.shutdown()
            await self.transition(RuntimeStatus.TERMINATED)
            self._hooks.clear()
        except Exception as exc:
            self._fail()
            raise RuntimeShutdownError("Runtime resource release failed") from exc

    async def transition(self, target: RuntimeStatus) -> None:
        self._state.transition(target)

    def state(self) -> LifecycleState:
        return self._state.snapshot()

    def health(self) -> HealthStatus:
        return HealthStatus.ERROR if self.status is RuntimeStatus.FAILED else HealthStatus.OK

    def _fail(self) -> None:
        if self.status is not RuntimeStatus.FAILED and self._state.can_transition(
            RuntimeStatus.FAILED
        ):
            self._state.transition(RuntimeStatus.FAILED)


__all__ = ["LifecycleRuntime"]
