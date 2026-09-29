"""Immutable public contracts for the Wave 3 Layout Runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from src.kernel.contracts.runtime import RuntimeContract


class LayoutDirection(StrEnum):
    """Supported direct-child arrangement directions."""

    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"


@dataclass(slots=True, frozen=True, kw_only=True)
class LayoutSize:
    """Explicit width and height for a layout node."""

    width: float
    height: float


@dataclass(slots=True, frozen=True, kw_only=True)
class LayoutRect:
    """An absolute geometry rectangle without pixel rounding."""

    x: float
    y: float
    width: float
    height: float


@dataclass(slots=True, frozen=True, kw_only=True)
class LayoutNode:
    """An immutable input node for deterministic geometric arrangement."""

    node_id: str
    size: LayoutSize
    direction: LayoutDirection = LayoutDirection.VERTICAL
    gap: float = 0.0
    children: tuple[LayoutNode, ...] = ()


@dataclass(slots=True, frozen=True, kw_only=True)
class LayoutBox:
    """An immutable recursive result of arranging a LayoutNode tree."""

    node_id: str
    rect: LayoutRect
    children: tuple[LayoutBox, ...] = ()


class LayoutContract(RuntimeContract, ABC):
    """Runtime contract for validation and deterministic layout arrangement."""

    @abstractmethod
    def validate(self, root: LayoutNode) -> None:
        """Validate a complete immutable layout tree."""

    @abstractmethod
    def layout(self, root: LayoutNode) -> LayoutBox:
        """Validate and arrange a complete immutable layout tree."""


__all__ = [
    "LayoutBox",
    "LayoutContract",
    "LayoutDirection",
    "LayoutNode",
    "LayoutRect",
    "LayoutSize",
]
