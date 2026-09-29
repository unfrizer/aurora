"""Immutable public contracts for the Wave 8 Platform Runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.kernel.contracts.runtime import RuntimeContract


@dataclass(slots=True, frozen=True, kw_only=True)
class PlatformDescriptor:
    """An immutable, caller-supplied target-platform description."""

    platform_id: str
    display_name: str


@dataclass(slots=True, frozen=True, kw_only=True)
class PlatformSnapshot:
    """An immutable revisioned view of the configured platform."""

    revision: int
    platform: PlatformDescriptor | None


class PlatformContract(RuntimeContract, ABC):
    """Runtime contract for deterministic platform descriptor ownership."""

    @abstractmethod
    def current(self) -> PlatformDescriptor | None: ...
    @abstractmethod
    def snapshot(self) -> PlatformSnapshot: ...
    @abstractmethod
    def configure(self, platform: PlatformDescriptor) -> PlatformSnapshot: ...
    @abstractmethod
    def clear(self) -> PlatformSnapshot: ...


__all__ = ["PlatformContract", "PlatformDescriptor", "PlatformSnapshot"]
