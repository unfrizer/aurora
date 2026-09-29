"""Contract tests for the Accessibility Runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from src.accessibility.contracts import (
    AccessibilityContract,
    AccessibilityIssue,
    AccessibilityNode,
    AccessibilityReport,
)
from src.kernel.contracts.runtime import RuntimeContract


def test_accessibility_models_are_frozen_dataclasses() -> None:
    node = AccessibilityNode(node_id="button", role="button", is_interactive=True)
    issue = AccessibilityIssue(node_id="button", message="Missing label")
    report = AccessibilityReport(issues=(issue,), is_accessible=False)

    assert all(is_dataclass(model) for model in (node, issue, report))
    with pytest.raises(FrozenInstanceError):
        node.role = "link"  # type: ignore[misc]


def test_accessibility_contract_is_abstract_runtime_contract() -> None:
    assert issubclass(AccessibilityContract, RuntimeContract)
    assert AccessibilityContract.__abstractmethods__ == {
        "audit",
        "health",
        "initialize",
        "runtime_layer",
        "runtime_name",
        "shutdown",
        "start",
        "stop",
        "validate",
    }
