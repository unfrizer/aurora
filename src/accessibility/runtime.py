"""Deterministic implementation of the Wave 7 Accessibility Runtime."""

# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

from src.accessibility.contracts import (
    AccessibilityContract,
    AccessibilityIssue,
    AccessibilityNode,
    AccessibilityReport,
)
from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer


class AccessibilityRuntime(AccessibilityContract):
    """Validate and audit immutable semantic trees without platform resources."""

    @property
    def runtime_name(self) -> str:
        return "accessibility"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L6_ACCESSIBILITY

    async def initialize(self) -> None:
        return None

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    def health(self) -> HealthStatus:
        return HealthStatus.OK

    def validate(self, root: AccessibilityNode) -> None:
        self._validate_node(root, node_ids=set(), ancestors=set())

    def audit(self, root: AccessibilityNode) -> AccessibilityReport:
        self.validate(root)
        issues: list[AccessibilityIssue] = []
        self._audit_node(root, issues)
        return AccessibilityReport(issues=tuple(issues), is_accessible=not issues)

    def _validate_node(
        self,
        node: AccessibilityNode,
        *,
        node_ids: set[str],
        ancestors: set[int],
    ) -> None:
        if not isinstance(node, AccessibilityNode):
            raise ValidationError("Accessibility tree contains an invalid node")
        if not node.node_id.strip():
            raise ValidationError("Accessibility node ID must be non-empty")
        if not node.role.strip():
            raise ValidationError("Accessibility node role must be non-empty")
        if node.node_id in node_ids:
            raise ValidationError("Accessibility node IDs must be unique", node_id=node.node_id)
        if id(node) in ancestors:
            raise ValidationError("Accessibility tree must be acyclic", node_id=node.node_id)
        if not isinstance(node.is_interactive, bool):
            raise ValidationError("Accessibility node interactivity must be boolean")
        if node.label is not None and not isinstance(node.label, str):
            raise ValidationError("Accessibility node label must be a string or None")
        if not isinstance(node.children, tuple):
            raise ValidationError("Accessibility node children must be an immutable tuple")

        node_ids.add(node.node_id)
        next_ancestors = ancestors | {id(node)}
        for child in node.children:
            self._validate_node(child, node_ids=node_ids, ancestors=next_ancestors)

    def _audit_node(self, node: AccessibilityNode, issues: list[AccessibilityIssue]) -> None:
        if node.is_interactive and (node.label is None or not node.label.strip()):
            issues.append(
                AccessibilityIssue(
                    node_id=node.node_id,
                    message="Interactive node requires an accessible label",
                )
            )
        for child in node.children:
            self._audit_node(child, issues)


__all__ = ["AccessibilityRuntime"]
