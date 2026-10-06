# AURORA MASTER HANDOFF v1.0

**Document ID:** M-09

**Document Name:** Test Matrix

**File:** `docs/architecture/master/09_TEST_MATRIX.md`

**Status:** CANONICAL TEST SPECIFICATION

**Authority:** AB-00A + Wave1 Implementation Handoff

---

# Purpose

This document defines the complete Wave 1 testing specification.

It specifies:

- every required test file;
- every test case;
- edge cases;
- validation order;
- coverage requirements;
- CI quality gates.

Tests are part of the architecture and **must exist** before Wave 1 is considered complete.

---

# Test Philosophy

Wave 1 tests validate the Kernel Runtime.

Tests are divided into three groups:

1. Foundation.
2. Kernel Runtime.
3. Runtime Execution.

Every public API defined in M-03 must have executable tests.

---

# Test Directory Structure

tests/
├── core/
│   ├── test_types.py
│   ├── test_settings.py
│   └── test_logger.py
│
├── kernel/
│   ├── test_contracts.py
│   ├── test_container.py
│   ├── test_registry.py
│   ├── test_scope.py
│   ├── test_resolver.py
│   ├── test_lifecycle.py
│   └── test_event_bus.py
│
└── runtime/
    ├── test_context.py
    ├── test_pipeline.py
    ├── test_executor.py
    ├── test_bootstrap.py
    └── test_runtime.py

---

# KR-001 Tests

## tests/core/test_types.py

### Purpose

Validate canonical Foundation types.

### Required Cases

- RuntimeLayer contains L0–L8 only.
- DIScope contains exactly four scopes.
- RuntimeStatus vocabulary unchanged.
- EventPriority vocabulary unchanged.
- EventPhase vocabulary unchanged.
- Metadata is JSON-compatible.
- Payload accepts nested JSON objects.

### Edge Cases

- Invalid RuntimeLayer creation.
- Invalid enum lookup.
- Nested JSON payload.

### Coverage

100% public symbols.

---

# KR-002 Tests

## tests/core/test_settings.py

### Required Cases

- Load .env successfully.
- Missing environment variable raises MissingConfigurationError.
- Invalid APP_ENV raises InvalidConfigurationError.
- Invalid LOG_LEVEL rejected.
- Path validation succeeds.
- reload_settings returns new immutable object.

### Edge Cases

- Empty .env.
- Invalid timezone.
- Unknown environment profile.

Coverage target:

100%.

---

# KR-003 Tests

## tests/core/test_logger.py

### Required Cases

- Logger factory returns Logger.
- Logger name preserved.
- JSON formatter enabled.
- Console formatter enabled.
- Correlation ID injected.
- Trace ID injected.
- Session ID injected.

### Edge Cases

- Multiple calls return cached logger.
- Unknown logger name.
- Missing context values.

Coverage target:

100%.

---

# KR-004 Tests

## tests/kernel/test_contracts.py

### RuntimeContract

- ABC cannot instantiate.
- Required methods exist.

### RuntimeModuleManifest

- module_id required.
- runtime_layer required.
- depends_on immutable.
- provides immutable.
- version required.

### RuntimeContext

- frozen dataclass.
- AB-00D fields, UTC timestamps and independent metadata default factories.
- ADR-004: frozen shell, not deeply immutable JSON; runtime-boundary detached
  snapshots are tested in KR-008, not direct dataclass construction.

### RuntimeEvent

- required field order valid.
- AB-00C priority/default and independent payload default factories.
- ADR-004: detached publication/per-handler payload snapshots belong to KR-007;
  direct event dataclasses do not implement dispatch, copying or validation.
- trace immutable.

### ServiceContract / ServiceDescriptor — ADR-004

- Exactly async initialize/shutdown abstract methods, no universal execute.
- Exactly service_id, scope, implementation, eager, dependencies fields.
- implementation is type[ServiceContract]; dependencies is
  tuple[tuple[str, ServiceId], ...], default ().
- Old no-dependency construction preserved; eager defaults False.
- Frozen/slotted/keyword-only descriptor; immutable explicit binding tuples.
- Different constructor parameters may bind the same ServiceId.
- Descriptor construction does not construct, initialize or resolve a service.
- Shape/graph/scope rejection and initialization timing belong to KR-005 tests.

### LifecycleState

- default state valid.

Coverage target:

100%.

---

# KR-005 Tests

ADR-004 explicitly authorizes `tests/kernel/test_container.py` adjustments while
its owner remains KR-011. APPROVED `../wave1/KR-005_DI.md` supplies the reconciled
acceptance matrix: async readiness/injection, complete graph preflight, all 16
scope edges, identities, rollback/retry, transient descendant release, consumer
guards, reverse cleanup and multiple errors, cancellation/resumable ownership,
same-ID replacement, and re-entrancy rejection. Legacy sync-only examples below
are superseded for KR-005. Do not create or modify other test files in this task.


## tests/kernel/test_registry.py

### Registry Cases

- Register descriptor.
- Lookup descriptor.
- Duplicate registration raises ServiceRegistrationError.
- Remove descriptor.

---

## tests/kernel/test_scope.py

### Scope Cases

- Application scope lifetime.
- Session scope lifetime.
- Pipeline scope lifetime.
- Transient scope lifetime.

### Edge Cases

- Access disposed scope.
- Nested pipeline scope.
- Session disposal clears pipeline scope.

---

## tests/kernel/test_resolver.py

### Resolver Cases

- Resolve singleton.
- Resolve transient.
- Resolve nested dependencies.
- Resolve pipeline dependency.

### Edge Cases

- Missing dependency.
- Circular dependency.
- Invalid scope dependency.

---

## tests/kernel/test_container.py

### Container Cases

- Register provider.
- Resolve provider.
- has(service_id)
- remove(service_id)
- shutdown()

### Edge Cases

- Duplicate service.
- Unknown service.
- Shutdown disposes services.
- Eager initialization.

Coverage target:

100%.

---

# KR-006 Tests

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

## tests/kernel/test_lifecycle.py

### State Machine

- CREATED → INITIALIZING
- INITIALIZING → READY
- READY → RUNNING
- RUNNING → STOPPED
- RUNNING → FAILED

### Invalid Transitions

- CREATED → RUNNING
- READY → CREATED
- STOPPED → RUNNING

### Hooks

- BEFORE_INITIALIZE
- AFTER_INITIALIZE
- BEFORE_START
- AFTER_START
- BEFORE_STOP
- AFTER_STOP

Coverage target:

100%.

---

# KR-007 Tests

**Authority:** APPROVED ADR-005 E-01–E-04, ADR-004 P-04 and AB-00C/D (2026-10-06).
The exact signatures and acceptance contract are `../wave1/KR-007_EVENT_BUS.md`.
Only KR-007 entries are reconciled; other module contracts remain unchanged.

## tests/kernel/test_event_bus.py

Owner KR-011, authorized contract-required adjustments with active KR-007.

- Every facade/internal method and constructor/export boundary, exact async APIs.
- All five event priorities (CRITICAL/HIGH/NORMAL/LOW/BACKGROUND), stable FIFO and
  sequential insertion-ordered handlers; priority is on events, not handlers.
- Invalid mandatory fields, trace/IDs, priority, UTC timestamp and dict-root JSON.
- Non-string keys, non-finite floats, invalid Unicode, cycles/non-JSON values;
  repeated acyclic references; depth 256 accepted, 257 rejected without RecursionError.
- Detached caller/create/publication/per-handler/batch data, preserved logical
  identity fields and validation before any handler side effect.
- Duplicate/missing registration errors with unchanged registry; tuple snapshots,
  mutations affecting later/nested events, independent bus instances.
- Nested inline publication, empty batch/no handlers, first ordinary handler error
  abort with EventHandlerError/original cause, cancellation/BaseException propagation.
- Runtime identity/health/lifecycle cleanup and cleared handler references.

Use Publisher/facade for new logical events; contract-only direct construction stays
in contract tests. No sync wrappers, obsolete method aliases or ignored duplicates.
Executable-line coverage target: 100%; report actual measured coverage/gaps.
Ruff, strict Pyright, discovered full Pytest, Kernel smoke and latest-head CI required.

# KR-008 Tests

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

# KR-009 Tests

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

# KR-010 Tests

## tests/runtime/test_bootstrap.py

### Startup

- Settings loaded.
- Logger initialized.
- Container built.
- EventBus created.
- Lifecycle initialized.

### Shutdown

- Reverse shutdown order.
- Resource cleanup.
- EventBus disposed.

Coverage target:

100%.

---

## tests/runtime/test_runtime.py

### Runtime

- boot()
- shutdown()
- execute_pipeline()

### Health

- Healthy runtime.
- Failed runtime.
- Runtime restart forbidden.

Coverage target:

100%.

---

# Integration Matrix

| Runtime Component | Test File |
|-------------------|-----------|
| Foundation Types | test_types.py |
| Configuration | test_settings.py |
| Logger | test_logger.py |
| Contracts | test_contracts.py |
| Registry | test_registry.py |
| Resolver | test_resolver.py |
| Container | test_container.py |
| Lifecycle | test_lifecycle.py |
| Event Bus | test_event_bus.py |
| Context | test_context.py |
| Pipeline | test_pipeline.py |
| Executor | test_executor.py |
| Bootstrap | test_bootstrap.py |
| Runtime | test_runtime.py |

---

# Validation Order

After each KR implementation:

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

If any command fails:

STOP implementation.

Do not continue to the next KR.

---

# CI Quality Gates

## Ruff

- Zero violations.
- Import graph valid.
- Formatting valid.

## Pyright

- Zero errors.
- Zero warnings.
- Strict typing.

## Pytest

- No skipped Wave 1 tests.
- No xfail.
- No collected 0 items.

---

# Coverage Targets

| Runtime | Minimum Coverage |
|----------|-----------------:|
| KR-001 | 100% |
| KR-002 | 100% |
| KR-003 | 100% |
| KR-004 | 100% |
| KR-005 | 95% |
| KR-006 | 95% |
| KR-007 | 95% |
| KR-008 | 95% |
| KR-009 | 95% |
| KR-010 | 95% |

Overall Wave 1 coverage target:

**≥97% public API coverage**

---

# Definition of Done

Wave 1 testing is complete only if:

- every required test file exists;
- every public API has executable tests;
- Ruff passes;
- Pyright passes;
- Pytest executes non-empty test suite;
- Kernel Runtime boots successfully through `main.py`.
