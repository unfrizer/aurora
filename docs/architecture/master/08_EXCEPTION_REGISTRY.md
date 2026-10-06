# AURORA MASTER HANDOFF v1.0

## Approved KR-010 Error Mapping — ADR-008

**Status:** APPROVED — ADR-008 B-01–B-05, 2026-10-06.
Exact contract: [KR-010](../wave1/KR-010_RUNNER_BOOTSTRAP.md).
Authority: [ADR-008](../ADR-008_KR010_Bootstrap_Reconciliation_Proposal_v1.0.md).

No Foundation exception class changes; use existing exceptions only.

| Boundary | Existing behavior |
| --- | --- |
| Bootstrap configuration | ConfigurationError propagates unchanged |
| Other ordinary construction failure | RuntimeInitializationError with original cause/safe message |
| Invalid Kernel Pipeline object/UUID ID | InvalidManifestError before scope cleanup |
| Kernel execution not RUNNING or busy mutation | RuntimeStateError, no side effect/disposal |
| Invalid Kernel Session UUID ID | ContractValidationError before removal |
| Missing Session | existing Session RuntimeStateError before DI action |
| Lifecycle/DI work or teardown failure | original existing exception/cause, no new wrapper vocabulary |
| Secondary cleanup error/cancellation | ordered ExceptionGroup/BaseExceptionGroup cause, prior explicit cause preserved |
| Main failure | first original error propagates after independent stop/shutdown attempts |

Cleanup-only error/cancellation propagates unchanged; primary CancelledError remains
that same cancellation, not success. SystemExit/KeyboardInterrupt are not converted.
No PipelineExecutionError/DirectoryValidationError or raw payload/secret log. Partial
startup cleanup delegates only existing legal FAILED transition; not recovery.
This is limited KR-010 precedence; other modules' error mapping stays unchanged.

## Scoped KR-009 Reconciliation — ADR-007, APPROVED 2026-10-06

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


This scoped canonical reconciliation takes precedence over any retained historical
KR-009 example/summary elsewhere in this document. In particular Executor health,
lifecycle/shutdown participation, private-only _execution_order, ContextRuntime
storage access, invented PipelineCycleError/PipelineExecutionError, continuation
after failure, mandatory queue/DI resolution and noncanonical tests/runtime paths
are NOT implementation authority. Non-KR-009 declarations are unaffected.

**Document ID:** M-08

**Document Name:** Exception Registry

**File:** `docs/architecture/master/08_EXCEPTION_REGISTRY.md`

**Status:** CANONICAL EXCEPTION REGISTRY

**Authority:** AB-00A + Wave1 Implementation Handoff

---

# Purpose

This document defines the complete exception hierarchy for AURORA Wave 1.

It specifies:

- every exception class;
- owning module;
- when it is raised;
- who catches it;
- propagation rules;
- logging policy.

No new exception may be introduced without updating this registry.

---

# Exception Hierarchy

AuroraError
├── ConfigurationError
│   ├── MissingConfigurationError
│   └── InvalidConfigurationError
│
├── ValidationError
│   ├── ContractValidationError
│   └── StateValidationError
│
├── ManifestError
│   ├── InvalidManifestError
│   └── RuntimeDependencyError
│
├── ContainerError
│   ├── ServiceRegistrationError
│   ├── ServiceResolutionError
│   └── CircularDependencyError
│
├── ScopeViolationError
│
├── EventBusError
│   ├── EventValidationError
│   ├── InvalidEventError
│   ├── EventPublishError
│   └── EventHandlerError
│
└── RuntimeError
    ├── RuntimeInitializationError
    ├── RuntimeShutdownError
    └── RuntimeStateError

---

# Root Exception

## AuroraError

### Owner

`src/core/exceptions.py`

### Purpose

Root exception for the entire repository.

### Rules

- Every custom exception inherits from AuroraError.
- Never raise AuroraError directly.
- Never catch `Exception` when AuroraError is sufficient.

---

# Configuration Exceptions

## ConfigurationError

Raised when configuration subsystem fails.

Caught by:

- bootstrap.py
- runtime.py

Logs:

ERROR

Terminates Runtime startup.

---

## MissingConfigurationError

Raised when required ENV variable is absent.

Examples

- OPENROUTER_API_KEY missing.
- APP_ENV missing.

Caught by:

Configuration loader.

Propagated to Bootstrap.

---

## InvalidConfigurationError

Raised when ENV value is invalid.

Examples

- Invalid log level.
- Invalid timezone.
- Invalid directory path.

---

# Validation Exceptions

## ValidationError

Base validation failure.

Used by:

- Manifest validation.
- Runtime validation.
- Pipeline validation.

---

## ContractValidationError

Raised when a contract implementation violates KR-004.

Examples

- RuntimeModule missing manifest field.
- Invalid ServiceDescriptor.

---

## StateValidationError

Raised when lifecycle transition is illegal.

Examples

- CREATED → RUNNING.
- STOPPED → RUNNING.

---

# Manifest Exceptions

## ManifestError

Base manifest failure.

Used during module registration.

---

## InvalidManifestError

Raised when manifest schema is invalid.

Examples

- Missing `provides`.
- Missing `module_id`.
- Invalid runtime layer.

---

## RuntimeDependencyError

Raised when dependency graph is invalid.

Examples

- Unknown dependency.
- Dependency cycle.
- Duplicate module.

---

# Container Exceptions

## ContainerError

Base DI failure.

---

## ServiceRegistrationError

Raised during service registration.

Examples

- Duplicate ServiceId.
- Invalid scope.

---

## ServiceResolutionError

Raised when service cannot be resolved.

Examples

- Missing provider.
- Missing dependency.

---

## CircularDependencyError

Raised when resolver detects a cycle.

Examples

A → B → C → A

Implementation must stop immediately.

---

## ScopeViolationError

Raised when scope visibility is violated.

Examples

Application depends on Pipeline.

Session resolves Transient after disposal.

---

# Event Bus Exceptions

Canonical KR-007 mapping: explicitly APPROVED ADR-005 E-03 supersedes conflicting
legacy M-03/M-06 entries. Foundation classes remain unchanged. Do not introduce
EventDispatchError, DuplicateSubscriberError or UnknownSubscriberError.

## EventBusError

Base Event Bus failure.

---

## InvalidEventError

Existing Foundation class retained, but not required by reconciled KR-007.
Invalid event fields/data now use EventValidationError before any handler effect.

## EventValidationError

Existing Foundation class used for invalid mandatory event fields, trace/IDs,
priority, UTC timestamp or JSON. Reject cycles, invalid keys/Unicode/non-finite
floats/non-JSON objects and depth over 256 containers without coercion or payload
disclosure. No contract dataclass constructor becomes a hidden validator.

---

## EventPublishError

Existing Foundation class retained; reconciled KR-007 adds no stopped-bus policy
or artificial use of this exception. No lifecycle state ownership moves here.

---

## EventHandlerError

KR-007 raises this existing class for duplicate registration or missing
unsubscription (without registry mutation) and ordinary handler Exception.

Rules

An ordinary handler failure aborts remaining handlers/events; its original
exception is preserved as cause. Only safe handler identity is included, not
event data/secrets. Cancellation and other BaseException propagate unchanged.

---

# Runtime Exceptions

## RuntimeError

Base runtime execution failure.

---

## RuntimeInitializationError

Raised during startup.

Examples

Container failed.

Logger failed.

Configuration failed.

Lifecycle initialization failed.

Startup stops immediately.

---

## RuntimeShutdownError

Raised during graceful shutdown.

Examples

Module stop failure.

Resource cleanup failure.

Shutdown continues collecting failures.

---

## RuntimeStateError

Raised when runtime state machine is violated.

Examples

Execute pipeline before RUNNING.

Shutdown before INITIALIZED.

---

# Exception Ownership Matrix

| Exception Group | Owner Runtime |
|-----------------|---------------|
| Configuration | KR-002 |
| Validation | KR-001 |
| Manifest | KR-004 |
| Container | KR-005 |
| Scope | KR-005 |
| Event Bus | KR-007 |
| Runtime | KR-006 / KR-010 |

No exception is owned by multiple runtimes.

---

# Logging Policy

| Exception | Log Level |
|-----------|-----------|
| MissingConfigurationError | ERROR |
| InvalidConfigurationError | ERROR |
| ContractValidationError | ERROR |
| RuntimeDependencyError | ERROR |
| CircularDependencyError | ERROR |
| EventPublishError | ERROR |
| EventHandlerError | ERROR |
| RuntimeInitializationError | CRITICAL |
| RuntimeShutdownError | WARNING |
| RuntimeStateError | ERROR |

Exceptions are logged exactly once.

---

# Catching Rules

## Allowed

```python
except AuroraError:
```

```python
except ConfigurationError:
```

```python
except ContainerError:
```

## Forbidden

```python
except Exception:
```

unless re-raising AuroraError.

Never swallow exceptions silently.

---

# Propagation Rules

Configuration

Settings

↓

Bootstrap

↓

RuntimeInitializationError

Container

Resolver

↓

ServiceResolutionError

↓

RuntimeInitializationError

Event Bus

Handler

↓

EventHandlerError

↓

EventPublishError (optional propagation)

Pipeline

Stage

↓

AuroraError

↓

pipeline.failed event

↓

Runtime continues according to DAG policy.

---

# Exception Serialization Rules

Every AuroraError must expose:

- error_code
- message
- module_id (optional)
- details (JSON serializable)

Forbidden fields:

- traceback object
- logger
- file handle
- runtime object

---

# Validation Requirements

Pyright

- No bare Exception subclasses.
- No unknown exception types.

Ruff

- No empty except blocks.
- No broad exception catches.

Pytest

Required tests:

- configuration errors
- container errors
- circular dependency
- invalid manifest
- invalid event
- runtime initialization failure
- lifecycle state validation

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

# Definition of Done

Exception Registry is complete only if:

- every exception exists exactly once;
- every runtime owns only its exceptions;
- propagation follows this document;
- logging follows this document;
- serialization is JSON-compatible.
