from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError

import pytest

from src.kernel.contracts.runtime import RuntimeContract
from src.layout import (
    LayoutBox,
    LayoutContract,
    LayoutDirection,
    LayoutNode,
    LayoutRect,
    LayoutSize,
)


def test_layout_direction_has_exactly_the_canonical_members() -> None:
    assert tuple(LayoutDirection) == (LayoutDirection.HORIZONTAL, LayoutDirection.VERTICAL)


def test_layout_data_contracts_are_frozen_and_children_are_tuples() -> None:
    size = LayoutSize(width=10.0, height=5.0)
    node = LayoutNode(node_id="root", size=size)
    rect = LayoutRect(x=0.0, y=0.0, width=10.0, height=5.0)
    box = LayoutBox(node_id="root", rect=rect)

    assert node.children == ()
    assert box.children == ()
    with pytest.raises(FrozenInstanceError):
        size.width = 20.0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        rect.x = 1.0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        node.gap = 1.0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        box.node_id = "other"  # type: ignore[misc]


def test_layout_contract_is_abstract_and_extends_runtime_contract() -> None:
    assert inspect.isabstract(LayoutContract)
    assert issubclass(LayoutContract, RuntimeContract)


def test_layout_contract_exposes_exact_domain_methods() -> None:
    methods = {
        name
        for name, member in LayoutContract.__dict__.items()
        if inspect.isfunction(member) and not name.startswith("_")
    }

    assert methods == {"layout", "validate"}
