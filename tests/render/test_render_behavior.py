from typing import cast

import pytest

from src.core.exceptions import ValidationError
from src.core.types import RuntimeLayer
from src.render import RenderNode, RenderRuntime


def test_render_is_read_only_and_recursive() -> None:
    root = RenderNode(
        node_id="root",
        kind="document",
        children=(RenderNode(node_id="text", kind="text", text="Hi"),),
    )
    runtime = RenderRuntime()
    assert runtime.runtime_layer is RuntimeLayer.L8_RENDER
    assert runtime.render(root).root is root


@pytest.mark.parametrize(
    "root",
    [
        RenderNode(node_id=" ", kind="x"),
        RenderNode(node_id="root", kind=" "),
        RenderNode(node_id=cast(str, None), kind="document"),
        RenderNode(node_id="root", kind=cast(str, 1)),
        RenderNode(node_id="root", kind="document", text=cast(str, 1)),
        RenderNode(node_id="root", kind="document", children=cast(tuple[RenderNode, ...], [])),
        RenderNode(node_id="root", kind="document", children=(cast(RenderNode, None),)),
        RenderNode(node_id="root", kind="x", children=(RenderNode(node_id="root", kind="x"),)),
    ],
)
def test_invalid_tree_rejected(root: RenderNode) -> None:
    with pytest.raises(ValidationError):
        RenderRuntime().render(root)


def test_deep_tree_preserves_input_identity_without_recursion_limit() -> None:
    root = RenderNode(node_id="leaf", kind="text", text="Hello")
    for index in range(2000):
        root = RenderNode(node_id=f"group-{index}", kind="group", children=(root,))

    assert RenderRuntime().render(root).root is root


def test_cycle_is_rejected_without_recursion_error() -> None:
    root = RenderNode(node_id="root", kind="group")
    object.__setattr__(root, "children", (root,))

    with pytest.raises(ValidationError, match="acyclic"):
        RenderRuntime().render(root)
