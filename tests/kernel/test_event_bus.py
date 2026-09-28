from __future__ import annotations

from uuid import uuid4

from src.core.types import EventPriority, PipelineId, RuntimeLayer, SessionId, TraceId
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.events import EventHandlerContract, RuntimeEvent
from src.kernel.runtime.bus import EventBusRuntime


class RecordingHandler(EventHandlerContract):
    def __init__(self, calls: list[EventPriority]) -> None:
        self.calls = calls

    async def handle(self, event: RuntimeEvent) -> None:
        self.calls.append(event.priority)


def _context() -> RuntimeContext:
    return RuntimeContext(
        session_id=SessionId(uuid4()),
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=TraceContext(trace_id=TraceId(uuid4())),
    )


async def test_event_bus_orders_event_batches_by_priority() -> None:
    bus = EventBusRuntime()
    calls: list[EventPriority] = []
    bus.subscribe("test.event", RecordingHandler(calls))
    context = _context()
    low = bus.create_for_runtime(
        event_type="test.event",
        payload={},
        context=context,
        priority=EventPriority.LOW,
    )
    critical = bus.create_for_runtime(
        event_type="test.event",
        payload={},
        context=context,
        priority=EventPriority.CRITICAL,
    )
    await bus.publish_many((low, critical))
    assert calls == [EventPriority.CRITICAL, EventPriority.LOW]
