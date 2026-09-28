"""
AURORA Runtime Engine — KR-004 Kernel Contracts
Module: KR-004
File: src/kernel/contracts/events.py

Canonical Typed Event contracts.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.core.types import EventId, EventPriority, Payload, SessionId
from src.kernel.contracts.context import TraceContext

# ============================================================================
# Typed Default Factories
# ============================================================================


def _payload_factory() -> Payload:
    """Return an empty payload with the canonical Payload type."""
    return {}


def _timestamp_factory() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(UTC)


# ============================================================================
# Typed Event Contract
# ============================================================================


@dataclass(frozen=True, kw_only=True, slots=True)
class RuntimeEvent:
    """
    Canonical immutable Typed Event contract.

    Every event exchanged between runtime modules must conform to this
    structure defined by Architecture Freeze v1.0.
    """

    event_id: EventId
    event_type: str
    session_id: SessionId
    trace: TraceContext
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=_timestamp_factory)
    payload: Payload = field(default_factory=_payload_factory)


# ============================================================================
# Event Handler Contract
# ============================================================================


class EventHandlerContract(ABC):
    """
    Contract implemented by event handlers.

    Event handlers receive exactly one typed runtime event.
    """

    @abstractmethod
    async def handle(self, event: RuntimeEvent) -> None:
        """
        Handle a runtime event.

        No Event Bus behavior is implemented here.
        """


__all__ = ["EventHandlerContract", "RuntimeEvent"]
