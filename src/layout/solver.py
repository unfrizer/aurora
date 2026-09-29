"""Private deterministic stack solver for the Layout Runtime."""

# pyright: reportUnusedClass=false

from __future__ import annotations

from src.layout.contracts import LayoutBox, LayoutDirection, LayoutNode, LayoutRect


class _LayoutSolver:
    """Arrange a validated node tree recursively in absolute root coordinates."""

    def solve(self, root: LayoutNode) -> LayoutBox:
        return self._arrange(root, x=0.0, y=0.0)

    def _arrange(self, node: LayoutNode, *, x: float, y: float) -> LayoutBox:
        children: list[LayoutBox] = []
        cursor_x = x
        cursor_y = y

        for child in node.children:
            children.append(self._arrange(child, x=cursor_x, y=cursor_y))
            if node.direction is LayoutDirection.VERTICAL:
                cursor_y += child.size.height + node.gap
            else:
                cursor_x += child.size.width + node.gap

        return LayoutBox(
            node_id=node.node_id,
            rect=LayoutRect(x=x, y=y, width=node.size.width, height=node.size.height),
            children=tuple(children),
        )


__all__ = []
