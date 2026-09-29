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
        RenderNode(node_id="root", kind="x", children=(RenderNode(node_id="root", kind="x"),)),
    ],
)
def test_invalid_tree_rejected(root: RenderNode) -> None:
    with pytest.raises(ValidationError):
        RenderRuntime().render(root)
