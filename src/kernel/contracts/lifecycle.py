"""
AURORA Runtime Engine — KR-004 Kernel Contracts
Module: KR-004
File: src/kernel/contracts/lifecycle.py

Canonical Runtime Lifecycle contract.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from src.core.types import RuntimeStatus

# ============================================================================
# Lifecycle State Contract
# ============================================================================


@dataclass(frozen=True, kw_only=True, slots=True)
class LifecycleState:
    """
    Immutable lifecycle state of a runtime module.
    """

    current: RuntimeStatus
    previous: RuntimeStatus | None
    entered_at: datetime
    transition_count: int

    @property
    def is_running(self) -> bool:
        return self.current is RuntimeStatus.RUNNING

    @property
    def is_ready(self) -> bool:
        return self.current is RuntimeStatus.READY

    @property
    def is_failed(self) -> bool:
        return self.current is RuntimeStatus.FAILED

    @property
    def is_terminal(self) -> bool:
        return self.current in {RuntimeStatus.FAILED, RuntimeStatus.TERMINATED}

    def __post_init__(self) -> None:
        if self.transition_count < 0:
            raise ValueError("transition_count must be non-negative")
        if self.entered_at.tzinfo is None:
            raise ValueError("entered_at must be timezone-aware")


# ============================================================================
# Lifecycle Contract
# ============================================================================


class LifecycleContract(ABC):
    """
    Canonical runtime lifecycle contract.

    Defines the mandatory lifecycle interface for runtime modules without
    providing any implementation.
    """

    @abstractmethod
    async def transition(self, target: RuntimeStatus) -> None:
        """Transition to a canonical lifecycle state."""

    @abstractmethod
    def state(self) -> LifecycleState:
        """Return the immutable lifecycle snapshot."""


__all__ = ["LifecycleContract", "LifecycleState"]
