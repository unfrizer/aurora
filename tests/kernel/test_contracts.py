from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.core.types import (
    EventId,
    EventPriority,
    ModuleId,
    PipelineId,
    RuntimeLayer,
    RuntimeStatus,
    SessionId,
    TraceId,
)
from src.kernel.contracts import RuntimeContract
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.events import RuntimeEvent
from src.kernel.contracts.lifecycle import LifecycleState
from src.kernel.contracts.module import RuntimeModuleManifest


def _trace() -> TraceContext:
    return TraceContext(trace_id=TraceId(uuid4()))


def test_contracts_are_immutable_and_complete() -> None:
    assert inspect.isabstract(RuntimeContract)
    manifest = RuntimeModuleManifest(
        module_id=ModuleId("kernel"),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        depends_on=(),
        provides=("runtime",),
        version="1.0",
    )
    assert manifest.provides == ("runtime",)
    state = LifecycleState(
        current=RuntimeStatus.CREATED,
        previous=None,
        entered_at=datetime.now(UTC),
        transition_count=0,
    )
    assert not state.is_terminal


def test_runtime_context_and_event_are_frozen() -> None:
    context = RuntimeContext(
        session_id=SessionId(uuid4()),
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=_trace(),
    )
    with pytest.raises(FrozenInstanceError):
        context.metadata = {}  # type: ignore[misc]
    event = RuntimeEvent(
        event_id=EventId(uuid4()),
        event_type="test.event",
        session_id=context.session_id,
        trace=context.trace,
        priority=EventPriority.HIGH,
    )
    assert event.priority is EventPriority.HIGH
