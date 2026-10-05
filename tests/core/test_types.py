from __future__ import annotations

from src.core.types import DIScope, EventPriority, RuntimeLayer, RuntimeStatus


def test_canonical_runtime_vocabulary() -> None:
    assert tuple(RuntimeLayer) == (
        RuntimeLayer.L0_KERNEL,
        RuntimeLayer.L1_STATE,
        RuntimeLayer.L2_LAYOUT,
        RuntimeLayer.L3_THEME,
        RuntimeLayer.L4_MOTION,
        RuntimeLayer.L5_INTERACTION,
        RuntimeLayer.L6_ACCESSIBILITY,
        RuntimeLayer.L7_PLATFORM,
        RuntimeLayer.L8_RENDER,
    )
    assert len(DIScope) == 4
    assert len(RuntimeStatus) == 10
    assert tuple(status.value for status in RuntimeStatus) == (
        "CREATED",
        "INITIALIZING",
        "READY",
        "STARTING",
        "RUNNING",
        "STOPPING",
        "STOPPED",
        "SHUTTING_DOWN",
        "TERMINATED",
        "FAILED",
    )


def test_event_priority_is_descending_numeric_vocabulary() -> None:
    assert EventPriority.CRITICAL > EventPriority.HIGH > EventPriority.NORMAL
    assert EventPriority.NORMAL > EventPriority.LOW > EventPriority.BACKGROUND
