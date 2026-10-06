"""AURORA KR-006: instance-owned sequential lifecycle hook registry."""

from __future__ import annotations

from asyncio import CancelledError
from collections.abc import Awaitable, Callable
from enum import StrEnum


class LifecycleHook(StrEnum):
    """Frozen lifecycle hook vocabulary; shutdown introduces no new phase."""

    BEFORE_INITIALIZE = "before_initialize"
    AFTER_INITIALIZE = "after_initialize"
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"


class HookRuntime:
    """Own ordered callbacks and interrupted stop-hook attempt progress."""

    def __init__(self) -> None:
        self._callbacks: dict[LifecycleHook, list[Callable[[], Awaitable[None]]]] = {
            hook: [] for hook in LifecycleHook
        }
        self._pending: dict[LifecycleHook, list[Callable[[], Awaitable[None]]]] = {}

    def register(self, hook: LifecycleHook, callback: Callable[[], Awaitable[None]]) -> None:
        callbacks = self._callbacks[hook]
        if not any(existing is callback for existing in callbacks):
            callbacks.append(callback)

    def unregister(self, hook: LifecycleHook, callback: Callable[[], Awaitable[None]]) -> None:
        callbacks = self._callbacks[hook]
        for index, existing in enumerate(callbacks):
            if existing is callback:
                del callbacks[index]
                break

    async def execute(self, hook: LifecycleHook) -> None:
        if hook not in (LifecycleHook.BEFORE_STOP, LifecycleHook.AFTER_STOP):
            for callback in tuple(self._callbacks[hook]):
                await callback()
            return
        pending = self._pending.setdefault(hook, list(self._callbacks[hook]))
        errors: list[Exception] = []
        while pending:
            callback = pending.pop(0)
            try:
                await callback()
            except CancelledError as cancelled:
                if errors:
                    raise cancelled from ExceptionGroup(
                        "Stop hook errors before cancellation", errors
                    )
                raise
            except Exception as exc:
                errors.append(exc)
        self._pending.pop(hook, None)
        if errors:
            raise ExceptionGroup("Lifecycle stop hook failures", errors)

    def clear(self) -> None:
        for callbacks in self._callbacks.values():
            callbacks.clear()
        self._pending.clear()


__all__ = ["HookRuntime", "LifecycleHook"]
