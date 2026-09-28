"""L1 Shared State Runtime implementation."""

# pyright: reportPrivateUsage=false

from __future__ import annotations

from src.core.types import HealthStatus, JSONValue, RuntimeLayer
from src.state.contracts import SharedStateContract, StateSnapshot
from src.state.store import _StateStore


class SharedStateRuntime(SharedStateContract):
    """Own shared in-process data state and detached snapshots."""

    def __init__(self) -> None:
        self._store: _StateStore | None = _StateStore()

    @property
    def runtime_name(self) -> str:
        return "shared_state"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L1_STATE

    async def initialize(self) -> None:
        if self._store is None:
            self._store = _StateStore()

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        self._store = None

    def health(self) -> HealthStatus:
        return HealthStatus.OK

    def get(self, key: str) -> JSONValue | None:
        return self._active_store().get(key)

    def contains(self, key: str) -> bool:
        return self._active_store().contains(key)

    def snapshot(self) -> StateSnapshot:
        return self._active_store().snapshot()

    def set(self, key: str, value: JSONValue) -> StateSnapshot:
        return self._active_store().set(key, value)

    def remove(self, key: str) -> StateSnapshot:
        return self._active_store().remove(key)

    def clear(self) -> StateSnapshot:
        return self._active_store().clear()

    def _active_store(self) -> _StateStore:
        if self._store is None:
            raise RuntimeError("Shared State Runtime is shut down")
        return self._store


__all__ = ["SharedStateRuntime"]
