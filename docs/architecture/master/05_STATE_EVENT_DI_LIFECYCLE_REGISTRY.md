<!-- ========================================================================= -->
<!-- AURORA ENGINEERING BIBLE -->
<!-- DOCUMENT M-05 — STATE / EVENT / DI / LIFECYCLE REGISTRY -->
<!-- FILE: 05_STATE_EVENT_DI_LIFECYCLE_REGISTRY.md -->
<!-- VERSION 1.1 CANONICAL -->
<!-- ========================================================================= -->

# M-05 — State / Event / Dependency Injection / Lifecycle Registry

**Document ID**

M-05

**Canonical File**

`docs/architecture/master/05_STATE_EVENT_DI_LIFECYCLE_REGISTRY.md`

**Version**

1.1 Canonical

**Status**

CANONICAL SOURCE OF TRUTH

**Runtime Layer**

L0 Runtime Kernel

**Owner**

AURORA Architecture Board

---

# Purpose

This document is the canonical registry for every runtime state, lifecycle state,
dependency injection lifecycle, runtime event, event payload, transition rule and
ownership rule used by Wave 1.

This document defines the runtime vocabulary used by every kernel subsystem.

No runtime implementation may invent additional states, lifecycle transitions,
dependency injection scopes or runtime events outside this registry.

Everything listed here is immutable unless a future Architecture Decision Record
changes the registry version.

---

# Authority

This registry is the source of truth for:

- RuntimeStatus.
- LifecycleState.
- HealthStatus.
- Dependency Injection lifecycle.
- RuntimeContext lifecycle.
- Session lifecycle.
- Pipeline lifecycle.
- RuntimeEvent catalog.
- Event payload schemas.
- Event ordering.
- Event propagation.
- Runtime transition matrix.

The following documents must reference this registry without redefining values:

- M-06 Module Specifications.
- M-07 Implementation Rules.
- M-08 Exception Registry.
- M-09 Test Matrix.
- M-10 Build Checklist.
- M-11 Codex Master Prompt.

---

# Registry Scope

The registry covers six independent runtime domains.

| Registry Domain | Owner Runtime |
|-----------------|---------------|
| Runtime State Registry | Lifecycle Runtime |
| Lifecycle Registry | Lifecycle Runtime |
| Dependency Injection Registry | Container Runtime |
| Runtime Context Registry | Context Runtime |
| Pipeline Execution Registry | Executor Runtime |
| Runtime Event Registry | EventBus Runtime |

Business events are explicitly outside the scope of this document.

---

# Canonical Registry Principles

## REGISTRY-001 — Registry Is Exhaustive

If a runtime state or runtime event is not defined inside this document,
it does not exist.

Implementations must never create undocumented runtime events.

---

## REGISTRY-002 — Ownership Is Unique

Every runtime state has exactly one owner runtime.

Every runtime event has exactly one producer runtime.

Ownership never overlaps.

---

## REGISTRY-003 — Events Are Immutable

Runtime events are immutable value objects.

After creation the following fields may never change:

- event_id
- event_type
- timestamp
- session_id
- trace
- payload
- headers

Mutation is forbidden.

---

## REGISTRY-004 — State Produces Events

Every observable runtime state transition emits exactly one canonical RuntimeEvent.

Silent state transitions are forbidden.

---

## REGISTRY-005 — Runtime Isolation

A runtime may mutate only its own state.

Cross-runtime communication happens exclusively through EventBusRuntime.

Direct state mutation across runtimes is forbidden.

---

# Runtime State Registry

## Ownership

**Owner Runtime**

Lifecycle Runtime

**Source Module**

`src/core/types.py`

**Mutable Runtime**

StateRuntime

**Readable By**

Entire Runtime Kernel

---

# RuntimeStatus Enumeration

RuntimeStatus describes the global lifecycle of RuntimeKernel.

<table columnSizing="equal">
  <table-row>
    <table-cell>**RuntimeStatus**</table-cell>
    <table-cell>**Description**</table-cell>
  </table-row>
  <table-row>
    <table-cell>CREATED</table-cell>
    <table-cell>Runtime object constructed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>INITIALIZING</table-cell>
    <table-cell>Dependencies are being initialized.</table-cell>
  </table-row>
  <table-row>
    <table-cell>READY</table-cell>
    <table-cell>Initialization completed successfully.</table-cell>
  </table-row>
  <table-row>
    <table-cell>STARTING</table-cell>
    <table-cell>Startup lifecycle executing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>RUNNING</table-cell>
    <table-cell>Runtime accepts pipeline execution.</table-cell>
  </table-row>
  <table-row>
    <table-cell>STOPPING</table-cell>
    <table-cell>Graceful shutdown started.</table-cell>
  </table-row>
  <table-row>
    <table-cell>STOPPED</table-cell>
    <table-cell>Execution stopped.</table-cell>
  </table-row>
  <table-row>
    <table-cell>SHUTTING_DOWN</table-cell>
    <table-cell>Resources are being released.</table-cell>
  </table-row>
  <table-row>
    <table-cell>TERMINATED</table-cell>
    <table-cell>Runtime destroyed successfully.</table-cell>
  </table-row>
  <table-row>
    <table-cell>FAILED</table-cell>
    <table-cell>Runtime entered unrecoverable failure state.</table-cell>
  </table-row>
</table>

This enumeration is exhaustive.

---

# RuntimeStatus Ownership Rules

<table columnSizing="equal">
  <table-row>
    <table-cell>**Operation**</table-cell>
    <table-cell>**Owner**</table-cell>
  </table-row>
  <table-row>
    <table-cell>Create RuntimeStatus</table-cell>
    <table-cell>StateRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Mutate RuntimeStatus</table-cell>
    <table-cell>StateRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Read RuntimeStatus</table-cell>
    <table-cell>RuntimeKernel / all public facades</table-cell>
  </table-row>
  <table-row>
    <table-cell>Publish transition event</table-cell>
    <table-cell>LifecycleRuntime</table-cell>
  </table-row>
</table>

No other runtime may mutate RuntimeStatus.

---

# Forbidden RuntimeStatus Mutations

The following modules may never change RuntimeStatus:

- RuntimeKernel
- BootstrapRuntime
- ContainerRuntime
- EventBusRuntime
- ContextRuntime
- ExecutorRuntime
- OrchestratorRuntime
- PublisherRuntime
- DispatcherRuntime
- SessionRuntime
- MetadataRuntime

Attempting to mutate RuntimeStatus outside StateRuntime is an Architecture Conflict.

---

# Runtime Lifecycle State Registry

## Owner Runtime

Lifecycle Runtime

## Source Module

`src/kernel/contracts/lifecycle.py`

---

# LifecycleState Schema

LifecycleState is an immutable snapshot.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row>
    <table-cell>status</table-cell>
    <table-cell>RuntimeStatus</table-cell>
  </table-row>
  <table-row>
    <table-cell>started_at</table-cell>
    <table-cell>datetime \| None</table-cell>
  </table-row>
  <table-row>
    <table-cell>stopped_at</table-cell>
    <table-cell>datetime \| None</table-cell>
  </table-row>
  <table-row>
    <table-cell>uptime_seconds</table-cell>
    <table-cell>float</table-cell>
  </table-row>
  <table-row>
    <table-cell>failure_reason</table-cell>
    <table-cell>str \| None</table-cell>
  </table-row>
</table>

Field set is immutable.

---

# Lifecycle Snapshot Rules

LifecycleState is recreated after every RuntimeStatus transition.

Snapshots are append-only.

Mutation is forbidden.

Example timeline:

```text
CREATED
   │
   ▼
LifecycleState(status=CREATED)

INITIALIZING
   │
   ▼
LifecycleState(status=INITIALIZING)

READY
   │
   ▼
LifecycleState(status=READY)
```

---

# Health Registry

## Owner Runtime

RuntimeKernel

## Source Module

`src/core/types.py`

---

# HealthStatus Enumeration

<table columnSizing="equal">
  <table-row>
    <table-cell>**HealthStatus**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>UNKNOWN</table-cell>
    <table-cell>Health has not been evaluated.</table-cell>
  </table-row>
  <table-row>
    <table-cell>HEALTHY</table-cell>
    <table-cell>Runtime is fully operational.</table-cell>
  </table-row>
  <table-row>
    <table-cell>DEGRADED</table-cell>
    <table-cell>Runtime works with warnings.</table-cell>
  </table-row>
  <table-row>
    <table-cell>UNHEALTHY</table-cell>
    <table-cell>Runtime partially unavailable.</table-cell>
  </table-row>
  <table-row>
    <table-cell>FAILED</table-cell>
    <table-cell>Runtime cannot continue execution safely.</table-cell>
  </table-row>
</table>

Values are exhaustive.

---

# Health Ownership Rules

<table columnSizing="equal">
  <table-row>
    <table-cell>**Operation**</table-cell>
    <table-cell>**Owner**</table-cell>
  </table-row>
  <table-row>
    <table-cell>Evaluate health</table-cell>
    <table-cell>RuntimeKernel</table-cell>
  </table-row>
  <table-row>
    <table-cell>Read health</table-cell>
    <table-cell>All runtimes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Publish health event</table-cell>
    <table-cell>RuntimeKernel</table-cell>
  </table-row>
</table>

HealthStatus never mutates RuntimeStatus directly.

---

# Dependency Injection Lifecycle Registry

## Owner Runtime

Container Runtime

## Source Modules

- `src/kernel/runtime/container.py`
- `src/kernel/runtime/scope.py`

---

# DI Scope Lifecycle Enumeration

<table columnSizing="equal">
  <table-row>
    <table-cell>**Lifecycle State**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>REGISTERED</table-cell>
    <table-cell>Service descriptor exists inside RegistryRuntime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>RESOLVING</table-cell>
    <table-cell>ResolverRuntime is resolving dependencies.</table-cell>
  </table-row>
  <table-row>
    <table-cell>CONSTRUCTING</table-cell>
    <table-cell>ProviderRuntime is creating service instance.</table-cell>
  </table-row>
  <table-row>
    <table-cell>INITIALIZED</table-cell>
    <table-cell>Service initialization hooks completed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>ACTIVE</table-cell>
    <table-cell>Service available for dependency injection.</table-cell>
  </table-row>
  <table-row>
    <table-cell>RELEASING</table-cell>
    <table-cell>Shutdown hooks executing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>DESTROYED</table-cell>
    <table-cell>Service removed from active scope cache.</table-cell>
  </table-row>
</table>

Lifecycle is exhaustive.

---

# DI Scope Ownership Matrix

<table columnSizing="equal">
  <table-row>
    <table-cell>**DI Scope**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>APPLICATION</table-cell>
    <table-cell>ScopeRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>SESSION</table-cell>
    <table-cell>ScopeRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>PIPELINE</table-cell>
    <table-cell>ScopeRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>TRANSIENT</table-cell>
    <table-cell>ResolverRuntime</table-cell>
  </table-row>
</table>

Ownership is immutable.

---

# Dependency Injection Lifecycle Rules

1. Every registered service starts in REGISTERED state.
2. Construction always happens after dependency resolution.
3. Initialization hooks execute once per lifecycle.
4. APPLICATION scope lives until RuntimeKernel shutdown.
5. SESSION scope lives until SessionRuntime removes the session.
6. PIPELINE scope lives until ExecutorRuntime finishes pipeline execution.
7. TRANSIENT scope is never cached.

---

# Runtime Context State Registry

## Owner Runtime

Context Runtime

## Source Modules

- `src/kernel/runtime/context.py`
- `src/kernel/runtime/session.py`
- `src/kernel/runtime/metadata.py`

---

# Runtime Context Lifecycle

<table columnSizing="equal">
  <table-row>
    <table-cell>**Context State**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>EMPTY</table-cell>
    <table-cell>No RuntimeContext exists.</table-cell>
  </table-row>
  <table-row>
    <table-cell>CREATED</table-cell>
    <table-cell>RuntimeContext constructed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>ACTIVE</table-cell>
    <table-cell>Attached to execution thread.</table-cell>
  </table-row>
  <table-row>
    <table-cell>PROPAGATING</table-cell>
    <table-cell>Attached to outgoing RuntimeEvent.</table-cell>
  </table-row>
  <table-row>
    <table-cell>CLEARED</table-cell>
    <table-cell>Context removed from runtime.</table-cell>
  </table-row>
</table>

---

# Runtime Context Ownership Rules

<table columnSizing="equal">
  <table-row>
    <table-cell>**Operation**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>Create RuntimeContext</table-cell>
    <table-cell>ContextRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Store RuntimeContext</table-cell>
    <table-cell>SessionRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Mutate Metadata</table-cell>
    <table-cell>MetadataRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Clear RuntimeContext</table-cell>
    <table-cell>ContextRuntime</table-cell>
  </table-row>
</table>

Context ownership is distributed but non-overlapping.

---

# Session Lifecycle Registry

## Owner Runtime

Session Runtime

---

# Session Lifecycle Enumeration

<table columnSizing="equal">
  <table-row>
    <table-cell>**Session State**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>CREATED</table-cell>
    <table-cell>Session allocated.</table-cell>
  </table-row>
  <table-row>
    <table-cell>ACTIVE</table-cell>
    <table-cell>Session currently executing runtime work.</table-cell>
  </table-row>
  <table-row>
    <table-cell>IDLE</table-cell>
    <table-cell>Session retained but inactive.</table-cell>
  </table-row>
  <table-row>
    <table-cell>EXPIRED</table-cell>
    <table-cell>Session lifetime exceeded.</table-cell>
  </table-row>
  <table-row>
    <table-cell>REMOVED</table-cell>
    <table-cell>Session permanently deleted.</table-cell>
  </table-row>
</table>

---

# Pipeline Execution Lifecycle Registry

## Owner Runtime

Executor Runtime

---

# Pipeline Lifecycle Enumeration

<table columnSizing="equal">
  <table-row>
    <table-cell>**Pipeline State**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>CREATED</table-cell>
    <table-cell>Pipeline instance created.</table-cell>
  </table-row>
  <table-row>
    <table-cell>VALIDATED</table-cell>
    <table-cell>Manifest validation completed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>QUEUED</table-cell>
    <table-cell>Waiting for execution.</table-cell>
  </table-row>
  <table-row>
    <table-cell>EXECUTING</table-cell>
    <table-cell>Stages executing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>COMPLETED</table-cell>
    <table-cell>Pipeline finished successfully.</table-cell>
  </table-row>
  <table-row>
    <table-cell>FAILED</table-cell>
    <table-cell>Pipeline terminated with failure.</table-cell>
  </table-row>
  <table-row>
    <table-cell>CANCELLED</table-cell>
    <table-cell>Pipeline cancelled before completion.</table-cell>
  </table-row>
</table>

Pipeline lifecycle is immutable.

---

# Global Ownership Matrix

| Registry Category | Mutable Owner | Read Access |
|-------------------|---------------|-------------|
| RuntimeStatus | StateRuntime | Entire Runtime |
| LifecycleState | LifecycleRuntime | Entire Runtime |
| HealthStatus | RuntimeKernel | Entire Runtime |
| DI Lifecycle | ContainerRuntime / ScopeRuntime | Entire Runtime |
| Context State | ContextRuntime | RuntimeKernel, ExecutorRuntime |
| Session State | SessionRuntime | ContextRuntime |
| Pipeline State | ExecutorRuntime | RuntimeKernel, OrchestratorRuntime |

Ownership never overlaps.

---

# Global Registry Integrity Rules

1. Every runtime owns exactly one mutable lifecycle category.
2. Every lifecycle transition produces a runtime event.
3. RuntimeStatus is centralized inside Lifecycle Runtime.
4. HealthStatus is evaluated independently.
5. Dependency Injection lifecycle is independent from RuntimeStatus.
6. Session lifecycle is independent from Pipeline lifecycle.
7. RuntimeContext propagation never mutates RuntimeContext.
8. Every lifecycle snapshot is immutable.
9. Registry values are exhaustive.

Violating any rule is an Architecture Conflict.

---

# Definition of Done — Part 1

Part 1 is complete only if:

- [x] RuntimeStatus registry defined.
- [x] LifecycleState registry defined.
- [x] HealthStatus registry defined.
- [x] Dependency Injection lifecycle registry defined.
- [x] RuntimeContext lifecycle registry defined.
- [x] Session lifecycle registry defined.
- [x] Pipeline lifecycle registry defined.
- [x] Ownership matrix defined.
- [x] Integrity rules defined.

---

**Document Status**

IN PROGRESS — Part 1 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 2 — Canonical Runtime Event Registry -->
<!-- ========================================================================= -->

# Canonical Runtime Event Registry

**Owner Runtime**

EventBus Runtime

**Source Module**

`src/kernel/contracts/events.py`

---

# Runtime Event Naming Constitution

Every runtime event follows one canonical naming convention.

## Event Type Format

```text
<runtime>.<action>[.<phase>]
```

Examples:

```text
runtime.initialized
runtime.started

container.service.registered

context.created

pipeline.stage.started
pipeline.completed
```

Naming is immutable.

---

## Runtime Event Namespace Registry

| Namespace | Owner Runtime |
|-----------|---------------|
| runtime.* | Lifecycle Runtime |
| health.* | RuntimeKernel |
| container.* | Container Runtime |
| lifecycle.* | Lifecycle Runtime |
| context.* | Context Runtime |
| session.* | Session Runtime |
| eventbus.* | EventBus Runtime |
| pipeline.* | Executor Runtime |
| orchestrator.* | Orchestrator Runtime |
| bootstrap.* | Bootstrap Runtime |

No additional namespaces exist in Wave 1.

---

# Runtime Lifecycle Events

**Producer**

LifecycleRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Emitted When**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.created`</table-cell>
    <table-cell>RuntimeKernel object constructed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.initializing`</table-cell>
    <table-cell>Initialization sequence started.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.initialized`</table-cell>
    <table-cell>Initialization completed successfully.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.starting`</table-cell>
    <table-cell>Startup hooks executing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.started`</table-cell>
    <table-cell>Runtime entered RUNNING state.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.stopping`</table-cell>
    <table-cell>Graceful shutdown started.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.stopped`</table-cell>
    <table-cell>Execution stopped.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.shutting_down`</table-cell>
    <table-cell>Resource cleanup started.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.terminated`</table-cell>
    <table-cell>Runtime fully destroyed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.failed`</table-cell>
    <table-cell>Runtime entered FAILED state.</table-cell>
  </table-row>
</table>

These events are exhaustive.

---

# Health Events

**Producer**

RuntimeKernel

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`health.changed`</table-cell>
    <table-cell>HealthStatus changed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`health.degraded`</table-cell>
    <table-cell>Runtime became DEGRADED.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`health.unhealthy`</table-cell>
    <table-cell>Runtime became UNHEALTHY.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`health.failed`</table-cell>
    <table-cell>Runtime health became FAILED.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`health.restored`</table-cell>
    <table-cell>Runtime returned to HEALTHY.</table-cell>
  </table-row>
</table>

---

# Bootstrap Runtime Events

**Producer**

BootstrapRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`bootstrap.started`</table-cell>
    <table-cell>Build Checklist entered.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`bootstrap.runtime.constructing`</table-cell>
    <table-cell>Runtime facades being created.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`bootstrap.runtime.constructed`</table-cell>
    <table-cell>RuntimeKernel assembled.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`bootstrap.completed`</table-cell>
    <table-cell>Bootstrap finished successfully.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`bootstrap.failed`</table-cell>
    <table-cell>Bootstrap failed before runtime start.</table-cell>
  </table-row>
</table>

Bootstrap emits events only once.

---

# Dependency Injection Events

**Producer**

ContainerRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.service.registered`</table-cell>
    <table-cell>ServiceDescriptor added.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.service.resolving`</table-cell>
    <table-cell>Dependency resolution started.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.service.resolved`</table-cell>
    <table-cell>Dependency resolution finished.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.service.constructing`</table-cell>
    <table-cell>ProviderRuntime creating instance.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.service.initialized`</table-cell>
    <table-cell>Initialization hooks completed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.service.destroyed`</table-cell>
    <table-cell>Instance removed from scope cache.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.scope.created`</table-cell>
    <table-cell>New DI scope created.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.scope.destroyed`</table-cell>
    <table-cell>Scope cache released.</table-cell>
  </table-row>
</table>

---

# Lifecycle Hook Events

**Producer**

LifecycleRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.initialize.started`</table-cell>
    <table-cell>Initialize hooks executing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.initialize.completed`</table-cell>
    <table-cell>Initialize hooks finished.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.start.started`</table-cell>
    <table-cell>Startup hooks executing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.start.completed`</table-cell>
    <table-cell>Startup hooks completed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.stop.started`</table-cell>
    <table-cell>Stop hooks executing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.stop.completed`</table-cell>
    <table-cell>Stop hooks completed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.shutdown.started`</table-cell>
    <table-cell>Shutdown hooks executing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.shutdown.completed`</table-cell>
    <table-cell>Shutdown hooks completed.</table-cell>
  </table-row>
</table>

---

# Runtime Context Events

**Producer**

ContextRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`context.created`</table-cell>
    <table-cell>RuntimeContext created.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`context.activated`</table-cell>
    <table-cell>Context attached to execution.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`context.updated`</table-cell>
    <table-cell>Metadata replaced.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`context.propagating`</table-cell>
    <table-cell>Context attached to RuntimeEvent.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`context.cleared`</table-cell>
    <table-cell>Context removed from runtime.</table-cell>
  </table-row>
</table>

---

# Session Events

**Producer**

SessionRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`session.created`</table-cell>
    <table-cell>Session allocated.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`session.activated`</table-cell>
    <table-cell>Session entered ACTIVE state.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`session.idle`</table-cell>
    <table-cell>Session entered IDLE state.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`session.expired`</table-cell>
    <table-cell>Session expired.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`session.removed`</table-cell>
    <table-cell>Session deleted permanently.</table-cell>
  </table-row>
</table>

---

# EventBus Runtime Events

**Producer**

EventBusRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`eventbus.event.created`</table-cell>
    <table-cell>PublisherRuntime created RuntimeEvent.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`eventbus.event.dispatching`</table-cell>
    <table-cell>DispatcherRuntime dispatch started.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`eventbus.event.dispatched`</table-cell>
    <table-cell>Dispatch completed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`eventbus.subscriber.registered`</table-cell>
    <table-cell>Subscriber registered.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`eventbus.subscriber.removed`</table-cell>
    <table-cell>Subscriber removed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`eventbus.dispatch.failed`</table-cell>
    <table-cell>Dispatch terminated with exception.</table-cell>
  </table-row>
</table>

---

# Pipeline Runtime Events

**Producer**

ExecutorRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.created`</table-cell>
    <table-cell>Pipeline instance created.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.validated`</table-cell>
    <table-cell>Manifest validation completed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.queued`</table-cell>
    <table-cell>Pipeline entered queue.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.started`</table-cell>
    <table-cell>Pipeline execution started.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.completed`</table-cell>
    <table-cell>Pipeline finished successfully.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.failed`</table-cell>
    <table-cell>Pipeline failed.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.cancelled`</table-cell>
    <table-cell>Pipeline cancelled.</table-cell>
  </table-row>
</table>

---

# Pipeline Stage Events

**Producer**

ExecutorRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.stage.started`</table-cell>
    <table-cell>Stage execution started.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.stage.completed`</table-cell>
    <table-cell>Stage finished successfully.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.stage.failed`</table-cell>
    <table-cell>Stage terminated with exception.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.stage.skipped`</table-cell>
    <table-cell>Stage skipped by executor.</table-cell>
  </table-row>
</table>

---

# Orchestrator Events

**Producer**

OrchestratorRuntime

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`orchestrator.module.registered`</table-cell>
    <table-cell>Runtime module registered.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`orchestrator.pipeline.registered`</table-cell>
    <table-cell>Pipeline definition registered.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`orchestrator.pipeline.execution.requested`</table-cell>
    <table-cell>Execution requested through OrchestratorRuntime.</table-cell>
  </table-row>
</table>

---

# Runtime Failure Events

<table columnSizing="equal">
  <table-row>
    <table-cell>**Event Type**</table-cell>
    <table-cell>**Producer Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.failed`</table-cell>
    <table-cell>LifecycleRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>`bootstrap.failed`</table-cell>
    <table-cell>BootstrapRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>`container.service.failed`</table-cell>
    <table-cell>ContainerRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>`eventbus.dispatch.failed`</table-cell>
    <table-cell>EventBusRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.failed`</table-cell>
    <table-cell>ExecutorRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>`pipeline.stage.failed`</table-cell>
    <table-cell>ExecutorRuntime</table-cell>
  </table-row>
</table>

Failure events are unique.

---

# Runtime Event Producer Matrix

| Producer Runtime | Event Count |
|------------------|------------:|
| LifecycleRuntime | 18 |
| RuntimeKernel | 5 |
| BootstrapRuntime | 5 |
| ContainerRuntime | 8 |
| ContextRuntime | 5 |
| SessionRuntime | 5 |
| EventBusRuntime | 6 |
| ExecutorRuntime | 11 |
| OrchestratorRuntime | 3 |

**Total canonical runtime events:** **66**

No additional runtime events exist in Wave 1.

---

# Runtime Event Naming Integrity Rules

1. Event names use lowercase only.
2. Event names use dot-separated namespaces.
3. Producer runtime is unique.
4. Every lifecycle transition emits exactly one runtime event.
5. Every runtime event appears exactly once in this registry.
6. Event type strings are immutable API identifiers.
7. Business modules may subscribe to runtime events but may not redefine them.

Violating any rule is an Architecture Conflict.

---

# Definition of Done — Part 2

Part 2 is complete only if:

- [x] Runtime lifecycle event catalog defined.
- [x] Health event catalog defined.
- [x] Bootstrap event catalog defined.
- [x] DI event catalog defined.
- [x] Context event catalog defined.
- [x] Session event catalog defined.
- [x] EventBus event catalog defined.
- [x] Pipeline event catalog defined.
- [x] Producer ownership matrix defined.
- [x] Event naming constitution defined.

---

**Document Status**

IN PROGRESS — Part 2 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 3 — Runtime Event Payload Schema Registry -->
<!-- ========================================================================= -->

# Runtime Event Payload Schema Registry

**Owner Runtime**

EventBus Runtime

**Source Module**

`src/kernel/contracts/events.py`

---

# Purpose

Every RuntimeEvent contains an immutable payload object.

This section defines the canonical payload schema for every runtime event namespace.

Payload schemas are immutable public API.

Implementations may not add, remove or rename payload fields.

---

# Payload Design Principles

## PAYLOAD-001 — Immutable Payload

Payload is created exactly once.

After RuntimeEvent creation payload mutation is forbidden.

---

## PAYLOAD-002 — Minimal Required Fields

Payload contains only runtime information required for subscribers.

Diagnostic information belongs in metadata.

---

## PAYLOAD-003 — Strong Typing

Every payload field has exactly one canonical type.

Optional fields are explicitly marked.

---

# Shared Payload Vocabulary

These reusable fields appear across multiple payload schemas.

| Field | Type | Description |
|-------|------|-------------|
| `runtime_status` | RuntimeStatus | Current runtime lifecycle status. |
| `previous_status` | RuntimeStatus | Previous runtime lifecycle status. |
| `health_status` | HealthStatus | Runtime health snapshot. |
| `module_id` | ModuleId | Runtime module identifier. |
| `pipeline_id` | PipelineId | Pipeline execution identifier. |
| `stage_id` | str | Pipeline stage identifier. |
| `session_id` | SessionId | Runtime session identifier. |
| `service_id` | ServiceId | Dependency Injection service identifier. |
| `scope` | DIScope | Dependency Injection scope. |
| `trace_id` | TraceId | Distributed trace identifier. |
| `reason` | str | Human-readable failure reason. |
| `duration_ms` | float | Execution duration in milliseconds. |

Vocabulary is immutable.

---

# Runtime Lifecycle Payloads

## runtime.created

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>architecture_version</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>kernel_version</table-cell><table-cell>str</table-cell></table-row>
</table>

---

## runtime.initializing

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>previous_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
</table>

---

## runtime.initialized

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>duration_ms</table-cell><table-cell>float</table-cell></table-row>
</table>

---

## runtime.started

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>started_at</table-cell><table-cell>datetime</table-cell></table-row>
</table>

---

## runtime.stopping

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>active_sessions</table-cell><table-cell>int</table-cell></table-row>
  <table-row><table-cell>active_pipelines</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## runtime.stopped

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>stopped_at</table-cell><table-cell>datetime</table-cell></table-row>
  <table-row><table-cell>uptime_seconds</table-cell><table-cell>float</table-cell></table-row>
</table>

---

## runtime.terminated

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>released_services</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## runtime.failed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>exception_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>recoverable</table-cell><table-cell>bool</table-cell></table-row>
</table>

---

# Health Payloads

## health.changed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>previous_health</table-cell><table-cell>HealthStatus</table-cell></table-row>
  <table-row><table-cell>health_status</table-cell><table-cell>HealthStatus</table-cell></table-row>
</table>

---

## health.degraded / unhealthy / failed / restored

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>health_status</table-cell><table-cell>HealthStatus</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
</table>

---

# Bootstrap Payloads

## bootstrap.started

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>architecture_version</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>environment</table-cell><table-cell>str</table-cell></table-row>
</table>

---

## bootstrap.runtime.constructing

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_count</table-cell><table-cell>int</table-cell></table-row>
  <table-row><table-cell>completed</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## bootstrap.runtime.constructed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_modules</table-cell><table-cell>list[str]</table-cell></table-row>
  <table-row><table-cell>duration_ms</table-cell><table-cell>float</table-cell></table-row>
</table>

---

## bootstrap.completed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>duration_ms</table-cell><table-cell>float</table-cell></table-row>
  <table-row><table-cell>health_status</table-cell><table-cell>HealthStatus</table-cell></table-row>
</table>

---

## bootstrap.failed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>exception_type</table-cell><table-cell>str</table-cell></table-row>
</table>

---

# Dependency Injection Payloads

## container.service.registered

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>service_id</table-cell><table-cell>ServiceId</table-cell></table-row>
  <table-row><table-cell>scope</table-cell><table-cell>DIScope</table-cell></table-row>
  <table-row><table-cell>implementation</table-cell><table-cell>str</table-cell></table-row>
</table>

---

## container.service.resolving

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>service_id</table-cell><table-cell>ServiceId</table-cell></table-row>
  <table-row><table-cell>dependency_count</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## container.service.resolved

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>service_id</table-cell><table-cell>ServiceId</table-cell></table-row>
  <table-row><table-cell>resolved_dependencies</table-cell><table-cell>list[ServiceId]</table-cell></table-row>
</table>

---

## container.service.constructing

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>service_id</table-cell><table-cell>ServiceId</table-cell></table-row>
  <table-row><table-cell>scope</table-cell><table-cell>DIScope</table-cell></table-row>
</table>

---

## container.service.initialized

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>service_id</table-cell><table-cell>ServiceId</table-cell></table-row>
  <table-row><table-cell>scope</table-cell><table-cell>DIScope</table-cell></table-row>
  <table-row><table-cell>duration_ms</table-cell><table-cell>float</table-cell></table-row>
</table>

---

## container.service.destroyed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>service_id</table-cell><table-cell>ServiceId</table-cell></table-row>
  <table-row><table-cell>scope</table-cell><table-cell>DIScope</table-cell></table-row>
</table>

---

## container.scope.created / destroyed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>scope</table-cell><table-cell>DIScope</table-cell></table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>SessionId \| None</table-cell></table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId \| None</table-cell></table-row>
</table>

---

# Lifecycle Hook Payloads

Every lifecycle hook event shares one schema.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>phase</table-cell><table-cell>EventPhase</table-cell></table-row>
  <table-row><table-cell>hook_count</table-cell><table-cell>int</table-cell></table-row>
  <table-row><table-cell>duration_ms</table-cell><table-cell>float \| None</table-cell></table-row>
</table>

---

# Context Payloads

## context.created

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>SessionId</table-cell></table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>TraceId</table-cell></table-row>
  <table-row><table-cell>metadata_keys</table-cell><table-cell>list[str]</table-cell></table-row>
</table>

---

## context.activated

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>SessionId</table-cell></table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId \| None</table-cell></table-row>
</table>

---

## context.updated

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>updated_keys</table-cell><table-cell>list[str]</table-cell></table-row>
  <table-row><table-cell>metadata_size</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## context.propagating

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>TraceId</table-cell></table-row>
  <table-row><table-cell>event_type</table-cell><table-cell>str</table-cell></table-row>
</table>

---

## context.cleared

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>SessionId</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
</table>

---

# Session Payloads

Every session event shares one schema.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>SessionId</table-cell></table-row>
  <table-row><table-cell>state</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>created_at</table-cell><table-cell>datetime</table-cell></table-row>
  <table-row><table-cell>expires_at</table-cell><table-cell>datetime \| None</table-cell></table-row>
</table>

---

# EventBus Payloads

## eventbus.event.created

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>event_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>priority</table-cell><table-cell>EventPriority</table-cell></table-row>
  <table-row><table-cell>phase</table-cell><table-cell>EventPhase</table-cell></table-row>
</table>

---

## eventbus.event.dispatching / dispatched

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>event_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>subscriber_count</table-cell><table-cell>int</table-cell></table-row>
  <table-row><table-cell>duration_ms</table-cell><table-cell>float \| None</table-cell></table-row>
</table>

---

## eventbus.subscriber.registered / removed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>event_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>handler_name</table-cell><table-cell>str</table-cell></table-row>
</table>

---

## eventbus.dispatch.failed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>event_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>handler_name</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>exception_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
</table>

---

# Pipeline Payloads

## pipeline.created

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>module_count</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## pipeline.validated

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>stage_count</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## pipeline.queued

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>queue_position</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## pipeline.started

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>SessionId</table-cell></table-row>
</table>

---

## pipeline.completed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>duration_ms</table-cell><table-cell>float</table-cell></table-row>
  <table-row><table-cell>stage_count</table-cell><table-cell>int</table-cell></table-row>
</table>

---

## pipeline.failed

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>failed_stage</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>exception_type</table-cell><table-cell>str</table-cell></table-row>
</table>

---

## pipeline.cancelled

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
</table>

---

# Pipeline Stage Payloads

Every stage event shares one schema.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>stage_id</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>module_id</table-cell><table-cell>ModuleId</table-cell></table-row>
  <table-row><table-cell>duration_ms</table-cell><table-cell>float \| None</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str \| None</table-cell></table-row>
</table>

---

# Orchestrator Payloads

Every orchestrator event shares one schema.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>module_id</table-cell><table-cell>ModuleId \| None</table-cell></table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId \| None</table-cell></table-row>
  <table-row><table-cell>manifest_version</table-cell><table-cell>str</table-cell></table-row>
</table>

---

# Payload Validation Rules

Every RuntimeEvent payload must satisfy:

1. All required fields exist.
2. No undocumented fields exist.
3. Every field matches its canonical type.
4. Optional fields may be omitted only if marked optional.
5. Payload is JSON-serializable.
6. Payload size must remain deterministic.
7. Payload mutation after event creation is forbidden.

Payload validation happens before dispatch.

---

# Payload Integrity Rules

1. Event type uniquely determines payload schema.
2. Payload schema never depends on subscriber.
3. Metadata never duplicates payload fields.
4. Payload contains runtime facts only.
5. Trace information belongs to RuntimeContext, not payload.
6. Payload versioning follows document version.
7. Payload schemas are append-only across architecture versions.

Violating any rule is an Architecture Conflict.

---

# Definition of Done — Part 3

Part 3 is complete only if:

- [x] Shared payload vocabulary defined.
- [x] Lifecycle payload schemas defined.
- [x] Health payload schemas defined.
- [x] Bootstrap payload schemas defined.
- [x] DI payload schemas defined.
- [x] Context payload schemas defined.
- [x] Session payload schemas defined.
- [x] EventBus payload schemas defined.
- [x] Pipeline payload schemas defined.
- [x] Payload validation rules defined.

---

**Document Status**

IN PROGRESS — Part 3 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 4 — Event Priority, Event Phase & Dispatch Registry -->
<!-- ========================================================================= -->

# Event Priority Registry

**Owner Runtime**

EventBus Runtime

**Source Modules**

- `src/kernel/contracts/events.py`
- `src/kernel/runtime/publisher.py`
- `src/kernel/runtime/dispatcher.py`

---

# Purpose

Every RuntimeEvent has exactly one dispatch priority.

Priority determines dispatch ordering inside EventBusRuntime.

Priority never changes after RuntimeEvent creation.

---

# EventPriority Enumeration

**Canonical Enumeration**

| Priority | Value | Purpose |
|----------|------:|---------|
| CRITICAL | 100 | Runtime survival events. |
| HIGH | 75 | Lifecycle and shutdown events. |
| NORMAL | 50 | Ordinary runtime events. |
| LOW | 25 | Informational runtime events. |
| BACKGROUND | 0 | Diagnostics and telemetry events. |

Enumeration is exhaustive.

---

## Priority Ordering Rule

Dispatch always follows descending priority.

```text
CRITICAL
    │
    ▼
HIGH
    │
    ▼
NORMAL
    │
    ▼
LOW
    │
    ▼
BACKGROUND
```

Within the same priority, FIFO ordering is mandatory.

---

# Canonical Priority Assignment Matrix

## Runtime Lifecycle Events

| Event | Priority |
|-------|----------|
| runtime.failed | CRITICAL |
| runtime.shutting_down | HIGH |
| runtime.stopping | HIGH |
| runtime.started | HIGH |
| runtime.starting | HIGH |
| runtime.initialized | HIGH |
| runtime.initializing | HIGH |
| runtime.created | NORMAL |
| runtime.stopped | NORMAL |
| runtime.terminated | NORMAL |

---

## Health Events

| Event | Priority |
|-------|----------|
| health.failed | CRITICAL |
| health.unhealthy | HIGH |
| health.degraded | NORMAL |
| health.restored | NORMAL |
| health.changed | LOW |

---

## Bootstrap Events

| Event | Priority |
|-------|----------|
| bootstrap.failed | CRITICAL |
| bootstrap.started | HIGH |
| bootstrap.runtime.constructing | NORMAL |
| bootstrap.runtime.constructed | NORMAL |
| bootstrap.completed | NORMAL |

---

## Dependency Injection Events

| Event | Priority |
|-------|----------|
| container.service.constructing | HIGH |
| container.service.initialized | HIGH |
| container.service.resolving | NORMAL |
| container.service.resolved | NORMAL |
| container.service.registered | LOW |
| container.service.destroyed | LOW |
| container.scope.created | LOW |
| container.scope.destroyed | LOW |

---

## Lifecycle Hook Events

| Event | Priority |
|-------|----------|
| lifecycle.initialize.started | HIGH |
| lifecycle.initialize.completed | HIGH |
| lifecycle.start.started | HIGH |
| lifecycle.start.completed | HIGH |
| lifecycle.stop.started | HIGH |
| lifecycle.stop.completed | HIGH |
| lifecycle.shutdown.started | HIGH |
| lifecycle.shutdown.completed | HIGH |

---

## Context Events

| Event | Priority |
|-------|----------|
| context.created | NORMAL |
| context.activated | NORMAL |
| context.updated | LOW |
| context.propagating | LOW |
| context.cleared | LOW |

---

## Session Events

| Event | Priority |
|-------|----------|
| session.created | NORMAL |
| session.activated | NORMAL |
| session.idle | LOW |
| session.expired | NORMAL |
| session.removed | LOW |

---

## EventBus Events

| Event | Priority |
|-------|----------|
| eventbus.dispatch.failed | HIGH |
| eventbus.event.created | LOW |
| eventbus.event.dispatching | LOW |
| eventbus.event.dispatched | LOW |
| eventbus.subscriber.registered | BACKGROUND |
| eventbus.subscriber.removed | BACKGROUND |

---

## Pipeline Events

| Event | Priority |
|-------|----------|
| pipeline.failed | HIGH |
| pipeline.cancelled | HIGH |
| pipeline.started | NORMAL |
| pipeline.completed | NORMAL |
| pipeline.created | LOW |
| pipeline.validated | LOW |
| pipeline.queued | LOW |

---

## Pipeline Stage Events

| Event | Priority |
|-------|----------|
| pipeline.stage.failed | HIGH |
| pipeline.stage.started | NORMAL |
| pipeline.stage.completed | NORMAL |
| pipeline.stage.skipped | LOW |

---

## Orchestrator Events

| Event | Priority |
|-------|----------|
| orchestrator.pipeline.execution.requested | NORMAL |
| orchestrator.module.registered | LOW |
| orchestrator.pipeline.registered | LOW |

Priority assignment is immutable.

---

# Event Phase Registry

**Owner Runtime**

DispatcherRuntime

---

# EventPhase Enumeration

Every RuntimeEvent belongs to exactly one phase.

| Phase | Purpose |
|-------|---------|
| CREATE | PublisherRuntime creates RuntimeEvent. |
| QUEUE | Event enters dispatch queue. |
| DISPATCH | DispatcherRuntime dispatching subscribers. |
| HANDLE | Subscriber handler execution. |
| COMPLETE | Dispatch finished successfully. |
| FAILED | Dispatch terminated with exception. |

Enumeration is exhaustive.

---

## Phase Transition Graph

```text
CREATE
   │
   ▼
QUEUE
   │
   ▼
DISPATCH
   │
   ▼
HANDLE
   │
   ▼
COMPLETE
```

Failure path:

```text
HANDLE
   │
   ▼
FAILED
```

No additional phases exist.

---

# Event Phase Ownership Matrix

| Phase | Owner Runtime |
|-------|---------------|
| CREATE | PublisherRuntime |
| QUEUE | EventBusRuntime |
| DISPATCH | DispatcherRuntime |
| HANDLE | SubscriberRuntime |
| COMPLETE | DispatcherRuntime |
| FAILED | DispatcherRuntime |

Ownership never overlaps.

---

# Dispatch Queue Registry

## Queue Ordering Rules

DispatcherRuntime maintains one logical priority queue.

Ordering algorithm:

1. Highest priority first.
2. FIFO within priority.
3. Stable ordering across subscribers.

---

## Queue Invariants

DispatcherRuntime guarantees:

- deterministic ordering;
- stable priority ordering;
- immutable queue entries;
- no duplicate RuntimeEvent IDs.

---

# Subscriber Execution Registry

## Subscriber Ordering

Subscribers execute in registration order.

Example:

```text
Subscriber A
      │
      ▼
Subscriber B
      │
      ▼
Subscriber C
```

Ordering is deterministic.

---

## Subscriber Isolation Rule

Each subscriber executes independently.

Failure of one subscriber does not stop remaining subscribers unless the event priority is CRITICAL and dispatcher policy requires abort.

---

## Subscriber Failure Policy

<table columnSizing="equal">
  <table-row>
    <table-cell>**Priority**</table-cell>
    <table-cell>**Failure Behaviour**</table-cell>
  </table-row>
  <table-row>
    <table-cell>CRITICAL</table-cell>
    <table-cell>Abort dispatch and emit `eventbus.dispatch.failed`.</table-cell>
  </table-row>
  <table-row>
    <table-cell>HIGH</table-cell>
    <table-cell>Log failure, continue remaining subscribers.</table-cell>
  </table-row>
  <table-row>
    <table-cell>NORMAL</table-cell>
    <table-cell>Continue remaining subscribers.</table-cell>
  </table-row>
  <table-row>
    <table-cell>LOW</table-cell>
    <table-cell>Continue remaining subscribers.</table-cell>
  </table-row>
  <table-row>
    <table-cell>BACKGROUND</table-cell>
    <table-cell>Failure logged only.</table-cell>
  </table-row>
</table>

Policy is immutable.

---

# Dispatch Completion Rules

A RuntimeEvent reaches COMPLETE only if:

- queue processing finished;
- every subscriber finished according to policy;
- payload remained immutable;
- context propagation completed.

Otherwise dispatcher emits FAILED.

---

# Event Retry Registry

Wave 1 runtime events are **never retried automatically**.

| Event Category | Retry |
|---------------|-------|
| Runtime Events | No |
| Lifecycle Events | No |
| Health Events | No |
| Context Events | No |
| DI Events | No |
| Pipeline Events | No |

Retry behaviour belongs to future application-layer logic, not EventBusRuntime.

---

# Event Timeout Registry

DispatcherRuntime executes subscribers without runtime-managed timeout.

Subscriber implementations are responsible for cancellation behaviour.

Runtime never injects timeout into dispatch flow.

---

# Event Ordering Guarantees

DispatcherRuntime guarantees:

1. Priority ordering.
2. FIFO inside priority.
3. Single dispatch per RuntimeEvent.
4. Stable subscriber ordering.
5. Immutable payload.
6. Immutable RuntimeContext propagation.
7. Deterministic completion phase.

---

# Event Dispatch Integrity Rules

DispatcherRuntime must never:

- reorder equal-priority events;
- mutate payloads;
- mutate RuntimeContext;
- dispatch duplicate event IDs;
- execute subscriber twice for one RuntimeEvent.

Violating any rule is an Architecture Conflict.

---

# Priority Visibility Matrix

| Runtime | Reads Priority | Assigns Priority |
|---------|----------------|------------------|
| PublisherRuntime | ✅ | ✅ |
| EventBusRuntime | ✅ | ❌ |
| DispatcherRuntime | ✅ | ❌ |
| SubscriberRuntime | ✅ | ❌ |
| RuntimeKernel | ✅ | ❌ |

Priority assignment belongs exclusively to PublisherRuntime.

---

# Phase Visibility Matrix

| Runtime | Reads Phase | Writes Phase |
|---------|-------------|--------------|
| PublisherRuntime | CREATE | CREATE |
| EventBusRuntime | QUEUE | QUEUE |
| DispatcherRuntime | DISPATCH / COMPLETE / FAILED | DISPATCH / COMPLETE / FAILED |
| SubscriberRuntime | HANDLE | HANDLE |

Phase ownership is immutable.

---

# Definition of Done — Part 4

Part 4 is complete only if:

- [x] EventPriority registry defined.
- [x] EventPhase registry defined.
- [x] Priority assignment matrix defined.
- [x] Queue ordering defined.
- [x] Subscriber ordering defined.
- [x] Subscriber failure policy defined.
- [x] Dispatch completion rules defined.
- [x] Retry registry defined.
- [x] Timeout registry defined.
- [x] Visibility matrices defined.

---

**Document Status**

IN PROGRESS — Part 4 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 5 — Lifecycle Transition Matrix -->
<!-- ========================================================================= -->

# Lifecycle Transition Matrix

**Owner Runtime**

Lifecycle Runtime

**Authority**

M-02 Runtime Graph

M-04 Import Graph

Part 1 Runtime State Registry

---

# Purpose

This section defines every legal state transition inside Wave 1.

Every transition specifies:

- source state;
- destination state;
- transition owner;
- emitted RuntimeEvent;
- transition trigger.

Transitions not listed here are forbidden.

---

# Transition Principles

## TRANSITION-001 — Explicit Only

Only transitions documented in this registry are legal.

Undefined transitions must throw `InvalidLifecycleTransitionError`.

---

## TRANSITION-002 — Single Owner

Every transition has exactly one runtime owner.

Only the owner runtime may perform the transition.

---

## TRANSITION-003 — Transition Emits Event

Every successful transition emits exactly one RuntimeEvent.

Failed transitions emit no lifecycle transition event.

---

## TRANSITION-004 — Atomic Transition

A transition is atomic.

Either:

- state changes completely;
- event emitted;

or nothing changes.

---

# RuntimeStatus Transition Matrix

**Owner Runtime**

LifecycleRuntime

---

<table columnSizing="equal">
  <table-row>
    <table-cell>**From**</table-cell>
    <table-cell>**To**</table-cell>
    <table-cell>**Event**</table-cell>
    <table-cell>**Trigger**</table-cell>
  </table-row>
  <table-row><table-cell>CREATED</table-cell><table-cell>INITIALIZING</table-cell><table-cell>`runtime.initializing`</table-cell><table-cell>`RuntimeKernel.initialize()`</table-cell></table-row>
  <table-row><table-cell>INITIALIZING</table-cell><table-cell>READY</table-cell><table-cell>`runtime.initialized`</table-cell><table-cell>Initialization successful.</table-cell></table-row>
  <table-row><table-cell>READY</table-cell><table-cell>STARTING</table-cell><table-cell>`runtime.starting`</table-cell><table-cell>`RuntimeKernel.start()`</table-cell></table-row>
  <table-row><table-cell>STARTING</table-cell><table-cell>RUNNING</table-cell><table-cell>`runtime.started`</table-cell><table-cell>Startup hooks completed.</table-cell></table-row>
  <table-row><table-cell>RUNNING</table-cell><table-cell>STOPPING</table-cell><table-cell>`runtime.stopping`</table-cell><table-cell>`RuntimeKernel.stop()`</table-cell></table-row>
  <table-row><table-cell>STOPPING</table-cell><table-cell>STOPPED</table-cell><table-cell>`runtime.stopped`</table-cell><table-cell>Pipeline execution finished.</table-cell></table-row>
  <table-row><table-cell>STOPPED</table-cell><table-cell>SHUTTING_DOWN</table-cell><table-cell>`runtime.shutting_down`</table-cell><table-cell>`RuntimeKernel.shutdown()`</table-cell></table-row>
  <table-row><table-cell>SHUTTING_DOWN</table-cell><table-cell>TERMINATED</table-cell><table-cell>`runtime.terminated`</table-cell><table-cell>All resources released.</table-cell></table-row>
</table>

---

# Runtime Failure Transitions

<table columnSizing="equal">
  <table-row>
    <table-cell>**Allowed Failure Source**</table-cell>
    <table-cell>**Destination**</table-cell>
    <table-cell>**Event**</table-cell>
  </table-row>
  <table-row><table-cell>INITIALIZING</table-cell><table-cell>FAILED</table-cell><table-cell>`runtime.failed`</table-cell></table-row>
  <table-row><table-cell>READY</table-cell><table-cell>FAILED</table-cell><table-cell>`runtime.failed`</table-cell></table-row>
  <table-row><table-cell>STARTING</table-cell><table-cell>FAILED</table-cell><table-cell>`runtime.failed`</table-cell></table-row>
  <table-row><table-cell>RUNNING</table-cell><table-cell>FAILED</table-cell><table-cell>`runtime.failed`</table-cell></table-row>
  <table-row><table-cell>STOPPING</table-cell><table-cell>FAILED</table-cell><table-cell>`runtime.failed`</table-cell></table-row>
  <table-row><table-cell>SHUTTING_DOWN</table-cell><table-cell>FAILED</table-cell><table-cell>`runtime.failed`</table-cell></table-row>
</table>

FAILED is terminal.

---

# Forbidden RuntimeStatus Transitions

The following transitions are architecture violations.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Transition**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row><table-cell>CREATED → RUNNING</table-cell><table-cell>Initialization skipped.</table-cell></table-row>
  <table-row><table-cell>INITIALIZING → STARTING</table-cell><table-cell>READY state skipped.</table-cell></table-row>
  <table-row><table-cell>RUNNING → TERMINATED</table-cell><table-cell>Shutdown skipped.</table-cell></table-row>
  <table-row><table-cell>READY → STOPPED</table-cell><table-cell>Runtime never started.</table-cell></table-row>
  <table-row><table-cell>FAILED → RUNNING</table-cell><table-cell>Runtime recovery unsupported.</table-cell></table-row>
  <table-row><table-cell>TERMINATED → CREATED</table-cell><table-cell>Runtime object cannot restart.</table-cell></table-row>
</table>

---

# RuntimeStatus Transition Graph

```text
CREATED
   │
   ▼
INITIALIZING
   │
   ▼
READY
   │
   ▼
STARTING
   │
   ▼
RUNNING
   │
   ▼
STOPPING
   │
   ▼
STOPPED
   │
   ▼
SHUTTING_DOWN
   │
   ▼
TERMINATED
```

Failure edges point to FAILED from every active state.

---

# HealthStatus Transition Matrix

**Owner Runtime**

RuntimeKernel

---

<table columnSizing="equal">
  <table-row>
    <table-cell>**From**</table-cell>
    <table-cell>**To**</table-cell>
    <table-cell>**Event**</table-cell>
  </table-row>
  <table-row><table-cell>UNKNOWN</table-cell><table-cell>HEALTHY</table-cell><table-cell>`health.changed`</table-cell></table-row>
  <table-row><table-cell>HEALTHY</table-cell><table-cell>DEGRADED</table-cell><table-cell>`health.degraded`</table-cell></table-row>
  <table-row><table-cell>DEGRADED</table-cell><table-cell>HEALTHY</table-cell><table-cell>`health.restored`</table-cell></table-row>
  <table-row><table-cell>HEALTHY</table-cell><table-cell>UNHEALTHY</table-cell><table-cell>`health.unhealthy`</table-cell></table-row>
  <table-row><table-cell>DEGRADED</table-cell><table-cell>UNHEALTHY</table-cell><table-cell>`health.unhealthy`</table-cell></table-row>
  <table-row><table-cell>UNHEALTHY</table-cell><table-cell>FAILED</table-cell><table-cell>`health.failed`</table-cell></table-row>
</table>

---

# Health Transition Rules

Health transitions never mutate RuntimeStatus automatically.

RuntimeStatus reacts independently through LifecycleRuntime.

---

# Dependency Injection Lifecycle Matrix

**Owner Runtime**

ContainerRuntime

---

<table columnSizing="equal">
  <table-row>
    <table-cell>**From**</table-cell>
    <table-cell>**To**</table-cell>
    <table-cell>**Event**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row><table-cell>REGISTERED</table-cell><table-cell>RESOLVING</table-cell><table-cell>`container.service.resolving`</table-cell><table-cell>ResolverRuntime</table-cell></table-row>
  <table-row><table-cell>RESOLVING</table-cell><table-cell>CONSTRUCTING</table-cell><table-cell>`container.service.resolved`</table-cell><table-cell>ResolverRuntime</table-cell></table-row>
  <table-row><table-cell>CONSTRUCTING</table-cell><table-cell>INITIALIZED</table-cell><table-cell>`container.service.constructing`</table-cell><table-cell>ProviderRuntime</table-cell></table-row>
  <table-row><table-cell>INITIALIZED</table-cell><table-cell>ACTIVE</table-cell><table-cell>`container.service.initialized`</table-cell><table-cell>ContainerRuntime</table-cell></table-row>
  <table-row><table-cell>ACTIVE</table-cell><table-cell>RELEASING</table-cell><table-cell>`container.service.destroyed`</table-cell><table-cell>ScopeRuntime</table-cell></table-row>
  <table-row><table-cell>RELEASING</table-cell><table-cell>DESTROYED</table-cell><table-cell>`container.service.destroyed`</table-cell><table-cell>ScopeRuntime</table-cell></table-row>
</table>

---

# DI Failure Transition

<table columnSizing="equal">
  <table-row>
    <table-cell>**State**</table-cell>
    <table-cell>**Failure Behaviour**</table-cell>
  </table-row>
  <table-row><table-cell>RESOLVING</table-cell><table-cell>Dependency resolution exception.</table-cell></table-row>
  <table-row><table-cell>CONSTRUCTING</table-cell><table-cell>Provider construction exception.</table-cell></table-row>
  <table-row><table-cell>INITIALIZED</table-cell><table-cell>Initialization hook exception.</table-cell></table-row>
</table>

Service never enters ACTIVE after failure.

---

# DI Scope Lifecycle Matrix

<table columnSizing="equal">
  <table-row>
    <table-cell>**Scope**</table-cell>
    <table-cell>**Created**</table-cell>
    <table-cell>**Destroyed**</table-cell>
  </table-row>
  <table-row><table-cell>APPLICATION</table-cell><table-cell>BootstrapRuntime</table-cell><table-cell>Runtime shutdown.</table-cell></table-row>
  <table-row><table-cell>SESSION</table-cell><table-cell>SessionRuntime</table-cell><table-cell>Session removed.</table-cell></table-row>
  <table-row><table-cell>PIPELINE</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>Pipeline completed/failed.</table-cell></table-row>
  <table-row><table-cell>TRANSIENT</table-cell><table-cell>ResolverRuntime</table-cell><table-cell>Immediately after resolve.</table-cell></table-row>
</table>

---

# RuntimeContext Lifecycle Matrix

**Owner Runtime**

ContextRuntime

---

<table columnSizing="equal">
  <table-row>
    <table-cell>**From**</table-cell>
    <table-cell>**To**</table-cell>
    <table-cell>**Event**</table-cell>
  </table-row>
  <table-row><table-cell>EMPTY</table-cell><table-cell>CREATED</table-cell><table-cell>`context.created`</table-cell></table-row>
  <table-row><table-cell>CREATED</table-cell><table-cell>ACTIVE</table-cell><table-cell>`context.activated`</table-cell></table-row>
  <table-row><table-cell>ACTIVE</table-cell><table-cell>PROPAGATING</table-cell><table-cell>`context.propagating`</table-cell></table-row>
  <table-row><table-cell>PROPAGATING</table-cell><table-cell>ACTIVE</table-cell><table-cell>`context.updated`</table-cell></table-row>
  <table-row><table-cell>ACTIVE</table-cell><table-cell>CLEARED</table-cell><table-cell>`context.cleared`</table-cell></table-row>
  <table-row><table-cell>CLEARED</table-cell><table-cell>EMPTY</table-cell><table-cell>None</table-cell></table-row>
</table>

---

# Context Transition Rules

- Only one ACTIVE RuntimeContext per session.
- PROPAGATING is temporary.
- CLEARED removes metadata permanently.

---

# Session Lifecycle Matrix

**Owner Runtime**

SessionRuntime

---

<table columnSizing="equal">
  <table-row>
    <table-cell>**From**</table-cell>
    <table-cell>**To**</table-cell>
    <table-cell>**Event**</table-cell>
  </table-row>
  <table-row><table-cell>CREATED</table-cell><table-cell>ACTIVE</table-cell><table-cell>`session.activated`</table-cell></table-row>
  <table-row><table-cell>ACTIVE</table-cell><table-cell>IDLE</table-cell><table-cell>`session.idle`</table-cell></table-row>
  <table-row><table-cell>IDLE</table-cell><table-cell>ACTIVE</table-cell><table-cell>`session.activated`</table-cell></table-row>
  <table-row><table-cell>ACTIVE</table-cell><table-cell>EXPIRED</table-cell><table-cell>`session.expired`</table-cell></table-row>
  <table-row><table-cell>IDLE</table-cell><table-cell>EXPIRED</table-cell><table-cell>`session.expired`</table-cell></table-row>
  <table-row><table-cell>EXPIRED</table-cell><table-cell>REMOVED</table-cell><table-cell>`session.removed`</table-cell></table-row>
</table>

---

# Session Transition Rules

- Session may reactivate only from IDLE.
- EXPIRED sessions never become ACTIVE again.
- REMOVED is terminal.

---

# Pipeline Lifecycle Matrix

**Owner Runtime**

ExecutorRuntime

---

<table columnSizing="equal">
  <table-row>
    <table-cell>**From**</table-cell>
    <table-cell>**To**</table-cell>
    <table-cell>**Event**</table-cell>
  </table-row>
  <table-row><table-cell>CREATED</table-cell><table-cell>VALIDATED</table-cell><table-cell>`pipeline.validated`</table-cell></table-row>
  <table-row><table-cell>VALIDATED</table-cell><table-cell>QUEUED</table-cell><table-cell>`pipeline.queued`</table-cell></table-row>
  <table-row><table-cell>QUEUED</table-cell><table-cell>EXECUTING</table-cell><table-cell>`pipeline.started`</table-cell></table-row>
  <table-row><table-cell>EXECUTING</table-cell><table-cell>COMPLETED</table-cell><table-cell>`pipeline.completed`</table-cell></table-row>
  <table-row><table-cell>EXECUTING</table-cell><table-cell>FAILED</table-cell><table-cell>`pipeline.failed`</table-cell></table-row>
  <table-row><table-cell>QUEUED</table-cell><table-cell>CANCELLED</table-cell><table-cell>`pipeline.cancelled`</table-cell></table-row>
  <table-row><table-cell>EXECUTING</table-cell><table-cell>CANCELLED</table-cell><table-cell>`pipeline.cancelled`</table-cell></table-row>
</table>

---

# Pipeline Stage Lifecycle Matrix

Each pipeline stage has an independent lifecycle.

<table columnSizing="equal">
  <table-row>
    <table-cell>**From**</table-cell>
    <table-cell>**To**</table-cell>
    <table-cell>**Event**</table-cell>
  </table-row>
  <table-row><table-cell>CREATED</table-cell><table-cell>EXECUTING</table-cell><table-cell>`pipeline.stage.started`</table-cell></table-row>
  <table-row><table-cell>EXECUTING</table-cell><table-cell>COMPLETED</table-cell><table-cell>`pipeline.stage.completed`</table-cell></table-row>
  <table-row><table-cell>EXECUTING</table-cell><table-cell>FAILED</table-cell><table-cell>`pipeline.stage.failed`</table-cell></table-row>
  <table-row><table-cell>CREATED</table-cell><table-cell>SKIPPED</table-cell><table-cell>`pipeline.stage.skipped`</table-cell></table-row>
</table>

---

# Pipeline Stage Transition Rules

- Stage executes once.
- FAILED stage terminates pipeline unless recovery policy explicitly exists.
- SKIPPED stage never executes later.

---

# Lifecycle Hook Transition Matrix

Lifecycle hooks execute in deterministic order.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Hook Phase**</table-cell>
    <table-cell>**Event Pair**</table-cell>
  </table-row>
  <table-row><table-cell>Initialize</table-cell><table-cell>`lifecycle.initialize.started` → `lifecycle.initialize.completed`</table-cell></table-row>
  <table-row><table-cell>Start</table-cell><table-cell>`lifecycle.start.started` → `lifecycle.start.completed`</table-cell></table-row>
  <table-row><table-cell>Stop</table-cell><table-cell>`lifecycle.stop.started` → `lifecycle.stop.completed`</table-cell></table-row>
  <table-row><table-cell>Shutdown</table-cell><table-cell>`lifecycle.shutdown.started` → `lifecycle.shutdown.completed`</table-cell></table-row>
</table>

Every phase executes exactly once.

---

# Transition Ownership Summary

| Lifecycle Category | Transition Owner |
|--------------------|------------------|
| RuntimeStatus | LifecycleRuntime |
| HealthStatus | RuntimeKernel |
| DI Lifecycle | ContainerRuntime / ResolverRuntime / ProviderRuntime / ScopeRuntime |
| RuntimeContext | ContextRuntime |
| Session Lifecycle | SessionRuntime |
| Pipeline Lifecycle | ExecutorRuntime |
| Pipeline Stage Lifecycle | ExecutorRuntime |

Ownership is immutable.

---

# Transition Integrity Rules

Wave 1 guarantees:

1. Every transition is explicitly documented.
2. Every transition has one owner runtime.
3. Every successful transition emits exactly one RuntimeEvent.
4. Every transition is atomic.
5. Terminal states cannot transition back.
6. Illegal transitions raise lifecycle exceptions.
7. Transition order is deterministic.

Violating any rule is an Architecture Conflict.

---

# Definition of Done — Part 5

Part 5 is complete only if:

- [x] RuntimeStatus transition matrix defined.
- [x] Health transition matrix defined.
- [x] DI lifecycle transition matrix defined.
- [x] DI scope lifecycle matrix defined.
- [x] RuntimeContext lifecycle matrix defined.
- [x] Session lifecycle matrix defined.
- [x] Pipeline lifecycle matrix defined.
- [x] Pipeline stage lifecycle matrix defined.
- [x] Lifecycle hook transition matrix defined.
- [x] Transition integrity rules defined.

---

**Document Status**

IN PROGRESS — Part 5 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 6 — Runtime Event Propagation Graph -->
<!-- ========================================================================= -->

# Runtime Event Propagation Graph

**Owner Runtime**

EventBus Runtime

**Source Modules**

- `src/kernel/runtime/bus.py`
- `src/kernel/runtime/publisher.py`
- `src/kernel/runtime/dispatcher.py`
- `src/kernel/runtime/subscriber.py`

**Related KR**

KR-007 EventBus Runtime

---

# Purpose

This section defines the canonical propagation model for every RuntimeEvent inside
Wave 1.

Every runtime event follows exactly one propagation pipeline.

Propagation order, delivery guarantees and subscriber execution are immutable.

No runtime may bypass EventBusRuntime.

---

# Event Propagation Constitution

Runtime event propagation follows four immutable stages.

```text
Producer Runtime
       │
       ▼
PublisherRuntime
       │
       ▼
EventBusRuntime
       │
       ▼
DispatcherRuntime
       │
       ▼
SubscriberRuntime
```

Every RuntimeEvent passes through every stage exactly once.

---

## PROPAGATION-001 — Single Entry Point

Every RuntimeEvent enters the runtime through **PublisherRuntime.publish()**.

No runtime may inject RuntimeEvents directly into DispatcherRuntime.

Forbidden:

```python
dispatcher.dispatch(event)
```

Required:

```python
publisher.publish(event)
```

---

## PROPAGATION-002 — Immutable Transport

PublisherRuntime may attach metadata.

PublisherRuntime may never mutate payload after event creation.

---

## PROPAGATION-003 — Fan-Out Only

DispatcherRuntime performs fan-out delivery.

Subscribers never publish to each other directly.

---

## PROPAGATION-004 — No Bubbling

Runtime events do not bubble upward.

Propagation is always downstream.

---

# Canonical Propagation Pipeline

## Stage 1 — Event Creation

**Owner Runtime**

PublisherRuntime

**Input**

- RuntimeEvent
- RuntimeContext

**Output**

Immutable RuntimeEvent.

Responsibilities:

- validate event type;
- validate payload schema;
- attach RuntimeContext;
- assign priority;
- assign phase CREATE.

---

## Stage 2 — Queue Registration

**Owner Runtime**

EventBusRuntime

Responsibilities:

- enqueue RuntimeEvent;
- preserve FIFO ordering;
- preserve priority ordering;
- assign phase QUEUE.

No subscribers execute here.

---

## Stage 3 — Dispatch

**Owner Runtime**

DispatcherRuntime

Responsibilities:

- determine subscribers;
- execute subscriber ordering;
- assign phase DISPATCH.

Dispatcher never mutates RuntimeEvent.

---

## Stage 4 — Subscriber Execution

**Owner Runtime**

SubscriberRuntime

Responsibilities:

- execute handlers;
- read payload;
- read RuntimeContext;
- optionally publish new RuntimeEvents.

Subscribers never mutate received RuntimeEvent.

---

## Stage 5 — Completion

**Owner Runtime**

DispatcherRuntime

Responsibilities:

- mark COMPLETE;
- emit dispatch metrics;
- release dispatch resources.

If dispatch fails:

phase becomes FAILED.

---

# Event Fan-Out Model

DispatcherRuntime delivers one RuntimeEvent to N subscribers.

```text
RuntimeEvent
      │
      ├────────► Subscriber A
      │
      ├────────► Subscriber B
      │
      ├────────► Subscriber C
      │
      └────────► Subscriber D
```

Every subscriber receives the same immutable RuntimeEvent instance.

---

# Delivery Ordering Rules

Subscribers execute in deterministic order.

Ordering algorithm:

1. Registration order.
2. Stable ordering.
3. No parallel execution inside one RuntimeEvent.

Example:

```text
A
│
▼
B
│
▼
C
│
▼
D
```

Execution order never changes during dispatch.

---

# Fan-Out Guarantees

Dispatcher guarantees:

- each subscriber receives event once;
- subscribers cannot skip earlier subscribers;
- subscribers cannot reorder dispatch queue.

---

# Subscriber Registration Registry

Subscribers register by event type.

Example registry.

| Event Type | Subscribers |
|------------|-------------|
| runtime.started | LifecycleRuntime, DiagnosticsRuntime |
| context.created | SessionRuntime |
| pipeline.completed | OrchestratorRuntime, RuntimeKernel |
| pipeline.failed | RuntimeKernel, DiagnosticsRuntime |
| container.service.registered | DiagnosticsRuntime |

Registry is append-only.

---

# Subscription Resolution Algorithm

Dispatcher resolves subscribers in four steps.

## Step 1

Lookup event type.

## Step 2

Collect subscribers.

## Step 3

Sort by registration order.

## Step 4

Execute sequentially.

Resolution is deterministic.

---

# RuntimeContext Propagation Pipeline

RuntimeContext travels together with RuntimeEvent.

```text
ContextRuntime
      │
      ▼
PublisherRuntime
      │
      ▼
RuntimeEvent.trace
      │
      ▼
DispatcherRuntime
      │
      ▼
SubscriberRuntime
```

RuntimeContext is read-only during propagation.

---

# Trace Propagation Rules

Every propagated RuntimeEvent contains:

| Field | Required |
|-------|----------|
| trace_id | Yes |
| session_id | Yes |
| pipeline_id | Optional |
| module_id | Optional |

Trace fields never disappear during propagation.

---

# Context Merge Rules

PublisherRuntime merges metadata into RuntimeContext before dispatch.

Rules:

- existing keys preserved unless explicitly replaced;
- merge is immutable;
- subscriber receives merged snapshot.

Subscribers never merge context.

---

# Event Metadata Transport

RuntimeEvent metadata travels separately from payload.

Metadata contains:

| Metadata Field | Purpose |
|---------------|---------|
| event_id | Unique event identifier. |
| timestamp | Creation timestamp. |
| priority | Dispatch priority. |
| phase | Current propagation phase. |
| producer_runtime | Runtime that emitted event. |

Metadata is immutable.

---

# Delivery Guarantee Registry

Wave 1 delivery guarantees.

| Guarantee | Supported |
|-----------|-----------|
| At Most Once | Yes |
| At Least Once | No |
| Exactly Once | Within one runtime process only |
| Ordered Delivery | Yes |
| Durable Queue | No |
| Persistent Replay | No |

Wave 1 EventBus is in-memory only.

---

# Event Replay Policy

Replay is unsupported.

Reasons:

- runtime events describe live runtime state;
- replay would duplicate lifecycle transitions.

Future Wave versions may introduce replay for business events only.

---

# Event Deduplication Rules

DispatcherRuntime never deduplicates events.

Uniqueness is guaranteed by PublisherRuntime through `event_id`.

Duplicate `event_id` generation is architecture-breaking.

---

# Nested Event Publishing

Subscribers may publish new RuntimeEvents.

Canonical flow:

```text
Subscriber
     │
     ▼
PublisherRuntime.publish()
     │
     ▼
New RuntimeEvent
```

Nested RuntimeEvents enter a new propagation pipeline.

---

## Nested Publishing Rules

- parent RuntimeEvent remains immutable;
- child RuntimeEvent gets new `event_id`;
- child RuntimeEvent inherits RuntimeContext;
- child RuntimeEvent receives new timestamp.

---

# Propagation Boundary Rules

RuntimeEvent crosses runtime boundaries only through EventBusRuntime.

Allowed:

```text
ContainerRuntime
      │
      ▼
EventBusRuntime
      │
      ▼
LifecycleRuntime
```

Forbidden:

```text
ContainerRuntime
      │
      ▼
LifecycleRuntime
```

Direct runtime communication is prohibited.

---

# Cross-Runtime Propagation Matrix

| Producer | Allowed Consumers |
|----------|-------------------|
| LifecycleRuntime | RuntimeKernel, DiagnosticsRuntime |
| ContainerRuntime | RuntimeKernel, DiagnosticsRuntime |
| ContextRuntime | SessionRuntime, ExecutorRuntime |
| SessionRuntime | ContextRuntime |
| ExecutorRuntime | RuntimeKernel, OrchestratorRuntime |
| BootstrapRuntime | RuntimeKernel |

Communication is event-driven only.

---

# Dispatch Failure Propagation

Failure path.

```text
DispatcherRuntime
      │
      ▼
Subscriber Exception
      │
      ▼
eventbus.dispatch.failed
      │
      ▼
Remaining Subscriber Policy
```

Failure handling follows Part 4 subscriber policy.

---

# Event Cancellation Rules

RuntimeEvent dispatch cannot be cancelled after DISPATCH phase begins.

Cancellation is allowed only while event is queued.

Queue cancellation produces no RuntimeEvent.

---

# Event Completion Guarantees

Dispatcher marks COMPLETE only if:

- all required subscribers executed;
- failure policy satisfied;
- RuntimeContext propagated successfully;
- payload remained immutable.

Otherwise phase becomes FAILED.

---

# Event Lifetime Timeline

```text
CREATE
   │
QUEUE
   │
DISPATCH
   │
HANDLE
   │
COMPLETE
```

FAILED replaces COMPLETE when dispatch terminates unsuccessfully.

---

# Event Visibility Registry

| Runtime | Can Read Payload | Can Read Context | Can Mutate Event |
|---------|------------------|------------------|------------------|
| PublisherRuntime | Yes | Yes | Before publish only |
| EventBusRuntime | Yes | Yes | No |
| DispatcherRuntime | Yes | Yes | Phase only |
| SubscriberRuntime | Yes | Yes | No |
| RuntimeKernel | Yes | Yes | No |

Mutation ownership is immutable.

---

# Event Propagation Integrity Rules

Wave 1 guarantees:

1. Every RuntimeEvent enters through PublisherRuntime.
2. Every RuntimeEvent passes through EventBusRuntime exactly once.
3. DispatcherRuntime performs deterministic fan-out.
4. Subscribers receive immutable RuntimeEvents.
5. RuntimeContext propagates unchanged.
6. Nested events create new propagation pipelines.
7. Direct runtime-to-runtime event delivery is forbidden.
8. Delivery ordering is deterministic.
9. Replay is unsupported.
10. Duplicate event IDs are forbidden.

Violating any rule is an Architecture Conflict.

---

# Definition of Done — Part 6

Part 6 is complete only if:

- [x] Canonical propagation pipeline defined.
- [x] Fan-out model defined.
- [x] Subscriber ordering defined.
- [x] RuntimeContext propagation defined.
- [x] Delivery guarantees defined.
- [x] Nested publishing defined.
- [x] Cross-runtime propagation matrix defined.
- [x] Dispatch failure propagation defined.
- [x] Event visibility registry defined.
- [x] Propagation integrity rules defined.

---

**Document Status**

IN PROGRESS — Part 6 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 7 — Runtime Context & Trace Propagation Registry -->
<!-- ========================================================================= -->

# Runtime Context & Trace Propagation Registry

**Owner Runtime**

Context Runtime

**Source Modules**

- `src/kernel/contracts/context.py`
- `src/kernel/runtime/context.py`
- `src/kernel/runtime/session.py`
- `src/kernel/runtime/metadata.py`

**Related KR**

KR-008 Runtime Context Runtime

---

# Purpose

RuntimeContext is the canonical execution context shared across every runtime
subsystem during pipeline execution.

This section defines:

- RuntimeContext schema.
- TraceContext schema.
- metadata ownership.
- propagation rules.
- inheritance rules.
- isolation rules.
- correlation rules.
- lifecycle rules.

RuntimeContext is immutable during propagation.

---

# Context Architecture

Canonical ownership graph.

```text
RuntimeContext
      │
      ├──────── TraceContext
      │
      └──────── Metadata
```

ContextRuntime owns RuntimeContext.

MetadataRuntime owns metadata mutation.

SessionRuntime owns storage.

---

## CONTEXT-001 — Context Is Immutable During Propagation

After RuntimeContext enters EventBusRuntime it becomes immutable.

Only MetadataRuntime may create a new RuntimeContext snapshot.

Mutation is forbidden.

---

## CONTEXT-002 — Trace Is Immutable

TraceContext is immutable.

Every child RuntimeEvent inherits TraceContext.

---

## CONTEXT-003 — Metadata Uses Copy-On-Write

Metadata updates create a new RuntimeContext snapshot.

Existing snapshots remain unchanged.

---

# RuntimeContext Schema

**Canonical Dataclass**

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
    <table-cell>**Required**</table-cell>
  </table-row>
  <table-row><table-cell>trace</table-cell><table-cell>TraceContext</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>SessionId</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId \| None</table-cell><table-cell>No</table-cell></table-row>
  <table-row><table-cell>module_id</table-cell><table-cell>ModuleId \| None</table-cell><table-cell>No</table-cell></table-row>
  <table-row><table-cell>metadata</table-cell><table-cell>Mapping[str, Any]</table-cell><table-cell>Yes</table-cell></table-row>
</table>

Field set is immutable.

---

# TraceContext Schema

**Canonical Dataclass**

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
    <table-cell>**Required**</table-cell>
  </table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>TraceId</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>parent_trace_id</table-cell><table-cell>TraceId \| None</table-cell><table-cell>No</table-cell></table-row>
  <table-row><table-cell>root_trace_id</table-cell><table-cell>TraceId</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>span_depth</table-cell><table-cell>int</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>created_at</table-cell><table-cell>datetime</table-cell><table-cell>Yes</table-cell></table-row>
</table>

TraceContext is immutable.

---

# Trace Identifier Registry

| Identifier | Owner | Lifetime |
|------------|-------|----------|
| trace_id | ContextRuntime | One RuntimeEvent chain. |
| root_trace_id | ContextRuntime | Entire execution tree. |
| parent_trace_id | PublisherRuntime | Parent RuntimeEvent only. |

Identifiers never change after creation.

---

# Trace Generation Rules

ContextRuntime generates identifiers.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Identifier**</table-cell>
    <table-cell>**Generation Rule**</table-cell>
  </table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>UUIDv7.</table-cell></table-row>
  <table-row><table-cell>root_trace_id</table-cell><table-cell>UUIDv7 created once per root execution.</table-cell></table-row>
  <table-row><table-cell>parent_trace_id</table-cell><table-cell>Copied from parent RuntimeEvent trace_id.</table-cell></table-row>
</table>

Generation ownership is immutable.

---

# Trace Tree Model

Nested RuntimeEvents create a trace tree.

```text
root_trace_id
      │
      ▼
trace A
      │
      ├──────── trace B
      │
      ├──────── trace C
      │
      └──────── trace D
```

All child traces share the same root_trace_id.

---

# Span Depth Rules

<table columnSizing="equal">
  <table-row>
    <table-cell>**RuntimeEvent**</table-cell>
    <table-cell>**span_depth**</table-cell>
  </table-row>
  <table-row><table-cell>Root RuntimeEvent</table-cell><table-cell>0</table-cell></table-row>
  <table-row><table-cell>Child RuntimeEvent</table-cell><table-cell>1</table-cell></table-row>
  <table-row><table-cell>Grandchild RuntimeEvent</table-cell><table-cell>2</table-cell></table-row>
</table>

Depth increments exactly by one.

---

# Metadata Registry

Metadata belongs exclusively to MetadataRuntime.

Metadata is a mapping.

Allowed value types:

- str
- int
- float
- bool
- UUID
- datetime
- list
- dict
- None

Objects are forbidden.

---

# Reserved Metadata Keys

Wave 1 reserves the following metadata keys.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Key**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row><table-cell>environment</table-cell><table-cell>Runtime environment.</table-cell></table-row>
  <table-row><table-cell>architecture_version</table-cell><table-cell>Bible version.</table-cell></table-row>
  <table-row><table-cell>kernel_version</table-cell><table-cell>Kernel version.</table-cell></table-row>
  <table-row><table-cell>request_id</table-cell><table-cell>External request identifier.</table-cell></table-row>
  <table-row><table-cell>user_id</table-cell><table-cell>External caller identifier.</table-cell></table-row>
  <table-row><table-cell>locale</table-cell><table-cell>Execution locale.</table-cell></table-row>
  <table-row><table-cell>timezone</table-cell><table-cell>Execution timezone.</table-cell></table-row>
</table>

These keys may not be repurposed.

---

# Metadata Ownership Rules

<table columnSizing="equal">
  <table-row>
    <table-cell>**Operation**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row><table-cell>Create metadata</table-cell><table-cell>MetadataRuntime</table-cell></table-row>
  <table-row><table-cell>Replace metadata snapshot</table-cell><table-cell>MetadataRuntime</table-cell></table-row>
  <table-row><table-cell>Read metadata</table-cell><table-cell>All runtimes</table-cell></table-row>
  <table-row><table-cell>Store metadata</table-cell><table-cell>SessionRuntime</table-cell></table-row>
</table>

Metadata ownership never overlaps.

---

# Metadata Update Rules

Updates follow copy-on-write.

Example.

```text
Context V1
    │
    ▼
Metadata Update
    │
    ▼
Context V2
```

Context V1 remains immutable.

---

# Context Inheritance Registry

RuntimeContext inheritance depends on execution boundary.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Boundary**</table-cell>
    <table-cell>**Inheritance Rule**</table-cell>
  </table-row>
  <table-row><table-cell>Nested RuntimeEvent</table-cell><table-cell>Full inheritance.</table-cell></table-row>
  <table-row><table-cell>Pipeline Stage</table-cell><table-cell>Pipeline inherits parent RuntimeContext.</table-cell></table-row>
  <table-row><table-cell>New Session</table-cell><table-cell>New RuntimeContext created.</table-cell></table-row>
  <table-row><table-cell>Bootstrap Runtime</table-cell><table-cell>Creates root RuntimeContext.</table-cell></table-row>
</table>

---

# Context Propagation Matrix

<table columnSizing="equal">
  <table-row>
    <table-cell>**Producer Runtime**</table-cell>
    <table-cell>**Propagation Behaviour**</table-cell>
  </table-row>
  <table-row><table-cell>BootstrapRuntime</table-cell><table-cell>Create root RuntimeContext.</table-cell></table-row>
  <table-row><table-cell>ContainerRuntime</table-cell><table-cell>Read-only.</table-cell></table-row>
  <table-row><table-cell>LifecycleRuntime</table-cell><table-cell>Read-only.</table-cell></table-row>
  <table-row><table-cell>EventBusRuntime</table-cell><table-cell>Transport only.</table-cell></table-row>
  <table-row><table-cell>ExecutorRuntime</table-cell><table-cell>Attach pipeline_id.</table-cell></table-row>
  <table-row><table-cell>OrchestratorRuntime</table-cell><table-cell>Read-only.</table-cell></table-row>
</table>

Only ContextRuntime creates new snapshots.

---

# Context Boundary Registry

## Runtime Boundary

Same RuntimeContext instance.

## Session Boundary

New RuntimeContext.

## Pipeline Boundary

Inherited RuntimeContext plus pipeline_id.

## Module Boundary

Inherited RuntimeContext plus module_id.

---

# Pipeline Context Enrichment

ExecutorRuntime enriches RuntimeContext before stage execution.

Added fields.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Owner**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>ExecutorRuntime</table-cell></table-row>
  <table-row><table-cell>stage_id</table-cell><table-cell>ExecutorRuntime metadata.</table-cell></table-row>
  <table-row><table-cell>module_id</table-cell><table-cell>ExecutorRuntime metadata.</table-cell></table-row>
</table>

Enrichment creates a new RuntimeContext snapshot.

---

# Context Isolation Rules

RuntimeContexts are isolated between sessions.

```text
Session A Context
        │
        ▼
Pipeline A

Session B Context
        │
        ▼
Pipeline B
```

No shared mutable metadata exists.

---

# Session Context Registry

SessionRuntime stores RuntimeContext snapshots.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Session State**</table-cell>
    <table-cell>**Context Behaviour**</table-cell>
  </table-row>
  <table-row><table-cell>CREATED</table-cell><table-cell>Create RuntimeContext.</table-cell></table-row>
  <table-row><table-cell>ACTIVE</table-cell><table-cell>Context available.</table-cell></table-row>
  <table-row><table-cell>IDLE</table-cell><table-cell>Context retained.</table-cell></table-row>
  <table-row><table-cell>EXPIRED</table-cell><table-cell>Context frozen.</table-cell></table-row>
  <table-row><table-cell>REMOVED</table-cell><table-cell>Context destroyed.</table-cell></table-row>
</table>

---

# Context Cleanup Rules

ContextRuntime clears RuntimeContext only after:

- session removal;
- runtime shutdown;
- bootstrap failure cleanup.

Pipeline completion does not clear session context.

---

# Trace Correlation Registry

Trace correlation fields appear in:

| System | Required Fields |
|--------|-----------------|
| RuntimeEvent | trace_id, session_id |
| Logger | trace_id, session_id, pipeline_id |
| Diagnostics | trace_id |
| Exceptions | trace_id |
| Metrics | trace_id |

Correlation identifiers are consistent everywhere.

---

# Logging Correlation Rules

Every runtime log record contains:

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Required**</table-cell>
  </table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>Optional</table-cell></table-row>
  <table-row><table-cell>module_id</table-cell><table-cell>Optional</table-cell></table-row>
</table>

Logger never generates correlation identifiers.

---

# Exception Correlation Rules

Every ArchitectureException contains:

- trace_id
- session_id
- pipeline_id (optional)
- module_id (optional)

Exception correlation is mandatory.

---

# Context Serialization Rules

RuntimeContext is JSON serializable.

Forbidden metadata values:

- open file handles;
- sockets;
- coroutine objects;
- runtime instances;
- service instances.

Serialization must always succeed.

---

# Context Integrity Rules

Wave 1 guarantees:

1. RuntimeContext has one owner runtime.
2. TraceContext is immutable.
3. Metadata uses copy-on-write snapshots.
4. RuntimeEvents inherit RuntimeContext.
5. Sessions isolate RuntimeContext.
6. Pipelines enrich RuntimeContext without mutation.
7. Logging uses RuntimeContext for correlation.
8. Exceptions carry trace identifiers.
9. RuntimeContext serialization is deterministic.
10. Metadata keys are append-only.

Violating any rule is an Architecture Conflict.

---

# Definition of Done — Part 7

Part 7 is complete only if:

- [x] RuntimeContext schema defined.
- [x] TraceContext schema defined.
- [x] Metadata registry defined.
- [x] Trace generation rules defined.
- [x] Context inheritance registry defined.
- [x] Context propagation matrix defined.
- [x] Context isolation rules defined.
- [x] Logging correlation rules defined.
- [x] Exception correlation rules defined.
- [x] Context integrity rules defined.

---

**Document Status**

IN PROGRESS — Part 7 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 8 — Pipeline Execution Timeline & Runtime Timeline Registry -->
<!-- ========================================================================= -->

# Pipeline Execution Timeline Registry

**Owner Runtime**

Pipeline Runtime

**Primary Runtime**

ExecutorRuntime

**Coordinator Runtime**

OrchestratorRuntime

**Related KR**

KR-009 Pipeline Runtime

---

# Purpose

This section defines the complete execution timeline of every pipeline executed
inside Wave 1.

Every pipeline follows the exact same execution sequence.

No runtime may skip, reorder or repeat timeline phases.

---

# Pipeline Execution Constitution

Pipeline execution consists of nine immutable phases.

```text
REQUEST
   │
REGISTER
   │
VALIDATE
   │
QUEUE
   │
START
   │
EXECUTE STAGES
   │
COMPLETE / FAIL / CANCEL
   │
STOP
   │
DESTROY PIPELINE SCOPE
```

This order is immutable.

---

## PIPELINE-001 — One Execution Context

Each pipeline execution owns exactly one:

- PipelineId
- RuntimeContext snapshot
- Pipeline DI Scope
- Execution Timeline

---

## PIPELINE-002 — Stage Order Is Deterministic

Pipeline stages execute strictly according to PipelineDefinition.

Parallel execution is not supported in Wave 1.

---

## PIPELINE-003 — Pipeline Scope Isolation

Every pipeline owns one isolated PIPELINE DI scope.

The scope is destroyed immediately after pipeline completion.

---

# Canonical Pipeline Timeline

<table columnSizing="equal">
  <table-row>
    <table-cell>**Phase**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
    <table-cell>**Runtime Event**</table-cell>
  </table-row>
  <table-row><table-cell>Execution Requested</table-cell><table-cell>OrchestratorRuntime</table-cell><table-cell>`orchestrator.pipeline.execution.requested`</table-cell></table-row>
  <table-row><table-cell>Pipeline Created</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>`pipeline.created`</table-cell></table-row>
  <table-row><table-cell>Pipeline Validated</table-cell><table-cell>ManifestRuntime</table-cell><table-cell>`pipeline.validated`</table-cell></table-row>
  <table-row><table-cell>Pipeline Queued</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>`pipeline.queued`</table-cell></table-row>
  <table-row><table-cell>Pipeline Started</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>`pipeline.started`</table-cell></table-row>
  <table-row><table-cell>Stage Started</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>`pipeline.stage.started`</table-cell></table-row>
  <table-row><table-cell>Stage Completed</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>`pipeline.stage.completed`</table-cell></table-row>
  <table-row><table-cell>Pipeline Completed</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>`pipeline.completed`</table-cell></table-row>
  <table-row><table-cell>Pipeline Failed</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>`pipeline.failed`</table-cell></table-row>
  <table-row><table-cell>Pipeline Cancelled</table-cell><table-cell>ExecutorRuntime</table-cell><table-cell>`pipeline.cancelled`</table-cell></table-row>
</table>

---

# Timeline Phase 1 — Execution Requested

**Producer Runtime**

OrchestratorRuntime

**Event**

`orchestrator.pipeline.execution.requested`

Responsibilities:

- receive execution request;
- resolve PipelineDefinition;
- allocate PipelineId;
- forward request to ExecutorRuntime.

No pipeline state exists before this phase.

---

# Timeline Phase 2 — Pipeline Creation

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.created`

Responsibilities:

- create execution object;
- allocate execution timestamps;
- create Pipeline RuntimeContext snapshot.

State transition:

```text
None
   │
   ▼
CREATED
```

---

# Timeline Phase 3 — Manifest Validation

**Producer Runtime**

ManifestRuntime

**Event**

`pipeline.validated`

Validation includes:

- stage graph;
- module existence;
- dependency ordering;
- duplicate stage detection;
- manifest version validation.

Transition:

```text
CREATED
   │
   ▼
VALIDATED
```

Validation failure terminates execution.

---

# Timeline Phase 4 — Queue Registration

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.queued`

Responsibilities:

- enqueue pipeline;
- assign queue timestamp;
- assign queue position.

Transition:

```text
VALIDATED
   │
   ▼
QUEUED
```

---

# Timeline Phase 5 — Pipeline Startup

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.started`

Responsibilities:

- create Pipeline DI Scope;
- activate RuntimeContext snapshot;
- publish pipeline start event.

Transition:

```text
QUEUED
   │
   ▼
EXECUTING
```

---

# Pipeline Scope Creation Timeline

During startup.

```text
Pipeline Started
      │
      ▼
container.scope.created
      │
      ▼
PIPELINE Scope ACTIVE
```

Owner:

ScopeRuntime.

---

# RuntimeContext Enrichment Timeline

ExecutorRuntime enriches RuntimeContext before first stage.

Additional context values:

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Source**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>ExecutorRuntime</table-cell></table-row>
  <table-row><table-cell>execution_started_at</table-cell><table-cell>ExecutorRuntime metadata.</table-cell></table-row>
  <table-row><table-cell>stage_count</table-cell><table-cell>PipelineDefinition.</table-cell></table-row>
</table>

Creates new RuntimeContext snapshot.

---

# Stage Execution Timeline

Each stage executes independently.

```text
Stage Created
      │
      ▼
pipeline.stage.started
      │
      ▼
Module Execute
      │
      ▼
pipeline.stage.completed
```

Failure path.

```text
pipeline.stage.started
      │
      ▼
Module Execute
      │
      ▼
pipeline.stage.failed
```

---

# Stage Execution Ownership

<table columnSizing="equal">
  <table-row>
    <table-cell>**Step**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row><table-cell>Prepare Stage Context</table-cell><table-cell>ExecutorRuntime</table-cell></table-row>
  <table-row><table-cell>Resolve Stage Dependencies</table-cell><table-cell>ContainerRuntime</table-cell></table-row>
  <table-row><table-cell>Execute Module</table-cell><table-cell>ExecutorRuntime</table-cell></table-row>
  <table-row><table-cell>Publish Stage Event</table-cell><table-cell>PublisherRuntime</table-cell></table-row>
</table>

Ownership never overlaps.

---

# Stage RuntimeContext Snapshot

Every stage receives a derived RuntimeContext.

Inherited:

- trace_id
- root_trace_id
- session_id
- pipeline_id

Added metadata:

- stage_id
- module_id
- stage_index

Snapshot is immutable.

---

# Stage Dependency Resolution Timeline

```text
Stage Started
      │
      ▼
ResolverRuntime
      │
      ▼
ProviderRuntime
      │
      ▼
Module Instance
      │
      ▼
Execute()
```

Transient services are destroyed immediately after execution.

---

# Stage Completion Timeline

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.stage.completed`

Responsibilities:

- record duration;
- publish completion;
- release transient scope.

---

# Stage Failure Timeline

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.stage.failed`

Responsibilities:

- record exception;
- publish failure;
- terminate pipeline execution.

Pipeline enters FAILED immediately.

---

# Stage Skip Timeline

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.stage.skipped`

Reasons:

- dependency disabled;
- conditional execution false;
- previous failure cancelled execution.

Skipped stages never execute later.

---

# Pipeline Completion Timeline

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.completed`

Responsibilities:

- compute duration;
- publish completion;
- destroy Pipeline Scope.

Transition:

```text
EXECUTING
   │
   ▼
COMPLETED
```

---

# Pipeline Failure Timeline

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.failed`

Responsibilities:

- publish failure;
- destroy Pipeline Scope;
- preserve RuntimeContext snapshot.

Transition:

```text
EXECUTING
   │
   ▼
FAILED
```

---

# Pipeline Cancellation Timeline

**Producer Runtime**

ExecutorRuntime

**Event**

`pipeline.cancelled`

Cancellation allowed only before completion.

Transition:

```text
QUEUED
   │
   ▼
CANCELLED
```

or

```text
EXECUTING
   │
   ▼
CANCELLED
```

---

# Pipeline Scope Destruction Timeline

After completion, failure or cancellation.

```text
Pipeline Finished
      │
      ▼
container.scope.destroyed
      │
      ▼
PIPELINE Scope DESTROYED
```

Scope destruction is mandatory.

---

# RuntimeContext Cleanup Timeline

Pipeline completion never clears Session RuntimeContext.

Cleanup order:

```text
Pipeline Scope Destroyed
      │
      ▼
Stage Metadata Removed
      │
      ▼
Pipeline Metadata Removed
      │
      ▼
Session Context Remains
```

---

# Execution Duration Registry

ExecutorRuntime records four canonical durations.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Duration**</table-cell>
    <table-cell>**Meaning**</table-cell>
  </table-row>
  <table-row><table-cell>queue_duration_ms</table-cell><table-cell>Queued → Started.</table-cell></table-row>
  <table-row><table-cell>execution_duration_ms</table-cell><table-cell>Started → Completed.</table-cell></table-row>
  <table-row><table-cell>stage_duration_ms</table-cell><table-cell>Stage execution time.</table-cell></table-row>
  <table-row><table-cell>total_duration_ms</table-cell><table-cell>Created → Finished.</table-cell></table-row>
</table>

Durations are immutable metrics.

---

# Pipeline Timeline Guarantees

Wave 1 guarantees:

1. One PipelineId per execution.
2. One RuntimeContext snapshot per execution.
3. One Pipeline Scope per execution.
4. Deterministic stage ordering.
5. One completion event.
6. One failure event maximum.
7. Scope destruction after terminal state.
8. RuntimeContext preserved until session cleanup.

---

# Pipeline Event Timeline Diagram

```text
Execution Requested
        │
        ▼
Pipeline Created
        │
        ▼
Pipeline Validated
        │
        ▼
Pipeline Queued
        │
        ▼
Pipeline Started
        │
        ▼
Stage Started
        │
        ▼
Stage Completed
        │
        ▼
Next Stage ...
        │
        ▼
Pipeline Completed
        │
        ▼
Pipeline Scope Destroyed
```

Failure replaces completion branch.

---

# Pipeline Terminal State Rules

Terminal pipeline states:

- COMPLETED
- FAILED
- CANCELLED

Terminal states:

- emit exactly one terminal event;
- destroy Pipeline Scope;
- never transition again.

---

# Execution Integrity Rules

Wave 1 guarantees:

1. Validation happens before queueing.
2. Queueing happens before execution.
3. Pipeline Scope exists only during execution.
4. RuntimeContext enrichment happens before first stage.
5. Every stage receives immutable RuntimeContext.
6. Transient services never outlive a stage.
7. Pipeline Scope never outlives pipeline execution.
8. Terminal states are irreversible.
9. Exactly one terminal RuntimeEvent exists.
10. Timeline order is deterministic.

Violating any rule is an Architecture Conflict.

---

# Definition of Done — Part 8

Part 8 is complete only if:

- [x] Canonical execution timeline defined.
- [x] Pipeline scope lifecycle defined.
- [x] RuntimeContext enrichment timeline defined.
- [x] Stage execution timeline defined.
- [x] Stage failure timeline defined.
- [x] Pipeline completion timeline defined.
- [x] Pipeline cancellation timeline defined.
- [x] Pipeline scope destruction defined.
- [x] Duration registry defined.
- [x] Timeline integrity rules defined.

---

**Document Status**

IN PROGRESS — Part 8 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 9 — Failure & Recovery Registry -->
<!-- ========================================================================= -->

# Failure & Recovery Registry

**Owner Runtime**

Runtime Kernel

**Primary Runtime**

LifecycleRuntime

**Related KR**

- KR-001 Runtime Kernel
- KR-005 Lifecycle Runtime
- KR-007 EventBus Runtime
- KR-009 Pipeline Runtime

---

# Purpose

This registry defines the canonical failure model for Wave 1.

It specifies:

- runtime failure categories;
- failure ownership;
- propagation rules;
- recovery policy;
- cleanup order;
- terminal failure behaviour.

Every runtime failure follows this registry.

---

# Failure Constitution

## FAILURE-001 — Failures Are Explicit Runtime States

Failures are represented through:

- RuntimeStatus = FAILED
- HealthStatus = FAILED
- PipelineState = FAILED
- StageState = FAILED

No hidden failure state exists.

---

## FAILURE-002 — Failure Ownership Is Unique

Every failure has exactly one runtime owner.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Failure Category**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row><table-cell>Runtime lifecycle failure</table-cell><table-cell>LifecycleRuntime</table-cell></table-row>
  <table-row><table-cell>Bootstrap failure</table-cell><table-cell>BootstrapRuntime</table-cell></table-row>
  <table-row><table-cell>Pipeline failure</table-cell><table-cell>ExecutorRuntime</table-cell></table-row>
  <table-row><table-cell>Stage failure</table-cell><table-cell>ExecutorRuntime</table-cell></table-row>
  <table-row><table-cell>DI failure</table-cell><table-cell>ContainerRuntime</table-cell></table-row>
  <table-row><table-cell>Dispatch failure</table-cell><table-cell>DispatcherRuntime</table-cell></table-row>
  <table-row><table-cell>Health failure</table-cell><table-cell>RuntimeKernel</table-cell></table-row>
</table>

Ownership never overlaps.

---

## FAILURE-003 — Every Failure Emits Exactly One Failure Event

Every terminal failure produces one canonical RuntimeEvent.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Failure**</table-cell>
    <table-cell>**Runtime Event**</table-cell>
  </table-row>
  <table-row><table-cell>Runtime failure</table-cell><table-cell>`runtime.failed`</table-cell></table-row>
  <table-row><table-cell>Bootstrap failure</table-cell><table-cell>`bootstrap.failed`</table-cell></table-row>
  <table-row><table-cell>Pipeline failure</table-cell><table-cell>`pipeline.failed`</table-cell></table-row>
  <table-row><table-cell>Stage failure</table-cell><table-cell>`pipeline.stage.failed`</table-cell></table-row>
  <table-row><table-cell>Dispatch failure</table-cell><table-cell>`eventbus.dispatch.failed`</table-cell></table-row>
  <table-row><table-cell>Health failure</table-cell><table-cell>`health.failed`</table-cell></table-row>
</table>

Failure events are unique.

---

# Runtime Failure Registry

## Runtime Failure Sources

Runtime may enter FAILED only from active lifecycle states.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Source RuntimeStatus**</table-cell>
    <table-cell>**Allowed Failure**</table-cell>
  </table-row>
  <table-row><table-cell>INITIALIZING</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>READY</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>STARTING</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>RUNNING</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>STOPPING</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>SHUTTING_DOWN</table-cell><table-cell>Yes</table-cell></table-row>
</table>

CREATED, TERMINATED and FAILED cannot fail again.

---

## Runtime Failure Payload

Canonical payload.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>runtime_status</table-cell><table-cell>RuntimeStatus</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>exception_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>recoverable</table-cell><table-cell>bool</table-cell></table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>TraceId</table-cell></table-row>
</table>

---

# Runtime Failure Cleanup Order

Runtime cleanup executes in deterministic order.

```text
Runtime FAILED
      │
      ▼
Stop accepting pipelines
      │
      ▼
Cancel active pipelines
      │
      ▼
Destroy Pipeline Scopes
      │
      ▼
Destroy Session Scopes
      │
      ▼
Destroy Application Scope
      │
      ▼
Runtime TERMINATED
```

Cleanup order is immutable.

---

# Bootstrap Failure Registry

## Bootstrap Failure Sources

Bootstrap may fail during:

- runtime construction;
- dependency registration;
- lifecycle initialization;
- manifest loading.

---

## Bootstrap Failure Behaviour

<table columnSizing="equal">
  <table-row>
    <table-cell>**Step**</table-cell>
    <table-cell>**Behaviour**</table-cell>
  </table-row>
  <table-row><table-cell>Publish `bootstrap.failed`</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>Destroy partially initialized services</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>Destroy Application Scope</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>Enter RuntimeStatus FAILED</table-cell><table-cell>Yes</table-cell></table-row>
</table>

Bootstrap never retries.

---

# Dependency Injection Failure Registry

## Resolution Failure

Occurs during RESOLVING lifecycle.

Causes:

- missing dependency;
- circular dependency;
- invalid provider.

Result:

- resolution aborted;
- service not constructed;
- ACTIVE state never reached.

---

## Construction Failure

Occurs during CONSTRUCTING.

Causes:

- constructor exception;
- provider exception;
- configuration exception.

Behaviour:

- publish `container.service.failed`;
- destroy partial instance;
- release transient dependencies.

---

## Initialization Failure

Occurs during INITIALIZED lifecycle.

Causes:

- initialize hook exception;
- invalid runtime state.

Behaviour:

- destroy instance;
- publish `container.service.failed`;
- service unavailable.

---

## DI Failure Cleanup

<table columnSizing="equal">
  <table-row>
    <table-cell>**Lifecycle State**</table-cell>
    <table-cell>**Cleanup**</table-cell>
  </table-row>
  <table-row><table-cell>RESOLVING</table-cell><table-cell>Release temporary dependency graph.</table-cell></table-row>
  <table-row><table-cell>CONSTRUCTING</table-cell><table-cell>Destroy partially built instance.</table-cell></table-row>
  <table-row><table-cell>INITIALIZED</table-cell><table-cell>Execute shutdown hooks if initialized.</table-cell></table-row>
</table>

---

# Pipeline Failure Registry

## Failure Sources

Pipeline fails because of:

- validation failure;
- stage failure;
- dependency resolution failure;
- module execution exception;
- runtime cancellation.

---

## Pipeline Failure Timeline

```text
Stage Failure
      │
      ▼
pipeline.stage.failed
      │
      ▼
pipeline.failed
      │
      ▼
Pipeline Scope Destroyed
```

Timeline is deterministic.

---

## Pipeline Failure Cleanup

ExecutorRuntime performs:

1. publish failure;
2. stop remaining stages;
3. destroy transient services;
4. destroy pipeline scope;
5. preserve session context.

---

## Pipeline Failure Payload

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>PipelineId</table-cell></table-row>
  <table-row><table-cell>failed_stage</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>exception_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>TraceId</table-cell></table-row>
</table>

---

# Stage Failure Registry

Stage failure is terminal for that stage.

Causes:

- module exception;
- dependency resolution failure;
- timeout (future versions only).

Behaviour:

- publish `pipeline.stage.failed`;
- stop module execution;
- propagate pipeline failure.

Stage recovery is unsupported.

---

# Event Dispatch Failure Registry

## Dispatch Failure Sources

Dispatcher failure occurs when:

- subscriber raises exception;
- dispatcher internal exception;
- invalid subscriber registry.

---

## Dispatch Failure Behaviour

<table columnSizing="equal">
  <table-row>
    <table-cell>**Priority**</table-cell>
    <table-cell>**Behaviour**</table-cell>
  </table-row>
  <table-row><table-cell>CRITICAL</table-cell><table-cell>Abort dispatch.</table-cell></table-row>
  <table-row><table-cell>HIGH</table-cell><table-cell>Continue remaining subscribers.</table-cell></table-row>
  <table-row><table-cell>NORMAL</table-cell><table-cell>Continue remaining subscribers.</table-cell></table-row>
  <table-row><table-cell>LOW</table-cell><table-cell>Log only.</table-cell></table-row>
</table>

Dispatch failure never mutates payload.

---

## Dispatch Failure Payload

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Type**</table-cell>
  </table-row>
  <table-row><table-cell>event_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>handler_name</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>exception_type</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>reason</table-cell><table-cell>str</table-cell></table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>TraceId</table-cell></table-row>
</table>

---

# Health Failure Registry

Health transitions are independent from RuntimeStatus.

```text
HEALTHY
    │
    ▼
DEGRADED
    │
    ▼
UNHEALTHY
    │
    ▼
FAILED
```

Health restoration:

```text
DEGRADED
    │
    ▼
HEALTHY
```

UNHEALTHY → HEALTHY is not allowed directly.

---

# Failure Propagation Matrix

<table columnSizing="equal">
  <table-row>
    <table-cell>**Failure Source**</table-cell>
    <table-cell>**Propagates To**</table-cell>
  </table-row>
  <table-row><table-cell>Stage failure</table-cell><table-cell>Pipeline failure.</table-cell></table-row>
  <table-row><table-cell>Pipeline failure</table-cell><table-cell>Runtime diagnostics.</table-cell></table-row>
  <table-row><table-cell>Bootstrap failure</table-cell><table-cell>Runtime failure.</table-cell></table-row>
  <table-row><table-cell>Dispatch failure</table-cell><table-cell>Diagnostics only.</table-cell></table-row>
  <table-row><table-cell>Health failure</table-cell><table-cell>Runtime monitoring.</table-cell></table-row>
</table>

Propagation ownership is immutable.

---

# Recoverable vs Terminal Failure Registry

<table columnSizing="equal">
  <table-row>
    <table-cell>**Failure Category**</table-cell>
    <table-cell>**Recoverable**</table-cell>
  </table-row>
  <table-row><table-cell>Runtime failure</table-cell><table-cell>No</table-cell></table-row>
  <table-row><table-cell>Bootstrap failure</table-cell><table-cell>No</table-cell></table-row>
  <table-row><table-cell>Pipeline failure</table-cell><table-cell>No (new execution required)</table-cell></table-row>
  <table-row><table-cell>Stage failure</table-cell><table-cell>No</table-cell></table-row>
  <table-row><table-cell>Dispatch failure</table-cell><table-cell>Yes (next event continues)</table-cell></table-row>
  <table-row><table-cell>Health degraded</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>Health unhealthy</table-cell><table-cell>Yes</table-cell></table-row>
</table>

Wave 1 runtime recovery is intentionally limited.

---

# Failure Cleanup Registry

<table columnSizing="equal">
  <table-row>
    <table-cell>**Resource**</table-cell>
    <table-cell>**Cleanup Owner**</table-cell>
  </table-row>
  <table-row><table-cell>Pipeline Scope</table-cell><table-cell>ScopeRuntime</table-cell></table-row>
  <table-row><table-cell>Transient Services</table-cell><table-cell>ResolverRuntime</table-cell></table-row>
  <table-row><table-cell>Session Scope</table-cell><table-cell>SessionRuntime</table-cell></table-row>
  <table-row><table-cell>Application Scope</table-cell><table-cell>ContainerRuntime</table-cell></table-row>
  <table-row><table-cell>RuntimeContext</table-cell><table-cell>ContextRuntime</table-cell></table-row>
</table>

Cleanup ownership never overlaps.

---

# Failure Logging Requirements

Every failure log must contain:

<table columnSizing="equal">
  <table-row>
    <table-cell>**Field**</table-cell>
    <table-cell>**Required**</table-cell>
  </table-row>
  <table-row><table-cell>trace_id</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>session_id</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>pipeline_id</table-cell><table-cell>Optional</table-cell></table-row>
  <table-row><table-cell>module_id</table-cell><table-cell>Optional</table-cell></table-row>
  <table-row><table-cell>exception_type</table-cell><table-cell>Yes</table-cell></table-row>
  <table-row><table-cell>failure_category</table-cell><table-cell>Yes</table-cell></table-row>
</table>

Correlation fields are mandatory.

---

# Failure Metrics Registry

RuntimeKernel records:

| Metric | Description |
|--------|-------------|
| runtime_failures_total | Runtime failures. |
| pipeline_failures_total | Pipeline failures. |
| stage_failures_total | Stage failures. |
| dispatch_failures_total | Event dispatch failures. |
| di_failures_total | Dependency injection failures. |
| bootstrap_failures_total | Bootstrap failures. |

Metrics are append-only.

---

# Recovery Policy Registry

Wave 1 recovery policy.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Failure**</table-cell>
    <table-cell>**Recovery Behaviour**</table-cell>
  </table-row>
  <table-row><table-cell>Runtime FAILED</table-cell><table-cell>Shutdown required.</table-cell></table-row>
  <table-row><table-cell>Bootstrap FAILED</table-cell><table-cell>Restart runtime required.</table-cell></table-row>
  <table-row><table-cell>Pipeline FAILED</table-cell><table-cell>Create new pipeline execution.</table-cell></table-row>
  <table-row><table-cell>Stage FAILED</table-cell><table-cell>Create new pipeline execution.</table-cell></table-row>
  <table-row><table-cell>Dispatch FAILED</table-cell><table-cell>Next RuntimeEvent unaffected.</table-cell></table-row>
</table>

Automatic recovery is unsupported.

---

# Failure Integrity Rules

Wave 1 guarantees:

1. Every failure has one owner runtime.
2. Every terminal failure emits one RuntimeEvent.
3. Cleanup order is deterministic.
4. RuntimeContext survives until cleanup boundary.
5. Pipeline Scope is always destroyed.
6. Runtime recovery never mutates FAILED status.
7. Dispatch failures never corrupt EventBus state.
8. Recoverable health failures never restart runtime.
9. Metrics are recorded exactly once.
10. Recovery policy is deterministic.

Violating any rule is an Architecture Conflict.

---

# Definition of Done — Part 9

Part 9 is complete only if:

- [x] Failure constitution defined.
- [x] Runtime failure registry defined.
- [x] Bootstrap failure registry defined.
- [x] DI failure registry defined.
- [x] Pipeline failure registry defined.
- [x] Dispatch failure registry defined.
- [x] Cleanup registry defined.
- [x] Recovery policy defined.
- [x] Failure metrics defined.
- [x] Failure integrity rules defined.

---

**Document Status**

IN PROGRESS — Part 9 of 10.

<!-- ========================================================================= -->
<!-- M-05 PART 10 — Global Validation Registry & Canonical Completion -->
<!-- ========================================================================= -->

# Global Validation Registry

**Owner Runtime**

RuntimeKernel

**Authority**

Entire Runtime Kernel

**Related Documents**

- M-00 Development Constitution
- M-01 Canonical Architecture Index
- M-02 Runtime Graph
- M-03 API Registry
- M-04 Import Graph
- M-06 Module Specifications
- M-07 Implementation Rules
- M-08 Exception Registry
- M-09 Test Matrix
- M-10 Build Checklist
- M-11 Codex Master Prompt

---

# Purpose

This section defines the global validation rules that guarantee runtime integrity.

These rules are evaluated during:

- bootstrap validation;
- manifest validation;
- runtime initialization;
- pipeline execution;
- architecture audit;
- CI validation.

Every Wave 1 runtime implementation must satisfy every invariant defined below.

---

# Runtime Validation Constitution

## VALIDATION-001 — Registry Completeness

Every runtime state, lifecycle state, event, payload schema and transition must be defined in this document.

Undefined runtime entities are architecture violations.

---

## VALIDATION-002 — Registry Immutability

Canonical registry entries are immutable.

Allowed changes between architecture versions:

- append new registry entries;
- deprecate entries through ADR.

Forbidden:

- rename registry identifiers;
- reuse identifiers;
- change ownership.

---

## VALIDATION-003 — Validation Before Execution

Runtime validation completes before RuntimeStatus becomes RUNNING.

Pipeline execution is impossible before successful validation.

---

# Global Runtime Invariants

## RuntimeStatus Invariants

<table columnSizing="equal">
  <table-row>
    <table-cell>**Invariant ID**</table-cell>
    <table-cell>**Rule**</table-cell>
  </table-row>
  <table-row>
    <table-cell>RS-001</table-cell>
    <table-cell>Exactly one RuntimeStatus exists globally.</table-cell>
  </table-row>
  <table-row>
    <table-cell>RS-002</table-cell>
    <table-cell>RuntimeStatus has one mutable owner.</table-cell>
  </table-row>
  <table-row>
    <table-cell>RS-003</table-cell>
    <table-cell>RuntimeStatus transitions follow Part 5 only.</table-cell>
  </table-row>
  <table-row>
    <table-cell>RS-004</table-cell>
    <table-cell>FAILED is terminal.</table-cell>
  </table-row>
  <table-row>
    <table-cell>RS-005</table-cell>
    <table-cell>TERMINATED is terminal.</table-cell>
  </table-row>
</table>

---

## HealthStatus Invariants

<table columnSizing="equal">
  <table-row>
    <table-cell>**Invariant ID**</table-cell>
    <table-cell>**Rule**</table-cell>
  </table-row>
  <table-row>
    <table-cell>HS-001</table-cell>
    <table-cell>HealthStatus is independent from RuntimeStatus.</table-cell>
  </table-row>
  <table-row>
    <table-cell>HS-002</table-cell>
    <table-cell>Only RuntimeKernel evaluates health.</table-cell>
  </table-row>
  <table-row>
    <table-cell>HS-003</table-cell>
    <table-cell>Health restoration never changes RuntimeStatus automatically.</table-cell>
  </table-row>
</table>

---

## RuntimeContext Invariants

<table columnSizing="equal">
  <table-row>
    <table-cell>**Invariant ID**</table-cell>
    <table-cell>**Rule**</table-cell>
  </table-row>
  <table-row>
    <table-cell>CTX-001</table-cell>
    <table-cell>RuntimeContext always contains TraceContext.</table-cell>
  </table-row>
  <table-row>
    <table-cell>CTX-002</table-cell>
    <table-cell>RuntimeContext is immutable during propagation.</table-cell>
  </table-row>
  <table-row>
    <table-cell>CTX-003</table-cell>
    <table-cell>Metadata uses copy-on-write.</table-cell>
  </table-row>
  <table-row>
    <table-cell>CTX-004</table-cell>
    <table-cell>Every RuntimeEvent contains RuntimeContext.</table-cell>
  </table-row>
  <table-row>
    <table-cell>CTX-005</table-cell>
    <table-cell>Session contexts are isolated.</table-cell>
  </table-row>
</table>

---

## EventBus Invariants

<table columnSizing="equal">
  <table-row>
    <table-cell>**Invariant ID**</table-cell>
    <table-cell>**Rule**</table-cell>
  </table-row>
  <table-row>
    <table-cell>EV-001</table-cell>
    <table-cell>PublisherRuntime is the only event entry point.</table-cell>
  </table-row>
  <table-row>
    <table-cell>EV-002</table-cell>
    <table-cell>Every RuntimeEvent has a unique event_id.</table-cell>
  </table-row>
  <table-row>
    <table-cell>EV-003</table-cell>
    <table-cell>Payload is immutable.</table-cell>
  </table-row>
  <table-row>
    <table-cell>EV-004</table-cell>
    <table-cell>Priority ordering is deterministic.</table-cell>
  </table-row>
  <table-row>
    <table-cell>EV-005</table-cell>
    <table-cell>Dispatch ordering is deterministic.</table-cell>
  </table-row>
  <table-row>
    <table-cell>EV-006</table-cell>
    <table-cell>Replay is unsupported.</table-cell>
  </table-row>
  <table-row>
    <table-cell>EV-007</table-cell>
    <table-cell>Duplicate event IDs are forbidden.</table-cell>
  </table-row>
</table>

---

## Dependency Injection Invariants

<table columnSizing="equal">
  <table-row>
    <table-cell>**Invariant ID**</table-cell>
    <table-cell>**Rule**</table-cell>
  </table-row>
  <table-row>
    <table-cell>DI-001</table-cell>
    <table-cell>Every service has one DI scope.</table-cell>
  </table-row>
  <table-row>
    <table-cell>DI-002</table-cell>
    <table-cell>APPLICATION scope exists once.</table-cell>
  </table-row>
  <table-row>
    <table-cell>DI-003</table-cell>
    <table-cell>SESSION scope belongs to one session.</table-cell>
  </table-row>
  <table-row>
    <table-cell>DI-004</table-cell>
    <table-cell>PIPELINE scope belongs to one pipeline.</table-cell>
  </table-row>
  <table-row>
    <table-cell>DI-005</table-cell>
    <table-cell>TRANSIENT services are never cached.</table-cell>
  </table-row>
</table>

---

## Pipeline Invariants

<table columnSizing="equal">
  <table-row>
    <table-cell>**Invariant ID**</table-cell>
    <table-cell>**Rule**</table-cell>
  </table-row>
  <table-row>
    <table-cell>PL-001</table-cell>
    <table-cell>Every execution owns one PipelineId.</table-cell>
  </table-row>
  <table-row>
    <table-cell>PL-002</table-cell>
    <table-cell>Stage ordering is deterministic.</table-cell>
  </table-row>
  <table-row>
    <table-cell>PL-003</table-cell>
    <table-cell>Exactly one terminal event exists.</table-cell>
  </table-row>
  <table-row>
    <table-cell>PL-004</table-cell>
    <table-cell>Pipeline scope is destroyed after terminal state.</table-cell>
  </table-row>
  <table-row>
    <table-cell>PL-005</table-cell>
    <table-cell>RuntimeContext snapshot exists for every stage.</table-cell>
  </table-row>
</table>

---

# Cross-Registry Consistency Matrix

Every registry defined in M-05 must be referenced consistently.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Registry**</table-cell>
    <table-cell>**Referenced By**</table-cell>
  </table-row>
  <table-row>
    <table-cell>RuntimeStatus Registry</table-cell>
    <table-cell>M-02, M-06, M-07, M-10, M-11</table-cell>
  </table-row>
  <table-row>
    <table-cell>Event Registry</table-cell>
    <table-cell>M-06, M-07, M-08, M-09</table-cell>
  </table-row>
  <table-row>
    <table-cell>Payload Registry</table-cell>
    <table-cell>M-06, M-07</table-cell>
  </table-row>
  <table-row>
    <table-cell>Transition Registry</table-cell>
    <table-cell>M-08, M-09, M-10</table-cell>
  </table-row>
  <table-row>
    <table-cell>Failure Registry</table-cell>
    <table-cell>M-08, M-09, M-11</table-cell>
  </table-row>
  <table-row>
    <table-cell>Context Registry</table-cell>
    <table-cell>M-06, M-08, M-11</table-cell>
  </table-row>
</table>

No document may redefine registry values.

---

# Runtime Validation Checklist

Runtime initialization validates the following checklist before entering RUNNING.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Validation**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>Runtime graph valid.</table-cell>
    <table-cell>BootstrapRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Dependency graph acyclic.</table-cell>
    <table-cell>ContainerRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>All ServiceDescriptors registered.</table-cell>
    <table-cell>RegistryRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>RuntimeStatus registry initialized.</table-cell>
    <table-cell>LifecycleRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Event registry initialized.</table-cell>
    <table-cell>EventBusRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Subscriber registry initialized.</table-cell>
    <table-cell>DispatcherRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>RuntimeContext registry initialized.</table-cell>
    <table-cell>ContextRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Health registry initialized.</table-cell>
    <table-cell>RuntimeKernel</table-cell>
  </table-row>
</table>

Every validation must pass.

---

# Pipeline Validation Checklist

ExecutorRuntime validates before execution.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Validation**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>PipelineDefinition exists.</table-cell>
    <table-cell>ManifestRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Stage graph valid.</table-cell>
    <table-cell>ManifestRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Module dependencies satisfied.</table-cell>
    <table-cell>ContainerRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>RuntimeContext available.</table-cell>
    <table-cell>ContextRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>Pipeline Scope created.</table-cell>
    <table-cell>ScopeRuntime</table-cell>
  </table-row>
</table>

Validation failure prevents execution.

---

# Event Validation Checklist

PublisherRuntime validates every RuntimeEvent.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Validation**</table-cell>
    <table-cell>**Required**</table-cell>
  </table-row>
  <table-row>
    <table-cell>event_id present.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>event_type registered.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>payload schema valid.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>trace_id present.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>priority assigned.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>phase = CREATE.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
</table>

Invalid RuntimeEvents are rejected before entering EventBusRuntime.

---

# Failure Validation Checklist

LifecycleRuntime validates every terminal failure.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Validation**</table-cell>
    <table-cell>**Required**</table-cell>
  </table-row>
  <table-row>
    <table-cell>Failure owner exists.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Failure RuntimeEvent emitted.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Cleanup executed.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Terminal transition recorded.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
</table>

---

# Architecture Audit Checklist

Every CI architecture audit validates this document.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Audit Category**</table-cell>
    <table-cell>**Must Pass**</table-cell>
  </table-row>
  <table-row>
    <table-cell>Registry completeness.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Transition legality.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Payload schema completeness.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Ownership uniqueness.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Trace propagation invariants.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
  <table-row>
    <table-cell>Event propagation invariants.</table-cell>
    <table-cell>Yes</table-cell>
  </table-row>
</table>

Architecture audit is deterministic.

---

# Runtime Metrics Registry

RuntimeKernel publishes immutable runtime metrics.

## Lifecycle Metrics

<table columnSizing="equal">
  <table-row>
    <table-cell>**Metric**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>runtime_startups_total</table-cell>
    <table-cell>LifecycleRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>runtime_shutdowns_total</table-cell>
    <table-cell>LifecycleRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>runtime_failures_total</table-cell>
    <table-cell>LifecycleRuntime</table-cell>
  </table-row>
</table>

## EventBus Metrics

<table columnSizing="equal">
  <table-row>
    <table-cell>**Metric**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>events_published_total</table-cell>
    <table-cell>PublisherRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>events_dispatched_total</table-cell>
    <table-cell>DispatcherRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>dispatch_failures_total</table-cell>
    <table-cell>DispatcherRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>subscriber_invocations_total</table-cell>
    <table-cell>DispatcherRuntime</table-cell>
  </table-row>
</table>

## Pipeline Metrics

<table columnSizing="equal">
  <table-row>
    <table-cell>**Metric**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>pipelines_started_total</table-cell>
    <table-cell>ExecutorRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>pipelines_completed_total</table-cell>
    <table-cell>ExecutorRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>pipelines_failed_total</table-cell>
    <table-cell>ExecutorRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>pipeline_duration_ms</table-cell>
    <table-cell>ExecutorRuntime</table-cell>
  </table-row>
</table>

## Dependency Injection Metrics

<table columnSizing="equal">
  <table-row>
    <table-cell>**Metric**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row>
    <table-cell>services_registered_total</table-cell>
    <table-cell>RegistryRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>services_constructed_total</table-cell>
    <table-cell>ProviderRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>services_destroyed_total</table-cell>
    <table-cell>ScopeRuntime</table-cell>
  </table-row>
  <table-row>
    <table-cell>di_failures_total</table-cell>
    <table-cell>ContainerRuntime</table-cell>
  </table-row>
</table>

Metrics are append-only.

---

# Cross-Document Contract Registry

This document exports canonical contracts consumed elsewhere.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Exported Contract**</table-cell>
    <table-cell>**Consumed By**</table-cell>
  </table-row>
  <table-row>
    <table-cell>RuntimeStatus</table-cell>
    <table-cell>M-06 Module Specifications</table-cell>
  </table-row>
  <table-row>
    <table-cell>LifecycleState</table-cell>
    <table-cell>M-08 Exception Registry</table-cell>
  </table-row>
  <table-row>
    <table-cell>RuntimeEvent Catalog</table-cell>
    <table-cell>M-06 Module Specifications</table-cell>
  </table-row>
  <table-row>
    <table-cell>Payload Schemas</table-cell>
    <table-cell>M-07 Implementation Rules</table-cell>
  </table-row>
  <table-row>
    <table-cell>Transition Matrix</table-cell>
    <table-cell>M-08 Exception Registry</table-cell>
  </table-row>
  <table-row>
    <table-cell>Context Registry</table-cell>
    <table-cell>M-06, M-08</table-cell>
  </table-row>
  <table-row>
    <table-cell>Failure Registry</table-cell>
    <table-cell>M-11 Codex Master Prompt</table-cell>
  </table-row>
</table>

These contracts are the only source of truth.

---

# Canonical State/Event Audit Summary

## Registry Coverage Summary

<table columnSizing="equal">
  <table-row>
    <table-cell>**Registry Category**</table-cell>
    <table-cell>**Status**</table-cell>
  </table-row>
  <table-row>
    <table-cell>Runtime States</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Lifecycle States</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Health Registry</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>DI Lifecycle Registry</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>RuntimeContext Registry</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Session Registry</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Pipeline Registry</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Runtime Event Catalog</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Payload Registry</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Priority Registry</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Transition Matrix</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>Failure Registry</table-cell>
    <table-cell>COMPLETE</table-cell>
  </table-row>
</table>

Wave 1 registry coverage is complete.

---

# Canonical Guarantees

Wave 1 Runtime guarantees:

1. One canonical RuntimeStatus registry.
2. One canonical RuntimeEvent catalog.
3. One immutable payload schema per RuntimeEvent.
4. One deterministic transition matrix.
5. One immutable RuntimeContext propagation model.
6. One deterministic EventBus dispatch model.
7. One deterministic Pipeline execution timeline.
8. One deterministic failure propagation model.
9. One ownership model for every mutable runtime entity.
10. One canonical validation registry for CI and Architecture Audit.

These guarantees are normative.

---

# Definition of Done — M-05

`05_STATE_EVENT_DI_LIFECYCLE_REGISTRY.md` is complete only if:

- [x] Runtime State Registry complete.
- [x] Lifecycle Registry complete.
- [x] Health Registry complete.
- [x] DI Lifecycle Registry complete.
- [x] RuntimeContext Registry complete.
- [x] Session Lifecycle Registry complete.
- [x] Pipeline Lifecycle Registry complete.
- [x] Runtime Event Catalog complete.
- [x] Payload Schema Registry complete.
- [x] Event Priority Registry complete.
- [x] Event Phase Registry complete.
- [x] Lifecycle Transition Matrix complete.
- [x] Runtime Event Propagation Registry complete.
- [x] Runtime Context Propagation Registry complete.
- [x] Pipeline Execution Timeline complete.
- [x] Failure & Recovery Registry complete.
- [x] Validation Registry complete.
- [x] Metrics Registry complete.
- [x] Cross-document contract registry complete.

All Wave 1 runtime registries are defined.

---

# Canonical Completion Marker

<table columnSizing="equal">
  <table-row>
    <table-cell>**Document ID**</table-cell>
    <table-cell>M-05</table-cell>
  </table-row>
  <table-row>
    <table-cell>**Canonical File**</table-cell>
    <table-cell>`docs/architecture/master/05_STATE_EVENT_DI_LIFECYCLE_REGISTRY.md`</table-cell>
  </table-row>
  <table-row>
    <table-cell>**Version**</table-cell>
    <table-cell>1.1 CANONICAL</table-cell>
  </table-row>
  <table-row>
    <table-cell>**Status**</table-cell>
    <table-cell>CANONICAL COMPLETE</table-cell>
  </table-row>
  <table-row>
    <table-cell>**Runtime Layer**</table-cell>
    <table-cell>L0 Runtime Kernel</table-cell>
  </table-row>
  <table-row>
    <table-cell>**Authority**</table-cell>
    <table-cell>Architecture Bible — Source of Truth</table-cell>
  </table-row>
</table>

---

**END OF DOCUMENT — M-05 STATE / EVENT / DI / LIFECYCLE REGISTRY**