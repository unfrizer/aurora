"""KR-006 lifecycle hook registry."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from enum import StrEnum


class LifecycleHook(StrEnum):
    """Frozen lifecycle hook vocabulary."""

    BEFORE_INITIALIZE = "before_initialize"
    AFTER_INITIALIZE = "after_initialize"
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"


class HookRuntime:
    """Own ordered hook registration and sequential execution."""

    def __init__(self) -> None:
        self._callbacks: dict[LifecycleHook, list[Callable[[], Awaitable[None]]]] = {
            hook: [] for hook in LifecycleHook
        }

    def register(self, hook: LifecycleHook, callback: Callable[[], Awaitable[None]]) -> None:
        callbacks = self._callbacks[hook]
        if callback not in callbacks:
            callbacks.append(callback)

    def unregister(self, hook: LifecycleHook, callback: Callable[[], Awaitable[None]]) -> None:
        callbacks = self._callbacks[hook]
        if callback in callbacks:
            callbacks.remove(callback)

    async def execute(self, hook: LifecycleHook) -> None:
        for callback in tuple(self._callbacks[hook]):
            await callback()

    def clear(self) -> None:
        for callbacks in self._callbacks.values():
            callbacks.clear()


__all__ = ["HookRuntime", "LifecycleHook"]
