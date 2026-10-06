# AURORA — KR-007 Event Bus Reconciliation Proposal v1.0

**Document ID:** ADR-005

**Status:** APPROVED — CANONICAL KR-007 RECONCILIATION DECISION

**Date:** 2026-10-06

**Module:** KR-007 — Event Bus Runtime

**Inspected baseline:** `5ac77ce4da63cf708b691e35bc5665e574271eca`

**Implementation authority:** Compile the exact KR-007 contract and reconcile
its registries, then implement only the authorized KR-007 files and tests.

## Explicit Approval Record — 2026-10-06

After receiving this complete proposal and the explicit E-01–E-04 approval
request, the Architecture Authority replied directly:

> Утверждаю ADR-005 полностью, включая E-01–E-04  , дальше

This approves the full decision package, the narrow intra-KR-007 import
clarification, exact method/error behavior, registry reconciliation and canonical
test adjustments below. It is not an independent human code review or a claim
that the not-yet-built implementation has passed acceptance. ADR-003 governs
routine PR/merge handling; all unaffected frozen decisions remain unchanged.

## Кратко для Architecture Authority

KR-006 завершён: PR #19 слит обычным merge после шести успешных проверок CI.
Локальный master синхронизирован; полный набор содержит 495 passing tests.

При компиляции контракта следующего модуля KR-007 обнаружены противоречия,
которые не закрыты ADR-004. Рекомендуемый пакет решений:

1. Явно разрешить уже существующую внутреннюю связь Publisher -> Dispatcher
   внутри KR-007. Не менять конструкторы и не добавлять посредников.
2. Сохранить async publication/dispatch и существующие имена методов. Удалить
   противоречащие им старые записи из документации, а не создавать sync-обёртки.
3. Использовать только существующие исключения Foundation: EventValidationError
   для невалидных событий, EventHandlerError для ошибок регистрации и handlers.
   Ошибку handler сохранять как cause; отмену не оборачивать.
4. Запретить повторную регистрацию, сохранить immutable tuple снимок handlers
   для текущего события и разрешить nested publication без фоновых задач.
5. Выполнить уже утверждённую ADR-004 P-04 изоляцию JSON и расширить канонические
   tests/kernel/test_event_bus.py, не изменяя contracts или другие модули.

Пакет утверждён прямым ответом Architecture Authority, приведённым выше.
Routine PR/merge authorization из ADR-003 сам по себе не является разрешением
нового архитектурного или публичного решения.

## Authority and Inspected Sources

- AGENTS.md: stop on conflicting authoritative documents, missing authority,
  required ADR, or ambiguity changing public behavior.
- ADR-001: delegated documents may be approved only if consistent with the frozen
  baseline, Master Pack and previous approved decisions.
- ADR-004: APPROVED P-04 detached JSON snapshots; explicit KR-007 file/test scope.
  Its P-03 import clarification concerns Orchestrator/EventBus, not Publisher.
- AB-00C: five unchanged event priorities and descending stable event ordering.
- AB-00D Resolution-001/002/006: sole Publisher factory, four-file layout,
  priority on RuntimeEvent and unchanged canonical RuntimeContract. Its gate
  expressly prohibits silent resolution of newly discovered contradictions.
- Master Pack M-01 KR-007 file registry; M-03 EVENT-API-001–004 and behavioral
  registry; M-03A KR-007 symbol/dependency index; M-04 EVENT-IMPORT-001–004;
  M-06 KR-007 module specification; M-07 authority/import rules; M-08 Event Bus
  exception entries; M-09 KR-007 test matrix; PATCH_ERRATA_v1.0.md.
- RCN-001 and AUD-001 K-04; current four KR-007 files, Foundation exceptions,
  frozen event/context contracts and tests/kernel/test_event_bus.py.

The initial root dependency/API registries supply no more specific resolution
of the import or method/exception discrepancies described below. Existing code
and passing tests are implementation evidence, not architectural authority.

## Conflict Register

| ID | Classification | Observed conflict | Approved resolution |
| --- | --- | --- | --- |
| E-01 | Architecture Conflict | M-04 EVENT-IMPORT-002 explicitly forbids Publisher importing Dispatcher; M-03A also lists Publisher as contracts-only. M-06 EVENT-003 explicitly imports Dispatcher. Current publisher.py uses that import and constructor dependency. | Narrowly approve the existing intra-KR-007 Publisher -> Dispatcher edge and reconcile all relevant import/dependency entries. |
| E-02 | Contract Conflict | M-03/M-03A list dispatch_sync(), dispatch_async() and Subscriber.handlers_for(); M-06/current code use async dispatch()/dispatch_many() and Subscriber.handlers(). M-03 also has legacy sync publication wording. | Approve the exact surface below; do not add aliases, event-loop wrappers or additional methods. |
| E-03 | Contract Conflict | M-03 requests EventDispatchError, DuplicateSubscriberError and UnknownSubscriberError, absent from the canonical Foundation implementation/M-08 event family. M-06 propagates the first handler exception; M-08 requires EventHandlerError with the original cause. | Use existing exception classes with the precise behavior below; no Foundation change or new class. |
| E-04 | Contract Conflict | M-03/M-06 forbid duplicates; M-09 says duplicate subscription is ignored. Active-dispatch registry immutability wording does not specify whether nested registry changes are rejected or affect later events. | Reject duplicates and missing unsubscription; capture handlers per event, with later mutations affecting only later dispatch snapshots. |

M-07 gives the import/API registries priority over implementation specifications.
That priority does not itself approve a replacement constructor, a new public
API or a new import edge. The Build Protocol therefore requires this explicit
decision rather than choosing either inconsistent implementation in code.

## Approved Decision E-01 — Minimal Existing Composition

Keep the four existing owners and constructors:

```text
EventBusRuntime.__init__(self) -> None
SubscriberRuntime.__init__(self) -> None
DispatcherRuntime.__init__(self, subscribers: SubscriberRuntime) -> None
PublisherRuntime.__init__(self, dispatcher: DispatcherRuntime) -> None
```

EventBusRuntime owns and wires those instance-local objects. Publisher owns new
logical event construction, validation and the publication entrypoint. Dispatcher
owns sequential handler execution; Subscriber owns registration. No owner moves.

Approved M-04 clarification: Publisher may import/reference its existing
Dispatcher for its constructor and publication delegation. Dispatcher must not
import Publisher or EventBus. This is the only newly approved concrete import
edge; it remains within KR-007/L0 and introduces no cycle or upward layer import.
The equivalent M-03A/M-01 dependency entries must be reconciled explicitly.

Alternative considered, not selected: constructor-injected dispatch callbacks.
This would preserve M-04's contracts-only Publisher imports but would change
constructor wiring and add an abstraction. The existing composition is the
smaller public/API change and is approved. The callback alternative is not authorized.

## Approved Decision E-02 — Exact Method Surface

Retain these existing methods; no other public method is approved by this decision:

| Class | Methods |
| --- | --- |
| EventBusRuntime | subscribe(event_type, handler), unsubscribe(event_type, handler), async publish(event), async publish_many(events), create_for_runtime(*, event_type, payload, context, priority=EventPriority.NORMAL), handlers(event_type), contains(event_type), clear(); canonical runtime_name/runtime_layer, async initialize/start/stop/shutdown and sync health() |
| PublisherRuntime | create(*, event_type, payload, context, priority=EventPriority.NORMAL), validate(event), async publish(event), async publish_many(events) |
| DispatcherRuntime | async dispatch(event), async dispatch_many(events) |
| SubscriberRuntime | subscribe(event_type, handler), unsubscribe(event_type, handler), handlers(event_type), contains(event_type), clear() |

Use the current approved types: RuntimeEvent, RuntimeContext, Payload,
EventPriority, EventHandlerContract, HealthStatus and RuntimeLayer. Batches are
tuple[RuntimeEvent, ...]; handler snapshots are tuple[EventHandlerContract, ...].
contains(event_type) means at least one registered handler for that exact type.
Methods retain their current return values and argument signatures.

create_for_runtime is a delegating facade, not a second factory: only
PublisherRuntime constructs a new logical RuntimeEvent. Ordinary copies of an
existing event for isolation remain permitted by ADR-004 P-04.

No handlers_for(), dispatch_sync(), dispatch_async(), sync publication wrapper,
second factory, headers field or compatibility alias is introduced. Supersede
the conflicting M-03/M-03A descriptions with these exact existing method names.
This removes documentation-only obligations; it does not remove a current API
used anywhere in src/ or tests/ at the inspected baseline.

## Approved Decision E-03 — Validation and Failures

Publisher remains the event-validation owner. Invalid event data, including
mandatory field/type failures and invalid JSON, raises existing
EventValidationError before any handler runs. Do not add a new exception class.
No coercion, payload dumping, new event-name grammar or inferred domain policy.

Keep the current event schema and validate its existing data: nonempty valid
Unicode event_type; UUID-valued IDs and the existing TraceContext fields;
EventPriority member; timezone-aware UTC timestamp; dictionary-root JSON payload.
Optional trace fields remain optional. Context fields unrelated to constructing
the event remain KR-008's concern; no context-storage behavior changes here.

Subscription with the same existing handler for the same event type and removal
of an unregistered handler raise existing EventHandlerError, without mutating
the registry. Preserve current handler equality/membership semantics; do not
invent handler IDs. Event-type matching remains case-sensitive.

For an ordinary Exception from handler execution: abort remaining handlers and
events; raise EventHandlerError with the original exception as its cause. Use
only safe handler identity in the message; do not include event payloads or
secrets. Cancellation and other BaseException control flow propagate unchanged
and are not converted into successful publication or a business failure.

Supersede the legacy EventDispatchError/DuplicateSubscriberError/
UnknownSubscriberError obligations and M-06's raw ordinary-error propagation
only for these KR-007 operations. EventPublishError and InvalidEventError remain
existing Foundation classes, but this contract adds no artificial use of them.
Foundation source, other runtime exception policies and lifecycle vocabulary
remain outside this decision's scope.

## Approved Decision E-04 — Deterministic Dispatch and Re-entry

- Batch event order remains CRITICAL -> HIGH -> NORMAL -> LOW -> BACKGROUND;
  equal-priority events retain stable input FIFO. Handler order is insertion
  order, not a handler priority property.
- Every handler is awaited sequentially; no scheduled/background work or global
  state. A handler may await publication of another event; the nested call runs
  sequentially at that point. No new re-entry rejection is introduced.
- Before the first handler of each event runs, capture that event's immutable
  handler tuple. subscribe/unsubscribe/clear during a handler cannot change the
  captured tuple; those changes affect subsequent event dispatch snapshots,
  including a later nested publication. They are not silently rejected.
- Duplicate subscription is an error, not a no-op. Missing unsubscription is an
  error. Empty/missing-handler publication and an empty batch are valid no-ops.
- shutdown clears registration. Do not introduce another lifecycle state owner,
  a stopped-bus policy, new status values or hidden locks/queues.

## Already Approved P-04 — Requirements Unchanged

This decision does not reopen or weaken ADR-004 P-04:

- create recursively detaches caller payload; publication captures all batch
  event data before the first handler executes and gives each handler a separate
  detached event snapshot.
- Copying preserves event_id, timestamp, trace, priority and all other schema
  values. It creates no new logical event. Frozen dataclass shells and the
  JSON aliases remain unchanged; nested dict/list values are not called frozen.
- Reject non-string object keys, non-finite floats, invalid Unicode, cycles,
  non-JSON objects and depth over 256 dict/list levels (root counts as one).
  Repeated acyclic references are accepted and detached. No RecursionError or
  user-data coercion substitutes for EventValidationError.
- Invalid batch data prevents every handler side effect. No caller/sibling
  handler can mutate another handler's captured input.

Implementation helpers may remain private inside authorized KR-007 files.
There is no new shared utility module or cross-owner helper dependency.

## Authorized Scope

Production: src/kernel/runtime/bus.py, publisher.py, dispatcher.py and
subscriber.py only if needed. Canonical tests: tests/kernel/test_event_bus.py,
owned by KR-011 with the contract-required adjustment authority from ADR-004.

Governance: compile docs/architecture/wave1/KR-007_EVENT_BUS.md and reconcile
only the relevant KR-007 entries in the existing Master Pack registries/specs,
test matrix and exception registry. Do not rewrite unrelated sections.

Do not modify Foundation, KR-004 contracts, DI, Lifecycle, Context, Pipeline,
Bootstrap, product runtimes, dependencies or project configuration. No new
Runtime, directory, dependency, provider, persistence, network integration,
mutable global, scope, layer, event phase/priority or lifecycle state is approved.

## Required Acceptance Evidence After Implementation

Canonical tests must cover the full facade/composition, all five priorities,
stable FIFO and handler order, duplicate/missing registration, immutable handler
snapshots and their mutation semantics, nested publication, empty dispatch,
first ordinary failure with preserved cause, cancellation, cleanup and isolation
between different EventBus instances.

P-04 tests must cover nested caller/handler/batch mutation, preserved event
identity fields, all invalid JSON classes, cyclic vs repeated acyclic references,
256-level acceptance and 257-level rejection, and failure before side effects.
Contract tests remain the only tests allowed to construct new RuntimeEvents
directly. Use the Publisher facade elsewhere; copying existing events to test
validation is not another logical event factory.

Run Ruff, strict Pyright and discovered Pytest tests, Kernel smoke and current
Windows/Linux latest-head CI. Existing unapproved failures outside KR-007 must
be reported rather than repaired. State actual coverage, not an inferred claim.

## Approval Gate and Next Action

The explicit approval record above supplies authority for E-01–E-04, not the
earlier KR-006 acceptance or routine merge permission. The filename retains its
original Proposal spelling for stable references; its status is APPROVED.

Compile/reconcile the exact contract and registries; implement KR-007
in its separate branch; validate and publish under ADR-003; produce one module
report and return to Tech Lead. Do not start KR-008 in the same module task.
