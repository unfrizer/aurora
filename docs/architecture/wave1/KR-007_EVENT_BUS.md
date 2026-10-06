# KR-007 — Event Bus Contract v1.0

**Status:** APPROVED — EXACT MODULE IMPLEMENTATION CONTRACT

**Authority:** AB-00C/D, ADR-004 P-04 and explicitly approved ADR-005 E-01–E-04.
**Layer:** L0 Kernel. **Module:** KR-007. **Date:** 2026-10-06.

## Purpose, Ownership and Dependencies

Consume frozen KR-004 RuntimeEvent/TraceContext/RuntimeContext/EventHandlerContract
and RuntimeContract; use KR-001 identifiers, JSON aliases and exceptions unchanged.
Four existing production files only:

| File | Export | Responsibility | Concrete dependencies |
| --- | --- | --- | --- |
| src/kernel/runtime/bus.py | EventBusRuntime | Public facade and instance composition | Publisher, Dispatcher, Subscriber |
| src/kernel/runtime/publisher.py | PublisherRuntime | Sole new logical event factory, validation, publication | Dispatcher (ADR-005 E-01) |
| src/kernel/runtime/dispatcher.py | DispatcherRuntime | Detached per-handler delivery and sequential ordering | Subscriber |
| src/kernel/runtime/subscriber.py | SubscriberRuntime | Instance-local registration | None |

Each file exports exactly its existing class. Private typed validation/copy helpers
may live inside these files, not in a new package or cross-owner utility. Standard
library datetime, uuid, math, typing, copy and dataclasses are allowed as needed.
No reverse edge, higher-layer import, DI/lifecycle state, I/O, background task,
mutable global, new dependency, Runtime, scope, vocabulary member or schema field.

## Exact API

Signatures retain the existing types and parameters. This is the complete surface;
no handlers_for, dispatch_sync/async, compatibility wrapper or second factory:

```python
class EventBusRuntime(RuntimeContract):
    def __init__(self) -> None: ...
    @property
    def runtime_name(self) -> str: ...
    @property
    def runtime_layer(self) -> RuntimeLayer: ...
    def subscribe(self, event_type: str, handler: EventHandlerContract) -> None: ...
    def unsubscribe(self, event_type: str, handler: EventHandlerContract) -> None: ...
    async def publish(self, event: RuntimeEvent) -> None: ...
    async def publish_many(self, events: tuple[RuntimeEvent, ...]) -> None: ...
    def create_for_runtime(
        self,
        *,
        event_type: str,
        payload: Payload,
        context: RuntimeContext,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> RuntimeEvent: ...
    def handlers(self, event_type: str) -> tuple[EventHandlerContract, ...]: ...
    def contains(self, event_type: str) -> bool: ...
    def clear(self) -> None: ...
    async def initialize(self) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def shutdown(self) -> None: ...
    def health(self) -> HealthStatus: ...


class PublisherRuntime:
    def __init__(self, dispatcher: DispatcherRuntime) -> None: ...
    def create(
        self,
        *,
        event_type: str,
        payload: Payload,
        context: RuntimeContext,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> RuntimeEvent: ...
    def validate(self, event: RuntimeEvent) -> None: ...
    async def publish(self, event: RuntimeEvent) -> None: ...
    async def publish_many(self, events: tuple[RuntimeEvent, ...]) -> None: ...


class DispatcherRuntime:
    def __init__(self, subscribers: SubscriberRuntime) -> None: ...
    async def dispatch(self, event: RuntimeEvent) -> None: ...
    async def dispatch_many(self, events: tuple[RuntimeEvent, ...]) -> None: ...


class SubscriberRuntime:
    def __init__(self) -> None: ...
    def subscribe(self, event_type: str, handler: EventHandlerContract) -> None: ...
    def unsubscribe(self, event_type: str, handler: EventHandlerContract) -> None: ...
    def handlers(self, event_type: str) -> tuple[EventHandlerContract, ...]: ...
    def contains(self, event_type: str) -> bool: ...
    def clear(self) -> None: ...
```

## Construction and Validation

EventBus owns one Subscriber, its Dispatcher and its Publisher. Facade creation
delegates to Publisher.create; only that owner constructs a new logical event.
It generates UUID event_id and UTC timestamp, deriving session/trace from context.
No context-storage validation or mutation is added to KR-007.

Publisher validates nonempty valid-Unicode event_type; UUID event_id/session_id;
TraceContext and UUID trace_id/optional parent_trace_id/correlation_id;
EventPriority member; aware UTC datetime; dict-root JSON payload. Invalid data
raises EventValidationError without dumping payloads, coercion or handler effects.
validate is observational, not normalization. A publication batch is fully validated
and captured before its first handler. Internal dispatch receives validated events;
it copies existing snapshots, never constructs a new logical event or imports Publisher.

JSON accepts string/int/finite float/bool/null, string-keyed dicts and lists. Reject
non-string keys, invalid Unicode, cycles, non-JSON objects and depth over 256
dict/list levels; root is level one. Repeated acyclic references are accepted and
recursively detached. Excessive depth is EventValidationError, not RecursionError.
create detaches caller data; publication detaches every batch event; each handler
gets its own detached snapshot. Preserve every logical identity/schema field.
Frozen shells do not make nested dict/list values immutable; locally editing a
handler's copy cannot change caller, captured event or sibling input (ADR-004 P-04).

## Dispatch and Registration

Batch events: CRITICAL, HIGH, NORMAL, LOW, BACKGROUND; equal priorities retain
stable input FIFO. Handlers retain insertion order and are awaited sequentially.
Nested publication is allowed inline, without a queue, task or re-entry rejection.
Capture handlers as a tuple before each event's first handler. Registry mutation
during delivery does not change this tuple; later events, including nested calls,
observe the later registry. No mutation of lifecycle/status ownership is introduced.

Duplicate registration and missing unsubscription raise EventHandlerError without
registry mutation. Preserve existing equality/membership semantics and exact-case
event matching. contains means any handler for that type; clear removes all.
Ordinary handler Exception aborts remaining handlers/events and raises
EventHandlerError with original cause and safe handler identity only. Cancellation
and other BaseException control flow propagate unchanged. Empty batch/no-handler
dispatch are no-ops. Lifecycle initialize/start/stop do not gate publication;
shutdown clears handlers; identity is event_bus/L0_KERNEL and health is OK.

## Tests and Definition of Done

Only tests/kernel/test_event_bus.py may change; ownership stays KR-011 under
ADR-004/005's explicit contract-required test authority. Cover every method,
constructor/export boundary, validation field, priority/FIFO/order guarantee,
duplicate/missing registration, tuple mutation semantics, nested publication,
cause preservation, cancellation, cleanup and independent bus instances.
Cover caller/sibling/batch mutation isolation, cyclic vs repeated references,
invalid JSON, identity preservation and 256/257-level boundaries before effects.
Create new events through Publisher/facade, not direct contract construction.

Run uv run pyright, uv run ruff check ., uv run pytest; actual collection/execution
is mandatory. Check scoped formatting, Kernel smoke, import DAG, public surface
and latest-head Windows/Linux CI. M-09's executable-line coverage target is 100%;
state measured results and any gap honestly. No fixes outside this module.
One branch/task/report and Tech Lead review gate; do not start KR-008 here.
