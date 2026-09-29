"""Integration test for the Wave 7 Accessibility Runtime."""

from __future__ import annotations

import pytest

from src.accessibility import AccessibilityContract, AccessibilityNode, AccessibilityRuntime


@pytest.mark.asyncio
async def test_accessibility_runtime_supports_a_complete_in_memory_lifecycle() -> None:
    runtime: AccessibilityContract = AccessibilityRuntime()
    root = AccessibilityNode(
        node_id="root",
        role="document",
        children=(
            AccessibilityNode(node_id="save", role="button", label="Save", is_interactive=True),
        ),
    )

    await runtime.initialize()
    await runtime.start()
    report = runtime.audit(root)

    assert report.is_accessible is True

    await runtime.stop()
    await runtime.shutdown()
