"""Read-only deterministic implementation of the Wave 9 Render Runtime."""

# pyright: reportUnnecessaryIsInstance=false
from __future__ import annotations

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.render.contracts import RenderContract, RenderNode, RenderTree


class RenderRuntime(RenderContract):
    @property
    def runtime_name(self) -> str:
        return "render"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L8_RENDER

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

    def validate(self, root: RenderNode) -> None:
        ids: set[str] = set()
        ancestors: set[int] = set()
        pending = [(root, False)]
        while pending:
            node, exiting = pending.pop()
            if exiting:
                ancestors.remove(id(node))
                continue
            self._validate(node, ids=ids, ancestors=ancestors)
            ids.add(node.node_id)
            ancestors.add(id(node))
            pending.append((node, True))
            pending.extend((child, False) for child in reversed(node.children))

    def render(self, root: RenderNode) -> RenderTree:
        self.validate(root)
        return RenderTree(root=root)

    def _validate(self, node: RenderNode, *, ids: set[str], ancestors: set[int]) -> None:
        if not isinstance(node, RenderNode):
            raise ValidationError("Render tree contains an invalid node")
        for value in (node.node_id, node.kind):
            if not isinstance(value, str) or not value.strip():
                raise ValidationError("Render node ID and kind must be non-empty strings")
        if id(node) in ancestors:
            raise ValidationError("Render tree must be acyclic", node_id=node.node_id)
        if node.node_id in ids:
            raise ValidationError("Render node IDs must be unique", node_id=node.node_id)
        if node.text is not None and not isinstance(node.text, str):
            raise ValidationError("Render node text must be a string or None")
        if not isinstance(node.children, tuple):
            raise ValidationError("Render node children must be an immutable tuple")


__all__ = ["RenderRuntime"]
