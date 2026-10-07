# AURORA ENGINEERING BIBLE v1.1

## Approved core/test reconciliation — ADR-009

**Status:** APPROVED — explicit T-01–T-05 approval and root-admission clarification,
2026-10-07. Exact normative contracts:
[KR-002](../wave1/KR-002_CONFIGURATION.md),
[KR-003](../wave1/KR-003_LOGGING.md),
[KR-011](../wave1/KR-011_KERNEL_TEST_SUITE.md).

Only affected KR-002/KR-003/KR-011 declarations are superseded. Legacy duplicate
summaries/counts/examples for those modules elsewhere in this document are NOT
authority when they conflict with these exact contracts. Other module ownership,
L0–L8, DI/event/lifecycle vocabularies and approved ADR-004–008 acceptance remain.

KR-002: immutable BaseSettings, eight fields, Environment alias, three properties,
two validators; get_settings and validate_configuration, lru_cache(maxsize=1).
No reload_settings/clear_settings_cache/validate_settings, missing-.env error,
provider fields, absolute/existing-path or timezone-database validation requirement.

KR-003: get_logger(name, config=None), LOGGER; LoggingConfig (three fields, frozen/
slotted, positional-compatible), RuntimeContextFilter, ConsoleFormatter, JsonFormatter,
seven explicit correlation/session context functions and two default constants.
No configure_logging/reset_logging/ContextFilter alias, root configuration or
automatic trace/pipeline/runtime injection. Empty name and EXACT "root" plus invalid
levels reject before registry access/mutation with existing InvalidConfigurationError
and fixed safe messages. Keep cache and first-installed handlers. Foundation
constants keep KR-001 ownership; logger -> logging_config/ Foundation is allowed,
logging_config -> logger or concrete runtime is forbidden. No new import direction.

KR-011: eleven executable test modules plus tests/conftest.py (seven named fresh
function-scoped fixtures), exact paths and all public API/coverage gates in its
linked contract. No tests/runtime or split Registry/Scope/Resolver/Executor files.
Current narrow KR-003 changes only logger.py and test_logger.py; no other production,
test, dependency or workflow edit. KR-011 is a separate subsequent reviewed task.
Approved contract compilation is not a claim of implementation/test acceptance.


Document ID: M-01

Document Name: File Registry

Path:
docs/architecture/master/01_FILE_REGISTRY.md

Status: CANONICAL SOURCE OF TRUTH

Authority:
- AB-00 Development Constitution
- AB-00A Architecture Reconciliation
- M-00 Canonical Index

Version: 1.1 Canonical

---

# Purpose

This document is the canonical registry of every production file that exists inside the AURORA repository.

It defines:

- every production file;
- ownership (KR owner);
- runtime layer;
- implementation stage;
- public exports;
- dependency boundaries;
- lifecycle status;
- validation ownership.

This document **does not** define implementation logic.
Implementation belongs exclusively to M-06.

If a production file is not listed here, it must not exist.

---

# File Registry Constitution

## Registry Invariants

Every production file satisfies the following invariants.

1. One file has one owner KR.
2. One file has one primary responsibility.
3. One file belongs to exactly one runtime layer.
4. One file exports one documented public API surface.
5. One file appears exactly once inside this registry.

Violating any invariant is an architecture violation.

---

## Runtime Layers

| Layer | Description |
|-------|-------------|
| L0 | Kernel Runtime |
| L1 | Shared Runtime State |
| L2 | Layout Runtime |
| L3 | Theme Runtime |
| L4 | Motion Runtime |
| L5 | Interaction Runtime |
| L6 | Accessibility Runtime |
| L7 | Platform Runtime |
| L8 | Render Runtime |

Wave 1 owns only L0.

---

## Status Vocabulary

| Status | Meaning |
|--------|---------|
| GREEN | Implemented and validated. |
| YELLOW | Exists but implementation incomplete. |
| RED | Planned but absent. |
| FROZEN | Canonical specification frozen. |

---

# Repository Root Ownership

| Path | Owner | Layer |
|------|-------|-------|
| `src/` | Runtime | L0-L8 |
| `tests/` | KR-011 | Validation |
| `docs/architecture/` | Engineering Bible | Documentation |
| `.env.example` | KR-002 | Configuration |
| `pyproject.toml` | Repository | Toolchain |
| `README.md` | Repository | Documentation |

No additional root production directories are allowed.

---

# Wave 1 Production Registry Overview

Wave 1 contains exactly **33 production Python files**.

| KR | Files |
|----|------:|
| KR-001 | 5 |
| KR-002 | 2 |
| KR-003 | 2 |
| KR-004 | 7 |
| KR-005 | 5 |
| KR-006 | 3 |
| KR-007 | 4 |
| KR-008 | 3 |
| KR-009 | 4 |
| KR-010 | 3 |

**Total:** 38 files including `src/main.py`.

---

# KR-001 — Foundation Core Registry

Runtime Layer: **L0 Kernel**

Directory:

```
src/core/
```

Files:

| File | Status | Public API |
|------|--------|-----------|
| `__init__.py` | FROZEN | Foundation exports |
| `types.py` | FROZEN | Canonical types |
| `constants.py` | FROZEN | Canonical constants |
| `exceptions.py` | FROZEN | Exception hierarchy |
| `version.py` | FROZEN | Version metadata |

---

## CORE-001 — src/core/__init__.py

### Owner

KR-001 Foundation Core

### Responsibility

Foundation export surface.

### Runtime Layer

L0

### Imported By

Entire repository.

### Public Exports

#### Constants

- PROJECT_NAME
- PROJECT_DISPLAY_NAME
- ARCHITECTURE_VERSION
- ARCHITECTURE_FREEZE
- PYTHON_VERSION
- ENGINE_VERSION
- ENGINE_STAGE
- KERNEL_RUNTIME_VERSION

#### Enums

- RuntimeLayer
- RuntimeStatus
- HealthStatus
- DIScope
- EventPriority
- EventPhase

### Forbidden Responsibilities

- implementation logic;
- runtime creation;
- configuration loading.

---

## CORE-002 — src/core/types.py

### Owner

KR-001 Foundation Core

### Responsibility

Canonical typing vocabulary.

### Runtime Layer

L0

### Imported By

Every KR.

### Public Type Aliases

#### Identifiers

- ModuleId
- SessionId
- PipelineId
- EventId
- TraceId
- ServiceId

#### JSON Types

- JSONPrimitive
- JSONValue
- JSONDict
- Payload
- Metadata
- Headers

### Public Enums

- RuntimeLayer
- RuntimeStatus
- HealthStatus
- DIScope
- EventPriority
- EventPhase

### Export Count

18 symbols.

### Forbidden Responsibilities

- validation logic;
- runtime state;
- business models.

---

## CORE-003 — src/core/constants.py

### Owner

KR-001 Foundation Core

### Responsibility

Canonical repository constants.

### Runtime Layer

L0

### Imported By

KR-002…KR-010.

### Public Constant Groups

#### Manifest

- MANIFEST_FIELD_MODULE_ID
- MANIFEST_FIELD_RUNTIME_LAYER
- MANIFEST_FIELD_DEPENDS_ON
- MANIFEST_FIELD_PROVIDES
- MANIFEST_FIELD_VERSION

#### Event

- EVENT_REQUIRED_FIELDS
- EVENT_VERSION

#### Runtime

- RUNTIME_CONTAINER
- RUNTIME_EVENT_BUS
- RUNTIME_CONFIG
- RUNTIME_LOGGER

#### Logging

- LOGGER_NAME
- LOG_FORMAT
- LOG_DATE_FORMAT

#### Filesystem

- ENV_FILENAME
- CONFIG_DIRECTORY
- LOG_DIRECTORY
- CACHE_DIRECTORY
- DATA_DIRECTORY

### Forbidden Responsibilities

- duplicated version metadata;
- runtime objects.

---

## CORE-004 — src/core/exceptions.py

### Owner

KR-001 Foundation Core

### Responsibility

Canonical exception hierarchy.

### Runtime Layer

L0

### Imported By

Entire repository.

### Public Exception Families

Configuration

Container

Manifest

Runtime

Validation

EventBus

Diagnostics

### Total Public Exceptions

22+

### Forbidden Responsibilities

- exception handling logic;
- logging.

---

## CORE-005 — src/core/version.py

### Owner

KR-001 Foundation Core

### Responsibility

Canonical version metadata.

### Runtime Layer

L0

### Imported By

constants.py

__init__.py

BootstrapRuntime

### Public Version Symbols

- VERSION
- __version__
- API_VERSION
- KERNEL_RUNTIME_VERSION
- PROJECT_NAME
- PROJECT_DISPLAY_NAME
- ARCHITECTURE_VERSION
- ARCHITECTURE_FREEZE
- ENGINE_VERSION
- ENGINE_STAGE
- PYTHON_VERSION

### Canonical Ownership Rule

Only this file owns version metadata.

No duplicate literal values anywhere else.

<!-- ========================================================================= -->
<!-- M-01 PART 2 — KR-002 Configuration Runtime + KR-003 Logging Runtime -->
<!-- ========================================================================= -->

# KR-002 — Configuration Runtime Registry

APPROVED exact schema/API/validation: [KR-002](../wave1/KR-002_CONFIGURATION.md).

| File | Owner / L0 responsibility | Public surface |
| --- | --- | --- |
| src/core/settings.py | KR-002 environment/.env parsing, frozen BaseSettings validation | Environment; Settings; eight fields, three properties, two validators |
| src/core/config.py | KR-002 immutable Application-wide loader/cache | get_settings; validate_configuration |

Settings -> Foundation constants/exceptions + existing Pydantic. Config -> Settings/
Foundation exception + lru_cache/Pydantic ValidationError. No logging/DI/runtime
import or file/directory creation. Defaults/relative paths accepted; test-only
decorator cache_clear is not a new public loader contract.

# KR-003 — Logging Runtime Registry

APPROVED exact surface/behavior: [KR-003](../wave1/KR-003_LOGGING.md).

| File | Owner / L0 responsibility | Public surface |
| --- | --- | --- |
| src/core/logging_config.py | KR-003 frozen config, ContextVars/filter/formatters | LoggingConfig; RuntimeContextFilter; ConsoleFormatter; JsonFormatter; seven context functions; DEFAULT_LOGGING_CONFIG; DEFAULT_CONTEXT_FILTER |
| src/core/logger.py | KR-003 named logger acquisition/cache and handler construction | get_logger; LOGGER |

Factory -> sibling config/filter/formatters and existing Foundation exception.
Logging primitives -> Foundation constants, never reverse or higher runtime.
Reject empty/"root"/invalid level before logger acquisition/mutation. No root
configuration/reset or automatic runtime trace fields. Keep handler/cache
semantics, fixed errors and infrastructure exception to hidden-runtime-state rule.
Only logger.py and canonical test_logger.py are reopened in the narrow task.
Test ownership remains KR-011; shared fixtures wait for its separate task.

<!-- M-01 PART 3 — KR-004 Kernel Contracts Registry -->
<!-- ========================================================================= -->

# KR-004 — Kernel Contracts Registry

**Runtime Layer:** L0 Kernel

Directory:

```
src/kernel/contracts/
```

Kernel Contracts define every immutable public contract used by the runtime.

Contracts contain **zero runtime implementation**.

Files:

| File | Status | Public API |
|------|--------|------------|
| `__init__.py` | FROZEN | Contract export surface |
| `context.py` | FROZEN | RuntimeContext contract |
| `events.py` | FROZEN | RuntimeEvent contract |
| `lifecycle.py` | FROZEN | Lifecycle contracts |
| `module.py` | FROZEN | Runtime module manifest |
| `runtime.py` | FROZEN | Runtime contracts |
| `service.py` | FROZEN | DI service contracts |

Contracts may only depend on Foundation Core.

---

# Contract Layer Constitution

Kernel Contracts own:

- immutable dataclasses;
- Protocols;
- ABC interfaces;
- runtime manifests;
- descriptors.

Kernel Contracts never own:

- runtime state;
- logging;
- DI implementation;
- event dispatch;
- lifecycle transitions;
- pipeline execution.

---

## CONTRACT-001 — src/kernel/contracts/__init__.py

### Owner

KR-004 Kernel Contracts

### Responsibility

Canonical contract export surface.

### Runtime Layer

L0

### Imported By

Entire runtime.

### Public Exports

#### Context Contracts

- RuntimeContext
- TraceContext

#### Event Contracts

- RuntimeEvent
- EventTrace

#### Lifecycle Contracts

- RuntimeLifecycleContract
- LifecycleState

#### Runtime Contracts

- RuntimeContract

#### Module Contracts

- RuntimeModuleManifest

#### Service Contracts

- ServiceDescriptor
- ServiceFactory
- ServiceContract

### Export Rules

Exports only public contracts.

No implementation exports.

### Forbidden Responsibilities

- runtime initialization;
- helper functions;
- validation.

---

## CONTRACT-002 — src/kernel/contracts/context.py

### Owner

KR-004 Kernel Contracts

### Responsibility

Runtime execution context contracts.

### Runtime Layer

L0

### Imported By

- ContextRuntime
- EventRuntime
- PipelineRuntime
- LifecycleRuntime

### Public Dataclasses

#### TraceContext

Immutable trace propagation object.

**Fields**

| Field | Type |
|-------|------|
| trace_id | TraceId |
| parent_trace_id | TraceId \| None |
| root_trace_id | TraceId |

---

#### RuntimeContext

Immutable execution context.

**Fields**

| Field | Type |
|-------|------|
| session_id | SessionId |
| pipeline_id | PipelineId |
| trace | TraceContext |
| metadata | Metadata |

### Factory Rules

Metadata uses immutable default factory.

### Forbidden Responsibilities

- metadata mutation;
- session management;
- trace generation.

### Validation Owner

ContextRuntime validates RuntimeContext construction.

---

## CONTRACT-003 — src/kernel/contracts/events.py

### Owner

KR-004 Kernel Contracts

### Responsibility

Runtime event contracts.

### Runtime Layer

L0

### Imported By

- EventRuntime
- DispatcherRuntime
- PublisherRuntime
- Subscribers
- Tests

### Public Dataclasses

#### EventTrace

Immutable event trace metadata.

**Fields**

| Field | Type |
|-------|------|
| trace_id | TraceId |
| parent_trace_id | TraceId \| None |
| root_trace_id | TraceId |

---

#### RuntimeEvent

Immutable runtime event.

**Required Fields**

| Field | Type |
|-------|------|
| event_id | EventId |
| event_type | str |
| session_id | SessionId |
| trace | EventTrace |

**Default Fields**

| Field | Type |
|-------|------|
| timestamp | datetime |
| payload | Payload |

### Required Event Fields

Vocabulary frozen.

- event_id
- event_type
- session_id
- trace
- timestamp
- payload

### Validation Rules

- UTC timestamp.
- JSON payload.
- Immutable dataclass.
- Required fields before defaults.

### Forbidden Responsibilities

- event publishing;
- handler registration;
- dispatch.

---

## CONTRACT-004 — src/kernel/contracts/lifecycle.py

### Owner

KR-004 Kernel Contracts

### Responsibility

Lifecycle interfaces.

### Runtime Layer

L0

### Imported By

LifecycleRuntime.

### Public Dataclasses

#### LifecycleState

Immutable lifecycle snapshot.

**Fields**

| Field | Type |
|-------|------|
| current | RuntimeStatus |
| previous | RuntimeStatus \| None |

### Public Protocols

#### RuntimeLifecycleContract

Abstract runtime lifecycle.

**Required Methods**

- initialize()
- start()
- stop()
- shutdown()

### Lifecycle Vocabulary

Uses RuntimeStatus only.

Vocabulary frozen.

### Forbidden Responsibilities

- transitions;
- runtime state mutation.

---

## CONTRACT-005 — src/kernel/contracts/module.py

### Owner

KR-004 Kernel Contracts

### Responsibility

Runtime module manifest contract.

### Runtime Layer

L0

### Imported By

ContainerRuntime

OrchestratorRuntime

BootstrapRuntime

### Public Dataclasses

#### RuntimeModuleManifest

Immutable runtime manifest.

**Fields**

| Field | Type |
|-------|------|
| module_id | ModuleId |
| runtime_layer | RuntimeLayer |
| depends_on | tuple[ModuleId, ...] |
| provides | tuple[ServiceId, ...] |
| version | str |

### Manifest Rules

- immutable;
- provides mandatory;
- dependency identifiers only.

### Forbidden Responsibilities

- dependency validation;
- registration.

---

## CONTRACT-006 — src/kernel/contracts/runtime.py

### Owner

KR-004 Kernel Contracts

### Responsibility

Runtime abstraction contracts.

### Runtime Layer

L0

### Imported By

BootstrapRuntime

RuntimeKernel

Tests

### Public Protocols

#### RuntimeContract

Canonical runtime interface.

**Required Methods**

- initialize()
- start()
- stop()
- shutdown()
- health()

### Runtime Guarantees

Every runtime implements RuntimeContract.

### Forbidden Responsibilities

- runtime creation;
- runtime ownership.

---

## CONTRACT-007 — src/kernel/contracts/service.py

### Owner

KR-004 Kernel Contracts

### Responsibility

Dependency Injection contracts.

### Runtime Layer

L0

### Imported By

ContainerRuntime

ResolverRuntime

RegistryRuntime

ProviderRuntime

### Public Protocols

#### ServiceContract

Canonical DI service interface.

Methods:

- initialize()
- shutdown()

---

ADR-004 and the approved KR-004 reconciliation preserve only ServiceContract
and ServiceDescriptor exports. The former ServiceFactory reservation is not a
public implementation contract.

### Public Dataclasses

#### ServiceDescriptor

Immutable DI descriptor.

**Fields**

| Field | Type |
|-------|------|
| service_id | ServiceId |
| implementation | type[ServiceContract] |
| scope | DIScope |
| eager | bool |
| dependencies | tuple[tuple[str, ServiceId], ...] |

### Validation Rules

- implementation parameterized.
- dependencies immutable.
- eager defaults False; dependencies defaults ().
- ADR-004: explicit constructor keyword/ServiceId bindings; validation belongs
  to KR-005, not descriptor construction.

### Forbidden Responsibilities

- service construction;
- service caching;
- resolution logic.

---

# KR-004 Export Matrix

| File | Exports |
|------|---------|
| context.py | RuntimeContext, TraceContext |
| events.py | RuntimeEvent, EventTrace |
| lifecycle.py | RuntimeLifecycleContract, LifecycleState |
| module.py | RuntimeModuleManifest |
| runtime.py | RuntimeContract |
| service.py | ServiceContract, ServiceDescriptor |

Every export appears in M-03.

---

# KR-004 Dependency Matrix

| File | Allowed Imports |
|------|------------------|
| context.py | src.core.types |
| events.py | src.core.types, context.py |
| lifecycle.py | src.core.types |
| module.py | src.core.types |
| runtime.py | lifecycle.py |
| service.py | src.core.types |

Contracts never import runtime implementation.

---

# KR-004 Ownership Matrix

| Object | Owner |
|--------|-------|
| RuntimeContext | context.py |
| TraceContext | context.py |
| RuntimeEvent | events.py |
| EventTrace | events.py |
| LifecycleState | lifecycle.py |
| RuntimeLifecycleContract | lifecycle.py |
| RuntimeModuleManifest | module.py |
| RuntimeContract | runtime.py |
| ServiceDescriptor | service.py |
| ServiceFactory | service.py |
| ServiceContract | service.py |

No contract has multiple owners.

---

# KR-004 Validation Ownership

Validation is performed by runtime implementations.

| Runtime | Validates |
|----------|-----------|
| ContextRuntime | RuntimeContext |
| EventRuntime | RuntimeEvent |
| LifecycleRuntime | LifecycleState transitions |
| ContainerRuntime | ServiceDescriptor |
| ManifestRuntime | RuntimeModuleManifest |

Contracts themselves perform no validation.

---

# KR-004 Forbidden Patterns

Kernel Contracts may never contain:

- logging;
- filesystem access;
- HTTP clients;
- dependency injection implementation;
- event dispatch;
- ContextVar;
- asyncio tasks;
- mutable globals.

Contracts remain pure immutable definitions.

---

<!-- ========================================================================= -->
<!-- M-01 PART 4 — KR-005 Dependency Injection Runtime Registry -->
<!-- ========================================================================= -->

# KR-005 — Dependency Injection Runtime Registry

## Approved ADR-004 reconciliation

The APPROVED `../wave1/KR-005_DI.md` compiles ADR-004 P-01/P-02/P-05.
It supersedes legacy method/signature and cache-freezing examples in this KR-005
section only. Ownership and these five production paths remain unchanged.
Container exposes register/contains/descriptors and async resolve/remove/release/
clear_session/clear_pipeline. Registry retains register/unregister/get/contains/list.
Resolver owns graph traversal and transient lifetime; Provider constructs and
awaits hooks; generic Scope owns cached lifetimes through a typed async callback.
No public component properties or additional Runtime are authorized.


**Runtime Layer:** L0 Kernel

Directory:

```
src/kernel/runtime/
```

Dependency Injection Runtime owns service registration, dependency resolution, lifetime management and scope isolation.

No other runtime may create, cache or resolve services.

Files:

| File | Status | Public API |
|------|--------|------------|
| `container.py` | FROZEN | ContainerRuntime |
| `registry.py` | FROZEN | RegistryRuntime |
| `resolver.py` | FROZEN | ResolverRuntime |
| `provider.py` | FROZEN | ProviderRuntime |
| `scope.py` | FROZEN | ScopeRuntime |

---

# DI Runtime Constitution

Dependency Injection Runtime owns:

- service descriptors;
- service registry;
- dependency graph;
- constructor injection;
- scope caches;
- service disposal.

Dependency Injection Runtime never owns:

- runtime lifecycle;
- logging;
- event dispatch;
- configuration loading;
- pipeline execution.

---

## DI-001 — src/kernel/runtime/container.py

### Owner

KR-005 Dependency Injection Runtime

### Responsibility

Public dependency injection container.

### Runtime Layer

L0

### Imported By

- BootstrapRuntime
- RuntimeKernel
- OrchestratorRuntime
- Tests

### Public Exports

#### Classes

- `ContainerRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `register()` | Register service descriptor. |
| `unregister()` | Remove service descriptor. |
| `resolve()` | Resolve initialized service. |
| `contains()` | Check service registration. |
| `shutdown()` | Dispose cached services. |

### Internal Ownership

ContainerRuntime owns:

- RegistryRuntime
- ResolverRuntime
- ScopeRuntime
- ProviderRuntime

### Forbidden Responsibilities

- creating runtime graph;
- lifecycle transitions;
- event publishing.

---

## DI-002 — src/kernel/runtime/registry.py

### Owner

KR-005 Dependency Injection Runtime

### Responsibility

Canonical service registry.

### Runtime Layer

L0

### Imported By

ContainerRuntime

ResolverRuntime

Tests

### Public Exports

#### Classes

- `RegistryRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `register()` | Store descriptor. |
| `remove()` | Remove descriptor. |
| `descriptor()` | Retrieve descriptor. |
| `contains()` | Check descriptor existence. |
| `list()` | Immutable descriptor snapshot. |

### Internal Storage

Owns:

```
dict[ServiceId, ServiceDescriptor]
```

### Forbidden Responsibilities

- instance creation;
- dependency resolution;
- scope cache.

---

## DI-003 — src/kernel/runtime/resolver.py

### Owner

KR-005 Dependency Injection Runtime

### Responsibility

Dependency graph resolver.

### Runtime Layer

L0

### Imported By

ContainerRuntime

Tests

### Public Exports

#### Classes

- `ResolverRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `resolve()` | Resolve service recursively. |
| `dependencies()` | Return dependency graph. |

### Private Methods

| Method | Purpose |
|--------|---------|
| `_resolve_descriptor()` | Recursive resolution. |
| `_detect_cycle()` | DFS cycle detection. |
| `_construct()` | Constructor injection. |

### Validation Ownership

Validates:

- descriptor existence;
- dependency existence;
- circular dependencies;
- constructor compatibility.

### Forbidden Responsibilities

- descriptor registration;
- caching;
- lifecycle shutdown.

---

## DI-004 — src/kernel/runtime/provider.py

### Owner

KR-005 Dependency Injection Runtime

### Responsibility

Service instantiation runtime.

### Runtime Layer

L0

### Imported By

ResolverRuntime

Tests

### Public Exports

#### Classes

- `ProviderRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `build()` | Instantiate service. |
| `initialize()` | Execute initialization hook. |
| `shutdown()` | Execute shutdown hook. |

### Construction Rules

- constructor injection only;
- async initialize supported;
- shutdown exactly once.

### Forbidden Responsibilities

- dependency traversal;
- descriptor registry;
- scope ownership.

---

## DI-005 — src/kernel/runtime/scope.py

### Owner

KR-005 Dependency Injection Runtime

### Responsibility

Scope cache manager.

### Runtime Layer

L0

### Imported By

ContainerRuntime

ResolverRuntime

ProviderRuntime

Tests

### Public Exports

#### Classes

- `ScopeRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `get()` | Retrieve cached scoped instance. |
| `store()` | Cache scoped instance. |
| `clear_session()` | Dispose session scope. |
| `clear_pipeline()` | Dispose pipeline scope. |
| `clear_application()` | Dispose application scope. |
| `clear_all()` | Dispose all caches. |

### Scope Ownership

Owns exactly four caches.

| Scope | Cache |
|-------|-------|
| Application | Global runtime cache |
| Session | Session cache |
| Pipeline | Pipeline cache |
| Transient | No cache |

### Forbidden Responsibilities

- service construction;
- descriptor validation;
- dependency graph.

---

# KR-005 Export Matrix

| File | Public Symbols |
|------|----------------|
| container.py | ContainerRuntime |
| registry.py | RegistryRuntime |
| resolver.py | ResolverRuntime |
| provider.py | ProviderRuntime |
| scope.py | ScopeRuntime |

---

# KR-005 Dependency Matrix

| File | Allowed Imports |
|------|------------------|
| container.py | registry, resolver, provider, scope, contracts |
| registry.py | service contracts |
| resolver.py | registry, provider, scope, contracts |
| provider.py | service contracts |
| scope.py | core.types |

No file imports LifecycleRuntime, EventBusRuntime or BootstrapRuntime.

---

# KR-005 Ownership Matrix

| Object | Owner |
|--------|-------|
| Service descriptors | RegistryRuntime |
| Dependency graph | ResolverRuntime |
| Constructor injection | ProviderRuntime |
| Scope caches | ScopeRuntime |
| Public DI API | ContainerRuntime |

Every DI object has exactly one owner.

---

# KR-005 Runtime Cache Ownership

| Cache | Lifetime |
|-------|----------|
| Application cache | Runtime lifetime |
| Session cache | Session lifetime |
| Pipeline cache | Pipeline lifetime |
| Transient cache | No cache |

Application cache is immutable after initialization.

---

# KR-005 Validation Ownership

| Runtime | Validates |
|----------|-----------|
| RegistryRuntime | Duplicate registration |
| ResolverRuntime | Missing dependencies |
| ResolverRuntime | Circular dependencies |
| ProviderRuntime | Service initialization |
| ScopeRuntime | Scope consistency |

---

# KR-005 Forbidden Patterns

Dependency Injection Runtime may never contain:

- singleton globals;
- manual service factories outside ProviderRuntime;
- setter/property injection;
- event publishing;
- lifecycle state transitions;
- filesystem or network access.

DI Runtime owns dependency management only.

---

<!-- ========================================================================= -->
<!-- M-01 PART 5 — KR-006 Lifecycle Runtime + KR-007 Event Bus Runtime -->
<!-- ========================================================================= -->

# KR-006 — Lifecycle Runtime Registry

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

**Runtime Layer:** L0 Kernel

Directory:

```
src/kernel/runtime/
```

Lifecycle Runtime owns the runtime state machine and lifecycle transitions.

Files:

| File | Status | Public API |
|------|--------|------------|
| `lifecycle.py` | FROZEN | LifecycleRuntime |
| `state.py` | FROZEN | StateRuntime |
| `hooks.py` | FROZEN | HookRuntime |

Lifecycle Runtime never owns runtime construction or dependency injection.

---

## LIFECYCLE-001 — src/kernel/runtime/lifecycle.py

### Owner

KR-006 Lifecycle Runtime

### Responsibility

Public lifecycle runtime coordinator.

### Runtime Layer

L0

### Imported By

- RuntimeKernel
- BootstrapRuntime
- Tests

### Public Exports

#### Classes

- `LifecycleRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `initialize()` | Initialize runtime graph. |
| `start()` | Transition READY → RUNNING. |
| `stop()` | Transition RUNNING → STOPPED. |
| `shutdown()` | Dispose runtime graph. |
| `status()` | Return current RuntimeStatus. |

### Internal Ownership

Owns:

- StateRuntime
- HookRuntime

### Forbidden Responsibilities

- DI registration.
- Event publishing.
- Runtime creation.
- Pipeline execution.

---

## LIFECYCLE-002 — src/kernel/runtime/state.py

### Owner

KR-006 Lifecycle Runtime

### Responsibility

Runtime state machine.

### Runtime Layer

L0

### Imported By

LifecycleRuntime

Tests

### Public Exports

#### Classes

- `StateRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `current()` | Current RuntimeStatus. |
| `previous()` | Previous RuntimeStatus. |
| `transition()` | Execute validated transition. |
| `can_transition()` | Validate transition. |
| `reset()` | Reset state (tests only). |

### Internal Storage

Owns immutable LifecycleState snapshot.

### Transition Authority

Only StateRuntime may mutate lifecycle state.

### Forbidden Responsibilities

- hooks.
- runtime shutdown.
- logging.

---

## LIFECYCLE-003 — src/kernel/runtime/hooks.py

### Owner

KR-006 Lifecycle Runtime

### Responsibility

Lifecycle hook registry.

### Runtime Layer

L0

### Imported By

LifecycleRuntime

Tests

### Public Exports

#### Classes

- `HookRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `register_initialize()` | Register initialize hook. |
| `register_start()` | Register start hook. |
| `register_stop()` | Register stop hook. |
| `register_shutdown()` | Register shutdown hook. |
| `run_initialize()` | Execute initialize hooks. |
| `run_start()` | Execute start hooks. |
| `run_stop()` | Execute stop hooks. |
| `run_shutdown()` | Execute shutdown hooks. |

### Hook Ordering

Hooks execute in registration order.

Shutdown executes reverse registration order.

### Forbidden Responsibilities

- runtime transitions.
- dependency resolution.

---

# KR-006 Export Matrix

| File | Public Symbols |
|------|----------------|
| lifecycle.py | LifecycleRuntime |
| state.py | StateRuntime |
| hooks.py | HookRuntime |

---

# KR-006 Dependency Matrix

| File | Allowed Imports |
|------|------------------|
| lifecycle.py | state.py, hooks.py, contracts |
| state.py | contracts, core.types |
| hooks.py | contracts |

Lifecycle Runtime never imports ContainerRuntime or EventBusRuntime.

---

# KR-006 Ownership Matrix

| Object | Owner |
|--------|-------|
| Runtime state machine | StateRuntime |
| Lifecycle transitions | LifecycleRuntime |
| Hook registry | HookRuntime |
| Hook execution | HookRuntime |

---

# KR-006 Validation Ownership

| Runtime | Validates |
|----------|-----------|
| StateRuntime | Transition legality |
| LifecycleRuntime | Lifecycle order |
| HookRuntime | Hook registration consistency |

---

# KR-006 Forbidden Patterns

Lifecycle Runtime may never contain:

- DI logic.
- Event handlers.
- Context mutation.
- Runtime creation.
- Filesystem access.
- Network access.

Lifecycle Runtime owns runtime state transitions only.

---

# KR-007 — Event Bus Runtime Registry

**Authority:** APPROVED ADR-005 E-01–E-04, ADR-004 P-04 and AB-00C/D (2026-10-06).
The exact signatures and acceptance contract are `../wave1/KR-007_EVENT_BUS.md`.
Only KR-007 entries are reconciled; other module contracts remain unchanged.

| File | Export | Responsibility | Concrete dependencies |
| --- | --- | --- | --- |
| bus.py | EventBusRuntime | Public facade/composition | Publisher, Dispatcher, Subscriber |
| publisher.py | PublisherRuntime | Sole new event factory, validation, publication | Dispatcher |
| dispatcher.py | DispatcherRuntime | Sequential snapshot delivery | Subscriber |
| subscriber.py | SubscriberRuntime | Instance-local registry | None |

| Class | Exact method names |
| --- | --- |
| EventBusRuntime | subscribe, unsubscribe, async publish, async publish_many, create_for_runtime, handlers, contains, clear; async initialize/start/stop/shutdown, health; runtime_name/runtime_layer properties |
| PublisherRuntime | create, validate, async publish, async publish_many |
| DispatcherRuntime | async dispatch, async dispatch_many |
| SubscriberRuntime | subscribe, unsubscribe, handlers, contains, clear |

Each file exports only its listed class. Subscriber stores a private
`dict[str, list[EventHandlerContract]]` and returns immutable handler tuples.
Publisher is consumed by Bus/tests, not Dispatcher; Dispatcher is consumed by
Publisher/Bus/tests. Foundation, contracts and all runtime ownership stay unchanged.

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

Tests: `tests/kernel/test_event_bus.py`, owned by KR-011 with approved active-module
adjustments. No event.py/EventRuntime, utilities, globals, I/O, DI or lifecycle state.

<!-- ========================================================================= -->
<!-- M-01 PART 6 — KR-008 Runtime Context Runtime + KR-009 Pipeline Runtime -->
<!-- ========================================================================= -->

# KR-008 — Runtime Context Runtime Registry

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

# KR-009 — Pipeline Runtime Registry

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

<!-- ========================================================================= -->
<!-- M-01 PART 7 — KR-010 Bootstrap Runtime + KR-011 Test Suite Registry -->
<!-- ========================================================================= -->

# KR-010 — Bootstrap Runtime Registry

**Status:** APPROVED — ADR-008 B-01–B-05, 2026-10-06.
Exact contract: [KR-010](../wave1/KR-010_RUNNER_BOOTSTRAP.md).
Authority: [ADR-008](../ADR-008_KR010_Bootstrap_Reconciliation_Proposal_v1.0.md).

Three production files only; same owners/exports. Canonical test ownership remains
KR-011 with active-module adjustments explicitly approved by ADR-004/008.

| File | Owner / export | Dependencies / responsibility |
| --- | --- | --- |
| src/kernel/runtime/bootstrap.py | KR-010 / BootstrapRuntime | Configuration, Logging, public Container/Lifecycle/EventBus/Context/Orchestrator, RuntimeKernel; narrow SessionRuntime construction exception |
| src/kernel/runtime/runtime.py | KR-010 / RuntimeKernel | Existing Foundation/version and contracts, PipelineDefinition, five facades and explicit SessionRuntime reference; lifecycle/DI composition only |
| src/main.py | KR-010 / main | asyncio, Bootstrap, existing Foundation vocabulary and optional Logger; bounded startup/finalization |

Construction: Settings, Logging, Context, Session(context) storage collaborator,
Container, EventBus, Orchestrator(event_bus), Lifecycle, Kernel. Build is async,
returns a wired CREATED graph, never initializes/resolves/publishes/creates directories.
Lifecycle registers Context, Container, EventBus, Orchestrator in forward order;
stop/shutdown use reverse touched order. Bootstrap never constructs an Executor.

Public builders retain current signatures; Kernel retains all existing properties
and adds explicit required constructor session, read-only session and async
remove_session(SessionId). Kernel implements existing RuntimeContract. No renamed
entrypoints, new Runtime, moved ownership, business pipeline or dependency package.
execute requires RUNNING and guarded finally Container.clear_pipeline; removal
uses Container.clear_session then Session.remove; full admitted shutdown drains
Session registry after Lifecycle, including failure/cancellation. First errors and
legal terminal FAILED are preserved. main is bounded smoke, no signal wait/inputless execute.

Canonical acceptance: tests/kernel/test_bootstrap.py and
tests/integration/test_runtime_startup.py; all APIs and 100% executable-line target
per three files, required gates/CI. Other module files and tests remain frozen.

---

# KR-011 — Wave 1 Test Suite Registry

**Runtime Layer:** Validation Layer

Directory:

```
tests/
```

KR-011 owns every executable validation artifact for Wave 1.

Production code never imports tests.

---

# Test Suite Constitution

Wave 1 contains exactly eleven executable test modules.

| File | Status | Purpose |
|------|--------|---------|
| tests/conftest.py | FROZEN | Shared fixtures |
| tests/core/test_types.py | FROZEN | Foundation types |
| tests/core/test_settings.py | FROZEN | Configuration Runtime |
| tests/core/test_logger.py | FROZEN | Logging Runtime |
| tests/kernel/test_contracts.py | FROZEN | Kernel Contracts |
| tests/kernel/test_container.py | FROZEN | DI Runtime |
| tests/kernel/test_lifecycle.py | FROZEN | Lifecycle Runtime |
| tests/kernel/test_event_bus.py | FROZEN | Event Runtime |
| tests/kernel/test_context.py | FROZEN | Runtime Context Runtime |
| tests/kernel/test_pipeline.py | FROZEN | Pipeline Runtime |
| tests/kernel/test_bootstrap.py | FROZEN | Bootstrap Runtime |
| tests/integration/test_runtime_startup.py | FROZEN | Runtime integration |

---

## TEST-001 — tests/conftest.py

### Owner

KR-011

### Responsibility

Shared fixtures only.

### Public Fixtures

| Fixture | Responsibility |
|---------|----------------|
| settings | Immutable Settings |
| trace_context | TraceContext |
| runtime_context | RuntimeContext |
| container | ContainerRuntime |
| lifecycle | LifecycleRuntime |
| event_bus | EventBusRuntime |
| orchestrator | OrchestratorRuntime |

### Forbidden Responsibilities

- test logic;
- assertions.

---

## TEST-002 — tests/core/test_types.py

### Owner

KR-011

### Responsibility

Validate Foundation Core typing.

### Coverage

- RuntimeLayer vocabulary.
- RuntimeStatus vocabulary.
- HealthStatus vocabulary.
- EventPriority vocabulary.
- EventPhase vocabulary.
- Metadata JSON compatibility.

---

## TEST-003 — tests/core/test_settings.py

### Owner

KR-011

### Responsibility

Validate Configuration Runtime.

### Coverage

- .env loading.
- immutable Settings.
- get_settings / validate_configuration and all T-02 fields/helpers/validators.
- default/env/.env/alias/extra/frozen/error policies.
- relative Path conversion without filesystem creation.
- isolated stdlib cache identity/invalidation.

---

## TEST-004 — tests/core/test_logger.py

### Owner

KR-011

### Responsibility

Validate Logging Runtime.

### Coverage

- logger cache.
- formatter output.
- handler creation.
- context injection.

---

## TEST-005 — tests/kernel/test_contracts.py

### Owner

KR-011

### Responsibility

Validate Kernel Contracts.

### Coverage

- RuntimeEvent.
- RuntimeContext.
- RuntimeModuleManifest.
- ServiceDescriptor.
- LifecycleState.
- RuntimeContract exports.

---

## TEST-006 — tests/kernel/test_container.py

### Owner

KR-011

### Responsibility

Validate DI Runtime.

### Coverage

- registration.
- resolution.
- scopes.
- circular dependency detection.
- shutdown disposal.

---

## TEST-007 — tests/kernel/test_lifecycle.py

### Owner

KR-011

### Responsibility

Validate Lifecycle Runtime.

### Coverage

- transitions.
- invalid transitions.
- hook execution.
- shutdown ordering.

---

## TEST-008 — tests/kernel/test_event_bus.py

### Owner

KR-011

### Responsibility

Validate Event Runtime.

### Coverage

- subscriptions.
- publication.
- dispatch ordering.
- handler failures.

---

## TEST-009 — tests/kernel/test_context.py

### Owner

KR-011

### Responsibility

Validate Runtime Context Runtime.

### Coverage

- RuntimeContext creation.
- metadata updates.
- session lifecycle.
- immutable snapshots.

---

## TEST-010 — tests/kernel/test_pipeline.py

### Owner

KR-011

### Responsibility

Validate Pipeline Runtime.

### Coverage

- DAG validation.
- dependency validation.
- execution ordering.
- pipeline failure behavior.

---

## TEST-011 — tests/kernel/test_bootstrap.py

### Owner

KR-011

### Responsibility

Validate Bootstrap Runtime.

### Coverage

- runtime construction.
- startup sequence.
- shutdown sequence.
- health aggregation.

---

## TEST-012 — tests/integration/test_runtime_startup.py

### Owner

KR-011

### Responsibility

End-to-end Wave 1 runtime validation.

### Coverage

- Bootstrap.
- Initialize.
- Start.
- Execute pipeline.
- Stop.
- Shutdown.

---

# KR-011 Ownership Matrix

| Artifact | Owner |
|----------|-------|
| Shared fixtures | conftest.py |
| Foundation tests | tests/core |
| Runtime tests | tests/kernel |
| Integration tests | tests/integration |

---

# KR-011 Validation Ownership

KR-011 validates every KR exactly once.

| KR | Test Module |
|----|-------------|
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
| Runtime | test_runtime_startup.py |

Coverage is mandatory.

---

# KR-011 Forbidden Patterns

Tests may never contain:

- skipped production tests;
- placeholder assertions;
- shared mutable runtime state;
- production implementation.

Tests validate public API only.

---

<!-- ========================================================================= -->
<!-- M-01 PART 8 — Global Registry Index + Ownership Matrix + Definition of Done -->
<!-- ========================================================================= -->

# Global Production File Registry

This section is the canonical inventory of every production Python file that exists in Wave 1.

The registry is exhaustive.

If a production file is absent from this table, it must not exist.

---

## Wave 1 Production Inventory

| KR | File | Layer | Status |
|----|------|-------|--------|
| KR-001 | src/core/__init__.py | L0 | FROZEN |
| KR-001 | src/core/types.py | L0 | FROZEN |
| KR-001 | src/core/constants.py | L0 | FROZEN |
| KR-001 | src/core/exceptions.py | L0 | FROZEN |
| KR-001 | src/core/version.py | L0 | FROZEN |
| KR-002 | src/core/settings.py | L0 | FROZEN |
| KR-002 | src/core/config.py | L0 | FROZEN |
| KR-003 | src/core/logging_config.py | L0 | FROZEN |
| KR-003 | src/core/logger.py | L0 | FROZEN |
| KR-004 | src/kernel/contracts/__init__.py | L0 | FROZEN |
| KR-004 | src/kernel/contracts/context.py | L0 | FROZEN |
| KR-004 | src/kernel/contracts/events.py | L0 | FROZEN |
| KR-004 | src/kernel/contracts/lifecycle.py | L0 | FROZEN |
| KR-004 | src/kernel/contracts/module.py | L0 | FROZEN |
| KR-004 | src/kernel/contracts/runtime.py | L0 | FROZEN |
| KR-004 | src/kernel/contracts/service.py | L0 | FROZEN |
| KR-005 | src/kernel/runtime/container.py | L0 | FROZEN |
| KR-005 | src/kernel/runtime/registry.py | L0 | FROZEN |
| KR-005 | src/kernel/runtime/resolver.py | L0 | FROZEN |
| KR-005 | src/kernel/runtime/provider.py | L0 | FROZEN |
| KR-005 | src/kernel/runtime/scope.py | L0 | FROZEN |
| KR-006 | src/kernel/runtime/lifecycle.py | L0 | FROZEN |
| KR-006 | src/kernel/runtime/state.py | L0 | FROZEN |
| KR-006 | src/kernel/runtime/hooks.py | L0 | FROZEN |
| KR-007 | src/kernel/runtime/bus.py | L0 | FROZEN |
| KR-007 | src/kernel/runtime/publisher.py | L0 | FROZEN |
| KR-007 | src/kernel/runtime/dispatcher.py | L0 | FROZEN |
| KR-007 | src/kernel/runtime/subscriber.py | L0 | FROZEN |
| KR-008 | src/kernel/runtime/context.py | L0 | FROZEN |
| KR-008 | src/kernel/runtime/metadata.py | L0 | FROZEN |
| KR-008 | src/kernel/runtime/session.py | L0 | FROZEN |
| KR-009 | src/kernel/runtime/pipeline.py | L0 | FROZEN |
| KR-009 | src/kernel/runtime/manifest.py | L0 | FROZEN |
| KR-009 | src/kernel/runtime/executor.py | L0 | FROZEN |
| KR-009 | src/kernel/runtime/orchestrator.py | L0 | FROZEN |
| KR-010 | src/kernel/runtime/bootstrap.py | L0 | FROZEN |
| KR-010 | src/kernel/runtime/runtime.py | L0 | FROZEN |
| KR-010 | src/main.py | L0 | FROZEN |

**Total production files: 38**

---

# Repository Directory Ownership Matrix

| Directory | Owner KR | Purpose |
|-----------|----------|---------|
| src/core | KR-001–003 | Foundation runtime infrastructure. |
| src/kernel/contracts | KR-004 | Immutable runtime contracts. |
| src/kernel/runtime | KR-005–010 | Runtime implementation. |
| tests/core | KR-011 | Foundation tests. |
| tests/kernel | KR-011 | Runtime tests. |
| tests/integration | KR-011 | End-to-end runtime tests. |
| docs/architecture/master | Engineering Bible | Canonical documentation. |

No production implementation may exist outside these directories during Wave 1.

---

# Runtime Layer Ownership Matrix

## L0 — Kernel Runtime

All Wave 1 production files belong to L0.

| Runtime | Files |
|---------|------:|
| Foundation Core | 5 |
| Configuration Runtime | 2 |
| Logging Runtime | 2 |
| Kernel Contracts | 7 |
| Dependency Injection Runtime | 5 |
| Lifecycle Runtime | 3 |
| Event Bus Runtime | 4 |
| Runtime Context Runtime | 3 |
| Pipeline Runtime | 4 |
| Bootstrap Runtime | 3 |

**Total L0 files: 38**

Layers L1–L8 contain directory scaffolding only.

---

# File → Runtime Ownership Matrix

## Foundation Runtime

| File | Runtime |
|------|---------|
| types.py | Foundation Core |
| constants.py | Foundation Core |
| exceptions.py | Foundation Core |
| version.py | Foundation Core |

## Configuration Runtime

| File | Runtime |
|------|---------|
| settings.py | Configuration Runtime |
| config.py | Configuration Runtime |

## Logging Runtime

| File | Runtime |
|------|---------|
| logger.py | Logging Runtime |
| logging_config.py | Logging Runtime |

## Kernel Contracts

| File | Runtime |
|------|---------|
| context.py | Kernel Contracts |
| events.py | Kernel Contracts |
| lifecycle.py | Kernel Contracts |
| module.py | Kernel Contracts |
| runtime.py | Kernel Contracts |
| service.py | Kernel Contracts |

## Dependency Injection Runtime

| File | Runtime |
|------|---------|
| container.py | DI Runtime |
| registry.py | DI Runtime |
| resolver.py | DI Runtime |
| provider.py | DI Runtime |
| scope.py | DI Runtime |

## Lifecycle Runtime

| File | Runtime |
|------|---------|
| lifecycle.py | Lifecycle Runtime |
| state.py | Lifecycle Runtime |
| hooks.py | Lifecycle Runtime |

## Event Runtime

| File | Runtime |
|------|---------|
| bus.py | Event Bus Runtime |
| publisher.py | Event Bus Runtime |
| dispatcher.py | Event Bus Runtime |
| subscriber.py | Event Bus Runtime |

## Runtime Context Runtime

| File | Runtime |
|------|---------|
| context.py | Runtime Context Runtime |
| metadata.py | Runtime Context Runtime |
| session.py | Runtime Context Runtime |

## Pipeline Runtime

| File | Runtime |
|------|---------|
| pipeline.py | Pipeline Runtime |
| manifest.py | Pipeline Runtime |
| executor.py | Pipeline Runtime |
| orchestrator.py | Pipeline Runtime |

## Bootstrap Runtime

| File | Runtime |
|------|---------|
| bootstrap.py | Bootstrap Runtime |
| runtime.py | Bootstrap Runtime |
| src/main.py | Bootstrap Runtime |

---

# Public Export Ownership Matrix

Every public symbol has exactly one file owner.

| Symbol Group | Canonical Owner |
|--------------|-----------------|
| RuntimeLayer | src/core/types.py |
| RuntimeStatus | src/core/types.py |
| DIScope | src/core/types.py |
| EventPriority | src/core/types.py |
| EventPhase | src/core/types.py |
| Settings | src/core/settings.py |
| get_settings | src/core/config.py |
| RuntimeContext | src/kernel/contracts/context.py |
| TraceContext | src/kernel/contracts/context.py |
| RuntimeEvent | src/kernel/contracts/events.py |
| RuntimeModuleManifest | src/kernel/contracts/module.py |
| ServiceDescriptor | src/kernel/contracts/service.py |
| ContainerRuntime | src/kernel/runtime/container.py |
| LifecycleRuntime | src/kernel/runtime/lifecycle.py |
| EventBusRuntime | src/kernel/runtime/bus.py |
| ContextRuntime | src/kernel/runtime/context.py |
| PipelineDefinition | src/kernel/runtime/pipeline.py |
| ExecutorRuntime | src/kernel/runtime/executor.py |
| RuntimeKernel | src/kernel/runtime/runtime.py |

Duplicate public symbol ownership is forbidden.

---

# Import Visibility Matrix

Defines which repository layers may import which directories.

| Importing Layer | Allowed Targets |
|-----------------|-----------------|
| src/core | Standard Library only |
| src/kernel/contracts | src/core |
| src/kernel/runtime | src/core + src/kernel/contracts |
| src | src/core + src/kernel/runtime |
| tests | Entire repository public API |
| docs | None |

Reverse imports are forbidden.

---

# File Lifecycle Matrix

| Lifecycle Phase | Files Responsible |
|-----------------|------------------|
| Configuration Load | settings.py, config.py |
| Logging Setup | logging_config.py, logger.py |
| Runtime Build | bootstrap.py |
| DI Initialization | container.py |
| Lifecycle Initialization | lifecycle.py |
| EventBus Initialization | bus.py |
| Context Creation | context.py |
| Pipeline Validation | manifest.py |
| Pipeline Execution | executor.py |
| Runtime Shutdown | lifecycle.py + bootstrap.py |

Every lifecycle phase has one owner.

---

# Validation Ownership Matrix

| Validation | Owner File |
|-----------|------------|
| Environment validation | settings.py |
| Logging validation | logging_config.py |
| Manifest validation | manifest.py |
| Runtime state validation | state.py |
| Event validation | publisher.py |
| Context validation | context.py |
| DI validation | resolver.py |
| Bootstrap validation | bootstrap.py |

No validation responsibility is duplicated.

---

# Repository Integrity Rules

A repository is architecture-valid only if:

## File Rules

- Every production file exists exactly once.
- Every production file belongs to one KR.
- Every production file belongs to one runtime layer.
- Every production file has one public API owner.

## Directory Rules

- No undocumented directories.
- No undocumented production files.
- No implementation inside documentation directories.

## Ownership Rules

- No duplicated runtime owners.
- No duplicated public API owners.
- No duplicated manifest owners.
- No duplicated version owners.

Violating any rule is an Architecture Conflict.

---

# Wave 1 Registry Freeze

The following repository elements are frozen for Wave 1.

## Frozen Directories

- src/core
- src/kernel/contracts
- src/kernel/runtime
- tests/core
- tests/kernel
- tests/integration

## Frozen File Count

- Production files: **38**
- Test modules: **11**
- Documentation index files: **11**

No additions without an ADR.

---

# M-01 Definition of Done

`01_FILE_REGISTRY.md` is GREEN only if:

- Every production file is listed.
- Every production file has an owner KR.
- Every production file has one runtime layer.
- Every production file has one responsibility.
- Every public export has one canonical owner.
- Every directory ownership rule is defined.
- Repository inventory totals match Wave 1 architecture.
- No undocumented production file exists.

---

# Canonical Completion Marker

**Document ID:** M-01

**Document Name:** File Registry

**Version:** 1.1 Canonical

**Status:** COMPLETE

**Authority:** AURORA Engineering Bible v1.1

**END OF DOCUMENT**
