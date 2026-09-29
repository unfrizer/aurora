"""Immutable public contracts for the Wave 9 Render Runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.kernel.contracts.runtime import RuntimeContract


@dataclass(slots=True, frozen=True, kw_only=True)
class RenderNode:
    node_id: str
    kind: str
    text: str | None = None
    children: tuple[RenderNode, ...] = ()


@dataclass(slots=True, frozen=True, kw_only=True)
class RenderTree:
    root: RenderNode


class RenderContract(RuntimeContract, ABC):
    @abstractmethod
    def validate(self, root: RenderNode) -> None: ...
    @abstractmethod
    def render(self, root: RenderNode) -> RenderTree: ...


__all__ = ["RenderContract", "RenderNode", "RenderTree"]
