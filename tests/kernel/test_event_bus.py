"""KR-007 canonical acceptance under AB-00C/D and ADR-004/005."""

from __future__ import annotations

import asyncio
import gc
from collections.abc import Awaitable, Callable
from dataclasses import fields, replace
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4
from weakref import ref

import pytest

from src.core.exceptions import EventHandlerError, EventValidationError
from src.core.types import (
    EventId,
    EventPriority,
    HealthStatus,
    JSONValue,
    Payload,
    PipelineId,
    RuntimeLayer,
    SessionId,
    TraceId,
)
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.events import EventHandlerContract, RuntimeEvent
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime import bus as bus_module
from src.kernel.runtime import dispatcher as dispatcher_module
from src.kernel.runtime import publisher as publisher_module
from src.kernel.runtime import subscriber as subscriber_module
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.dispatcher import DispatcherRuntime
from src.kernel.runtime.publisher import PublisherRuntime
from src.kernel.runtime.subscriber import SubscriberRuntime


class RecordingHandler(EventHandlerContract):
    def __init__(self, callback: Callable[[RuntimeEvent], Awaitable[None]] | None = None) -> None:
        self.events: list[RuntimeEvent] = []
        self.callback = callback

    async def handle(self, event: RuntimeEvent) -> None:
        self.events.append(event)
        if self.callback is not None:
            await self.callback(event)


class EqualHandler(RecordingHandler):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, EqualHandler)


class InvalidOffset(tzinfo):
    def utcoffset(self, dt: datetime | None) -> timedelta:
        return timedelta(hours=25)


def _context() -> RuntimeContext:
    return RuntimeContext(
        session_id=SessionId(uuid4()),
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=TraceContext(
            trace_id=TraceId(uuid4()),
            parent_trace_id=TraceId(uuid4()),
            correlation_id=uuid4(),
        ),
    )


def _publisher() -> PublisherRuntime:
    return PublisherRuntime(DispatcherRuntime(SubscriberRuntime()))


def _event(
    bus: EventBusRuntime | None = None,
    *,
    payload: Payload | None = None,
    event_type: str = "test.event",
    priority: EventPriority = EventPriority.NORMAL,
) -> RuntimeEvent:
    return (bus or EventBusRuntime()).create_for_runtime(
        event_type=event_type,
        payload={} if payload is None else payload,
        context=_context(),
        priority=priority,
    )


def _nested(levels: int, kind: str) -> Payload:
    value: JSONValue = "leaf"
    for index in range(levels - 1):
        value = {"child": value} if kind == "dict" or (kind == "mixed" and index % 2) else [value]
    return {"root": value}


def _leaf(payload: Payload) -> JSONValue:
    value: JSONValue = payload["root"]
    while isinstance(value, dict | list):
        value = value["child"] if isinstance(value, dict) else value[0]
    return value


async def test_event_bus_orders_event_batches_by_priority() -> None:
    bus = EventBusRuntime()
    handler = RecordingHandler()
    bus.subscribe("test.event", handler)
    events = tuple(_event(bus, priority=priority) for priority in EventPriority)
    await bus.publish_many(events)
    assert [event.priority for event in handler.events] == [
        EventPriority.CRITICAL,
        EventPriority.HIGH,
        EventPriority.NORMAL,
        EventPriority.LOW,
        EventPriority.BACKGROUND,
    ]


async def test_fifo_and_handler_insertion_order_with_sequential_awaits() -> None:
    bus = EventBusRuntime()
    calls: list[tuple[str, EventId]] = []

    async def first(event: RuntimeEvent) -> None:
        calls.append(("first-start", event.event_id))
        await asyncio.sleep(0)
        calls.append(("first-end", event.event_id))

    async def second(event: RuntimeEvent) -> None:
        calls.append(("second", event.event_id))

    bus.subscribe("test.event", RecordingHandler(first))
    bus.subscribe("test.event", RecordingHandler(second))
    events = tuple(_event(bus) for _ in range(3))
    await bus.publish_many(events)
    assert calls == [
        (name, event.event_id)
        for event in events
        for name in ("first-start", "first-end", "second")
    ]


def test_exact_exports_schema_and_no_obsolete_surface() -> None:
    expected = (
        (bus_module, EventBusRuntime),
        (publisher_module, PublisherRuntime),
        (dispatcher_module, DispatcherRuntime),
        (subscriber_module, SubscriberRuntime),
    )
    for module, runtime in expected:
        assert module.__all__ == [runtime.__name__]
    assert not hasattr(DispatcherRuntime, "dispatch_sync")
    assert not hasattr(DispatcherRuntime, "dispatch_async")
    assert not hasattr(SubscriberRuntime, "handlers_for")
    assert [field.name for field in fields(RuntimeEvent)] == [
        "event_id",
        "event_type",
        "session_id",
        "trace",
        "priority",
        "timestamp",
        "payload",
    ]
    assert not (Path(bus_module.__file__).parent / "event.py").exists()


def test_create_identity_defaults_and_observational_validate() -> None:
    publisher = _publisher()
    context = _context()
    payload: Payload = {"value": [1, True, None, "RU/EN \u0410", 1.5]}
    event = publisher.create(event_type="test.event", payload=payload, context=context)
    other = publisher.create(event_type="test.event", payload={}, context=context)
    assert isinstance(event.event_id, UUID) and event.event_id != other.event_id
    assert event.timestamp.tzinfo is UTC
    assert event.priority is EventPriority.NORMAL
    assert event.session_id == context.session_id
    assert event.trace is context.trace
    captured = event.payload
    assert publisher.validate(event) is None
    assert event.payload is captured and payload == captured and payload is not captured


def test_create_detaches_repeated_acyclic_references_without_coercion() -> None:
    publisher = _publisher()
    shared: list[JSONValue] = [{"value": "original"}]
    payload: Payload = {"left": shared, "right": shared, "big": 2**1024, "zero": -0.0}
    event = publisher.create(event_type="test.event", payload=payload, context=_context())
    shared.append("caller change")
    assert event.payload["left"] == [{"value": "original"}]
    assert event.payload["left"] is not event.payload["right"]
    left = cast(list[JSONValue], event.payload["left"])
    left.append("local change")
    assert event.payload["right"] == [{"value": "original"}]
    assert event.payload["big"] == 2**1024 and event.payload["zero"] == -0.0


async def test_caller_and_sibling_payloads_are_detached() -> None:
    bus = EventBusRuntime()

    async def mutate(event: RuntimeEvent) -> None:
        cast(list[JSONValue], event.payload["nested"]).append("handler")
        event.payload["extra"] = True

    first, second = RecordingHandler(mutate), RecordingHandler()
    bus.subscribe("test.event", first)
    bus.subscribe("test.event", second)
    caller: Payload = {"nested": [{"text": "captured"}]}
    event = _event(bus, payload=caller)
    cast(list[JSONValue], caller["nested"]).append("caller")
    await bus.publish(event)
    assert event.payload == {"nested": [{"text": "captured"}]}
    assert second.events[0].payload == event.payload
    assert first.events[0].payload != event.payload
    assert first.events[0] is not second.events[0] and second.events[0] is not event
    for delivered in first.events + second.events:
        assert replace(delivered, payload=event.payload) == event
        assert delivered.trace is event.trace


async def test_entire_batch_captured_before_handler_can_mutate_later_input() -> None:
    bus = EventBusRuntime()
    first = _event(bus, payload={"number": 1})
    later = _event(bus, payload={"number": 2})

    async def mutate_later(event: RuntimeEvent) -> None:
        if event.event_id == first.event_id:
            later.payload.clear()
            later.payload["cycle"] = later.payload
            first.payload["number"] = 99

    handler = RecordingHandler(mutate_later)
    bus.subscribe("test.event", handler)
    await bus.publish_many((first, later))
    assert [event.payload for event in handler.events] == [{"number": 1}, {"number": 2}]


async def test_captured_payload_survives_caller_mutation_during_await() -> None:
    bus = EventBusRuntime()
    entered, resume = asyncio.Event(), asyncio.Event()

    async def wait(_: RuntimeEvent) -> None:
        entered.set()
        await resume.wait()

    first, second = RecordingHandler(wait), RecordingHandler()
    bus.subscribe("test.event", first)
    bus.subscribe("test.event", second)
    event = _event(bus, payload={"nested": [1]})
    task = asyncio.create_task(bus.publish(event))
    await asyncio.wait_for(entered.wait(), timeout=5)
    cast(list[JSONValue], event.payload["nested"]).append(2)
    resume.set()
    await task
    assert second.events[0].payload == {"nested": [1]}


@pytest.mark.parametrize("kind", ["dict", "list", "mixed"])
@pytest.mark.parametrize("levels", [1, 2, 128, 255, 256])
async def test_valid_depth_boundaries_reach_handlers(kind: str, levels: int) -> None:
    bus = EventBusRuntime()
    handler = RecordingHandler()
    bus.subscribe("test.event", handler)
    event = _event(bus, payload=_nested(levels, kind))
    await bus.publish(event)
    assert _leaf(handler.events[0].payload) == "leaf"


@pytest.mark.parametrize("kind", ["dict", "list", "mixed"])
@pytest.mark.parametrize("levels", [257, 258, 1100])
def test_excessive_depth_is_validation_error_not_recursion_error(kind: str, levels: int) -> None:
    with pytest.raises(EventValidationError, match="256"):
        _event(payload=_nested(levels, kind))


@pytest.mark.parametrize(
    "invalid",
    [
        {1: "value"},
        {"bad": float("nan")},
        {"bad": float("inf")},
        {"bad": float("-inf")},
        {"bad": object()},
        {"bad": uuid4()},
        {"bad": datetime.now(UTC)},
        {"bad": Path("private")},
        {"bad": (1, 2)},
        {"bad": {1, 2}},
        {"bad": b"data"},
        {"bad": bytearray(b"data")},
        {"bad": "\ud800"},
        {"\udfff": "value"},
        {"bad": ["\ud800"]},
        {"bad": {"child": {"bad": b"data"}}},
    ],
    ids=[
        "non-string-key",
        "nan",
        "positive-inf",
        "negative-inf",
        "object",
        "uuid",
        "datetime",
        "path",
        "tuple",
        "set",
        "bytes",
        "bytearray",
        "surrogate-value",
        "surrogate-key",
        "surrogate-list",
        "nested-invalid",
    ],
)
async def test_invalid_json_rejected_at_create_validate_and_publish(invalid: object) -> None:
    publisher = _publisher()
    with pytest.raises(EventValidationError):
        publisher.create(
            event_type="test.event", payload=cast(Payload, invalid), context=_context()
        )
    bus = EventBusRuntime()
    handler = RecordingHandler()
    bus.subscribe("test.event", handler)
    event = replace(_event(bus), payload=cast(Payload, invalid))
    with pytest.raises(EventValidationError):
        publisher.validate(event)
    with pytest.raises(EventValidationError):
        await bus.publish(event)
    assert handler.events == []


@pytest.mark.parametrize(
    "invalid", [None, [], 0, "payload", ()], ids=["none", "list", "int", "str", "tuple"]
)
async def test_payload_root_must_be_dictionary(invalid: object) -> None:
    publisher = _publisher()
    with pytest.raises(EventValidationError, match="JSON object"):
        publisher.create(
            event_type="test.event", payload=cast(Payload, invalid), context=_context()
        )
    with pytest.raises(EventValidationError, match="JSON object"):
        await publisher.publish(replace(_event(), payload=cast(Payload, invalid)))


@pytest.mark.parametrize("kind", ["dict", "list", "indirect"])
async def test_cycles_rejected_without_mutation_or_payload_disclosure(kind: str) -> None:
    payload: Payload = {"private-key": "secret-value"}
    if kind == "dict":
        payload["cycle"] = payload
    else:
        loop: list[JSONValue] = []
        payload["cycle"] = loop
        loop.append(loop if kind == "list" else payload)
    original_keys = tuple(payload)
    publisher = _publisher()
    with pytest.raises(EventValidationError, match="cycles") as raised:
        publisher.create(event_type="test.event", payload=payload, context=_context())
    assert "secret-value" not in str(raised.value) and "private-key" not in str(raised.value)
    assert tuple(payload) == original_keys
    with pytest.raises(EventValidationError, match="cycles"):
        await publisher.publish(replace(_event(), payload=payload))


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("event_type", ""),
        ("event_type", None),
        ("event_type", 1),
        ("event_type", "\ud800"),
        ("event_id", None),
        ("event_id", "uuid"),
        ("session_id", None),
        ("session_id", "uuid"),
        ("trace", None),
        ("trace", {}),
        ("trace", replace(_context().trace, trace_id=cast(TraceId, None))),
        ("trace", replace(_context().trace, parent_trace_id=cast(TraceId, "uuid"))),
        ("trace", replace(_context().trace, correlation_id=cast(UUID, "uuid"))),
        ("priority", 50),
        ("priority", None),
        ("priority", True),
        ("timestamp", None),
        ("timestamp", "date"),
        ("timestamp", datetime(2026, 1, 1)),
        ("timestamp", datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1)))),
        ("timestamp", datetime(2026, 1, 1, tzinfo=InvalidOffset())),
    ],
    ids=[
        "empty-type",
        "none-type",
        "int-type",
        "invalid-unicode-type",
        "none-id",
        "str-id",
        "none-session",
        "str-session",
        "none-trace",
        "dict-trace",
        "none-trace-id",
        "str-parent-id",
        "str-correlation-id",
        "int-priority",
        "none-priority",
        "bool-priority",
        "none-time",
        "str-time",
        "naive-time",
        "non-utc-time",
        "invalid-offset-time",
    ],
)
async def test_invalid_event_fields_use_canonical_validation_error(
    field: str, invalid: object
) -> None:
    event = replace(_event(), **{field: invalid})
    publisher = _publisher()
    with pytest.raises(EventValidationError):
        publisher.validate(event)
    with pytest.raises(EventValidationError):
        await publisher.publish(event)


@pytest.mark.parametrize("invalid", [None, {}, "event", 1])
async def test_non_event_rejected_with_canonical_error(invalid: object) -> None:
    publisher = _publisher()
    with pytest.raises(EventValidationError):
        publisher.validate(cast(RuntimeEvent, invalid))
    with pytest.raises(EventValidationError):
        await publisher.publish(cast(RuntimeEvent, invalid))


@pytest.mark.parametrize("invalid", [None, {}, "context"])
def test_non_context_rejected_with_canonical_error(invalid: object) -> None:
    with pytest.raises(EventValidationError):
        _publisher().create(
            event_type="test.event", payload={}, context=cast(RuntimeContext, invalid)
        )


def test_optional_trace_identifiers_can_be_none_and_event_type_remains_exact() -> None:
    context = replace(_context(), trace=TraceContext(trace_id=TraceId(uuid4())))
    event = _publisher().create(event_type="Mixed case \u0410", payload={}, context=context)
    assert event.trace.parent_trace_id is None and event.trace.correlation_id is None
    assert event.event_type == "Mixed case \u0410"


async def test_invalid_later_batch_event_prevents_all_handler_effects() -> None:
    bus = EventBusRuntime()
    handler = RecordingHandler()
    bus.subscribe("test.event", handler)
    valid = _event(bus, priority=EventPriority.CRITICAL)
    invalid = replace(_event(bus), payload=cast(Payload, {"bad": object()}))
    with pytest.raises(EventValidationError):
        await bus.publish_many((valid, invalid))
    assert handler.events == []


def test_registry_duplicate_and_missing_removal_are_atomic() -> None:
    registry = SubscriberRuntime()
    first, second = RecordingHandler(), RecordingHandler()
    registry.subscribe("test.event", first)
    captured = registry.handlers("test.event")
    with pytest.raises(EventHandlerError, match="already registered"):
        registry.subscribe("test.event", first)
    with pytest.raises(EventHandlerError, match="not registered"):
        registry.unsubscribe("test.event", second)
    with pytest.raises(EventHandlerError, match="not registered"):
        registry.unsubscribe("absent", second)
    assert registry.handlers("test.event") == captured
    registry.subscribe("test.event", second)
    assert captured == (first,)
    assert registry.handlers("test.event") == (first, second)
    registry.unsubscribe("test.event", first)
    assert registry.contains("test.event")
    registry.unsubscribe("test.event", second)
    assert not registry.contains("test.event") and registry.handlers("test.event") == ()
    registry.clear()
    assert registry.handlers("test.event") == ()


def test_equal_handler_membership_semantics_are_preserved() -> None:
    registry = SubscriberRuntime()
    first, second = EqualHandler(), EqualHandler()
    registry.subscribe("test.event", first)
    with pytest.raises(EventHandlerError):
        registry.subscribe("test.event", second)
    assert registry.handlers("test.event")[0] is first
    registry.unsubscribe("test.event", second)
    assert not registry.contains("test.event")


async def test_registry_mutations_affect_next_event_not_captured_handlers() -> None:
    bus = EventBusRuntime()
    calls: list[str] = []
    second, later = RecordingHandler(), RecordingHandler()

    async def change(_: RuntimeEvent) -> None:
        calls.append("first")
        bus.unsubscribe("test.event", second)
        bus.subscribe("test.event", later)
        bus.unsubscribe("test.event", first)

    first = RecordingHandler(change)
    bus.subscribe("test.event", first)
    bus.subscribe("test.event", second)
    await bus.publish_many((_event(bus), _event(bus)))
    assert calls == ["first"] and len(second.events) == 1 and len(later.events) == 1
    assert bus.handlers("test.event") == (later,)


async def test_clear_during_dispatch_does_not_skip_captured_handlers() -> None:
    bus = EventBusRuntime()

    async def clear(_: RuntimeEvent) -> None:
        bus.clear()

    first, second = RecordingHandler(clear), RecordingHandler()
    bus.subscribe("test.event", first)
    bus.subscribe("test.event", second)
    await bus.publish_many((_event(bus), _event(bus)))
    assert len(first.events) == len(second.events) == 1 and not bus.contains("test.event")


async def test_nested_publication_uses_updated_registry_and_runs_inline() -> None:
    bus = EventBusRuntime()
    calls: list[str] = []

    async def nested(_: RuntimeEvent) -> None:
        calls.append("nested")

    nested_handler = RecordingHandler(nested)

    async def outer(_: RuntimeEvent) -> None:
        calls.append("outer-start")
        bus.subscribe("nested.event", nested_handler)
        await bus.publish(_event(bus, event_type="nested.event"))
        calls.append("outer-end")

    async def second(_: RuntimeEvent) -> None:
        calls.append("second")

    bus.subscribe("test.event", RecordingHandler(outer))
    bus.subscribe("test.event", RecordingHandler(second))
    await bus.publish(_event(bus))
    assert calls == ["outer-start", "nested", "outer-end", "second"]


@pytest.mark.parametrize(
    "error", [ValueError("private-data"), EventValidationError("private-data")]
)
async def test_first_handler_failure_aborts_batch_with_original_cause(error: Exception) -> None:
    bus = EventBusRuntime()

    async def fail(_: RuntimeEvent) -> None:
        raise error

    first, second = RecordingHandler(fail), RecordingHandler()
    bus.subscribe("test.event", first)
    bus.subscribe("test.event", second)
    with pytest.raises(EventHandlerError) as raised:
        await bus.publish_many((_event(bus), _event(bus)))
    assert raised.value.__cause__ is error
    assert "RecordingHandler" in str(raised.value) and "private-data" not in str(raised.value)
    assert len(first.events) == 1 and second.events == []
    bus.unsubscribe("test.event", first)
    await bus.publish(_event(bus))
    assert len(second.events) == 1


@pytest.mark.parametrize(
    "error", [asyncio.CancelledError("cancel"), KeyboardInterrupt(), SystemExit()]
)
async def test_control_flow_propagates_unchanged_and_aborts_handlers(error: BaseException) -> None:
    bus = EventBusRuntime()

    async def fail(_: RuntimeEvent) -> None:
        raise error

    first, second = RecordingHandler(fail), RecordingHandler()
    bus.subscribe("test.event", first)
    bus.subscribe("test.event", second)
    with pytest.raises(type(error)) as raised:
        await bus.publish_many((_event(bus), _event(bus)))
    assert raised.value is error and len(first.events) == 1 and second.events == []


async def test_real_task_cancellation_is_not_wrapped_or_converted_to_success() -> None:
    bus = EventBusRuntime()
    entered = asyncio.Event()

    async def block(_: RuntimeEvent) -> None:
        entered.set()
        await asyncio.Event().wait()

    first, second = RecordingHandler(block), RecordingHandler()
    bus.subscribe("test.event", first)
    bus.subscribe("test.event", second)
    task = asyncio.create_task(bus.publish(_event(bus)))
    await asyncio.wait_for(entered.wait(), timeout=5)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert task.cancelled() and second.events == []
    bus.clear()
    await bus.publish(_event(bus))


async def test_direct_internal_dispatch_detaches_batch_and_siblings() -> None:
    registry = SubscriberRuntime()
    dispatcher = DispatcherRuntime(registry)
    first, later = _event(payload={"number": 1}), _event(payload={"number": 2})

    async def mutate(event: RuntimeEvent) -> None:
        event.payload["number"] = 99
        later.payload["number"] = 100

    modifying, observing = RecordingHandler(mutate), RecordingHandler()
    registry.subscribe("test.event", modifying)
    registry.subscribe("test.event", observing)
    await dispatcher.dispatch_many((first, later))
    assert [event.payload for event in observing.events] == [{"number": 1}, {"number": 2}]
    assert first.payload == {"number": 1}
    await dispatcher.dispatch(first)
    assert observing.events[-1].payload == {"number": 1}


async def test_lifecycle_identity_cleanup_empty_dispatch_and_independent_instances() -> None:
    bus, other = EventBusRuntime(), EventBusRuntime()
    assert isinstance(bus, RuntimeContract)
    assert bus.runtime_name == "event_bus" and bus.runtime_layer is RuntimeLayer.L0_KERNEL
    assert bus.health() is HealthStatus.OK
    await bus.initialize()
    await bus.start()
    await bus.stop()
    handler = RecordingHandler()
    reference = ref(handler)
    bus.subscribe("Test.Event", handler)
    assert bus.handlers("test.event") == () and bus.contains("Test.Event")
    assert not other.contains("Test.Event")
    await bus.publish(_event(bus))
    await bus.publish_many(())
    assert handler.events == []
    bus.unsubscribe("Test.Event", handler)
    bus.subscribe("test.event", handler)
    await bus.publish(_event(bus))
    assert len(handler.events) == 1
    del handler
    await bus.shutdown()
    await bus.shutdown()
    gc.collect()
    assert reference() is None and bus.health() is HealthStatus.OK
    assert bus.handlers("test.event") == () and not bus.contains("test.event")
    await bus.publish(_event(bus))
