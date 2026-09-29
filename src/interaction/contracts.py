"""Immutable public contracts for the Wave 6 Interaction Runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.kernel.contracts.runtime import RuntimeContract


@dataclass(slots=True, frozen=True, kw_only=True)
class InteractionRequest:
    """An immutable, opaque request from a future interaction surface."""

    interaction_id: str
    action: str
    target_id: str


@dataclass(slots=True, frozen=True, kw_only=True)
class InteractionSnapshot:
    """An immutable revisioned view of the most recent interaction request."""

    revision: int
    latest: InteractionRequest | None


class InteractionContract(RuntimeContract, ABC):
    """Runtime contract for deterministic latest-interaction ownership."""

    @abstractmethod
    def current(self) -> InteractionRequest | None:
        """Return the latest submitted request, if any."""

    @abstractmethod
    def snapshot(self) -> InteractionSnapshot:
        """Return the latest request and its revision."""

    @abstractmethod
    def submit(self, request: InteractionRequest) -> InteractionSnapshot:
        """Validate and record one interaction request."""

    @abstractmethod
    def clear(self) -> InteractionSnapshot:
        """Clear the latest request when one exists."""


__all__ = ["InteractionContract", "InteractionRequest", "InteractionSnapshot"]
