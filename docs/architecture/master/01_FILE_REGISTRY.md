# AURORA ENGINEERING BIBLE v1.1

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

**Runtime Layer:** L0 Kernel

Directory:

```
src/core/
```

Files:

| File | Status | Public API |
|------|--------|-----------|
| `settings.py` | FROZEN | Immutable Settings model |
| `config.py` | FROZEN | Configuration runtime API |

Configuration Runtime owns **all environment configuration**.

No other KR may read environment variables directly.

---

## CONFIG-001 — src/core/settings.py

### Owner

KR-002 Configuration Runtime

### Responsibility

Immutable runtime configuration model.

### Runtime Layer

L0

### Imported By

- BootstrapRuntime
- ContainerRuntime
- LoggingRuntime
- RuntimeKernel
- Tests

### Public Exports

#### Classes

- `Settings`

#### Type Aliases

- `EnvironmentName`

### Public Configuration Groups

#### Runtime

- app_name
- app_environment
- debug
- log_level

#### Directories

- project_root
- config_directory
- cache_directory
- data_directory
- log_directory

#### Event Runtime

- event_version
- trace_root_id

#### Container Runtime

- application_scope_cache_enabled

#### Logging Runtime

- console_logging_enabled
- json_logging_enabled

### Configuration Sources

Order is immutable.

1. Environment variables.
2. `.env`
3. Pydantic defaults.

### Validation Owner

Settings validates:

- directory paths;
- log level;
- environment name;
- required variables.

### Forbidden Responsibilities

- filesystem creation;
- logging configuration;
- dependency injection;
- runtime initialization.

---

## CONFIG-002 — src/core/config.py

### Owner

KR-002 Configuration Runtime

### Responsibility

Runtime configuration access API.

### Runtime Layer

L0

### Imported By

Entire runtime.

### Public Functions

| Function | Purpose |
|----------|---------|
| `get_settings()` | Returns immutable cached Settings instance. |
| `reload_settings()` | Invalidates cache and rebuilds Settings. |

### Cache Ownership

Owns exactly one immutable application cache.

Allowed cache:

```
functools.cache
```

No mutable cache.

### Dependency Owner

Uses only:

- settings.py
- functools
- pathlib
- pydantic-settings

### Forbidden Responsibilities

- environment parsing outside Settings;
- runtime state;
- global mutable configuration.

---

# KR-002 Ownership Matrix

| Object | Owner |
|--------|-------|
| Settings instance | config.py |
| Environment parsing | settings.py |
| Validation | settings.py |
| Cache invalidation | config.py |

No shared ownership.

---

# KR-003 — Logging Runtime Registry

**Runtime Layer:** L0 Kernel

Directory:

```
src/core/
```

Files:

| File | Status | Public API |
|------|--------|-----------|
| `logging_config.py` | FROZEN | Logging configuration runtime |
| `logger.py` | FROZEN | Logger factory API |

Logging Runtime owns every logging object.

No production file imports `logging` directly.

---

## LOGGING-001 — src/core/logging_config.py

### Owner

KR-003 Logging Runtime

### Responsibility

Logging configuration runtime.

### Runtime Layer

L0

### Imported By

BootstrapRuntime only.

### Public Classes

| Class | Purpose |
|-------|---------|
| `LoggingConfig` | Immutable logging configuration. |
| `ContextFilter` | Injects runtime context into log records. |
| `JsonFormatter` | Structured JSON formatter. |
| `ConsoleFormatter` | Human-readable formatter. |

### Public Functions

| Function | Purpose |
|----------|---------|
| `build_logging_config()` | Returns canonical logging configuration. |

### Runtime Ownership

Owns:

- formatter construction;
- filter construction;
- handler construction.

Does NOT own logger instances.

### Context Injection Fields

Injected automatically:

- trace_id
- session_id
- pipeline_id
- module_id

### Forbidden Responsibilities

- logger caching;
- logger retrieval;
- runtime initialization.

---

## LOGGING-002 — src/core/logger.py

### Owner

KR-003 Logging Runtime

### Responsibility

Canonical logger API.

### Runtime Layer

L0

### Imported By

Entire repository.

### Public Functions

| Function | Purpose |
|----------|---------|
| `get_logger(name)` | Returns configured logger instance. |
| `configure_logging()` | Installs repository logging configuration. |
| `reset_logging()` | Clears logging configuration (tests only). |

### Logger Cache

Owns immutable logger cache.

Cache key:

```
module.__name__
```

### Logging Rules

Returns configured logger only.

Never returns root logger.

Never exposes logging configuration internals.

### Forbidden Responsibilities

- custom handlers;
- environment parsing;
- runtime context mutation.

---

# KR-003 Ownership Matrix

| Object | Owner |
|--------|-------|
| Logger cache | logger.py |
| Formatter objects | logging_config.py |
| Logging handlers | logging_config.py |
| Context filter | logging_config.py |
| Logger retrieval | logger.py |

No duplicate logger owners.

---

# KR-002 / KR-003 Dependency Summary

```
settings.py
      │
config.py
      │
logging_config.py
      │
logger.py
```

Allowed import direction only.

---

# KR-002 Validation Ownership

Configuration Runtime validates:

- `.env` loading.
- Environment defaults.
- Directory paths.
- Immutable Settings construction.

---

# KR-003 Validation Ownership

Logging Runtime validates:

- formatter creation;
- handler creation;
- logger retrieval;
- context injection.

Validation does not emit logs during configuration.

<!-- ========================================================================= -->
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

**Runtime Layer:** L0 Kernel

Directory:

```
src/kernel/runtime/
```

Event Bus Runtime owns runtime event publication and dispatch.

Files:

| File | Status | Public API |
|------|--------|------------|
| `bus.py` | FROZEN | EventBusRuntime |
| `publisher.py` | FROZEN | PublisherRuntime |
| `dispatcher.py` | FROZEN | DispatcherRuntime |
| `subscriber.py` | FROZEN | SubscriberRuntime |

---

# Event Runtime Constitution

Event Runtime owns:

- event creation;
- subscription registry;
- publication;
- dispatch;
- handler ordering.

Event Runtime never owns:

- logging;
- lifecycle transitions;
- DI;
- runtime context mutation.

---

## EVENT-001 — src/kernel/runtime/bus.py

### Owner

KR-007 Event Bus Runtime

### Responsibility

Public Event Bus API.

### Runtime Layer

L0

### Imported By

- RuntimeKernel
- LifecycleRuntime
- PipelineRuntime
- BootstrapRuntime
- Tests

### Public Exports

#### Classes

- `EventBusRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `subscribe()` | Register handler. |
| `unsubscribe()` | Remove handler. |
| `publish()` | Publish one event. |
| `publish_many()` | Publish event batch. |
| `handlers()` | Immutable handler snapshot. |

### Internal Ownership

Owns:

- PublisherRuntime
- DispatcherRuntime
- SubscriberRuntime

### Forbidden Responsibilities

- handler implementation.
- runtime lifecycle.

---

## EVENT-002 — src/kernel/runtime/publisher.py

### Owner

KR-007 Event Bus Runtime

### Responsibility

Runtime event publisher.

### Runtime Layer

L0

### Imported By

EventBusRuntime

DispatcherRuntime

Tests

### Public Exports

#### Classes

- `PublisherRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `create()` | Create RuntimeEvent. |
| `publish()` | Publish validated event. |
| `publish_many()` | Publish immutable event collection. |

### Validation Ownership

Validates RuntimeEvent before dispatch.

### Forbidden Responsibilities

- handler registry.
- dispatch ordering.

---

## EVENT-003 — src/kernel/runtime/dispatcher.py

### Owner

KR-007 Event Bus Runtime

### Responsibility

Dispatch runtime events.

### Runtime Layer

L0

### Imported By

PublisherRuntime

EventBusRuntime

Tests

### Public Exports

#### Classes

- `DispatcherRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `dispatch()` | Dispatch single event. |
| `dispatch_many()` | Dispatch collection. |

### Dispatch Guarantees

- deterministic ordering;
- async dispatch;
- priority ordering;
- registration-order stability.

### Forbidden Responsibilities

- event creation.
- handler registration.

---

## EVENT-004 — src/kernel/runtime/subscriber.py

### Owner

KR-007 Event Bus Runtime

### Responsibility

Subscriber registry runtime.

### Runtime Layer

L0

### Imported By

EventBusRuntime

DispatcherRuntime

Tests

### Public Exports

#### Classes

- `SubscriberRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `subscribe()` | Register handler. |
| `unsubscribe()` | Remove handler. |
| `handlers_for()` | Return immutable handler list. |
| `contains()` | Check handler registration. |

### Internal Storage

Owns:

```
dict[str, tuple[EventHandlerContract, ...]]
```

### Forbidden Responsibilities

- event dispatch.
- event creation.
- runtime state.

---

# KR-007 Export Matrix

| File | Public Symbols |
|------|----------------|
| bus.py | EventBusRuntime |
| publisher.py | PublisherRuntime |
| dispatcher.py | DispatcherRuntime |
| subscriber.py | SubscriberRuntime |

---

# KR-007 Dependency Matrix

| File | Allowed Imports |
|------|------------------|
| bus.py | publisher.py, dispatcher.py, subscriber.py |
| publisher.py | contracts.events |
| dispatcher.py | subscriber.py, contracts.events |
| subscriber.py | contracts.events |

No imports from LifecycleRuntime or ContainerRuntime.

---

# KR-007 Ownership Matrix

| Object | Owner |
|--------|-------|
| EventBus public API | EventBusRuntime |
| RuntimeEvent creation | PublisherRuntime |
| Handler registry | SubscriberRuntime |
| Dispatch execution | DispatcherRuntime |
| Handler ordering | DispatcherRuntime |

---

# KR-007 Validation Ownership

| Runtime | Validates |
|----------|-----------|
| PublisherRuntime | RuntimeEvent validity |
| SubscriberRuntime | Duplicate handlers |
| DispatcherRuntime | Handler ordering |
| EventBusRuntime | Public API consistency |

---

# KR-007 Forbidden Patterns

Event Bus Runtime may never contain:

- mutable global subscribers;
- logging configuration;
- runtime lifecycle transitions;
- dependency injection;
- filesystem access;
- HTTP requests.

Event Bus Runtime owns runtime event flow only.

---

<!-- ========================================================================= -->
<!-- M-01 PART 6 — KR-008 Runtime Context Runtime + KR-009 Pipeline Runtime -->
<!-- ========================================================================= -->

# KR-008 — Runtime Context Runtime Registry

**Runtime Layer:** L0 Kernel

Directory:

```
src/kernel/runtime/
```

Runtime Context Runtime owns execution context propagation, session context lifecycle, metadata snapshots and trace propagation.

Files:

| File | Status | Public API |
|------|--------|------------|
| `context.py` | FROZEN | ContextRuntime |
| `metadata.py` | FROZEN | MetadataRuntime |
| `session.py` | FROZEN | SessionRuntime |

Runtime Context Runtime never owns dependency injection, lifecycle transitions, event dispatch or pipeline execution.

---

# Runtime Context Constitution

Runtime Context Runtime owns:

- RuntimeContext snapshots.
- TraceContext propagation.
- Metadata snapshots.
- Session context storage.

Runtime Context Runtime never owns:

- mutable RuntimeContext.
- global session registry outside SessionRuntime.
- trace generation.
- runtime state transitions.

---

## CONTEXT-001 — src/kernel/runtime/context.py

### Owner

KR-008 Runtime Context Runtime

### Responsibility

Canonical RuntimeContext manager.

### Runtime Layer

L0

### Imported By

- PipelineRuntime
- EventRuntime
- LifecycleRuntime
- BootstrapRuntime
- Tests

### Public Exports

#### Classes

- `ContextRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `create()` | Create immutable RuntimeContext. |
| `current()` | Return active RuntimeContext snapshot. |
| `replace()` | Replace current RuntimeContext snapshot. |
| `clear()` | Remove active RuntimeContext. |
| `has_context()` | Check context existence. |

### Internal Ownership

Owns current RuntimeContext reference.

Exactly one active RuntimeContext exists per execution flow.

### Forbidden Responsibilities

- metadata mutation.
- session registry.
- trace generation.
- pipeline execution.

---

## CONTEXT-002 — src/kernel/runtime/metadata.py

### Owner

KR-008 Runtime Context Runtime

### Responsibility

Immutable metadata manipulation runtime.

### Runtime Layer

L0

### Imported By

ContextRuntime

SessionRuntime

Tests

### Public Exports

#### Classes

- `MetadataRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `merge()` | Merge metadata snapshots. |
| `put()` | Return metadata with inserted value. |
| `remove()` | Return metadata without key. |
| `contains()` | Check metadata key existence. |
| `get()` | Read metadata value safely. |

### Metadata Rules

- Metadata immutable.
- JSON-compatible values only.
- No in-place mutation.

### Forbidden Responsibilities

- RuntimeContext ownership.
- session lifecycle.
- trace propagation.

---

## CONTEXT-003 — src/kernel/runtime/session.py

### Owner

KR-008 Runtime Context Runtime

### Responsibility

Session lifecycle runtime.

### Runtime Layer

L0

### Imported By

ContextRuntime

BootstrapRuntime

Tests

### Public Exports

#### Classes

- `SessionRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `create()` | Create session RuntimeContext. |
| `get()` | Retrieve RuntimeContext by SessionId. |
| `update_metadata()` | Replace metadata snapshot. |
| `remove()` | Destroy session RuntimeContext. |
| `contains()` | Check session existence. |
| `list()` | Immutable session snapshot. |

### Internal Storage

Owns:

```
dict[SessionId, RuntimeContext]
```

Storage is private.

### Forbidden Responsibilities

- RuntimeContext mutation.
- metadata merging.
- trace creation.

---

# KR-008 Export Matrix

| File | Public Symbols |
|------|----------------|
| context.py | ContextRuntime |
| metadata.py | MetadataRuntime |
| session.py | SessionRuntime |

---

# KR-008 Dependency Matrix

| File | Allowed Imports |
|------|------------------|
| context.py | contracts.context, metadata.py |
| metadata.py | core.types |
| session.py | context.py, contracts.context |

Runtime Context Runtime never imports EventBusRuntime or LifecycleRuntime.

---

# KR-008 Ownership Matrix

| Object | Owner |
|--------|-------|
| Active RuntimeContext | ContextRuntime |
| Metadata snapshots | MetadataRuntime |
| Session registry | SessionRuntime |
| Session RuntimeContext | SessionRuntime |

No shared ownership.

---

# KR-008 Validation Ownership

| Runtime | Validates |
|----------|-----------|
| ContextRuntime | RuntimeContext existence |
| MetadataRuntime | JSON compatibility |
| SessionRuntime | Session lifecycle |

---

# KR-008 Forbidden Patterns

Runtime Context Runtime may never contain:

- mutable RuntimeContext.
- global metadata.
- filesystem access.
- dependency injection.
- lifecycle transitions.

Runtime Context Runtime owns context propagation only.

---

# KR-009 — Pipeline Runtime Registry

**Runtime Layer:** L0 Kernel

Directory:

```
src/kernel/runtime/
```

Pipeline Runtime owns pipeline definitions, DAG validation, execution ordering and orchestration.

Files:

| File | Status | Public API |
|------|--------|------------|
| `pipeline.py` | FROZEN | Pipeline contracts |
| `manifest.py` | FROZEN | ManifestRuntime |
| `executor.py` | FROZEN | ExecutorRuntime |
| `orchestrator.py` | FROZEN | OrchestratorRuntime |

Pipeline Runtime never owns dependency injection, lifecycle transitions or logging configuration.

---

# Pipeline Runtime Constitution

Pipeline Runtime owns:

- PipelineDefinition.
- PipelineStage.
- DAG validation.
- Execution order.
- Module orchestration.

Pipeline Runtime never owns:

- runtime construction.
- event subscriptions.
- service resolution.
- runtime state transitions.

---

## PIPELINE-001 — src/kernel/runtime/pipeline.py

### Owner

KR-009 Pipeline Runtime

### Responsibility

Immutable pipeline definitions.

### Runtime Layer

L0

### Imported By

ManifestRuntime

ExecutorRuntime

OrchestratorRuntime

Tests

### Public Exports

#### Dataclasses

- `PipelineDefinition`
- `PipelineStage`

### Public Fields

#### PipelineStage

- stage_id
- module_id
- depends_on

#### PipelineDefinition

- pipeline_id
- stages

### Pipeline Rules

- immutable.
- stage IDs unique.
- DAG only.

### Forbidden Responsibilities

- execution.
- validation.
- orchestration.

---

## PIPELINE-002 — src/kernel/runtime/manifest.py

### Owner

KR-009 Pipeline Runtime

### Responsibility

Pipeline manifest validator.

### Runtime Layer

L0

### Imported By

ExecutorRuntime

OrchestratorRuntime

Tests

### Public Exports

#### Classes

- `ManifestRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `validate()` | Validate complete manifest. |
| `validate_stage_ids()` | Validate uniqueness. |
| `validate_dependencies()` | Validate references. |
| `validate_dag()` | Detect cycles. |

### Forbidden Responsibilities

- stage execution.
- runtime events.

---

## PIPELINE-003 — src/kernel/runtime/executor.py

### Owner

KR-009 Pipeline Runtime

### Responsibility

Pipeline execution runtime.

### Runtime Layer

L0

### Imported By

OrchestratorRuntime

Tests

### Public Exports

#### Classes

- `ExecutorRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `execute()` | Execute complete pipeline. |
| `execute_stage()` | Execute one stage. |

### Internal Helpers

- `_execution_order()`
- `_publish_stage_event()`

### Execution Guarantees

- sequential execution.
- deterministic ordering.
- immutable RuntimeContext.

### Forbidden Responsibilities

- DAG validation.
- module registration.

---

## PIPELINE-004 — src/kernel/runtime/orchestrator.py

### Owner

KR-009 Pipeline Runtime

### Responsibility

Runtime pipeline orchestration.

### Runtime Layer

L0

### Imported By

BootstrapRuntime

RuntimeKernel

Tests

### Public Exports

#### Classes

- `OrchestratorRuntime`

### Public Methods

| Method | Purpose |
|--------|---------|
| `register_module()` | Register RuntimeModuleManifest. |
| `unregister_module()` | Remove manifest. |
| `modules()` | Immutable manifest snapshot. |
| `execute()` | Validate and execute pipeline. |

### Internal Storage

Owns:

```
dict[ModuleId, RuntimeModuleManifest]
```

### Forbidden Responsibilities

- dependency injection.
- lifecycle transitions.
- runtime startup.

---

# KR-009 Export Matrix

| File | Public Symbols |
|------|----------------|
| pipeline.py | PipelineDefinition, PipelineStage |
| manifest.py | ManifestRuntime |
| executor.py | ExecutorRuntime |
| orchestrator.py | OrchestratorRuntime |

---

# KR-009 Dependency Matrix

| File | Allowed Imports |
|------|------------------|
| pipeline.py | core.types |
| manifest.py | pipeline.py |
| executor.py | pipeline.py, EventRuntime, ContextRuntime |
| orchestrator.py | manifest.py, executor.py, contracts.module |

Pipeline Runtime never imports BootstrapRuntime or LifecycleRuntime.

---

# KR-009 Ownership Matrix

| Object | Owner |
|--------|-------|
| PipelineDefinition | pipeline.py |
| PipelineStage | pipeline.py |
| Manifest validation | ManifestRuntime |
| Stage execution | ExecutorRuntime |
| Module orchestration | OrchestratorRuntime |

No shared ownership.

---

# KR-009 Validation Ownership

| Runtime | Validates |
|----------|-----------|
| ManifestRuntime | DAG validity |
| ManifestRuntime | Dependency references |
| ExecutorRuntime | Execution ordering |
| OrchestratorRuntime | Module manifest consistency |

---

# KR-009 Forbidden Patterns

Pipeline Runtime may never contain:

- parallel execution.
- dependency injection.
- lifecycle transitions.
- logging configuration.
- mutable PipelineDefinition.
- mutable PipelineStage.

Pipeline Runtime owns deterministic execution only.

---

<!-- ========================================================================= -->
<!-- M-01 PART 7 — KR-010 Bootstrap Runtime + KR-011 Test Suite Registry -->
<!-- ========================================================================= -->

# KR-010 — Bootstrap Runtime Registry

**Runtime Layer:** L0 Kernel

Directory:

```
src/kernel/runtime/
src/
```

Bootstrap Runtime is the only runtime responsible for constructing and destroying the runtime graph.

Files:

| File | Status | Public API |
|------|--------|------------|
| `bootstrap.py` | FROZEN | BootstrapRuntime |
| `runtime.py` | FROZEN | RuntimeKernel |
| `src/main.py` | FROZEN | Process entrypoint |

Bootstrap Runtime never owns business logic.

---

# Bootstrap Runtime Constitution

Bootstrap Runtime owns:

- runtime construction;
- runtime wiring;
- startup sequence;
- shutdown sequence;
- RuntimeKernel creation.

Bootstrap Runtime never owns:

- DI implementation;
- EventBus implementation;
- lifecycle state machine;
- pipeline execution.

---

## BOOTSTRAP-001 — src/kernel/runtime/bootstrap.py

### Owner

KR-010 Bootstrap Runtime

### Responsibility

Runtime graph construction.

### Runtime Layer

L0

### Imported By

- src/main.py
- RuntimeKernel tests

### Public Exports

#### Classes

- BootstrapRuntime

### Public Methods

| Method | Purpose |
|--------|---------|
| build() | Build RuntimeKernel. |

### Runtime Construction Order

1. Settings.
2. Logging.
3. Context Runtime.
4. Container Runtime.
5. Event Bus Runtime.
6. Orchestrator Runtime.
7. Lifecycle Runtime.
8. RuntimeKernel.

Order is immutable.

### Forbidden Responsibilities

- runtime execution;
- pipeline execution;
- lifecycle transitions.

---

## BOOTSTRAP-002 — src/kernel/runtime/runtime.py

### Owner

KR-010 Bootstrap Runtime

### Responsibility

Public runtime facade.

### Runtime Layer

L0

### Imported By

- src/main.py
- integration tests

### Public Exports

#### Classes

- RuntimeKernel

### Public Properties

| Property | Type |
|----------|------|
| container | ContainerRuntime |
| lifecycle | LifecycleRuntime |
| event_bus | EventBusRuntime |
| context | ContextRuntime |
| orchestrator | OrchestratorRuntime |

### Public Methods

| Method | Purpose |
|--------|---------|
| initialize() | Initialize runtime graph. |
| start() | Enter RUNNING state. |
| stop() | Graceful runtime stop. |
| shutdown() | Graceful runtime shutdown. |
| health() | Aggregate runtime health. |

### Health Ownership

RuntimeKernel aggregates health only.

Individual runtimes own health computation.

### Forbidden Responsibilities

- runtime creation;
- service registration;
- logging configuration.

---

## BOOTSTRAP-003 — src/main.py

### Owner

KR-010 Bootstrap Runtime

### Responsibility

Process entrypoint.

### Runtime Layer

L0

### Imported By

Process only.

### Public Exports

No public exports.

### Public Functions

| Function | Purpose |
|----------|---------|
| main() | Canonical async entrypoint. |

### Entry Sequence

1. BootstrapRuntime.build()
2. RuntimeKernel.initialize()
3. RuntimeKernel.start()
4. Await shutdown signal.
5. RuntimeKernel.stop()
6. RuntimeKernel.shutdown()

### Process Rules

- asyncio.run(main())
- exactly one entrypoint
- graceful shutdown in finally block

### Forbidden Responsibilities

- business logic;
- filesystem initialization;
- configuration parsing;
- service registration.

---

# KR-010 Export Matrix

| File | Public Symbols |
|------|----------------|
| bootstrap.py | BootstrapRuntime |
| runtime.py | RuntimeKernel |
| main.py | main |

---

# KR-010 Dependency Matrix

| File | Allowed Imports |
|------|------------------|
| bootstrap.py | Configuration, Logging, Container, Lifecycle, Context, EventBus, Orchestrator |
| runtime.py | Bootstrap runtimes only |
| main.py | BootstrapRuntime only |

No reverse imports into Bootstrap Runtime.

---

# KR-010 Ownership Matrix

| Object | Owner |
|--------|-------|
| Runtime graph | BootstrapRuntime |
| RuntimeKernel | runtime.py |
| Process entrypoint | src/main.py |
| Startup sequence | BootstrapRuntime |
| Shutdown sequence | BootstrapRuntime |

---

# KR-010 Validation Ownership

| Runtime | Validates |
|----------|-----------|
| BootstrapRuntime | Runtime graph creation |
| RuntimeKernel | Runtime health aggregation |
| main.py | Startup/shutdown execution flow |

---

# KR-010 Forbidden Patterns

Bootstrap Runtime may never contain:

- mutable runtime globals;
- event handlers;
- dependency registration outside ContainerRuntime;
- lifecycle state mutation outside LifecycleRuntime.

Bootstrap Runtime owns orchestration only.

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
- reload_settings().
- directory validation.
- cache invalidation.

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
