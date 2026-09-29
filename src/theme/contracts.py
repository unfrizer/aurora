"""Immutable public contracts for the Wave 4 Theme Runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.kernel.contracts.runtime import RuntimeContract


@dataclass(slots=True, frozen=True, kw_only=True)
class ThemeDefinition:
    """An immutable named visual theme with opaque, ordered string tokens."""

    theme_id: str
    display_name: str
    tokens: tuple[tuple[str, str], ...] = ()


@dataclass(slots=True, frozen=True, kw_only=True)
class ThemeSnapshot:
    """An immutable revisioned view of the active theme."""

    revision: int
    theme: ThemeDefinition | None


class ThemeContract(RuntimeContract, ABC):
    """Runtime contract for deterministic active-theme ownership."""

    @abstractmethod
    def get(self) -> ThemeDefinition | None:
        """Return the active theme, or ``None`` when one is not installed."""

    @abstractmethod
    def snapshot(self) -> ThemeSnapshot:
        """Return an immutable snapshot of the active theme and revision."""

    @abstractmethod
    def set(self, theme: ThemeDefinition) -> ThemeSnapshot:
        """Validate and install a theme, returning the new snapshot."""

    @abstractmethod
    def clear(self) -> ThemeSnapshot:
        """Clear the active theme when present, returning the current snapshot."""


__all__ = ["ThemeContract", "ThemeDefinition", "ThemeSnapshot"]
