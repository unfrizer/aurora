"""Behavior tests for the Accessibility Runtime."""

from __future__ import annotations

from typing import cast

import pytest

from src.accessibility import AccessibilityNode, AccessibilityRuntime
from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer


@pytest.mark.asyncio
async def test_identity_lifecycle_and_health_are_deterministic() -> None:
    runtime = AccessibilityRuntime()

    assert runtime.runtime_name == "accessibility"
    assert runtime.runtime_layer is RuntimeLayer.L6_ACCESSIBILITY
    assert runtime.health() is HealthStatus.OK
    await runtime.initialize()
    await runtime.start()
    await runtime.stop()
    await runtime.shutdown()


def test_audit_reports_unlabelled_interactive_nodes_in_preorder() -> None:
    root = AccessibilityNode(
        node_id="root",
        role="document",
        children=(
            AccessibilityNode(node_id="save", role="button", is_interactive=True),
            AccessibilityNode(
                node_id="section",
                role="group",
                children=(
                    AccessibilityNode(node_id="open", role="button", is_interactive=True),
                ),
            ),
        ),
    )

    report = AccessibilityRuntime().audit(root)

    assert report.is_accessible is False
    assert tuple(issue.node_id for issue in report.issues) == ("save", "open")


def test_audit_accepts_labelled_interactive_and_unlabelled_static_nodes() -> None:
    root = AccessibilityNode(
        node_id="root",
        role="document",
        children=(
            AccessibilityNode(node_id="save", role="button", label="Save", is_interactive=True),
            AccessibilityNode(node_id="ornament", role="image"),
        ),
    )

    report = AccessibilityRuntime().audit(root)

    assert report.is_accessible is True
    assert report.issues == ()


@pytest.mark.parametrize(
    "root",
    [
        AccessibilityNode(node_id=" ", role="document"),
        AccessibilityNode(node_id="root", role=" "),
        AccessibilityNode(node_id=cast(str, None), role="document"),
        AccessibilityNode(node_id="root", role=cast(str, 1)),
        AccessibilityNode(node_id="root", role="document", label=cast(str, 1)),
        AccessibilityNode(node_id="root", role="document", is_interactive=cast(bool, "yes")),
        AccessibilityNode(
            node_id="root", role="document", children=cast(tuple[AccessibilityNode, ...], [])
        ),
        AccessibilityNode(
            node_id="root", role="document", children=(cast(AccessibilityNode, None),)
        ),
        AccessibilityNode(
            node_id="root",
            role="document",
            children=(AccessibilityNode(node_id="root", role="group"),),
        ),
    ],
)
def test_invalid_trees_are_rejected(root: AccessibilityNode) -> None:
    with pytest.raises(ValidationError):
        AccessibilityRuntime().audit(root)


def test_deep_tree_audit_preserves_preorder_without_recursion_limit() -> None:
    root = AccessibilityNode(node_id="leaf", role="button", is_interactive=True)
    for index in range(2000):
        root = AccessibilityNode(
            node_id=f"group-{index}", role="group", is_interactive=True, children=(root,)
        )

    report = AccessibilityRuntime().audit(root)

    assert len(report.issues) == 2001
    assert report.issues[0].node_id == "group-1999"
    assert report.issues[-1].node_id == "leaf"
    assert report.is_accessible is False


def test_cycle_is_rejected_without_recursion_error() -> None:
    root = AccessibilityNode(node_id="root", role="group")
    object.__setattr__(root, "children", (root,))

    with pytest.raises(ValidationError, match="acyclic"):
        AccessibilityRuntime().audit(root)
