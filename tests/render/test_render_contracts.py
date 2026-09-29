from dataclasses import FrozenInstanceError

import pytest

from src.kernel.contracts.runtime import RuntimeContract
from src.render import RenderContract, RenderNode, RenderTree


def test_contract_and_models() -> None:
    node = RenderNode(node_id="root", kind="document")
    assert issubclass(RenderContract, RuntimeContract) and RenderTree(root=node).root == node
    with pytest.raises(FrozenInstanceError):
        node.kind = "other"  # type: ignore[misc]
