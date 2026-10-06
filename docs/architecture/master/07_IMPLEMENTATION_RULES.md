# AURORA ENGINEERING BIBLE v1.1

## Approved KR-010 Implementation Rules — ADR-008

**Status:** APPROVED — ADR-008 B-01–B-05, 2026-10-06.
Exact contract: [KR-010](../wave1/KR-010_RUNNER_BOOTSTRAP.md).
Authority: [ADR-008](../ADR-008_KR010_Bootstrap_Reconciliation_Proposal_v1.0.md).

Use the exact linked contract, same three production/two canonical test paths.
Retain public Bootstrap builders; async build returns CREATED, no initialization/
root context/event/directory/service work. Existing immutable config/cache/logger
owners unchanged; no configure_logging replacement or directory abstraction.
Bootstrap alone constructs the existing Session(context) collaborator; Kernel's
required session reference, read-only property and remove_session are B-02's exact
approved exception, not permission for arbitrary internal-runtime imports.

A Kernel-local guard spans mutation AND cleanup; RUNNING execution uses captured
valid Pipeline ID and Container finally disposal. Session DI uses Container, not
Session internals. Partial startup abort uses only legal Lifecycle FAILED transition;
FAILED remains terminal. First failure/cancellation/prior cause preserved, safe
logging only; no shield/task/wait loop/new vocabulary/recovery/compatibility API.
Main is bounded startup/finalization through facade, two independent cleanup attempts.
Canonical tests exercise every API with 100% executable-line target per source,
no skips/xfail/exclusions; all required gates and latest-head CI, one report and STOP.
This overrides only contradictory KR-010 constructor/lifetime/entrypoint/error
examples in this document; other implementation/ownership rules stay unchanged.

Document ID: M-07

Document Name: Implementation Rules

Path: docs/architecture/master/07_IMPLEMENTATION_RULES.md

Status: CANONICAL SOURCE OF TRUTH

Authority:
- AB-00 Development Constitution
- AB-00A Architecture Reconciliation
- M-01 File Registry
- M-02 Runtime Graph
- M-03 Public API Registry
- M-04 Import Graph
- M-05 Runtime Registry
- M-06 Module Specifications

Version: 1.1 Canonical

---

# 1. Purpose

This document defines the mandatory implementation constitution for every Python source file inside AURORA.

It exists to eliminate architectural drift, Ruff violations, Pyright violations, circular imports, inconsistent APIs and undocumented implementation behavior.

Codex must treat this document as executable law.

If this document conflicts with generated code, generated code is wrong.

---

# 2. Global Engineering Constitution

## 2.1 Source of Truth Hierarchy

Priority is immutable.

| Priority | Document | Authority |
|----------|----------|-----------|
| 1 | AB-00 Development Constitution | Absolute |
| 2 | Architecture Freeze v1.0 | Absolute |
| 3 | ADR documents | Absolute |
| 4 | M-01 File Registry | Absolute |
| 5 | M-02 Runtime Graph | Absolute |
| 6 | M-03 API Registry | Absolute |
| 7 | M-04 Import Graph | Absolute |
| 8 | M-05 Runtime Registry | Absolute |
| 9 | M-06 Module Specifications | Absolute |
| 10 | Generated implementation | Lowest |

Generated implementation may never override documentation.

---

## 2.2 Wave Ownership Rule

Every production file belongs to exactly one KR.

A file may never contain responsibilities belonging to another KR.

Example:

ContainerRuntime owns DI.

EventBusRuntime may consume DI.

EventBusRuntime may never resolve services directly.

---

## 2.3 Runtime Ownership Rule

Every runtime object has one owner.

Examples:

| Object | Owner |
|--------|-------|
| Settings | KR-002 |
| Logger | KR-003 |
| RuntimeContext | KR-008 |
| EventBus | KR-007 |
| Lifecycle | KR-006 |
| Pipeline | KR-009 |
| Container | KR-005 |

No shared ownership exists.

---

## 2.4 No Hidden Runtime Rule

Hidden runtime state is forbidden.

Forbidden examples:

- module-global mutable dictionaries;
- singleton runtime objects;
- service registries outside DI Runtime;
- global EventBus;
- global RuntimeContext.

Allowed exceptions:

| Exception | Reason |
|-----------|--------|
| functools.cache for immutable Settings | Approved |
| functools.cache for Logger factory | Approved |
| ContextVar inside Logging Runtime | Approved |

No additional exceptions exist.

---

## 2.5 Public API Rule

Every public API must appear in M-03.

Everything else is private.

Private names begin with underscore.

---

# 3. Canonical Python File Template

Every production file follows exactly this order.

```python
"""
Module docstring.
"""

from __future__ import annotations

# Standard Library Imports

# Third Party Imports

# Foundation Imports

# Runtime Imports

# Constants

# Type Aliases

# Dataclasses

# Public Classes

# Private Classes

# Public Functions

# Private Functions

__all__ = [...]
```

No deviations.

---

## 3.1 Module Docstring

Every module begins with a canonical docstring.

Template:

```python
"""
AURORA Kernel Runtime

KR-005 Dependency Injection Runtime

Container runtime implementation.
"""
```

Contains:

- project;
- KR owner;
- short purpose.

No license block.

---

## 3.2 Import Groups

Import order is frozen.

Group 1

```python
from __future__ import annotations
```

Always first.

Group 2

Python Standard Library.

Alphabetical.

Group 3

Third-party libraries.

Alphabetical.

Group 4

Foundation Core imports.

Group 5

Kernel Contract imports.

Group 6

Kernel Runtime imports.

Group 7

Application Runtime imports.

No mixing.

---

## 3.3 One Import Per Symbol Rule

Allowed:

```python
from src.core.types import ModuleId
from src.core.types import RuntimeLayer
```

Forbidden:

```python
from src.core.types import *
```

Forbidden:

```python
import src.core.types as types
```

---

## 3.4 Absolute Import Rule

All imports are absolute.

Allowed:

```python
from src.kernel.runtime.container import ContainerRuntime
```

Forbidden:

```python
from ..runtime.container import ContainerRuntime
```

Forbidden:

```python
from .container import ContainerRuntime
```

---

# 4. Import Constitution

## 4.1 Circular Imports

Circular imports are forbidden.

Dependency direction:

Foundation

↓

Contracts

↓

Runtime

↓

Application

Never upward.

---

## 4.2 Import Graph Validation

Every new import must exist in M-04.

If not listed, it is forbidden.

---

## 4.3 Runtime Layer Boundaries

| Layer | Allowed Imports |
|-------|-----------------|
| Core | Standard Library only |
| Contracts | Core only |
| Runtime | Core + Contracts |
| Application | Runtime + Contracts + Core |

Reverse imports forbidden.

---

## 4.4 Lazy Imports

Lazy imports are forbidden unless explicitly documented.

No runtime import inside functions.

Allowed only to resolve unavoidable typing cycles.

---

# 5. Naming Constitution

## 5.1 File Names

Rules:

- snake_case
- lowercase only
- singular responsibility

Examples:

container.py

runtime.py

event.py

subscriber.py

Forbidden:

Container.py

eventBus.py

utils.py

helpers.py

common.py

misc.py

---

## 5.2 Class Names

PascalCase only.

Runtime classes end with Runtime.

Examples:

ContainerRuntime

EventBusRuntime

LifecycleRuntime

Forbidden:

Container

Bus

RuntimeContainerManager

---

## 5.3 Contract Classes

Contract names end with Contract.

Examples:

RuntimeContract

LifecycleContract

ServiceContract

---

## 5.4 Dataclass Names

Noun only.

Examples:

RuntimeContext

TraceContext

PipelineStage

RuntimeEvent

No Manager suffix.

---

## 5.5 Function Names

snake_case only.

Public API uses verbs.

Examples:

register()

resolve()

publish()

shutdown()

Private helpers begin with underscore.

---

# 6. Typing Constitution

## 6.1 Pyright Strict

Repository target:

```
uv run pyright

0 errors
0 warnings
```

Strict mode is mandatory.

---

## 6.2 Forbidden Any

Public APIs may never expose Any.

Forbidden:

```python
payload: dict[str, Any]
```

Allowed:

```python
payload: Payload
```

---

## 6.3 JSON Types

Canonical aliases:

JSONPrimitive

JSONValue

JSONDict

Payload

Metadata

No alternative aliases allowed.

---

## 6.4 Typed Collections

Always parameterized.

Allowed:

```python
list[str]

tuple[ModuleId, ...]

dict[str, RuntimeEvent]
```

Forbidden:

```python
list

dict

tuple
```

---

## 6.5 Optional Types

Use explicit union.

Allowed:

```python
TraceId | None
```

Forbidden:

```python
Optional[TraceId]
```

Python 3.13 syntax is canonical.

---

## 6.6 NewType Rule

Identifiers use NewType.

ModuleId

SessionId

PipelineId

EventId

TraceId

ServiceId

Never raw strings in public APIs.

---

## 6.7 Literal Rule

Closed vocabularies use Literal only when defined in specification.

Environment uses Literal.

RuntimeStatus uses StrEnum.

EventPriority uses the five-member IntEnum fixed by AB-00C.

No duplicated literals.

---

# 7. Dataclass Constitution

Dataclasses are the primary immutable data structure of AURORA.

Every dataclass must follow one canonical style.

## 7.1 Canonical Dataclass Template

```python
from dataclasses import dataclass, field

@dataclass(
    slots=True,
    frozen=True,
    kw_only=True,
    repr=True,
    eq=True,
)
class RuntimeEvent:
    ...
```

Order of decorators is immutable.

---

## 7.2 Required Dataclass Parameters

| Parameter | Default |
|-----------|---------|
| slots | True |
| kw_only | True |
| repr | True |
| eq | True |

Only `frozen` varies by specification.

---

## 7.3 Frozen Rule

Use `frozen=True` for:

- contracts;
- manifests;
- events;
- runtime context;
- state snapshots;
- descriptors.

Use mutable dataclasses **only** if M-06 explicitly says so.

---

## 7.4 Field Ordering Rule (Pyright Critical)

Required fields **always come before** fields with defaults.

Correct:

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class RuntimeEvent:
    event_id: EventId
    event_type: str
    session_id: SessionId
    trace: TraceContext

    timestamp: datetime = field(default_factory=utc_now)
    payload: Payload = field(default_factory=dict)
```

Forbidden:

```python
payload: Payload = field(default_factory=dict)
trace: TraceContext
```

This rule prevents the Pyright error:

> Fields without default values cannot appear after fields with default values.

---

## 7.5 Mutable Default Rule

Forbidden:

```python
metadata: Metadata = {}
payload: Payload = {}
depends_on: list[str] = []
```

Allowed:

```python
metadata: Metadata = field(default_factory=dict)
payload: Payload = field(default_factory=dict)
depends_on: tuple[str, ...] = ()
```

---

## 7.6 Tuple Preference Rule

Immutable collections use tuples.

Allowed:

```python
tuple[ModuleId, ...]
tuple[PipelineStage, ...]
```

Forbidden:

```python
list[ModuleId]
list[PipelineStage]
```

---

## 7.7 Default Factory Rule

Every mutable value uses `field(default_factory=...)`.

Allowed factories:

- `dict`
- `list` (tests only)
- `set` (private runtime only)
- custom immutable builders

---

## 7.8 Dataclass Validation Rule

Dataclasses never validate themselves.

Validation belongs to runtime/service classes.

Example:

RuntimeEvent — immutable.

EventRuntime.validate() — validation.

---

# 8. Exception Constitution

Exceptions are part of the public API.

Every exception belongs to `src/core/exceptions.py`.

---

## 8.1 Exception Hierarchy

AuroraError

├── ConfigurationError

├── ContainerError

├── ManifestError

├── EventBusError

├── RuntimeError

├── ValidationError

└── DiagnosticsError

Hierarchy is frozen.

---

## 8.2 Exception Ownership

| Exception Group | Owner KR |
|-----------------|----------|
| ConfigurationError | KR-002 |
| ContainerError | KR-005 |
| ManifestError | KR-004 |
| EventBusError | KR-007 |
| RuntimeError | KR-006 / KR-010 |
| ValidationError | Foundation |
| DiagnosticsError | Future KR |

---

## 8.3 Raise Rule

Raise the most specific exception.

Forbidden:

```python
raise Exception(...)
```

Forbidden:

```python
raise ValueError(...)
```

Allowed:

```python
raise ServiceResolutionError(...)
```

---

## 8.4 Wrapping Rule

External exceptions are wrapped.

Example:

```python
try:
    Settings()
except ValidationError as exc:
    raise InvalidConfigurationError(...) from exc
```

Never expose third-party exceptions outside KR owner.

---

## 8.5 Exception Messages

Messages are deterministic.

Template:

```
Service 'event_bus' is not registered.
```

Not:

```
Oops.
```

No emojis.

No multiline messages.

---

# 9. Logging Constitution

Logging Runtime is the only owner of logging behavior.

---

## 9.1 Logging Entry Rule

Never import `logging` directly outside KR-003 unless implementing formatters.

Use:

```python
from src.core.logger import get_logger

logger = get_logger(__name__)
```

---

## 9.2 No print Rule

Forbidden everywhere in production code.

Use logger methods only.

---

## 9.3 Logger Naming

Always:

```python
logger = get_logger(__name__)
```

Never:

```python
logging.getLogger()
```

Never root logger.

---

## 9.4 Structured Logging Rule

Every log record may contain:

- trace_id
- session_id
- pipeline_id
- module_id

Injected through ContextFilter.

Production code never injects manually.

---

## 9.5 Log Levels

Allowed levels only.

DEBUG

INFO

WARNING

ERROR

CRITICAL

No custom levels.

---

## 9.6 Logging Message Style

Good:

```
Container initialized.
```

Good:

```
Resolved service 'event_bus'.
```

Bad:

```
Everything works!!!
```

Bad:

```
123
```

---

## 9.7 Logging Side Effects

Logging never changes runtime behavior.

Logging failures never crash runtime.

---

# 10. Dependency Injection Constitution

KR-005 owns all DI behavior.

---

## 10.1 Registration Rule

Services register descriptors only.

Never instances.

---

## 10.2 Constructor Injection Rule

Only constructor injection is allowed.

Forbidden:

Setter injection.

Property injection.

Attribute injection.

Global injection.

---

## 10.3 Scope Rule

Exactly four scopes exist.

Application

Session

Pipeline

Transient

No Singleton scope.

Application replaces Singleton.

---

## 10.4 Resolution Rule

`resolve()` returns initialized service.

Never returns None.

Failure raises ServiceResolutionError.

---

## 10.5 Lifetime Rule

Application lives until runtime shutdown.

Session lives until session removal.

Pipeline lives until pipeline completion.

Transient lives until reference is released.

---

## 10.6 Circular Dependency Rule

Resolver detects cycles before instantiation.

Algorithm:

Depth-first search.

Abort immediately.

Raise CircularDependencyError.

---

## 10.7 Disposal Rule

Every cached service receives:

```python
await shutdown()
```

Exactly once.

---

## 10.8 Eager Services

Allowed only through descriptor.

```python
eager=True
```

Bootstrap initializes eager services after registration.

---

# 11. Event Constitution

**Authority:** APPROVED ADR-005 E-01–E-04, ADR-004 P-04 and AB-00C/D (2026-10-06).
The exact signatures and acceptance contract are `../wave1/KR-007_EVENT_BUS.md`.
Only KR-007 entries are reconciled; other module contracts remain unchanged.

Only PublisherRuntime.create constructs new logical events. Facade creation delegates;
tests directly construct RuntimeEvent only to test the contract itself. Ordinary
standard-library copies during dispatch preserve logical identity and are not factories.
Never add an event.py, EventRuntime, headers field or handler-priority property.

Publisher is the only new logical RuntimeEvent constructor. Facade creation delegates
without becoming another factory. Standard-library copies of existing events preserve
all identity fields. Frozen event shells contain detached, locally mutable JSON;
caller, captured batch and sibling handler data are recursively isolated.

Validate complete batches before any handler. Reject invalid event fields/JSON with
EventValidationError; JSON is string-keyed dict/list/primitive, finite floats, valid
Unicode, no cycles or non-JSON objects, maximum 256 container levels including root.
Repeated acyclic references are accepted and detached without coercion.

Events are ordered CRITICAL -> HIGH -> NORMAL -> LOW -> BACKGROUND, stable input
FIFO within priority. Handlers run awaited in insertion order. Capture a handler
tuple per event; registry mutations affect later events, never that tuple. Nested
publication runs inline; no tasks, queue or re-entry rejection. Duplicate registration
and missing unsubscription raise EventHandlerError without registry mutation. Matching
is case-sensitive and membership semantics stay unchanged. Empty dispatch is a no-op.
Ordinary handler Exception aborts remaining delivery and becomes EventHandlerError
with original cause and safe handler identity. Cancellation/BaseException propagate.
Shutdown clears subscribers; no additional lifecycle state or publication gate.

RuntimeEvent fields remain frozen. Nested JSON may be edited in a detached local
snapshot without changing canonical/caller/sibling data. Standard-library copying,
strict object-based validation narrowing and private typed helpers are permitted
within KR-007; no public Any/Unknown, cross-owner utility or new abstraction.
All unaffected typing, ownership and build rules remain unchanged.

# 12. Runtime Ownership Rules

Defines ownership boundaries across Kernel Runtime.

---

## 12.1 Single Runtime Owner

Every runtime owns exactly one responsibility.

No overlaps.

---

## 12.2 Runtime Communication Rule

Communication happens through:

- contracts;
- EventBus;
- DI.

Never direct mutable shared state.

---

## 12.3 Runtime Context Rule

RuntimeContext flows downward.

Bootstrap

↓

Pipeline

↓

Stage

↓

Events

Never upward mutation.

---

## 12.4 Configuration Ownership

Settings are immutable.

Runtime modules receive Settings through DI.

Never call get_settings() repeatedly inside runtime code.

---

## 12.5 Shutdown Ownership

Bootstrap owns shutdown orchestration.

Lifecycle owns shutdown sequence.

Container owns service disposal.

No runtime disposes another runtime directly.

---

## 12.6 Runtime Creation Rule

Runtime objects are created exactly once by BootstrapRuntime.

Forbidden:

```python
container = ContainerRuntime()
```

inside EventBus, Pipeline, Lifecycle, etc.

Only Bootstrap constructs runtime graph.

---

**END OF M-07 PART 2**

---

# 13. State Machine Constitution

## Approved KR-006 lifecycle reconciliation

Apply the exact APPROVED `../wave1/KR-006_LIFECYCLE.md` compiled from AB-00B/D
and ADR-004 P-05. It supersedes obsolete KR-006 sync lifecycle signatures,
reset helpers, shutdown-hook APIs, first-error teardown and FAILED-to-STOPPED
examples below. StateRuntime alone owns the unchanged AB-00B ten-state matrix.
LifecycleRuntime preserves the current status property and exact existing API;
HookRuntime preserves only the six BEFORE/AFTER initialize/start/stop hooks.
Cleanup tracks touched participants, attempts all eligible resources despite
ordinary errors, preserves ordered causes and cancellation, resumes interrupted
ownership and clears final participant/hook references. FAILED remains terminal.
Only the three canonical KR-006 source files and canonical test_lifecycle.py
(owned by KR-011, explicitly authorized by ADR-004) may change in this module.
Standard-library cancellation/immutable matrix bookkeeping and existing
Foundation exceptions are allowed within the same DAG; no higher import is added.
Tests cover all 100 transitions and P-05 failures/cancellation/idempotency with
all public APIs exercised and at least 95% executable-line coverage per file.
Other module declarations, vocabulary and ownership remain unchanged.

Lifecycle state transitions are globally frozen.

Only KR-006 owns transition execution.

---

## 13.1 Canonical Runtime States

RuntimeStatus vocabulary is immutable.

| State | Meaning |
|-------|---------|
| CREATED | Runtime object constructed. |
| INITIALIZING | Runtime allocates resources. |
| READY | Runtime initialized but not executing. |
| RUNNING | Runtime actively executing. |
| FAILED | Runtime entered unrecoverable state. |
| STOPPED | Runtime completely stopped. |

No additional runtime states may exist.

---

## 13.2 Transition Matrix

Allowed transitions only.

| From | Allowed To |
|------|------------|
| CREATED | INITIALIZING |
| INITIALIZING | READY |
| INITIALIZING | FAILED |
| READY | RUNNING |
| RUNNING | STOPPED |
| RUNNING | FAILED |
| FAILED | STOPPED |

Everything else raises RuntimeStateError.

---

## 13.3 Transition Ownership

Only StateRuntime may mutate RuntimeStatus.

Forbidden:

```python
runtime.status = RuntimeStatus.RUNNING
```

Correct:

```python
state.transition(RuntimeStatus.RUNNING)
```

---

## 13.4 Startup Sequence

Canonical sequence:

```
CREATED
      │
INITIALIZING
      │
READY
      │
RUNNING
```

Every runtime follows identical lifecycle.

---

## 13.5 Shutdown Sequence

```
RUNNING
      │
STOPPED
```

Shutdown is terminal during Wave 1.

Restart is not implemented.

---

## 13.6 Failure Sequence

```
RUNNING
      │
FAILED
      │
STOPPED
```

Failure always ends in STOPPED.

---

# 14. Pipeline Constitution — Approved ADR-007

**Status:** APPROVED — ADR-007 O-01–O-05, 2026-10-06.

The exact canonical implementation contract is
[KR-009](../wave1/KR-009_PIPELINE_ORCHESTRATOR.md), compiled before source edits.
It supersedes only prior KR-009 API/import/behavior/test declarations and the
precise Bootstrap caller expression. Other module ownership remains frozen.

| File | Owner / scope |
| --- | --- |
| src/kernel/runtime/pipeline.py | KR-009 immutable models; preserve schema |
| src/kernel/runtime/manifest.py | KR-009 stateless graph validation |
| src/kernel/runtime/executor.py | KR-009 sequential operations/snapshots/events |
| src/kernel/runtime/orchestrator.py | KR-009 registration/bindings/preflight |
| tests/kernel/test_pipeline.py | KR-011 canonical test ownership; active acceptance authorized |
| src/kernel/runtime/bootstrap.py | KR-010; ONLY remove Executor import and use OrchestratorRuntime(event_bus) |

PipelineStage is frozen, keyword-only and slotted: stage_id: str,
module_id: ModuleId, depends_on: tuple[str, ...]. Derived dependency_count: int
and has_dependencies: bool remain. PipelineDefinition is frozen, keyword-only
and slotted: pipeline_id: PipelineId, stages: tuple[PipelineStage, ...].
Derived stage_count: int and is_empty: bool remain. Exactly five exported symbols:
PipelineStage, PipelineDefinition, ManifestRuntime, ExecutorRuntime,
OrchestratorRuntime. Each is exported only by its existing owner file.

ManifestRuntime retains:
validate(definition: PipelineDefinition) -> PipelineDefinition;
validate_stage_ids(definition: PipelineDefinition) -> None;
validate_dependencies(definition: PipelineDefinition) -> None;
validate_dag(definition: PipelineDefinition) -> None.
Orchestrator retains unregister_module(module_id: ModuleId) -> None,
modules() -> tuple[RuntimeModuleManifest, ...], contains(module_id: ModuleId) -> bool,
the two identity properties, async initialize/start/stop/shutdown and sync health.
No new public member or compatibility alias is authorized.

## Canonical Dependencies and Behavior

Orchestrator -> Manifest, Executor; EventBus construction/type annotation only;
Orchestrator and Executor -> stateless MetadataRuntime for detached JSON.
Executor -> EventBus facade and Manifest validation. Manifest -> frozen Pipeline
models/Foundation only. No ContextRuntime/SessionRuntime storage, Container, higher
layer, Publisher/Dispatcher/Subscriber internal or new event factory.
Bootstrap -> OrchestratorRuntime(event_bus), NOT Executor.

Executor is a plain internal class, not RuntimeContract: no health/lifecycle/identity.
Orchestrator is the RuntimeContract participant with name orchestrator, L0_KERNEL,
health OK, no-op initialize/start/stop, idle shutdown clears manifests and bindings.

Registration explicitly accepts operation: Callable[[RuntimeContext], Awaitable[None]]
| None; no callback in serialized models. Per-execution independent binding snapshot.
DAG validation returns the SAME definition; malformed structure -> InvalidManifestError,
cycle -> RuntimeDependencyError, iterative traversal without a stage-count cap.
Preserve stable ready-wave ordering: A, B(dep A), C -> A, C, B.
Reachable module dependencies must exist, be acyclic and point to the same/lower
RuntimeLayer; static dependencies never generate stage edges.
Every stage module/binding and detached context must validate before ANY event/effect.
Pipeline/context UUIDs must agree; supplied trace/UTC times preserved, expiry observational.
JSON copy/validation uses MetadataRuntime; each callback gets its own stage metadata.

Actual operation is awaited once per stage. First failure aborts later callbacks.
Executor alone creates/publishes events through EventBus.create_for_runtime.
Exact seven schemas/priorities and terminal rules are ADR-007 O-03:
pipeline.started; stage started -> awaited work -> stage completed; pipeline.completed.
On ordinary failure stage.failed when allowed then pipeline.failed; cancellation
pipeline.cancelled. Only ONE logical terminal pipeline attempt. Failure delivering
stage.completed does not produce a contradictory stage.failed. Terminal-delivery
failure never creates another terminal. Reasons/logs are safe fixed summaries.
Original exception object is re-raised; ordered secondary notification errors and
earlier explicit cause are retained without grouping the primary inside its own cause.
No KeyboardInterrupt/SystemExit conversion, background task, shield or new status.

Instance busy guards reject re-entry/concurrent execute/mutation with RuntimeStateError
and release in finally. Read-only registry/health remains available.
Canonical acceptance is tests/kernel/test_pipeline.py, 100% executable-line coverage
for all four production files, no exclusions/skips/xfail; Windows/Linux Pyright,
Ruff, discovered full Pytest, smoke and latest-head required CI. Full DI Pipeline
scope cleanup/Session composition/Main partial-startup remains KR-010, not this module.

---

# 15. Testing Constitution

Testing is part of the architecture.

A KR without tests is incomplete.

---

## 15.1 Test Ownership Rule

Each KR owns its tests.

| KR | Test File |
|----|-----------|
| KR-001 | test_types.py |
| KR-002 | test_settings.py |
| KR-003 | test_logger.py |
| KR-004 | test_contracts.py |
| KR-005 | test_container.py |
| KR-006 | test_lifecycle.py |
| KR-007 | test_event_bus.py |
| KR-008 | test_context.py |
| KR-009 | test_pipeline.py |
| KR-010 | test_bootstrap.py |

---

## 15.2 Public API Testing Rule

Tests validate public API only.

Private helpers are tested indirectly.

---

## 15.3 Test Naming Rule

Every test starts with `test_`.

Examples:

```python
def test_container_register():
```

Forbidden:

```python
def container_register():
```

---

## 15.4 Fixture Rule

Shared fixtures belong only in `tests/conftest.py`.

No duplicate fixtures across files.

---

## 15.5 Test Independence Rule

Tests never depend on execution order.

Every test creates fresh runtime objects.

---

## 15.6 Snapshot Rule

Immutable dataclasses compared by equality.

Runtime state compared through public APIs.

---

## 15.7 Integration Rule

Integration tests validate runtime startup.

They never duplicate unit tests.

---

## 15.8 Quality Rule

Skipped tests are forbidden.

Placeholder tests are forbidden.

Empty test files are forbidden.

---

# 16. Ruff Constitution

Repository must remain Ruff-clean.

---

## 16.1 Required Ruff Commands

```bash
uv run ruff check .
uv run ruff format .
```

Both must succeed.

---

## 16.2 Import Ordering Rule

Imports follow isort ordering.

Never manual mixed ordering.

---

## 16.3 __all__ Rule

`__all__` must be alphabetically sorted.

No duplicates.

No wildcard exports.

---

## 16.4 Mutable Default Rule

Ruff B006/B008 violations are forbidden.

Never instantiate dataclasses in default arguments.

Correct:

```python
config: LoggingConfig | None = None
```

Inside function:

```python
config = config or LoggingConfig()
```

---

## 16.5 Cache Rule

Use:

```python
from functools import cache
```

Instead of:

```python
lru_cache(maxsize=None)
```

For immutable caches.

---

## 16.6 Unused Imports Rule

Every import must be used.

Unused imports fail CI.

---

## 16.7 File Formatting Rule

Trailing whitespace forbidden.

Double blank lines follow Ruff formatting.

---

# 17. Pyright Constitution

Target:

```
0 errors
0 warnings
```

Strict mode is mandatory.

---

## 17.1 Unknown Type Rule

Unknown types forbidden.

Always parameterize collections.

---

## 17.2 Dataclass Rule

Field ordering must satisfy Pyright.

Required fields first.

Defaults last.

---

## 17.3 Any Rule

Explicit Any forbidden in public APIs.

Use canonical aliases.

---

## 17.4 Abstract Class Rule

Every ABC contains at least one abstract method.

Marker ABCs are forbidden.

---

## 17.5 Optional Return Rule

Functions returning optional values must declare them explicitly.

Never rely on implicit None.

---

## 17.6 Exhaustive Enum Rule

Pattern matching over enums must be exhaustive.

Default branch required only when future expansion is intentional.

---

# 18. Documentation Constitution

Implementation and documentation must stay synchronized.

---

## 18.1 Every Public API Must Exist In M-03

Missing documentation is a build blocker.

---

## 18.2 Every Production File Must Exist In M-01

No undocumented files.

---

## 18.3 Every Import Must Exist In M-04

Undocumented imports are forbidden.

---

## 18.4 Every Runtime Must Exist In M-05

No hidden runtimes.

---

## 18.5 Every File Must Match M-06

M-06 is the implementation contract.

Generated code must conform exactly.

---

**END OF M-07 PART 3**

---

# 19. Code Generation Constitution

This section defines mandatory rules for every Codex generation.

Codex is an implementation engine, not an architect.

It must generate code strictly from the Engineering Bible.

---

## 19.1 No Architecture Invention Rule

Codex may never invent:

- new runtime layers;
- new folders;
- new files;
- new public APIs;
- new enums;
- new lifecycle states;
- new event phases;
- new DI scopes.

Everything must already exist in M-01…M-06.

If documentation is missing, generation stops.

---

## 19.2 File Scope Rule

One implementation step = one KR.

Codex may only modify files belonging to the active KR.

Example:

Active KR-005.

Allowed:

- src/kernel/runtime/container.py
- src/kernel/runtime/provider.py
- src/kernel/runtime/resolver.py
- src/kernel/runtime/registry.py
- src/kernel/runtime/scope.py

Forbidden:

- logger.py
- lifecycle.py
- bootstrap.py

---

## 19.3 Full File Output Rule

Codex always returns complete files.

Never diffs.

Never patches.

Never "replace this function".

Every modified file is emitted completely.

---

## 19.4 Existing File Preservation Rule

If a file is outside active KR:

- do not modify;
- do not reformat;
- do not reorder imports;
- do not rename symbols.

---

## 19.5 Dependency Check Rule

Before generating a file Codex validates:

1. file exists in M-01;
2. imports allowed in M-04;
3. public API matches M-03;
4. owner KR matches M-06.

Failure stops generation.

---

## 19.6 Generation Order Rule

Wave 1 generation order is frozen.

KR-001

↓

KR-002

↓

KR-003

↓

KR-004

↓

KR-005

↓

KR-006

↓

KR-007

↓

KR-008

↓

KR-009

↓

KR-010

↓

KR-011

No skipping.

---

# 20. Codex Self-Validation Protocol

Codex performs mandatory validation before finishing generation.

No user interaction required.

---

## Stage 1 — Architecture Validation

Checklist:

- File belongs to active KR.
- Imports follow M-04.
- Public exports follow M-03.
- Runtime ownership preserved.

Failure aborts generation.

---

## Stage 2 — Typing Validation

Checklist:

- No Any.
- No Unknown.
- Typed collections only.
- Dataclass ordering valid.
- ABC contains abstract methods.

Target:

```
uv run pyright

0 errors
0 warnings
```

---

## Stage 3 — Ruff Validation

Checklist:

- import ordering;
- __all__ sorted;
- no mutable defaults;
- no unused imports;
- no formatting violations.

Target:

```
uv run ruff check .

All checks passed.
```

---

## Stage 4 — Runtime Validation

Checklist:

- startup sequence valid;
- shutdown sequence valid;
- DI ownership valid;
- EventBus ownership valid;
- Context ownership valid.

---

## Stage 5 — Test Validation

Checklist:

- tests created;
- fixtures valid;
- no skipped tests;
- integration test exists.

Target:

```
uv run pytest

All tests passed.
```

---

## Stage 6 — Completion Validation

Definition of Done checklist executed.

Only GREEN if every check passes.

---

# 21. Anti-Pattern Registry

These patterns are forbidden repository-wide.

---

## AP-001 Mutable Globals

Forbidden:

```python
SERVICES = {}
EVENTS = []
LOGGER = logging.getLogger()
```

Allowed only immutable constants.

---

## AP-002 Global Singleton Runtime

Forbidden:

```python
container = ContainerRuntime()
```

outside BootstrapRuntime.

---

## AP-003 Wildcard Imports

Forbidden:

```python
from module import *
```

---

## AP-004 Relative Imports

Forbidden:

```python
from ..runtime.container import ContainerRuntime
```

Absolute imports only.

---

## AP-005 Public Any

Forbidden:

```python
payload: dict[str, Any]
```

Use Payload.

---

## AP-006 Dataclass Mutable Defaults

Forbidden:

```python
metadata = {}
payload = []
```

Use default_factory.

---

## AP-007 Untyped Collections

Forbidden:

```python
list
dict
tuple
```

Always parameterized.

---

## AP-008 Business Logic In Kernel Runtime

Forbidden inside KR-001…KR-010:

- HTTP clients.
- Database.
- Filesystem writes.
- AI models.
- Network requests.

Kernel Runtime is infrastructure only.

---

## AP-009 Silent Exception Swallowing

Forbidden:

```python
except Exception:
    pass
```

Always wrap or re-raise.

---

## AP-010 Circular Dependency Resolution Hacks

Forbidden:

- imports inside methods to avoid cycles;
- runtime monkey-patching;
- late attribute injection.

Fix dependency graph instead.

---

# 22. Preflight / Build Protocol

Every Wave build starts with Preflight.

---

## Step 1

Read AGENTS.md completely.

---

## Step 2

Read active Wave handoff.

---

## Step 3

Read Architecture Bible documents.

Minimum required:

- AB-00
- M-01
- M-03
- M-04
- M-05
- M-06
- M-07

---

## Step 4

Repository Audit

Validate:

- ownership;
- imports;
- runtime graph;
- missing files.

---

## Step 5

Produce Preflight Report.

No code generation.

---

## Preflight Output

Must include:

- repository state;
- KR ownership audit;
- dependency audit;
- typing audit;
- Ruff audit;
- Pyright audit;
- testing audit;
- blockers.

Exactly once.

---

# 23. Postflight / Validation Protocol

Every implementation ends with Postflight.

---

## Validation Commands

Run in order.

### Ruff

```bash
uv run ruff check .
```

### Formatter

```bash
uv run ruff format .
```

### Pyright

```bash
uv run pyright
```

### Tests

```bash
uv run pytest
```

---

## Postflight Report

Must contain:

### Files Modified

Complete list.

### Validation Results

- Ruff
- Pyright
- Pytest

### Remaining Blockers

List only unresolved issues outside active KR.

### Definition of Done

GREEN or BLOCKED.

No prose outside report format.

---

# 24. Global Definition of Done

AURORA Wave 1 is complete only if every invariant below is satisfied.

---

## Architecture

- All production files exist exactly as defined in M-01.
- Directory structure matches M-02.
- Imports match M-04.
- Public APIs match M-03.
- Runtime ownership matches M-05.
- File implementations match M-06.
- Implementation rules match M-07.

---

## Static Validation

Repository passes:

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```

Results:

- 0 Ruff errors.
- 0 Pyright errors.
- 0 warnings.

---

## Dynamic Validation

Repository passes:

```bash
uv run pytest
```

Requirements:

- tests collected;
- all tests passed;
- zero skipped;
- zero xfailed.

---

## Runtime Validation

Runtime successfully executes canonical lifecycle.

1. Bootstrap
2. Initialize
3. Ready
4. Running
5. Pipeline execution
6. Graceful Stop
7. Shutdown

---

## Documentation Validation

No undocumented production API exists.

No undocumented runtime exists.

No undocumented import exists.

---

## Build Validation

Codex Postflight returns GREEN.

Repository is implementation-ready.

---

## Approved KR-008 reconciliation

The exact APPROVED [KR-008 contract](../wave1/KR-008_PIPELINE_CONTEXT.md), compiled
from AB-00B/D, ADR-004 P-04 and explicitly approved ADR-006 C-01–C-04, governs
this KR-008 section. Its full signatures and acceptance matrix are canonical.

| File | Sole export | Owner / project dependencies |
| --- | --- | --- |
| src/kernel/runtime/context.py | ContextRuntime | KR-008 active context; Foundation, contracts.context/runtime, MetadataRuntime |
| src/kernel/runtime/metadata.py | MetadataRuntime | KR-008 stateless JSON; Foundation only |
| src/kernel/runtime/session.py | SessionRuntime | KR-008 session registry; Foundation, contracts.context, ContextRuntime, MetadataRuntime |

Session → Context → Metadata, plus Session → Metadata, is the approved internal
DAG (ADR-006 C-01). Context never imports Session; no reverse/upward import,
shared abstraction, DI, event dispatch, pipeline work, network or persistence.
Existing constructors and three classes remain. RuntimeContext/TraceContext
fields and all core/lifecycle/event/DI vocabularies are unchanged.

Context implements the exact AB-00D RuntimeContract, with create/current/replace/
clear/has_context and health. create/replace/current validate and return detached
snapshots; active storage is private and separately detached. Missing context
uses RuntimeStateError. Lifecycle initialize/start/stop remain no-op; shutdown
clears active context only; no new shutdown/expiry state policy.

Metadata merge/put/remove/contains/get keep the exact existing signatures.
Validate and recursively detach JSON, including both merge inputs and final put
nesting; shallow key updates and deterministic insertion order, no recursive
merge. get validates/copies a default only if it is actually returned.
String keys/Unicode, finite numbers, cycles/non-JSON objects and the 256-container
depth boundary are checked; repeated acyclic references are detached. Invalid
metadata/context/session fields use existing ContractValidationError with safe
messages, not new/nonexistent exceptions or data dumps.

Session create/get/update_metadata/remove/contains/list keep their signatures.
list returns tuple[SessionId, ...] in insertion order, never contexts; there is
no Session.clear. Same-ID create atomically replaces the entry without reordering,
using the existing UUIDv4 PipelineId/L0_KERNEL. Separate session/active/returned
snapshots; failure changes neither owner. Update/remove affect active context only
on matching session_id. Missing get/update/remove uses RuntimeStateError.
Context.clear/shutdown do not delete an independent Session registry.

Supplied TraceContext is preserved, not generated; existing derived root/depth
properties only. IDs remain UUID-backed; RuntimeLayer is an actual enum member;
timestamps use aware UTC. Expiration is observational, with no hidden TTL,
automatic eviction, timestamp-order rule or trace-generation owner invention.
Frozen dataclass shells do not freeze nested JSON; value equality not identity.

Superseded KR-008 obligations only: opposite Context-to-Session DAG/prohibition,
context-valued list()/Session.clear, set/get context facade, shallow/deep-frozen/
identity guarantees, UUIDv7 trace/root generation and incompatible stored fields,
nonexistent MetadataValidationError/SessionNotFoundError/ContextNotAvailableError.
No unrelated module obligation is changed.

Canonical acceptance: tests/kernel/test_context.py (KR-011 ownership; ADR-004/006
explicitly allow active-module changes). All APIs/exports, malformed fields/JSON,
256/257/extreme depth, nested ingress/egress/session isolation, atomic errors,
shallow order/defaults, same-ID create and matching/nonmatching active lifetimes;
at least 95% executable lines per owned file, no acceptance skips/xfail.
Strict Pyright Windows/Linux, Ruff, collected Pytest, AST DAG/schema/factory
boundaries, Kernel smoke and required latest-head CI. One module/report/review gate.

---

# Canonical Completion Marker

Document ID: M-07

Document Name: Implementation Rules

Version: 1.1 Canonical

Status: COMPLETE

Authority: AURORA Engineering Bible v1.1

END OF DOCUMENT
