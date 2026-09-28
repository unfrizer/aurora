"""Public contracts for the Wave 2 Shared State Runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.core.types import JSONValue, Metadata
from src.kernel.contracts.runtime import RuntimeContract


@dataclass(slots=True, frozen=True, kw_only=True)
class StateSnapshot:
    """An immutable shell around a detached shared-state snapshot."""

    revision: int
    values: Metadata


class SharedStateContract(RuntimeContract, ABC):
    """Contract for the L1 runtime that owns shared in-process state."""

    @abstractmethod
    def get(self, key: str) -> JSONValue | None:
        """Return a detached value for ``key``, or ``None`` when it is absent."""

    @abstractmethod
    def contains(self, key: str) -> bool:
        """Return whether ``key`` is present in shared state."""

    @abstractmethod
    def snapshot(self) -> StateSnapshot:
        """Return the complete detached shared-state snapshot."""

    @abstractmethod
    def set(self, key: str, value: JSONValue) -> StateSnapshot:
        """Replace ``key`` with ``value`` and return the new snapshot."""

    @abstractmethod
    def remove(self, key: str) -> StateSnapshot:
        """Remove ``key`` when it is present and return the current snapshot."""

    @abstractmethod
    def clear(self) -> StateSnapshot:
        """Clear state when non-empty and return the current snapshot."""


__all__ = ["SharedStateContract", "StateSnapshot"]
