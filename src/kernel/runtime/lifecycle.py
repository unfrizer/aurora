"""AURORA KR-006: lifecycle coordination and resumable best-effort cleanup."""

from __future__ import annotations

from asyncio import CancelledError
from typing import NoReturn, cast

from src.core.exceptions import (
    RuntimeInitializationError,
    RuntimeShutdownError,
    RuntimeStateError,
)
from src.core.types import HealthStatus, RuntimeLayer, RuntimeStatus
from src.kernel.contracts.lifecycle import LifecycleContract, LifecycleState
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.hooks import HookRuntime, LifecycleHook
from src.kernel.runtime.state import StateRuntime


class LifecycleRuntime(LifecycleContract, RuntimeContract):
    """Coordinate touched participants without owning another status source."""

    def __init__(self) -> None:
        self._state = StateRuntime()
        self._hooks = HookRuntime()
        self._runtimes: list[RuntimeContract] = []
        self._initialize_touched: list[RuntimeContract] = []
        self._start_touched: list[RuntimeContract] = []
        self._errors: list[Exception] = []
        self._busy = False
        self._stop_started = False
        self._before_stop_complete = False
        self._after_stop_complete = False
        self._stop_complete = False
        self._shutdown_complete = False

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
        self._require_idle()
        if self.status is not RuntimeStatus.CREATED or runtime is self:
            raise RuntimeStateError(
                "Lifecycle registration requires an unstarted participant graph"
            )
        if not any(existing is runtime for existing in self._runtimes):
            self._runtimes.append(runtime)

    def hooks(self) -> HookRuntime:
        return self._hooks

    async def initialize(self) -> None:
        self._begin()
        try:
            self._state.transition(RuntimeStatus.INITIALIZING)
            try:
                await self._hooks.execute(LifecycleHook.BEFORE_INITIALIZE)
                for runtime in self._runtimes:
                    self._initialize_touched.append(runtime)
                    await runtime.initialize()
                await self._hooks.execute(LifecycleHook.AFTER_INITIALIZE)
                self._state.transition(RuntimeStatus.READY)
            except CancelledError as cancelled:
                self._fail()
                await self._cancel_cleanup(cancelled, stop=False, shutdown=True)
            except Exception as exc:
                self._errors.append(exc)
                self._fail()
                try:
                    await self._shutdown_cleanup()
                except CancelledError as cancelled:
                    self._raise_cancellation(cancelled)
                self._raise_initialization("Runtime initialization failed")
        finally:
            self._busy = False

    async def start(self) -> None:
        self._begin()
        try:
            self._state.transition(RuntimeStatus.STARTING)
            try:
                await self._hooks.execute(LifecycleHook.BEFORE_START)
                for runtime in self._runtimes:
                    self._start_touched.append(runtime)
                    await runtime.start()
                await self._hooks.execute(LifecycleHook.AFTER_START)
                self._state.transition(RuntimeStatus.RUNNING)
            except CancelledError as cancelled:
                self._fail()
                await self._cancel_cleanup(cancelled, stop=True, shutdown=True)
            except Exception as exc:
                self._errors.append(exc)
                self._fail()
                try:
                    await self._stop_cleanup()
                    await self._shutdown_cleanup()
                except CancelledError as cancelled:
                    self._raise_cancellation(cancelled)
                self._raise_initialization("Runtime startup failed")
        finally:
            self._busy = False

    async def stop(self) -> None:
        self._begin()
        try:
            if self._stop_complete or self._shutdown_complete:
                return
            if self.status is not RuntimeStatus.FAILED:
                self._state.transition(RuntimeStatus.STOPPING)
            try:
                await self._stop_cleanup()
            except CancelledError as cancelled:
                self._fail()
                await self._cancel_cleanup(cancelled, stop=True, shutdown=False)
            if self._errors:
                self._raise_shutdown("Runtime stop cleanup failed")
            if self.status is not RuntimeStatus.FAILED:
                self._state.transition(RuntimeStatus.STOPPED)
        finally:
            self._busy = False

    async def shutdown(self) -> None:
        self._begin()
        try:
            if self._shutdown_complete:
                return
            if self.status is not RuntimeStatus.FAILED:
                self._state.transition(RuntimeStatus.SHUTTING_DOWN)
            try:
                if self._start_touched or self._stop_started:
                    await self._stop_cleanup()
                await self._shutdown_cleanup()
            except CancelledError as cancelled:
                self._fail()
                await self._cancel_cleanup(cancelled, stop=True, shutdown=True)
            if self._errors:
                self._raise_shutdown("Runtime resource release failed")
            if self.status is not RuntimeStatus.FAILED:
                self._state.transition(RuntimeStatus.TERMINATED)
        finally:
            self._busy = False

    async def transition(self, target: RuntimeStatus) -> None:
        self._require_idle()
        self._state.transition(target)

    def state(self) -> LifecycleState:
        return self._state.snapshot()

    def health(self) -> HealthStatus:
        return HealthStatus.ERROR if self.status is RuntimeStatus.FAILED else HealthStatus.OK

    def _require_idle(self) -> None:
        if self._busy:
            raise RuntimeStateError("Lifecycle operation is already active")

    def _begin(self) -> None:
        self._require_idle()
        self._busy = True

    async def _stop_hook(self, hook: LifecycleHook) -> None:
        try:
            await self._hooks.execute(hook)
        except CancelledError as cancelled:
            cause = cancelled.__cause__
            if isinstance(cause, ExceptionGroup):
                self._errors.extend(cast("ExceptionGroup[Exception]", cause).exceptions)
            raise
        except ExceptionGroup as errors:
            self._errors.extend(errors.exceptions)
            self._fail()

    async def _stop_cleanup(self) -> None:
        if self._stop_complete:
            return
        self._stop_started = True
        if not self._before_stop_complete:
            await self._stop_hook(LifecycleHook.BEFORE_STOP)
            self._before_stop_complete = True
        while self._start_touched:
            runtime = self._start_touched[-1]
            try:
                await runtime.stop()
            except CancelledError:
                raise
            except Exception as exc:
                self._errors.append(exc)
                self._fail()
            self._start_touched.pop()
        if not self._after_stop_complete:
            await self._stop_hook(LifecycleHook.AFTER_STOP)
            self._after_stop_complete = True
        self._stop_complete = True

    async def _shutdown_cleanup(self) -> None:
        if self._shutdown_complete:
            return
        while self._initialize_touched:
            runtime = self._initialize_touched[-1]
            try:
                await runtime.shutdown()
            except CancelledError:
                raise
            except Exception as exc:
                self._errors.append(exc)
                self._fail()
            self._initialize_touched.pop()
        self._runtimes.clear()
        self._hooks.clear()
        self._shutdown_complete = True

    async def _cancel_cleanup(
        self, cancelled: CancelledError, *, stop: bool, shutdown: bool
    ) -> NoReturn:
        try:
            if stop:
                await self._stop_cleanup()
            if shutdown:
                await self._shutdown_cleanup()
        except CancelledError as interrupted:
            cancelled = interrupted
        self._raise_cancellation(cancelled)

    def _raise_initialization(self, message: str) -> NoReturn:
        errors = tuple(self._errors)
        self._errors.clear()
        cause = errors[0] if len(errors) == 1 else ExceptionGroup(message, errors)
        raise RuntimeInitializationError(message) from cause

    def _raise_shutdown(self, message: str) -> NoReturn:
        errors = tuple(self._errors)
        self._errors.clear()
        raise RuntimeShutdownError(message) from ExceptionGroup(message, errors)

    def _raise_cancellation(self, cancelled: CancelledError) -> NoReturn:
        if self._errors:
            errors = tuple(self._errors)
            self._errors.clear()
            raise cancelled from ExceptionGroup(
                "Lifecycle cleanup errors before cancellation", errors
            )
        raise cancelled

    def _fail(self) -> None:
        if self._state.can_transition(RuntimeStatus.FAILED):
            self._state.transition(RuntimeStatus.FAILED)


__all__ = ["LifecycleRuntime"]
