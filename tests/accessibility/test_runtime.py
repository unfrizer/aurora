"""Behavior tests for the Accessibility Runtime."""

from __future__ import annotations

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
