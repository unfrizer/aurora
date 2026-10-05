"""L2 deterministic Layout Runtime implementation."""

# pyright: reportUnnecessaryIsInstance=false

# pyright: reportPrivateUsage=false

from __future__ import annotations

import math

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.layout.contracts import LayoutBox, LayoutContract, LayoutDirection, LayoutNode, LayoutSize
from src.layout.solver import _LayoutSolver


class LayoutRuntime(LayoutContract):
    """Own deterministic validation and arrangement of immutable layout input."""

    @property
    def runtime_name(self) -> str:
        return "layout"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L2_LAYOUT

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

    def validate(self, root: LayoutNode) -> None:
        node_ids: set[str] = set()
        ancestors: set[int] = set()
        pending = [(root, False)]
        while pending:
            node, exiting = pending.pop()
            if exiting:
                ancestors.remove(id(node))
                continue
            self._validate_node(node, node_ids=node_ids, ancestors=ancestors)
            node_ids.add(node.node_id)
            ancestors.add(id(node))
            pending.append((node, True))
            pending.extend((child, False) for child in reversed(node.children))

    def layout(self, root: LayoutNode) -> LayoutBox:
        self.validate(root)
        return _LayoutSolver().solve(root)

    def _validate_node(
        self,
        node: LayoutNode,
        *,
        node_ids: set[str],
        ancestors: set[int],
    ) -> None:
        if not isinstance(node, LayoutNode):
            raise ValidationError("Layout tree contains an invalid node")
        if not isinstance(node.node_id, str) or not node.node_id.strip():
            raise ValidationError("Layout node ID must be non-empty")
        if node.node_id in node_ids:
            raise ValidationError("Layout node IDs must be unique", node_id=node.node_id)
        if id(node) in ancestors:
            raise ValidationError("Layout tree must be acyclic", node_id=node.node_id)
        if not isinstance(node.size, LayoutSize):
            raise ValidationError("Layout node size must be a LayoutSize", node_id=node.node_id)
        self._validate_dimension(node.size.width, field="width", node_id=node.node_id)
        self._validate_dimension(node.size.height, field="height", node_id=node.node_id)
        self._validate_dimension(node.gap, field="gap", node_id=node.node_id)
        if not isinstance(node.direction, LayoutDirection):
            raise ValidationError("Layout direction is invalid", node_id=node.node_id)
        if not isinstance(node.children, tuple):
            raise ValidationError(
                "Layout children must be an immutable tuple", node_id=node.node_id
            )

    @staticmethod
    def _validate_dimension(value: object, *, field: str, node_id: str) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(value, int | float)
            or not math.isfinite(value)
        ):
            raise ValidationError("Layout dimension must be finite", field=field, node_id=node_id)
        if value < 0.0:
            raise ValidationError(
                "Layout dimension must be non-negative", field=field, node_id=node_id
            )


__all__ = ["LayoutRuntime"]
