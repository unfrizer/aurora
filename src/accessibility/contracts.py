"""Immutable public contracts for the Wave 7 Accessibility Runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.kernel.contracts.runtime import RuntimeContract


@dataclass(slots=True, frozen=True, kw_only=True)
class AccessibilityNode:
    """An immutable platform-neutral semantic node for accessibility auditing."""

    node_id: str
    role: str
    label: str | None = None
    is_interactive: bool = False
    children: tuple[AccessibilityNode, ...] = ()


@dataclass(slots=True, frozen=True, kw_only=True)
class AccessibilityIssue:
    """One deterministic accessibility finding for an audited node."""

    node_id: str
    message: str


@dataclass(slots=True, frozen=True, kw_only=True)
class AccessibilityReport:
    """An immutable result of auditing a complete accessibility tree."""

    issues: tuple[AccessibilityIssue, ...]
    is_accessible: bool


class AccessibilityContract(RuntimeContract, ABC):
    """Runtime contract for validation and deterministic semantic auditing."""

    @abstractmethod
    def validate(self, root: AccessibilityNode) -> None:
        """Validate a complete immutable accessibility tree."""

    @abstractmethod
    def audit(self, root: AccessibilityNode) -> AccessibilityReport:
        """Validate and audit a complete immutable accessibility tree."""


__all__ = [
    "AccessibilityContract",
    "AccessibilityIssue",
    "AccessibilityNode",
    "AccessibilityReport",
]
