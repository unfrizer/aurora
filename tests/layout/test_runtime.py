from __future__ import annotations

import asyncio
from typing import cast

import pytest

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.layout import LayoutDirection, LayoutNode, LayoutRuntime, LayoutSize


def _node(
    node_id: str,
    *,
    width: float = 10.0,
    height: float = 10.0,
    direction: LayoutDirection = LayoutDirection.VERTICAL,
    gap: float = 0.0,
    children: tuple[LayoutNode, ...] = (),
) -> LayoutNode:
    return LayoutNode(
        node_id=node_id,
        size=LayoutSize(width=width, height=height),
        direction=direction,
        gap=gap,
        children=children,
    )


async def test_identity_lifecycle_and_background_work() -> None:
    runtime = LayoutRuntime()
    tasks_before = asyncio.all_tasks()

    await runtime.initialize()
    await runtime.start()
    await runtime.stop()
    await runtime.shutdown()

    assert runtime.runtime_name == "layout"
    assert runtime.runtime_layer is RuntimeLayer.L2_LAYOUT
    assert asyncio.all_tasks() == tasks_before


@pytest.mark.parametrize(
    "root",
    [
        _node("", width=1.0, height=1.0),
        _node("size", width=-1.0, height=1.0),
        _node("nan", width=float("nan"), height=1.0),
        _node("gap", width=1.0, height=1.0, gap=-1.0),
        _node("infinite_gap", width=1.0, height=1.0, gap=float("inf")),
        _node("direction", direction=cast(LayoutDirection, "diagonal")),
        _node("children", children=cast(tuple[LayoutNode, ...], [])),
    ],
)
def test_invalid_node_fields_are_rejected(root: LayoutNode) -> None:
    with pytest.raises(ValidationError):
        LayoutRuntime().validate(root)


def test_duplicate_node_ids_are_rejected() -> None:
    root = _node("root", children=(_node("shared"), _node("shared")))

    with pytest.raises(ValidationError):
        LayoutRuntime().validate(root)


def test_cyclic_input_is_rejected() -> None:
    root = _node("root")
    object.__setattr__(root, "children", (root,))

    with pytest.raises(ValidationError):
        LayoutRuntime().validate(root)


def test_vertical_layout_uses_absolute_y_coordinates() -> None:
    root = _node(
        "root",
        width=100.0,
        height=100.0,
        gap=2.0,
        children=(
            _node("first", width=20.0, height=10.0),
            _node("second", width=30.0, height=15.0),
        ),
    )

    result = LayoutRuntime().layout(root)

    assert result.rect.x == 0.0
    assert result.rect.y == 0.0
    assert result.children[0].rect.x == 0.0
    assert result.children[0].rect.y == 0.0
    assert result.children[1].rect.x == 0.0
    assert result.children[1].rect.y == 12.0


def test_horizontal_layout_uses_absolute_x_coordinates() -> None:
    root = _node(
        "root",
        width=100.0,
        height=100.0,
        direction=LayoutDirection.HORIZONTAL,
        gap=3.0,
        children=(_node("first", width=20.0), _node("second", width=30.0)),
    )

    result = LayoutRuntime().layout(root)

    assert result.children[0].rect.x == 0.0
    assert result.children[0].rect.y == 0.0
    assert result.children[1].rect.x == 23.0
    assert result.children[1].rect.y == 0.0


def test_nested_layout_preserves_order_and_uses_each_parent_direction() -> None:
    nested = _node(
        "nested",
        width=20.0,
        height=20.0,
        direction=LayoutDirection.HORIZONTAL,
        gap=1.0,
        children=(_node("nested_one", width=3.0), _node("nested_two", width=4.0)),
    )
    root = _node("root", gap=5.0, children=(nested, _node("sibling", height=7.0)))

    result = LayoutRuntime().layout(root)
    nested_box, sibling_box = result.children

    assert tuple(box.node_id for box in result.children) == ("nested", "sibling")
    assert nested_box.rect.y == 0.0
    assert nested_box.children[1].rect.x == 4.0
    assert sibling_box.rect.y == 25.0


def test_overflow_is_permitted_and_input_remains_immutable_and_deterministic() -> None:
    child = _node("child", width=50.0, height=50.0)
    root = _node("root", width=10.0, height=10.0, children=(child,))
    runtime = LayoutRuntime()

    first = runtime.layout(root)
    second = runtime.layout(root)

    assert first == second
    assert first.children[0].rect.width > first.rect.width
    assert root.children == (child,)


def test_health_is_read_only() -> None:
    runtime = LayoutRuntime()
    root = _node("root")

    assert runtime.health() is HealthStatus.OK
    assert runtime.layout(root) == runtime.layout(root)


def test_deep_valid_tree_does_not_depend_on_python_recursion_limit() -> None:
    root = _node("leaf")
    for index in range(1500):
        root = _node(f"parent-{index}", children=(root,))
    runtime = LayoutRuntime()
    runtime.validate(root)
    box = runtime.layout(root)
    depth = 0
    while box.children:
        assert box.rect.x == box.rect.y == 0.0
        assert len(box.children) == 1
        box = box.children[0]
        depth += 1
    assert box.node_id == "leaf"
    assert depth == 1500
