"""Private deterministic stack solver for the Layout Runtime."""

# pyright: reportUnusedClass=false

from __future__ import annotations

from src.layout.contracts import LayoutBox, LayoutDirection, LayoutNode, LayoutRect


class _LayoutSolver:
    """Arrange a validated node tree recursively in absolute root coordinates."""

    def solve(self, root: LayoutNode) -> LayoutBox:
        return self._arrange(root, x=0.0, y=0.0)

    def _arrange(self, node: LayoutNode, *, x: float, y: float) -> LayoutBox:
        boxes: dict[int, LayoutBox] = {}
        pending = [(node, x, y, False)]
        while pending:
            current, origin_x, origin_y, exiting = pending.pop()
            if exiting:
                boxes[id(current)] = LayoutBox(
                    node_id=current.node_id,
                    rect=LayoutRect(
                        x=origin_x,
                        y=origin_y,
                        width=current.size.width,
                        height=current.size.height,
                    ),
                    children=tuple(boxes[id(child)] for child in current.children),
                )
                continue
            pending.append((current, origin_x, origin_y, True))
            children: list[tuple[LayoutNode, float, float, bool]] = []
            cursor_x = origin_x
            cursor_y = origin_y
            for child in current.children:
                children.append((child, cursor_x, cursor_y, False))
                if current.direction is LayoutDirection.VERTICAL:
                    cursor_y += child.size.height + current.gap
                else:
                    cursor_x += child.size.width + current.gap
            pending.extend(reversed(children))
        return boxes[id(node)]


__all__ = []
