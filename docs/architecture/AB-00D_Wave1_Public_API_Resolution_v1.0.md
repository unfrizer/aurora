# AURORA — Wave 1 Public API Resolution v1.0

**Document ID:** AB-00D  
**Document Name:** Wave 1 Public API Resolution  
**Canonical Path:** `docs/architecture/AB-00D_Wave1_Public_API_Resolution_v1.0.md`  
**Version:** 1.0  
**Status:** APPROVED — CANONICAL RESOLUTION  
**Scope:** Wave 1 — Kernel Runtime  
**Authority:** Architecture Freeze v1.0 + AB-00B + AB-00C

---

# Purpose

This document resolves the remaining implementation-blocking Wave 1 public API contradictions in the current Master documents.

It does not create a new Runtime, change Runtime ownership, change Runtime layers, or redesign the frozen architecture.

For the six subjects explicitly resolved below, AB-00D supersedes conflicting lower-authority wording only to the extent necessary to apply these resolutions.

---

# RESOLUTION-001 — Event Creation Ownership

## Canonical file set

KR-007 Event Bus Runtime contains exactly these four implementation files:

```text
src/kernel/runtime/bus.py
src/kernel/runtime/publisher.py
src/kernel/runtime/dispatcher.py
src/kernel/runtime/subscriber.py
```

`src/kernel/runtime/event.py` does not exist.

`EventRuntime` does not exist.

No compatibility file, forwarding module, alias class, or second event factory may be created.

## Canonical owner

`PublisherRuntime` is the unique owner of `RuntimeEvent` construction and validation.

The canonical event-construction API is:

```python
def create(
    self,
    *,
    event_type: str,
    payload: Payload,
    context: RuntimeContext,
    priority: EventPriority = EventPriority.NORMAL,
) -> RuntimeEvent:
    ...
```

Responsibilities:

- generate `event_id`;
- generate the UTC event timestamp;
- derive event context data from `RuntimeContext`;
- attach the canonical `EventPriority`;
- validate the event before publication;
- return an immutable `RuntimeEvent`.

Direct `RuntimeEvent` construction is forbidden in production code outside `PublisherRuntime`.

Tests may construct `RuntimeEvent` directly only when testing the contract itself.

## Public API rule

`PublisherRuntime.create()` is the single canonical event-creation API.

No `EventRuntime.create()` and no duplicate event factory API are permitted.

Event publication remains owned by `EventBusRuntime` / `PublisherRuntime` according to the existing KR-007 ownership boundaries.

## Superseded text

Any M-06 section defining:

```text
src/kernel/runtime/event.py
EventRuntime
EventRuntime.create()
EventRuntime.validate()
```

is superseded.

M-01, M-03, M-04 and `PATCH_ERRATA_v1.0.md` are confirmed on the four-file KR-007 layout and PublisherRuntime creation ownership.

---

# RESOLUTION-002 — EventPriority Storage

AB-00C defines priority vocabulary and dispatch order.

AB-00D fixes where that priority is stored.

## Canonical rule

Priority is an immutable property of `RuntimeEvent`.

`RuntimeEvent` contains:

```python
priority: EventPriority = EventPriority.NORMAL
```

`EventPriority` is not a property of `EventHandlerContract`.

`EventHandlerContract` remains:

```python
class EventHandlerContract(ABC):
    @abstractmethod
    async def handle(
        self,
        event: RuntimeEvent,
    ) -> None:
        ...
```

No handler-level priority API is introduced.

## RuntimeEvent compatibility rule

The previously mandatory event fields remain mandatory.

AB-00D adds `priority` to the event contract; it does not remove:

```text
event_id
event_type
session_id
timestamp
payload
trace
```

Canonical dataclass ordering must keep non-default fields before defaulted fields.

A compliant layout is:

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class RuntimeEvent:
    event_id: EventId
    event_type: str
    session_id: SessionId
    trace: TraceContext

    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=utc_now)
    payload: Payload = field(default_factory=dict)
```

AB-00C ordering is therefore applied to events, not handlers:

```text
CRITICAL → HIGH → NORMAL → LOW → BACKGROUND
```

Within equal event priority, stable FIFO / registration ordering remains mandatory.

## Superseded text

Any lower-authority contract that defines RuntimeEvent without a place to carry EventPriority is superseded only by the addition of the `priority` field.

Any interpretation that assigns AB-00C priority to handlers instead of events is rejected.

---

# RESOLUTION-003 — RuntimeContext and ContextRuntime API

## RuntimeContext canonical owner

`src/kernel/contracts/context.py`

The canonical immutable `RuntimeContext` structure is:

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class RuntimeContext:
    session_id: SessionId
    pipeline_id: PipelineId
    runtime_layer: RuntimeLayer
    trace: TraceContext
    metadata: Metadata
    created_at: datetime
    expires_at: datetime | None
```

Canonical public fields are therefore exactly:

```text
session_id
pipeline_id
runtime_layer
trace
metadata
created_at
expires_at
```

Canonical derived properties are:

```text
is_expired
trace_id
root_trace_id
depth
```

`RuntimeContext` is immutable. Replacement creates a new snapshot.

## ContextRuntime canonical owner

`src/kernel/runtime/context.py`

ContextRuntime implements the canonical RuntimeContract defined by RESOLUTION-006 and exposes these domain methods:

```python
def create(
    self,
    *,
    session_id: SessionId,
    pipeline_id: PipelineId,
    runtime_layer: RuntimeLayer,
    metadata: Metadata,
    trace: TraceContext,
) -> RuntimeContext:
    ...
```

`create()` generates `created_at` in UTC and sets `expires_at` according to context lifetime policy; when no expiration is configured, `expires_at` is `None`.

```python
def current(self) -> RuntimeContext:
    ...
```

Raises the canonical context-not-available exception when no active context exists.

```python
def replace(
    self,
    context: RuntimeContext,
) -> RuntimeContext:
    ...
```

`replace()` stores the supplied immutable snapshot and returns that active snapshot.

```python
def clear(self) -> None:
    ...
```

```python
def has_context(self) -> bool:
    ...
```

```python
def health(self) -> HealthStatus:
    ...
```

In addition, ContextRuntime implements all lifecycle members required by the canonical RuntimeContract.

## Superseded text

The M-06 four-field RuntimeContext variant:

```text
session_id
pipeline_id
trace
metadata
```

is superseded.

The M-06 `ContextRuntime.create()` signature without `runtime_layer` is superseded.

The M-06 `replace(...)->None` signature is superseded.

Any ContextRuntime definition omitting `health()` while declaring that ContextRuntime implements RuntimeContract is superseded.

---

# RESOLUTION-004 — ManifestRuntime.validate()

## Canonical owner

`src/kernel/runtime/manifest.py`

The canonical signature is:

```python
def validate(
    self,
    definition: PipelineDefinition,
) -> PipelineDefinition:
    ...
```

Behavior:

1. validate stage IDs;
2. validate dependency references;
3. validate DAG topology;
4. raise the canonical validation exception on failure;
5. return the same immutable `PipelineDefinition` on success.

ManifestRuntime does not mutate, rebuild, execute, or own the pipeline.

Returning `PipelineDefinition` is a validation-pass-through contract for deterministic composition.

## Superseded text

Any M-06 signature declaring:

```python
def validate(...) -> None
```

is superseded.

M-03 `PipelineDefinition` return semantics are confirmed.

---

# RESOLUTION-005 — BootstrapRuntime.build()

## Canonical owner

`src/kernel/runtime/bootstrap.py`

The canonical signature is asynchronous:

```python
async def build(
    self,
) -> RuntimeKernel:
    ...
```

## Behavior

`build()`:

1. validates construction prerequisites;
2. creates the Wave 1 runtime graph in canonical order;
3. wires dependencies;
4. returns the fully constructed `RuntimeKernel`.

`build()` does **not** perform `RuntimeKernel.initialize()`.

Runtime initialization remains a separate lifecycle operation.

The canonical entry sequence is therefore:

```python
runtime = await bootstrap.build()
await runtime.initialize()
await runtime.start()
...
await runtime.stop()
await runtime.shutdown()
```

This avoids duplicate initialization and preserves separation between construction and lifecycle initialization.

## Superseded text

The synchronous M-03 signature:

```python
def build() -> RuntimeKernel
```

is superseded.

Any wording that describes `build()` as returning an already lifecycle-initialized RuntimeKernel is superseded.

M-06 asynchronous build ownership is confirmed, with the construction/initialization distinction clarified by AB-00D.

---

# RESOLUTION-006 — Canonical RuntimeContract

## Canonical owner

`src/kernel/contracts/runtime.py`

The canonical contract is an abstract lifecycle contract.

```python
from abc import ABC, abstractmethod

class RuntimeContract(ABC):
    @property
    @abstractmethod
    def runtime_name(self) -> str:
        ...

    @property
    @abstractmethod
    def runtime_layer(self) -> RuntimeLayer:
        ...

    @abstractmethod
    async def initialize(self) -> None:
        ...

    @abstractmethod
    async def start(self) -> None:
        ...

    @abstractmethod
    async def stop(self) -> None:
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        ...

    @abstractmethod
    def health(self) -> HealthStatus:
        ...
```

## Exact contract surface

Required properties:

```text
runtime_name: str
runtime_layer: RuntimeLayer
```

Required lifecycle methods:

```text
async initialize() -> None
async start() -> None
async stop() -> None
async shutdown() -> None
```

Required read-only health method:

```text
health() -> HealthStatus
```

## Explicit exclusions

`RuntimeContract` does **not** define:

```text
runtime_id
status()
state()
diagnostics()
execute()
```

Reasons:

- `RuntimeId` is not part of the approved core identifier vocabulary.
- RuntimeStatus mutation and state snapshots belong to Lifecycle/State ownership.
- `status()` / `state()` may exist on lifecycle-aware public facades such as RuntimeKernel or LifecycleRuntime, but they are not universal runtime requirements.
- diagnostics and pipeline execution are separate responsibilities.

`shutdown()` is mandatory.

`health()` is mandatory and read-only.

## Async rule

The four lifecycle methods are asynchronous for every RuntimeContract implementation.

`health()` and identity properties are synchronous and read-only.

Every class declared to implement RuntimeContract must implement this exact surface.

## Superseded text

The M-03 sync-only lifecycle signatures are superseded.

The M-03 contract variant containing only `initialize()`, `shutdown()`, and `health()` is superseded by the full lifecycle set.

Any current or historical RuntimeContract containing `runtime_id` or universal `status()` is superseded.

M-06's lifecycle method set is confirmed, and M-03's `runtime_name`, `runtime_layer`, and `health()` requirements are retained.

---

# Document Reconciliation Matrix

| Subject | Final AB-00D Resolution | Conflicting Sources Reconciled |
|---|---|---|
| Event creation | `PublisherRuntime.create()`; no `event.py` / no `EventRuntime` | M-01, M-03, M-04, M-06, PATCH_ERRATA |
| Priority storage | `RuntimeEvent.priority` | AB-00A-era event schema, M-03/M-03A, M-06, AB-00C |
| RuntimeContext | seven-field immutable M-03 form | M-01, M-03, M-03A, M-06 |
| ContextRuntime | M-03 domain API + canonical RuntimeContract | M-03, M-06 |
| Pipeline validation | `ManifestRuntime.validate() -> PipelineDefinition` | M-03, M-06 |
| Bootstrap | `async build() -> RuntimeKernel`, construction only | M-03, M-06 |
| RuntimeContract | identity + async full lifecycle + sync health | M-01, M-03, M-03A, M-06, current/historical KR-004 variants |

---

# Precedence

For subjects explicitly resolved by AB-00D:

```text
Architecture Freeze v1.0
        ↓
AB-00B Wave 1 Architecture Resolution v1.0
        ↓
AB-00C Wave 1 EventPriority Resolution v1.0
        ↓
AB-00D Wave 1 Public API Resolution v1.0
        ↓
M-01 / M-03 / M-03A / M-04 / M-05 / M-06
        ↓
AB-00A implementation/reconciliation documents
        ↓
KR-001_Reconciliation_Decision_v1.0.md
        ↓
PATCH_ERRATA_v1.0.md
        ↓
Generated implementation
```

AB-00D does not alter any subject outside the six resolutions in this document.

Where a lower document already agrees with AB-00D, it is confirmed rather than replaced.

---

# Implementation Gate

After approval of AB-00D:

1. KR-004 contracts may be implemented/regenerated against AB-00B, AB-00C and AB-00D.
2. KR-005 through KR-011 may then proceed sequentially.
3. No implementation agent may choose an alternative event factory, priority storage model, context signature, pipeline validation return type, bootstrap sync model, or RuntimeContract surface.
4. Any newly discovered contradiction outside AB-00B, AB-00C and AB-00D remains an Architecture Conflict and must not be silently resolved in code.

---

# Validation Requirements

AB-00D reconciliation is complete only when:

- KR-007 contains no `event.py`;
- `EventRuntime` does not exist;
- event creation is owned by `PublisherRuntime.create()`;
- RuntimeEvent carries immutable `EventPriority`;
- EventHandlerContract does not own priority;
- RuntimeContext matches the canonical seven-field contract;
- ContextRuntime includes `runtime_layer`, returns RuntimeContext from `replace()`, and reports `health()`;
- `ManifestRuntime.validate()` returns `PipelineDefinition`;
- `BootstrapRuntime.build()` is async and does not initialize RuntimeKernel;
- RuntimeContract matches RESOLUTION-006 exactly;
- conflicting M-03/M-06/test specifications are reconciled before implementation is declared GREEN;
- Ruff passes;
- Pyright passes with 0 errors, 0 warnings, and 0 informations;
- Pytest collects, executes and passes all relevant Wave 1 tests.

---

# Definition of Done

- [x] Event creation ownership resolved.
- [x] Event factory file conflict resolved.
- [x] EventPriority storage resolved.
- [x] RuntimeContext contract resolved.
- [x] ContextRuntime API resolved.
- [x] Pipeline validation return contract resolved.
- [x] Bootstrap build async contract resolved.
- [x] Bootstrap construction vs initialization boundary resolved.
- [x] RuntimeContract exact lifecycle surface resolved.
- [x] Superseded alternatives explicitly identified.
- [x] Wave 1 implementation no longer requires choosing between these conflicting public APIs.

---

# Approval

**Architecture State:** FROZEN  
**Resolution State:** APPROVED  
**Effective Version:** v1.0  
**Applies From:** Wave 1 — Kernel Runtime  
**Change Policy:** Any change to a resolution in AB-00D requires a new explicit architecture resolution / ADR.

---

**END OF DOCUMENT — AB-00D WAVE 1 PUBLIC API RESOLUTION v1.0**
