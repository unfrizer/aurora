# AURORA ENGINEERING BIBLE v1.1

Document ID: M-02

Document Name: Runtime Graph

Path:
docs/architecture/master/02_RUNTIME_GRAPH.md

Status: CANONICAL SOURCE OF TRUTH

Authority:
- AB-00 Development Constitution
- AB-00A Architecture Reconciliation
- M-00 Canonical Index
- M-01 File Registry

Version: 1.1 Canonical

---

# Purpose

This document defines the complete runtime topology of AURORA.

It is the canonical source of truth for:

- repository directory graph;
- runtime ownership graph;
- runtime communication graph;
- runtime creation graph;
- runtime dependency graph;
- startup graph;
- shutdown graph.

This document **does not** define implementation logic or public APIs.

Implementation belongs to M-06.

---

# Runtime Graph Constitution

Every runtime relationship inside AURORA must satisfy these invariants.

## Topology Invariants

1. Runtime communication is directional.
2. Runtime ownership is unique.
3. Runtime creation is deterministic.
4. Runtime destruction is deterministic.
5. Circular runtime ownership is forbidden.
6. Runtime dependency direction always flows downward.

Violating any invariant is an Architecture Conflict.

---

# Repository Runtime Topology

The repository is divided into canonical architecture domains.

```text
Repository
│
├── docs/
│   └── architecture/
│       └── master/
│
├── src/
│   ├── core/
│   ├── kernel/
│   │   ├── contracts/
│   │   └── runtime/
│   └── main.py
│
├── tests/
│   ├── core/
│   ├── kernel/
│   └── integration/
│
├── pyproject.toml
└── .env.example
```

Every directory has exactly one architectural owner.

---

# Directory Ownership Graph

| Directory | Owner | Layer | Purpose |
|-----------|-------|-------|---------|
| docs/architecture/master | Engineering Bible | Documentation | Canonical architecture documents. |
| src/core | KR-001–003 | L0 | Foundation runtime infrastructure. |
| src/kernel/contracts | KR-004 | L0 | Immutable runtime contracts. |
| src/kernel/runtime | KR-005–010 | L0 | Runtime implementation layer. |
| tests/core | KR-011 | Validation | Foundation runtime tests. |
| tests/kernel | KR-011 | Validation | Runtime tests. |
| tests/integration | KR-011 | Validation | Integration tests. |

No production implementation may exist outside these directories.

---

# Runtime Layer Topology

Wave 1 implements only Layer L0.

Future layers already exist architecturally.

| Layer | Runtime | Wave |
|-------|---------|------|
| L0 | Kernel Runtime | Wave 1 |
| L1 | Shared State Runtime | Wave 2 |
| L2 | Layout Runtime | Wave 3 |
| L3 | Theme Runtime | Wave 4 |
| L4 | Motion Runtime | Wave 5 |
| L5 | Interaction Runtime | Wave 6 |
| L6 | Accessibility Runtime | Wave 7 |
| L7 | Platform Runtime | Wave 8 |
| L8 | Render Runtime | Wave 9 |

Directory scaffolding for future layers is reserved.

Implementation is forbidden before the owning Wave.

---

# Layer Expansion Rule

Layers are cumulative.

```text
L8 Render
▲
L7 Platform
▲
L6 Accessibility
▲
L5 Interaction
▲
L4 Motion
▲
L3 Theme
▲
L2 Layout
▲
L1 Shared State
▲
L0 Kernel
```

Higher layers may depend only on lower layers.

Lower layers never depend on higher layers.

This rule is immutable.

---

# Wave 1 Runtime Inventory

Wave 1 runtime graph contains exactly ten runtime systems.

| Runtime | KR | Directory |
|----------|----|-----------|
| Foundation Core | KR-001 | src/core |
| Configuration Runtime | KR-002 | src/core |
| Logging Runtime | KR-003 | src/core |
| Kernel Contracts | KR-004 | src/kernel/contracts |
| DI Runtime | KR-005 | src/kernel/runtime |
| Lifecycle Runtime | KR-006 | src/kernel/runtime |
| Event Bus Runtime | KR-007 | src/kernel/runtime |
| Runtime Context Runtime | KR-008 | src/kernel/runtime |
| Pipeline Runtime | KR-009 | src/kernel/runtime |
| Bootstrap Runtime | KR-010 | src/kernel/runtime |

These runtimes form the complete Layer L0 topology.

---

# Runtime Dependency Hierarchy

The dependency graph is strictly layered.

```text
Bootstrap Runtime
│
├── Configuration Runtime
├── Logging Runtime
├── Context Runtime
├── DI Runtime
├── Event Bus Runtime
├── Pipeline Runtime
└── Lifecycle Runtime
        │
        ▼
Runtime Kernel
```

BootstrapRuntime is the root constructor.

No runtime depends on BootstrapRuntime after construction.

---

# Runtime Ownership Hierarchy

Ownership is unique.

```text
BootstrapRuntime
│
├── RuntimeKernel
│   ├── ContainerRuntime
│   ├── LifecycleRuntime
│   ├── EventBusRuntime
│   ├── ContextRuntime
│   └── OrchestratorRuntime
```

Every runtime instance has exactly one owner.

Shared ownership is forbidden.

---

# Foundation Dependency Graph

Foundation Core is the base of every runtime.

```text
types.py
│
├── constants.py
├── exceptions.py
├── version.py
│
├── settings.py
│     │
│     ▼
config.py
│
├── logging_config.py
│       │
│       ▼
logger.py
```

Foundation files never depend on Kernel Runtime.

---

# Canonical Completion Marker

Document ID: M-02

Document Name: Runtime Graph

Version: 1.1 Canonical

Status: IN PROGRESS (Part 1 of 8)

Authority: AURORA Engineering Bible v1.1

<!-- ========================================================================= -->
<!-- M-02 PART 2 — Runtime Creation Graph + Startup Topology -->
<!-- ========================================================================= -->

# Runtime Creation Graph

This section defines how every runtime instance is created.

Creation order is immutable.

No runtime may create another runtime unless explicitly authorized.

---

## Canonical Runtime Creation Order

BootstrapRuntime is the root constructor.

```text
BootstrapRuntime
        │
        ▼
Configuration Runtime
        │
        ▼
Logging Runtime
        │
        ▼
Context Runtime
        │
        ▼
Container Runtime
        │
        ▼
Event Bus Runtime
        │
        ▼
Pipeline Runtime
        │
        ▼
Lifecycle Runtime
        │
        ▼
RuntimeKernel
```

Every arrow represents ownership construction.

---

## Runtime Creation Matrix

| Runtime | Created By | Destroyed By |
|----------|------------|--------------|
| Settings | BootstrapRuntime | Process Exit |
| Logger | BootstrapRuntime | Process Exit |
| ContextRuntime | BootstrapRuntime | BootstrapRuntime |
| ContainerRuntime | BootstrapRuntime | BootstrapRuntime |
| EventBusRuntime | BootstrapRuntime | BootstrapRuntime |
| OrchestratorRuntime | BootstrapRuntime | BootstrapRuntime |
| LifecycleRuntime | BootstrapRuntime | BootstrapRuntime |
| RuntimeKernel | BootstrapRuntime | BootstrapRuntime |

Creation ownership is unique.

---

## Runtime Initialization Order

Creation and initialization are different phases.

### Creation Phase

Objects exist but are inactive.

```text
Settings
Logger
ContextRuntime
ContainerRuntime
EventBusRuntime
PipelineRuntime
LifecycleRuntime
RuntimeKernel
```

### Initialization Phase

```text
RuntimeKernel.initialize()
        │
        ├── ContainerRuntime.initialize()
        ├── EventBusRuntime.initialize()
        ├── ContextRuntime.initialize()
        ├── PipelineRuntime.initialize()
        └── LifecycleRuntime.initialize()
```

Initialization order is deterministic.

---

## Runtime Startup Graph

Startup begins only after initialization succeeds.

```text
RuntimeKernel.start()
        │
        ▼
LifecycleRuntime.start()
        │
        ▼
RuntimeStatus.RUNNING
```

No runtime starts independently.

---

## Runtime Shutdown Graph

Shutdown order is reverse initialization order.

```text
RuntimeKernel.stop()
        │
        ▼
LifecycleRuntime.stop()

RuntimeKernel.shutdown()
        │
        ├── PipelineRuntime.shutdown()
        ├── EventBusRuntime.shutdown()
        ├── ContainerRuntime.shutdown()
        ├── ContextRuntime.shutdown()
        └── Logger shutdown
```

Reverse ordering prevents dangling dependencies.

---

# Runtime Lifetime Graph

Every runtime has a canonical lifetime.

| Runtime | Lifetime |
|----------|----------|
| Settings | Entire process |
| Logger | Entire process |
| ContainerRuntime | Runtime lifetime |
| ContextRuntime | Runtime lifetime |
| EventBusRuntime | Runtime lifetime |
| PipelineRuntime | Runtime lifetime |
| LifecycleRuntime | Runtime lifetime |
| RuntimeKernel | Runtime lifetime |

No runtime survives RuntimeKernel shutdown.

---

# Runtime Ownership Boundaries

Each runtime owns a different category of objects.

| Runtime | Owns |
|----------|------|
| Configuration | Immutable Settings |
| Logging | Logger configuration |
| Container | Service instances |
| Lifecycle | Runtime state machine |
| Event Bus | Subscribers and dispatch |
| Context | RuntimeContext snapshots |
| Pipeline | Pipeline execution graph |
| Bootstrap | Runtime graph construction |

Ownership never overlaps.

---

# Runtime Construction Rules

BootstrapRuntime follows mandatory rules.

## Allowed Responsibilities

- Instantiate runtimes.
- Wire dependencies.
- Inject Settings.
- Inject Logger.
- Return RuntimeKernel.

## Forbidden Responsibilities

- Execute pipeline.
- Register services manually.
- Publish events.
- Change RuntimeStatus.

BootstrapRuntime constructs only.

---

# Runtime Wiring Graph

The runtime graph is dependency-injected after construction.

```text
RuntimeKernel
│
├── container
├── lifecycle
├── event_bus
├── context
└── orchestrator
```

Each property is immutable after construction.

---

# Runtime Health Graph

RuntimeKernel aggregates runtime health.

```text
RuntimeKernel.health()

        │

        ├── ContainerRuntime.health()
        ├── LifecycleRuntime.health()
        ├── EventBusRuntime.health()
        ├── ContextRuntime.health()
        └── PipelineRuntime.health()
```

Individual runtimes own health computation.

RuntimeKernel owns aggregation only.

---

# Runtime Failure Graph

Initialization failure aborts startup immediately.

```text
BootstrapRuntime.build()

        │

RuntimeKernel.initialize()

        │

Failure Detected

        │

LifecycleRuntime.shutdown()

        │

RuntimeKernel.shutdown()

        │

Process Exit
```

Partial startup is forbidden.

---

# Runtime Construction Invariants

The runtime graph satisfies:

1. BootstrapRuntime is the only constructor.
2. RuntimeKernel is created exactly once.
3. RuntimeKernel owns runtime references.
4. Runtime instances are immutable after construction.
5. Shutdown order is reverse startup order.
6. Runtime health aggregation never mutates runtime state.

Violating any invariant is an architecture violation.

---

<!-- ========================================================================= -->
<!-- M-02 PART 3 — Runtime Dependency Graph + Communication Graph -->
<!-- ========================================================================= -->

# Runtime Dependency Graph

This section defines the canonical dependency graph between every runtime in Wave 1.

Dependencies are directional.

A runtime may depend only on runtimes below or beside it as explicitly authorized.

---

## Global Runtime Dependency Graph

```text
                  BootstrapRuntime
                         │
                         ▼
                   RuntimeKernel
     ┌──────────────┬──────────────┬──────────────┐
     ▼              ▼              ▼              ▼
ContainerRuntime  LifecycleRuntime EventBusRuntime ContextRuntime
     │                                   ▲             │
     ▼                                   │             ▼
ResolverRuntime                      PublisherRuntime SessionRuntime
     │                                   │
     ▼                                   ▼
ProviderRuntime                     DispatcherRuntime
     │                                   │
     ▼                                   ▼
ScopeRuntime                       SubscriberRuntime

            RuntimeKernel
                  │
                  ▼
         OrchestratorRuntime
                  │
                  ▼
           ManifestRuntime
                  │
                  ▼
           ExecutorRuntime
```

Every dependency shown here is canonical.

---

# KR Dependency Matrix

Defines which KR is allowed to depend on another KR.

| KR | Allowed Dependencies |
|----|----------------------|
| KR-001 | Standard Library only |
| KR-002 | KR-001 |
| KR-003 | KR-001, KR-002 |
| KR-004 | KR-001 |
| KR-005 | KR-001, KR-004 |
| KR-006 | KR-001, KR-004 |
| KR-007 | KR-001, KR-004 |
| KR-008 | KR-001, KR-004 |
| KR-009 | KR-001, KR-004, KR-007, KR-008 |
| KR-010 | KR-001…KR-009 |
| KR-011 | Entire public repository |

No dependency outside this table is permitted.

---

# Foundation Dependency Graph

Foundation is the root of the repository.

```text
types.py
   │
   ├── constants.py
   ├── exceptions.py
   ├── version.py
   │
   ├── settings.py
   │      │
   │      ▼
   │   config.py
   │
   ▼
logging_config.py
       │
       ▼
logger.py
```

Rules:

- `types.py` is the deepest dependency.
- `version.py` has no runtime dependencies.
- `constants.py` re-exports version metadata only.
- Foundation never imports Kernel Runtime.

---

# Contract Dependency Graph

Kernel Contracts depend only on Foundation.

```text
types.py
   │
   ▼
context.py
   │
   ├── events.py
   │
   ├── lifecycle.py
   │
   ├── module.py
   │
   ├── runtime.py
   │
   └── service.py
```

Rules:

- contracts never import runtime implementation.
- contracts never import tests.
- contracts remain immutable.

---

# Dependency Injection Graph

DI Runtime owns dependency resolution.

```text
ContainerRuntime
      │
      ├── RegistryRuntime
      ├── ResolverRuntime
      ├── ProviderRuntime
      └── ScopeRuntime

ResolverRuntime
      │
      ▼
ProviderRuntime
      │
      ▼
ScopeRuntime
```

Rules:

- ResolverRuntime reads RegistryRuntime.
- ProviderRuntime constructs services.
- ScopeRuntime caches instances.
- ContainerRuntime exposes public API.

---

# Lifecycle Dependency Graph

Lifecycle Runtime owns runtime state transitions.

```text
LifecycleRuntime
      │
      ├── StateRuntime
      └── HookRuntime
```

Rules:

- StateRuntime owns RuntimeStatus.
- HookRuntime owns callbacks.
- LifecycleRuntime coordinates execution.

No external runtime mutates RuntimeStatus.

---

# Event Runtime Dependency Graph

```text
EventBusRuntime
      │
      ├── PublisherRuntime
      ├── DispatcherRuntime
      └── SubscriberRuntime

PublisherRuntime
      │
      ▼
DispatcherRuntime
      │
      ▼
SubscriberRuntime
```

Rules:

- Publisher validates RuntimeEvent.
- Dispatcher executes handlers.
- Subscriber owns subscriptions.
- EventBusRuntime owns public API.

---

# Context Runtime Dependency Graph

```text
ContextRuntime
      │
      ├── MetadataRuntime
      └── SessionRuntime
```

Rules:

- MetadataRuntime owns metadata snapshots.
- SessionRuntime owns RuntimeContext registry.
- ContextRuntime owns active RuntimeContext.

---

# Pipeline Runtime Dependency Graph

```text
OrchestratorRuntime
        │
        ▼
ManifestRuntime
        │
        ▼
ExecutorRuntime
        ▲
        │
PipelineDefinition
PipelineStage
```

Rules:

- ManifestRuntime validates.
- ExecutorRuntime executes.
- OrchestratorRuntime coordinates.

---

# Bootstrap Dependency Graph

```text
BootstrapRuntime
│
├── Configuration Runtime
├── Logging Runtime
├── Context Runtime
├── Container Runtime
├── Event Runtime
├── Pipeline Runtime
├── Lifecycle Runtime
└── RuntimeKernel
```

Bootstrap owns construction only.

---

# Runtime Communication Graph

Communication is different from dependency.

Dependencies are compile-time.

Communication is runtime interaction.

---

## Communication Topology

```text
RuntimeKernel
│
├──────── ContainerRuntime
│              │
│              ▼
│        EventBusRuntime
│              ▲
│              │
├──────── ContextRuntime
│              │
│              ▼
└─────── OrchestratorRuntime
               │
               ▼
         ExecutorRuntime
```

Only documented runtime communication paths are permitted.

---

# Runtime Communication Matrix

| Source Runtime | Allowed Communication Targets |
|---------------|-------------------------------|
| RuntimeKernel | All runtimes |
| ContainerRuntime | EventBusRuntime |
| LifecycleRuntime | EventBusRuntime, ContextRuntime |
| EventBusRuntime | SubscriberRuntime, DispatcherRuntime |
| ContextRuntime | EventBusRuntime |
| OrchestratorRuntime | ExecutorRuntime, EventBusRuntime, ContextRuntime |
| ExecutorRuntime | EventBusRuntime, ContextRuntime |

Communication outside this matrix is forbidden.

---

# Runtime Read-Only Access Matrix

Some runtimes may observe others without owning them.

| Runtime | Read-Only Access |
|----------|------------------|
| RuntimeKernel | Every runtime health/status |
| ExecutorRuntime | RuntimeContext snapshot |
| EventBusRuntime | RuntimeContext snapshot |
| LifecycleRuntime | RuntimeContext snapshot |
| Tests | Entire public runtime API |

Read-only access never implies ownership.

---

# Dependency Direction Rules

Every dependency follows one direction.

## Allowed Directions

- Foundation → Standard Library.
- Contracts → Foundation.
- Runtime → Contracts.
- Bootstrap → Runtime.
- Tests → Public APIs.

## Forbidden Directions

- Runtime → Bootstrap.
- Contracts → Runtime.
- Foundation → Runtime.
- Runtime → Tests.
- Production → Documentation.

Violations create architecture conflicts.

---

# Circular Dependency Prevention

Circular dependencies are forbidden at two levels.

## File Level

Forbidden:

```text
A imports B
B imports A
```

## Runtime Level

Forbidden:

```text
ContainerRuntime
        ▲
        │
EventBusRuntime
        ▲
        │
ContainerRuntime
```

Cycles must be eliminated through contracts.

---

# Runtime Dependency Invariants

Every Wave 1 runtime satisfies:

1. Foundation has no runtime dependencies.
2. Contracts depend only on Foundation.
3. Runtime implementation depends only on Foundation and Contracts.
4. Bootstrap depends on every runtime.
5. RuntimeKernel aggregates runtimes but does not create them.
6. Tests depend only on public APIs.
7. Circular runtime dependencies are forbidden.

These invariants are immutable.

---

<!-- ========================================================================= -->
<!-- M-02 PART 4 — Directory Graph + Package Graph + Repository Expansion Rules -->
<!-- ========================================================================= -->

# Repository Directory Graph

This section defines the canonical filesystem topology of the repository.

The directory graph is immutable for Wave 1.

Every production file belongs to exactly one directory.

---

## Canonical Repository Tree

```text
aurora/
│
├── docs/
│   └── architecture/
│       ├── AGENTS.md
│       ├── AB-00_Development_Constitution.md
│       ├── AB-00A_Architecture_Reconciliation.md
│       └── master/
│           ├── 00_CANONICAL_INDEX.md
│           ├── 01_FILE_REGISTRY.md
│           ├── 02_RUNTIME_GRAPH.md
│           ├── 03_API_REGISTRY.md
│           ├── 04_IMPORT_GRAPH.md
│           ├── 05_STATE_EVENT_DI_LIFECYCLE_REGISTRY.md
│           ├── 06_MODULE_SPECIFICATIONS.md
│           ├── 07_IMPLEMENTATION_RULES.md
│           ├── 08_EXCEPTION_REGISTRY.md
│           ├── 09_TEST_MATRIX.md
│           ├── 10_BUILD_CHECKLIST.md
│           └── 11_CODEX_MASTER_PROMPT.md
│
├── src/
│   ├── core/
│   ├── kernel/
│   │   ├── contracts/
│   │   └── runtime/
│   └── main.py
│
├── tests/
│   ├── core/
│   ├── kernel/
│   └── integration/
│
├── pyproject.toml
├── .env.example
└── README.md
```

The repository root is frozen.

---

# Directory Ownership Graph

Every directory has exactly one architectural owner.

| Directory | Owner KR | Responsibility |
|-----------|----------|----------------|
| src/core | KR-001–003 | Foundation runtime infrastructure. |
| src/kernel/contracts | KR-004 | Immutable runtime contracts. |
| src/kernel/runtime | KR-005–010 | Runtime implementation layer. |
| tests/core | KR-011 | Foundation runtime validation. |
| tests/kernel | KR-011 | Runtime validation. |
| tests/integration | KR-011 | Integration validation. |
| docs/architecture/master | Engineering Bible | Canonical documentation. |

Ownership is exclusive.

---

# Package Graph

Python packages are immutable.

```text
src
├── core
├── kernel
│   ├── contracts
│   └── runtime
└── main.py
```

Package hierarchy is frozen.

No additional package exists during Wave 1.

---

# Package Dependency Graph

Package imports are directional.

```text
core
 ▲
 │
contracts
 ▲
 │
runtime
 ▲
 │
main.py
```

Rules:

- `core` imports Standard Library only.
- `contracts` import `core`.
- `runtime` imports `core` and `contracts`.
- `main.py` imports runtime only.

Reverse imports are forbidden.

---

# src/core Directory Graph

```text
src/core/
│
├── __init__.py
├── types.py
├── constants.py
├── exceptions.py
├── version.py
├── settings.py
├── config.py
├── logging_config.py
└── logger.py
```

This directory is frozen.

---

## src/core Rules

Allowed contents:

- enums;
- type aliases;
- constants;
- immutable configuration;
- logging infrastructure.

Forbidden contents:

- business models;
- HTTP clients;
- runtime implementation;
- EventBus implementation;
- dependency injection.

---

# src/kernel/contracts Directory Graph

```text
src/kernel/contracts/
│
├── __init__.py
├── context.py
├── events.py
├── lifecycle.py
├── module.py
├── runtime.py
└── service.py
```

Contracts directory contains immutable contracts only.

---

## Contract Directory Rules

Allowed contents:

- dataclasses;
- Protocols;
- ABCs;
- descriptors;
- manifests.

Forbidden contents:

- mutable state;
- logging;
- ContextVar;
- asyncio tasks;
- runtime implementation.

---

# src/kernel/runtime Directory Graph

```text
src/kernel/runtime/
│
├── container.py
├── registry.py
├── resolver.py
├── provider.py
├── scope.py
│
├── lifecycle.py
├── state.py
├── hooks.py
│
├── bus.py
├── publisher.py
├── dispatcher.py
├── subscriber.py
│
├── context.py
├── metadata.py
├── session.py
│
├── pipeline.py
├── manifest.py
├── executor.py
├── orchestrator.py
│
├── bootstrap.py
└── runtime.py
```

Runtime implementation directory is frozen for Wave 1.

---

## Runtime Directory Rules

Allowed contents:

- runtime implementation;
- state machines;
- orchestration;
- caches;
- dispatchers.

Forbidden contents:

- AI models;
- HTTP providers;
- storage;
- renderer;
- UI logic.

---

# tests Directory Graph

```text
tests/
│
├── conftest.py
│
├── core/
│   ├── test_types.py
│   ├── test_settings.py
│   └── test_logger.py
│
├── kernel/
│   ├── test_contracts.py
│   ├── test_container.py
│   ├── test_lifecycle.py
│   ├── test_event_bus.py
│   ├── test_context.py
│   ├── test_pipeline.py
│   └── test_bootstrap.py
│
└── integration/
    └── test_runtime_startup.py
```

Test topology is frozen.

---

## Test Directory Rules

Allowed contents:

- fixtures;
- unit tests;
- integration tests.

Forbidden contents:

- production implementation;
- helper libraries duplicated from `src`.

---

# Documentation Graph

```text
docs/
└── architecture/
    ├── AGENTS.md
    ├── AB-00.md
    ├── AB-00A.md
    └── master/
        ├── M-00
        ├── M-01
        ├── ...
        └── M-11
```

Documentation never imports production code.

---

# Reserved Repository Directories

Future Waves already reserve directory ownership.

## Wave 2

```text
src/state/
```

Owner:

Shared State Runtime.

Status:

Reserved.

---

## Wave 3

```text
src/layout/
```

Owner:

Layout Runtime.

Reserved.

---

## Wave 4

```text
src/theme/
```

Reserved.

---

## Wave 5

```text
src/motion/
```

Reserved.

---

## Wave 6

```text
src/interaction/
```

Reserved.

---

## Wave 7

```text
src/accessibility/
```

Reserved.

---

## Wave 8

```text
src/platform/
```

Reserved.

---

## Wave 9

```text
src/render/
```

Reserved.

---

# Repository Expansion Rules

Repository growth is deterministic.

## Rule 1

New runtime directories appear only when their Wave begins.

## Rule 2

Existing directories are never renamed.

## Rule 3

Existing file paths remain stable.

## Rule 4

Production files are added only through an approved ADR.

## Rule 5

Directory ownership cannot change between Waves.

---

# Forbidden Repository Directories

The following directories are permanently forbidden inside `src/`.

| Directory | Reason |
|-----------|--------|
| utils | Violates ownership model. |
| common | Ambiguous ownership. |
| shared | Hidden dependency bucket. |
| helpers | Unbounded helper dumping ground. |
| misc | Undefined responsibility. |
| temp | Temporary production code forbidden. |
| legacy | Legacy implementation forbidden in canonical runtime. |

Utility code must belong to an owning runtime instead.

---

# Package Visibility Matrix

| Package | Visible To |
|---------|------------|
| core | Entire repository |
| kernel/contracts | Runtime + tests |
| kernel/runtime | main.py + tests |
| tests | Tests only |
| docs | Humans/Codex only |

Visibility never implies ownership.

---

# Filesystem Invariants

The repository filesystem satisfies:

1. Every directory has one owner.
2. Every package has one responsibility.
3. Future runtime directories are reserved.
4. Forbidden directories never exist.
5. Package hierarchy is immutable during Wave 1.

Violating any invariant is an architecture conflict.

---
<!-- ========================================================================= -->
<!-- M-02 PART 5 — State Graph + Event Flow Graph + DI Scope Graph -->
<!-- ========================================================================= -->

# Runtime State Graph

This section defines the canonical runtime state machine for Wave 1.

Runtime state transitions are immutable.

Only Lifecycle Runtime owns transition execution.

---

## Canonical Runtime State Machine

```text
           CREATED
               │
               ▼
        INITIALIZING
          │       │
          │       ▼
          │     FAILED
          ▼       │
         READY     │
          │        │
          ▼        │
        RUNNING ───┘
          │
          ▼
        STOPPED
```

No additional runtime states exist.

---

## State Transition Matrix

| Current State | Allowed Next States |
|---------------|--------------------|
| CREATED | INITIALIZING |
| INITIALIZING | READY, FAILED |
| READY | RUNNING |
| RUNNING | STOPPED, FAILED |
| FAILED | STOPPED |
| STOPPED | *(terminal in Wave 1)* |

Every other transition raises `RuntimeStateError`.

---

## Runtime State Ownership

| Runtime State | Owner |
|---------------|-------|
| CREATED | StateRuntime |
| INITIALIZING | StateRuntime |
| READY | StateRuntime |
| RUNNING | StateRuntime |
| FAILED | StateRuntime |
| STOPPED | StateRuntime |

`RuntimeKernel` reads state.

`LifecycleRuntime` requests transitions.

Only `StateRuntime` mutates state.

---

## State Observation Graph

```text
StateRuntime
      │
      ▼
LifecycleRuntime
      │
      ▼
RuntimeKernel
      │
      ▼
Public Health API
```

State flows upward only.

---

# Event Flow Graph

This section defines canonical runtime event propagation.

---

## Runtime Event Pipeline

```text
Runtime Module
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
      │
      ▼
Registered Handler
```

Every runtime event follows this exact path.

---

## Event Publication Ownership

| Step | Runtime Owner |
|------|---------------|
| Create RuntimeEvent | PublisherRuntime |
| Validate RuntimeEvent | PublisherRuntime |
| Publish | EventBusRuntime |
| Dispatch | DispatcherRuntime |
| Resolve Subscribers | SubscriberRuntime |
| Execute Handler | DispatcherRuntime |

Ownership is unique.

---

## Event Ordering Graph

Events preserve deterministic ordering.

```text
Publish Event A
Publish Event B
Publish Event C

        │

DispatcherRuntime

        │

Handler A1
Handler A2

Handler B1

Handler C1
Handler C2
Handler C3
```

Rules:

- publication order preserved;
- handler registration order preserved;
- priority applied before registration order.

---

## Event Failure Graph

```text
Handler Execution
       │
       ▼
 Exception Raised
       │
       ▼
 EventHandlerError
       │
       ▼
 DispatcherRuntime
       │
       ▼
 Next Handler Executes
```

A failing handler never stops dispatching remaining handlers unless explicitly configured.

---

## Event Categories

Wave 1 recognizes six canonical event families.

| Category | Examples |
|----------|----------|
| Lifecycle | STARTED, STOPPED, FAILED |
| Pipeline | PIPELINE_STARTED, STAGE_COMPLETED |
| Container | SERVICE_REGISTERED |
| Context | SESSION_CREATED |
| Diagnostics | HEALTH_UPDATED |
| Runtime | MODULE_INITIALIZED |

Vocabulary is frozen.

---

# Trace Propagation Graph

Trace propagation is immutable.

```text
Root Trace
    │
    ▼
Pipeline Trace
    │
    ▼
Stage Trace
    │
    ▼
Runtime Event Trace
```

Every child trace references its parent.

---

## Trace Ownership Matrix

| Trace Object | Owner |
|--------------|-------|
| Root Trace | BootstrapRuntime |
| Session Trace | ContextRuntime |
| Pipeline Trace | OrchestratorRuntime |
| Event Trace | PublisherRuntime |

Trace ownership never overlaps.

---

# Runtime Context Propagation Graph

RuntimeContext flows through execution without mutation.

```text
SessionRuntime
      │
      ▼
ContextRuntime
      │
      ▼
ExecutorRuntime
      │
      ├── EventBusRuntime
      ├── LifecycleRuntime
      └── Runtime Modules
```

Context flows downward only.

---

## Metadata Flow Graph

Metadata snapshots are immutable.

```text
MetadataRuntime
      │
      ▼
RuntimeContext
      │
      ▼
Pipeline Execution
      │
      ▼
RuntimeEvent.payload
```

Metadata is copied, never mutated in place.

---

## Session Lifecycle Graph

```text
Session Created
       │
       ▼
RuntimeContext Created
       │
       ▼
Pipeline Executed
       │
       ▼
Session Destroyed
```

SessionRuntime owns the entire lifecycle.

---

# Dependency Injection Scope Graph

Wave 1 defines exactly four DI scopes.

---

## Scope Hierarchy

```text
Application
    │
    ▼
 Session
    │
    ▼
 Pipeline
    │
    ▼
Transient
```

Higher scopes outlive lower scopes.

---

## Scope Lifetime Matrix

| Scope | Lifetime | Cache Owner |
|-------|----------|-------------|
| Application | Runtime lifetime | ScopeRuntime |
| Session | Session lifetime | ScopeRuntime |
| Pipeline | Pipeline lifetime | ScopeRuntime |
| Transient | Per resolution | None |

---

## Scope Resolution Graph

```text
ContainerRuntime
       │
       ▼
ResolverRuntime
       │
       ▼
ScopeRuntime
       │
       ▼
ProviderRuntime
```

Resolution checks cache before construction.

---

## Application Scope Graph

```text
Application Scope Cache
        │
        ├── Settings
        ├── Logger
        ├── EventBusRuntime
        ├── ContainerRuntime
        └── RuntimeKernel
```

Exactly one instance exists.

---

## Session Scope Graph

```text
SessionRuntime
      │
      ▼
Session Scope Cache
      │
      ├── RuntimeContext
      ├── Session Metadata
      └── Session Services
```

Destroyed at session shutdown.

---

## Pipeline Scope Graph

```text
Pipeline Created
      │
      ▼
Pipeline Scope Cache
      │
      ├── Pipeline Services
      ├── Pipeline Context
      └── Stage Resources
```

Destroyed immediately after pipeline completion.

---

## Transient Scope Graph

```text
Resolve Service
      │
      ▼
Construct Instance
      │
      ▼
Return Instance
      │
      ▼
Garbage Collection
```

No caching occurs.

---

# Scope Cleanup Graph

Cleanup order is reverse lifetime order.

```text
Pipeline Cache
      │
      ▼
Session Cache
      │
      ▼
Application Cache
```

Application cache is destroyed only during runtime shutdown.

---

# Scope Isolation Rules

| Scope | Visible To |
|-------|-------------|
| Application | Entire runtime |
| Session | Current session only |
| Pipeline | Current pipeline only |
| Transient | Caller only |

Cross-scope mutation is forbidden.

---

# Runtime State & Event Invariants

The runtime graph guarantees:

1. RuntimeStatus vocabulary is immutable.
2. RuntimeContext is immutable.
3. Metadata snapshots are immutable.
4. Events propagate through EventBusRuntime only.
5. Trace hierarchy is preserved.
6. DI scope lifetime is deterministic.
7. State mutation occurs only in StateRuntime.
8. Scope cleanup always follows reverse lifetime order.

Violating any invariant is an Architecture Conflict.

---

<!-- ========================================================================= -->
<!-- M-02 PART 6 — Health Graph + Diagnostics Graph + Error Propagation Graph -->
<!-- ========================================================================= -->

# Runtime Health Graph

This section defines how runtime health is produced, propagated, aggregated and exposed.

Health propagation is read-only.

No runtime may modify another runtime's health.

---

## Canonical Health Topology

```text
ContainerRuntime
LifecycleRuntime
EventBusRuntime
ContextRuntime
PipelineRuntime
        │
        ▼
RuntimeKernel.health()
        │
        ▼
Health Snapshot
        │
        ▼
Diagnostics Consumers
```

Every runtime computes its own health.

RuntimeKernel aggregates health snapshots.

---

## Runtime Health Ownership Matrix

| Runtime | Owns Health Computation |
|---------|--------------------------|
| ContainerRuntime | Yes |
| LifecycleRuntime | Yes |
| EventBusRuntime | Yes |
| ContextRuntime | Yes |
| OrchestratorRuntime | Yes |
| RuntimeKernel | Aggregation only |

Health ownership is exclusive.

---

## Canonical Health Vocabulary

Health status vocabulary is frozen.

| Status | Meaning |
|--------|---------|
| OK | Runtime operates normally. |
| WARNING | Runtime degraded but operational. |
| ERROR | Runtime unhealthy. |

No additional health states exist.

---

## Health Aggregation Graph

```text
Runtime Health

Container ─────┐
Lifecycle ─────┤
Event Bus ─────┤
Context ───────┤
Pipeline ──────┘
        │
        ▼
RuntimeKernel Aggregation
        │
        ▼
Repository Health Snapshot
```

Aggregation never mutates child health.

---

## Health Snapshot Contract

Health snapshots are immutable.

Snapshot contains:

| Field | Purpose |
|-------|---------|
| runtime | Runtime identifier |
| status | HealthStatus |
| timestamp | UTC timestamp |
| details | JSON-compatible metadata |

Snapshots are read-only.

---

# Diagnostics Graph

Diagnostics Runtime is conceptual during Wave 1.

No dedicated DiagnosticsRuntime implementation exists.

Diagnostics are produced by runtime owners.

---

## Diagnostics Ownership Matrix

| Runtime | Emits Diagnostics |
|----------|-------------------|
| Configuration Runtime | Configuration validation |
| Logging Runtime | Logging initialization |
| ContainerRuntime | Registration diagnostics |
| LifecycleRuntime | Lifecycle diagnostics |
| EventBusRuntime | Event diagnostics |
| ContextRuntime | Context diagnostics |
| PipelineRuntime | Pipeline diagnostics |
| BootstrapRuntime | Startup diagnostics |

Every runtime emits only diagnostics about itself.

---

## Diagnostics Flow Graph

```text
Runtime
   │
   ▼
Health Snapshot
   │
   ▼
RuntimeKernel
   │
   ▼
Diagnostics Consumer
```

Diagnostics never flow directly between runtimes.

---

## Diagnostics Categories

Wave 1 defines immutable diagnostic categories.

| Category | Produced By |
|----------|-------------|
| CONFIGURATION | KR-002 |
| LOGGING | KR-003 |
| CONTAINER | KR-005 |
| LIFECYCLE | KR-006 |
| EVENT | KR-007 |
| CONTEXT | KR-008 |
| PIPELINE | KR-009 |
| BOOTSTRAP | KR-010 |

Vocabulary is frozen.

---

## Diagnostics Event Graph

Diagnostics may publish runtime events through EventBusRuntime.

```text
Runtime
   │
   ▼
PublisherRuntime
   │
   ▼
EventBusRuntime
   │
   ▼
DispatcherRuntime
```

Diagnostics never bypass EventBusRuntime.

---

# Error Propagation Graph

Errors propagate upward only.

Ownership is preserved.

---

## Canonical Error Topology

```text
Runtime
   │
   ▼
Runtime Exception
   │
   ▼
RuntimeKernel
   │
   ▼
Shutdown Decision
```

Exceptions never travel downward.

---

## Error Ownership Matrix

| Error Family | Owner Runtime |
|--------------|---------------|
| ConfigurationError | KR-002 |
| ContainerError | KR-005 |
| RuntimeStateError | KR-006 |
| EventBusError | KR-007 |
| ValidationError | KR-004 |
| RuntimeInitializationError | KR-010 |
| RuntimeShutdownError | KR-010 |

Every exception family has exactly one owner.

---

## Error Escalation Levels

Wave 1 recognizes three escalation levels.

### Recoverable

Runtime continues execution.

Examples:

- handler failure
- missing subscriber
- transient pipeline stage failure

---

### Runtime Failure

Current runtime becomes unhealthy.

Examples:

- service resolution failure
- invalid transition
- manifest validation failure

---

### Fatal Failure

Entire runtime shuts down.

Examples:

- bootstrap failure
- configuration failure
- RuntimeKernel initialization failure

Fatal failures terminate startup.

---

## Error Escalation Graph

```text
Recoverable Error
        │
        ▼
Runtime Handles Error
        │
        ▼
Continue Execution

Runtime Failure
        │
        ▼
LifecycleRuntime.stop()

Fatal Failure
        │
        ▼
RuntimeKernel.shutdown()
        │
        ▼
Process Exit
```

Escalation direction is immutable.

---

## Runtime Failure Recovery Graph

```text
Runtime Failure
      │
      ▼
HealthStatus.ERROR
      │
      ▼
LifecycleRuntime.stop()
      │
      ▼
Shutdown Hooks
      │
      ▼
Runtime Shutdown
```

Wave 1 does not restart failed runtimes.

---

## Validation Failure Graph

Validation failures occur before runtime execution.

```text
Manifest Validation
        │
        ▼
ValidationError
        │
        ▼
Bootstrap Aborted
```

Validation failures never enter RUNNING state.

---

## Event Handler Failure Graph

```text
RuntimeEvent
     │
     ▼
DispatcherRuntime
     │
     ▼
Handler
     │
 Exception
     ▼
EventHandlerError
     │
     ▼
Dispatcher Continues
```

Remaining handlers continue unless cancellation policy exists.

---

## Container Failure Graph

```text
Resolve Service
      │
      ▼
Missing Descriptor
      │
      ▼
ServiceResolutionError
      │
      ▼
ResolverRuntime
      │
      ▼
ContainerRuntime
```

ContainerRuntime owns propagation.

---

## Bootstrap Failure Graph

```text
BootstrapRuntime.build()
       │
       ▼
Initialization Failure
       │
       ▼
RuntimeInitializationError
       │
       ▼
RuntimeKernel.shutdown()
       │
       ▼
Process Exit
```

Partial runtime graph is destroyed immediately.

---

# Runtime Shutdown Cascade Graph

Shutdown is reverse dependency order.

```text
RuntimeKernel
      │
      ▼
LifecycleRuntime.stop()

      │
      ▼
PipelineRuntime.shutdown()

      │
      ▼
EventBusRuntime.shutdown()

      │
      ▼
ContainerRuntime.shutdown()

      │
      ▼
ContextRuntime.shutdown()

      │
      ▼
LoggingRuntime.shutdown()
```

Every runtime shuts down exactly once.

---

# Health & Diagnostics Invariants

Wave 1 guarantees:

1. Health computation is owned by runtime owners.
2. RuntimeKernel aggregates but never computes child health.
3. Diagnostics never mutate runtime state.
4. Errors propagate upward only.
5. Fatal failures terminate startup.
6. Recoverable failures never bypass runtime ownership.
7. Shutdown cascade follows reverse dependency order.

Violating any invariant is an Architecture Conflict.

---

<!-- ========================================================================= -->
<!-- M-02 PART 7 — Bootstrap Timeline + Runtime Timeline + Pipeline Sequence -->
<!-- ========================================================================= -->

# Bootstrap Timeline

This section defines the canonical startup timeline of the entire AURORA runtime.

The startup timeline is deterministic.

No runtime may change its position.

---

## Complete Startup Timeline

```text
Process Start
    │
    ▼
main()
    │
    ▼
BootstrapRuntime.build()
    │
    ▼
Settings Loaded
    │
    ▼
Logging Configured
    │
    ▼
ContextRuntime Created
    │
    ▼
ContainerRuntime Created
    │
    ▼
EventBusRuntime Created
    │
    ▼
PipelineRuntime Created
    │
    ▼
LifecycleRuntime Created
    │
    ▼
RuntimeKernel Created
    │
    ▼
RuntimeKernel.initialize()
    │
    ▼
RuntimeKernel.start()
    │
    ▼
RuntimeStatus.RUNNING
```

Every startup follows this exact order.

---

## Startup Phase Matrix

| Phase | Owner Runtime | Result |
|-------|---------------|--------|
| Process Entry | `main.py` | Python process starts. |
| Build Runtime Graph | BootstrapRuntime | Runtime instances created. |
| Configuration Load | Configuration Runtime | Immutable Settings ready. |
| Logging Initialization | Logging Runtime | Logger configured. |
| Runtime Initialization | RuntimeKernel | Child runtimes initialized. |
| Lifecycle Start | LifecycleRuntime | Runtime enters RUNNING. |
| Runtime Ready | RuntimeKernel | Runtime accepts pipelines. |

Startup phases are immutable.

---

# Runtime Initialization Timeline

Initialization is separate from construction.

## Initialization Sequence

```text
RuntimeKernel.initialize()

        │

        ├──────── ContainerRuntime.initialize()

        ├──────── EventBusRuntime.initialize()

        ├──────── ContextRuntime.initialize()

        ├──────── OrchestratorRuntime.initialize()

        └──────── LifecycleRuntime.initialize()

        │

        ▼

RuntimeStatus.READY
```

Initialization finishes before startup begins.

---

## Initialization Responsibilities

| Runtime | Initializes |
|----------|-------------|
| ContainerRuntime | Registry, Resolver, Provider, Scope |
| EventBusRuntime | Publisher, Dispatcher, Subscriber |
| ContextRuntime | SessionRuntime, MetadataRuntime |
| OrchestratorRuntime | ManifestRuntime, ExecutorRuntime |
| LifecycleRuntime | StateRuntime, HookRuntime |

Every runtime initializes only its owned children.

---

# Runtime Startup Sequence Diagram

```text
main.py
   │
   │ build()
   ▼
BootstrapRuntime
   │
   │ create RuntimeKernel
   ▼
RuntimeKernel
   │
   │ initialize()
   ▼
ContainerRuntime

RuntimeKernel
   │
   ▼
EventBusRuntime

RuntimeKernel
   │
   ▼
ContextRuntime

RuntimeKernel
   │
   ▼
OrchestratorRuntime

RuntimeKernel
   │
   ▼
LifecycleRuntime

RuntimeKernel
   │
   │ start()
   ▼
LifecycleRuntime
   │
   ▼
RUNNING
```

Sequence ordering is frozen.

---

# Runtime Shutdown Timeline

Shutdown is deterministic and reverse-ordered.

## Shutdown Sequence

```text
RuntimeKernel.stop()
        │
        ▼
LifecycleRuntime.stop()
        │
        ▼
RuntimeStatus.STOPPED

RuntimeKernel.shutdown()
        │
        ▼
ExecutorRuntime.shutdown()

        ▼
EventBusRuntime.shutdown()

        ▼
ContainerRuntime.shutdown()

        ▼
ContextRuntime.shutdown()

        ▼
Logger Shutdown

        ▼
Process Exit
```

Every shutdown follows reverse dependency order.

---

## Shutdown Phase Matrix

| Phase | Owner Runtime |
|-------|---------------|
| Stop Runtime | LifecycleRuntime |
| Stop Pipelines | ExecutorRuntime |
| Remove Subscribers | EventBusRuntime |
| Dispose Services | ContainerRuntime |
| Remove Contexts | ContextRuntime |
| Flush Logs | Logging Runtime |
| Exit Process | main.py |

Shutdown phases are immutable.

---

# Runtime Session Timeline

Session lifetime is independent from runtime lifetime.

```text
Session Created
      │
      ▼
RuntimeContext Created
      │
      ▼
Metadata Snapshot Created
      │
      ▼
Pipeline Execution
      │
      ▼
Events Published
      │
      ▼
Pipeline Finished
      │
      ▼
Session Destroyed
```

SessionRuntime owns this timeline.

---

# Pipeline Timeline

Pipeline execution has six canonical phases.

## Pipeline Lifecycle

```text
Pipeline Requested
        │
        ▼
PipelineDefinition Loaded
        │
        ▼
Manifest Validation
        │
        ▼
Execution Order Built
        │
        ▼
Stages Executed
        │
        ▼
Pipeline Completed
```

No stage executes before validation succeeds.

---

## Pipeline Execution Matrix

| Phase | Owner |
|-------|-------|
| Pipeline Definition | Pipeline Runtime |
| Manifest Validation | ManifestRuntime |
| DAG Validation | ManifestRuntime |
| Execution Planning | ExecutorRuntime |
| Stage Execution | ExecutorRuntime |
| Completion Event | EventBusRuntime |

---

# Pipeline Stage Timeline

Each stage follows identical execution flow.

```text
Stage Ready
    │
    ▼
Publish STAGE_STARTED
    │
    ▼
Resolve Dependencies
    │
    ▼
Execute Stage
    │
    ▼
Publish STAGE_COMPLETED
```

Failure publishes STAGE_FAILED instead.

---

# Runtime Event Timeline

Runtime events follow deterministic propagation.

```text
Create RuntimeEvent
       │
       ▼
Validate RuntimeEvent
       │
       ▼
Publish Event
       │
       ▼
Resolve Subscribers
       │
       ▼
Dispatch Handlers
       │
       ▼
Complete Dispatch
```

Every runtime event follows this timeline.

---

# Dependency Resolution Timeline

```text
resolve(service_id)

      │

Lookup Descriptor

      │

Resolve Dependencies

      │

Check Scope Cache

      │

Create Instance

      │

Initialize Service

      │

Return Service
```

ResolverRuntime owns dependency traversal.

ProviderRuntime owns construction.

ScopeRuntime owns caching.

---

# Scope Cleanup Timeline

Cleanup occurs after execution.

```text
Pipeline Finished
      │
      ▼
Pipeline Scope Cleared

Session Finished
      │
      ▼
Session Scope Cleared

Runtime Shutdown
      │
      ▼
Application Scope Cleared
```

Cleanup always occurs from shortest lifetime to longest lifetime.

---

# Build Checklist Invariants

Wave 1 startup guarantees:

1. BootstrapRuntime is executed exactly once.
2. RuntimeKernel is initialized before RUNNING.
3. Pipeline execution begins only after READY.
4. Shutdown is reverse startup order.
5. Sessions never outlive RuntimeKernel.
6. Pipeline scopes never outlive sessions.
7. Application scope survives until runtime shutdown.

Violating any invariant is an Architecture Conflict.

---

<!-- ========================================================================= -->
<!-- M-02 PART 8 — Global Topology Matrix + Wave Expansion + Definition of Done -->
<!-- ========================================================================= -->

# Global Runtime Topology Matrix

This section is the canonical inventory of every runtime relationship in Wave 1.

The topology is exhaustive.

---

## Runtime Ownership Matrix

| Runtime | KR | Layer | Created By | Destroyed By |
|---------|----|-------|------------|--------------|
| Foundation Core | KR-001 | L0 | Python Import | Process Exit |
| Configuration Runtime | KR-002 | L0 | BootstrapRuntime | Process Exit |
| Logging Runtime | KR-003 | L0 | BootstrapRuntime | Process Exit |
| Kernel Contracts | KR-004 | L0 | Python Import | Process Exit |
| ContainerRuntime | KR-005 | L0 | BootstrapRuntime | BootstrapRuntime |
| LifecycleRuntime | KR-006 | L0 | BootstrapRuntime | BootstrapRuntime |
| EventBusRuntime | KR-007 | L0 | BootstrapRuntime | BootstrapRuntime |
| ContextRuntime | KR-008 | L0 | BootstrapRuntime | BootstrapRuntime |
| OrchestratorRuntime | KR-009 | L0 | BootstrapRuntime | BootstrapRuntime |
| RuntimeKernel | KR-010 | L0 | BootstrapRuntime | BootstrapRuntime |

Ownership is immutable.

---

## Runtime Responsibility Matrix

| Runtime | Canonical Responsibility |
|---------|---------------------------|
| Foundation | Types, constants, exceptions, versions |
| Configuration | Immutable Settings |
| Logging | Logging configuration and logger creation |
| Contracts | Immutable runtime contracts |
| Container | Dependency injection |
| Lifecycle | Runtime state machine |
| Event Bus | Event publication and dispatch |
| Context | RuntimeContext propagation |
| Pipeline | Pipeline validation and execution |
| Bootstrap | Runtime graph construction |

Every responsibility has one owner.

---

# Runtime Communication Matrix

| Source Runtime | Target Runtime | Communication |
|---------------|---------------|---------------|
| RuntimeKernel | ContainerRuntime | Direct API |
| RuntimeKernel | LifecycleRuntime | Direct API |
| RuntimeKernel | EventBusRuntime | Direct API |
| RuntimeKernel | ContextRuntime | Direct API |
| RuntimeKernel | OrchestratorRuntime | Direct API |
| LifecycleRuntime | EventBusRuntime | Lifecycle events |
| LifecycleRuntime | ContextRuntime | RuntimeContext snapshot |
| ExecutorRuntime | EventBusRuntime | Pipeline events |
| ExecutorRuntime | ContextRuntime | RuntimeContext snapshot |
| ContainerRuntime | EventBusRuntime | Container diagnostics |
| ContextRuntime | EventBusRuntime | Session events |

Communication paths are frozen.

---

## Runtime Visibility Matrix

Defines runtime visibility.

| Runtime | Visible To |
|----------|------------|
| Foundation | Entire repository |
| Contracts | Runtime implementation + tests |
| Runtime implementation | RuntimeKernel + tests |
| RuntimeKernel | main.py + tests |
| Tests | Public APIs only |

Visibility never implies ownership.

---

# Runtime Access Matrix

Defines permitted read/write access.

| Runtime | Read Access | Write Access |
|----------|-------------|--------------|
| RuntimeKernel | All runtime snapshots | None |
| LifecycleRuntime | RuntimeStatus | Transition requests |
| StateRuntime | RuntimeStatus | RuntimeStatus |
| ContextRuntime | RuntimeContext | RuntimeContext |
| MetadataRuntime | Metadata snapshot | Metadata snapshot |
| EventBusRuntime | RuntimeEvent | RuntimeEvent dispatch |
| ContainerRuntime | Service cache | Service cache |
| ScopeRuntime | Scope cache | Scope cache |

Write ownership is exclusive.

---

# Runtime Resource Lifetime Matrix

| Resource | Owner Runtime | Lifetime |
|----------|---------------|----------|
| Settings | Configuration Runtime | Process |
| Logger | Logging Runtime | Process |
| RuntimeContext | ContextRuntime | Session |
| Metadata | MetadataRuntime | RuntimeContext |
| Service Instance | ScopeRuntime | Scope-dependent |
| Event Subscribers | SubscriberRuntime | Runtime |
| PipelineDefinition | Pipeline Runtime | Immutable |
| RuntimeKernel | BootstrapRuntime | Runtime |

Lifetime ownership is frozen.

---

# Runtime Cache Matrix

| Cache | Owner | Scope |
|-------|-------|-------|
| Settings Cache | Configuration Runtime | Application |
| Logger Cache | Logging Runtime | Application |
| Application Scope Cache | ScopeRuntime | Application |
| Session Scope Cache | ScopeRuntime | Session |
| Pipeline Scope Cache | ScopeRuntime | Pipeline |
| Subscriber Registry | SubscriberRuntime | Runtime |

No additional caches exist during Wave 1.

---

# Wave Expansion Graph

Wave architecture expands layer by layer.

## Complete Layer Expansion

```text
Wave 9
└── L8 Render Runtime

Wave 8
└── L7 Platform Runtime

Wave 7
└── L6 Accessibility Runtime

Wave 6
└── L5 Interaction Runtime

Wave 5
└── L4 Motion Runtime

Wave 4
└── L3 Theme Runtime

Wave 3
└── L2 Layout Runtime

Wave 2
└── L1 Shared State Runtime

Wave 1
└── L0 Kernel Runtime
```

Higher layers may import lower layers only.

---

## Reserved Runtime Directories

Future directories are frozen before implementation.

| Wave | Directory | Status |
|------|-----------|--------|
| Wave 2 | `src/state/` | RESERVED |
| Wave 3 | `src/layout/` | RESERVED |
| Wave 4 | `src/theme/` | RESERVED |
| Wave 5 | `src/motion/` | RESERVED |
| Wave 6 | `src/interaction/` | RESERVED |
| Wave 7 | `src/accessibility/` | RESERVED |
| Wave 8 | `src/platform/` | RESERVED |
| Wave 9 | `src/render/` | RESERVED |

Repository expansion is deterministic.

---

# Cross-Document Reference Matrix

This table defines which Engineering Bible document owns each architectural concept.

| Concept | Canonical Document |
|--------|---------------------|
| Repository inventory | M-01 File Registry |
| Runtime topology | M-02 Runtime Graph |
| Public APIs | M-03 API Registry |
| Imports | M-04 Import Graph |
| State/Event/DI vocabulary | M-05 State Event DI Lifecycle Registry |
| File implementation | M-06 Module Specifications |
| Coding constitution | M-07 Implementation Rules |
| Exception hierarchy | M-08 Exception Registry |
| Test ownership | M-09 Test Matrix |
| Build validation | M-10 Build Checklist |
| Codex protocol | M-11 Codex Master Prompt |

Ownership is unique.

---

# Runtime Graph Integrity Rules

A repository is topology-valid only if all rules below are satisfied.

## Runtime Rules

- BootstrapRuntime is the only runtime constructor.
- RuntimeKernel owns runtime references.
- Runtime ownership is unique.
- Runtime communication follows canonical matrix.
- Runtime shutdown follows reverse startup order.

---

## Dependency Rules

- Foundation has no runtime dependencies.
- Contracts depend only on Foundation.
- Runtime implementation depends only on Foundation and Contracts.
- Bootstrap depends on runtime implementation only.
- Circular runtime dependencies are forbidden.

---

## State Rules

- RuntimeStatus vocabulary is immutable.
- Lifecycle transitions follow canonical graph.
- StateRuntime is the only state owner.

---

## Event Rules

- Runtime events propagate only through EventBusRuntime.
- Publisher validates.
- Dispatcher dispatches.
- Subscriber owns handlers.

---

## Context Rules

- RuntimeContext is immutable.
- Metadata snapshots are immutable.
- SessionRuntime owns session lifecycle.

---

## DI Rules

- Application scope is unique.
- Session scope is isolated.
- Pipeline scope is ephemeral.
- Transient scope is never cached.

---

# Runtime Graph Definition of Done

`02_RUNTIME_GRAPH.md` is GREEN only if:

## Repository Topology

- Every runtime appears exactly once.
- Every runtime has one owner.
- Every runtime has one layer.
- Every runtime has one constructor.

## Dependency Topology

- Runtime dependency graph is complete.
- Communication matrix is complete.
- Visibility matrix is complete.
- Ownership matrix is complete.

## Lifecycle Topology

- Startup timeline defined.
- Shutdown timeline defined.
- Session timeline defined.
- Pipeline timeline defined.
- Event timeline defined.

## Expansion Topology

- Wave expansion graph defined.
- Reserved directories defined.
- Future runtime layers reserved.
- No undefined runtime directories exist.

## Integrity

- No circular ownership.
- No circular construction.
- No undocumented runtime relationship.
- All runtime invariants documented.

---

# Canonical Completion Marker

**Document ID:** M-02

**Document Name:** Runtime Graph

**Version:** 1.1 Canonical

**Status:** COMPLETE

**Authority:** AURORA Engineering Bible v1.1

**END OF DOCUMENT**