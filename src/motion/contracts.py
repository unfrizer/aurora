"""Immutable public contracts for the Wave 5 Motion Runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.kernel.contracts.runtime import RuntimeContract


@dataclass(slots=True, frozen=True, kw_only=True)
class MotionDefinition:
    """An immutable request to sample progress over a finite duration."""

    motion_id: str
    duration_ms: float


@dataclass(slots=True, frozen=True, kw_only=True)
class MotionSample:
    """An immutable normalized progress result for one motion definition."""

    motion_id: str
    progress: float
    is_complete: bool


class MotionContract(RuntimeContract, ABC):
    """Runtime contract for deterministic, caller-clocked motion sampling."""

    @abstractmethod
    def validate(self, definition: MotionDefinition) -> None:
        """Validate an immutable motion definition."""

    @abstractmethod
    def sample(self, definition: MotionDefinition, elapsed_ms: float) -> MotionSample:
        """Validate and sample normalized progress at an elapsed time."""


__all__ = ["MotionContract", "MotionDefinition", "MotionSample"]
