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


Document ID: M-03A

Document Name: Public Symbol Index

Path:
docs/architecture/master/03A_PUBLIC_SYMBOL_INDEX.md

Status: CANONICAL SOURCE OF TRUTH

Authority:
- AB-00 Development Constitution
- M-00 Canonical Index
- M-03 API Registry
- M-06 Module Specifications

Version: 1.1 Canonical

---

# Purpose

This document is the canonical index of every public symbol exported by Wave 1.

Unlike M-03, which documents APIs by runtime, this document indexes symbols by identity.

The Public Symbol Index exists to provide O(1) lookup for engineering tools, Codex, reviews, tests and future documentation.

Implementation is forbidden here.

---

# Public Symbol Index Constitution

Every public symbol exported by Wave 1 appears exactly once inside this document.

## Symbol Index Invariants

1. Every public symbol appears exactly once.
2. Every symbol has one canonical owner.
3. Every symbol references one implementation file.
4. Every symbol references one API definition section.
5. Every symbol references one KR owner.
6. Every symbol has one export path.

Violating any invariant is an Architecture Conflict.

---

# Symbol Classification Vocabulary

Every symbol belongs to one category.

| Category | Meaning |
|----------|---------|
| TYPE_ALIAS | Public type alias. |
| ENUM | Public enum. |
| DATACLASS | Frozen dataclass. |
| PROTOCOL | Public protocol. |
| RUNTIME_CLASS | Runtime implementation class. |
| UTILITY_CLASS | Public non-runtime class. |
| FUNCTION | Public function. |
| CONSTANT | Public exported constant. |

Vocabulary is immutable.

---

# Canonical Symbol Record Format

Every symbol record contains the following fields.

| Field | Description |
|-------|-------------|
| Symbol | Canonical exported name. |
| Category | Symbol category. |
| KR Owner | Kernel Requirement owner. |
| Owner File | Canonical production file. |
| Export Path | Canonical import path. |
| API Registry | Section inside M-03. |
| Module Spec | Section inside M-06. |
| Test Owner | Section inside M-09. |

Every record is complete.

---

# KR-001 Symbol Index

Directory:

src/core/

Runtime Layer:

L0

---

# TYPE_ALIAS Registry

## ModuleId

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.ModuleId |
| API Registry | CONTRACT-001 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical runtime module identifier.

---

## SessionId

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.SessionId |
| API Registry | CONTRACT-002 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical session identifier.

---

## PipelineId

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.PipelineId |
| API Registry | CONTRACT-002 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical pipeline identifier.

---

## EventId

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.EventId |
| API Registry | CONTRACT-003 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical runtime event identifier.

---

## TraceId

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.TraceId |
| API Registry | CONTRACT-001 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical distributed trace identifier.

---

## ServiceId

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.ServiceId |
| API Registry | CONTRACT-006 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical Dependency Injection service identifier.

---

## JSONPrimitive

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.JSONPrimitive |
| API Registry | CORE-001 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical primitive JSON value.

---

## JSONValue

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.JSONValue |
| API Registry | CORE-001 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Recursive JSON value.

---

## JSONDict

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.JSONDict |
| API Registry | CORE-001 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical JSON dictionary.

---

## Payload

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.Payload |
| API Registry | CONTRACT-003 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

RuntimeEvent payload type.

---

## Metadata

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.Metadata |
| API Registry | CONTRACT-002 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Immutable runtime metadata snapshot.

---

## Headers

| Field | Value |
|-------|-------|
| Category | TYPE_ALIAS |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.Headers |
| API Registry | CONTRACT-003 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Types Tests |

Purpose:

Canonical runtime event headers.

---

# ENUM Registry

## RuntimeLayer

| Field | Value |
|-------|-------|
| Category | ENUM |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.RuntimeLayer |
| API Registry | ENUM-001 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Enum Tests |

Purpose:

Canonical runtime layer vocabulary.

---

## RuntimeStatus

| Field | Value |
|-------|-------|
| Category | ENUM |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.RuntimeStatus |
| API Registry | ENUM-002 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Enum Tests |

Purpose:

Canonical lifecycle vocabulary.

---

## HealthStatus

| Field | Value |
|-------|-------|
| Category | ENUM |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.HealthStatus |
| API Registry | ENUM-003 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Enum Tests |

Purpose:

Runtime health vocabulary.

---

## DIScope

| Field | Value |
|-------|-------|
| Category | ENUM |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.DIScope |
| API Registry | ENUM-004 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Enum Tests |

Purpose:

Dependency Injection scope vocabulary.

---

## EventPriority

| Field | Value |
|-------|-------|
| Category | ENUM |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.EventPriority |
| API Registry | ENUM-005 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Enum Tests |

Purpose:

Canonical event priority vocabulary.

---

## EventPhase

| Field | Value |
|-------|-------|
| Category | ENUM |
| KR Owner | KR-001 |
| Owner File | src/core/types.py |
| Export Path | src.core.types.EventPhase |
| API Registry | ENUM-006 |
| Module Spec | CORE-001 |
| Test Owner | KR-001 Enum Tests |

Purpose:

Canonical event lifecycle vocabulary.

---

# KR-001 Symbol Statistics

| Category | Count |
|----------|------:|
| Type Aliases | 11 |
| Enums | 6 |
| Total Symbols Indexed | 17 |

All Foundation Core public symbols are indexed.

---

Document Status:

IN PROGRESS (Part 1 of 6)

<!-- ========================================================================= -->
<!-- M-03A PART 2 — KR-002 + KR-003 Symbol Index -->
<!-- ========================================================================= -->

# KR-002 Symbol Index — APPROVED ADR-009

| Symbol | Category | Owner file | Test owner |
| --- | --- | --- | --- |
| Environment | TYPE_ALIAS | src/core/settings.py | KR-011 test_settings.py |
| Settings | BASE_SETTINGS | src/core/settings.py | KR-011 test_settings.py |
| get_settings | FUNCTION | src/core/config.py | KR-011 test_settings.py |
| validate_configuration | FUNCTION | src/core/config.py | KR-011 test_settings.py |

Public fields/defaults and five members:
| Field | Type | Default | Explicit alias |

| --- | --- | --- | --- |
| app_name | str | PROJECT_NAME | none |
| environment | Environment | development | AURORA_ENV |
| log_level | str | DEFAULT_LOG_LEVEL (INFO) | AURORA_LOG_LEVEL |
| timezone | str | DEFAULT_TIMEZONE (UTC) | none |
| config_path | Path | Path("config") | AURORA_CONFIG_PATH |
| data_path | Path | Path("data") | none |
| cache_path | Path | Path(".cache") | none |
| logs_path | Path | Path("logs") | none |

Exactly three read-only properties: is_development, is_testing, is_production,
each returning bool. Existing public class validators are
validate_log_level(cls, value: str) -> str and
validate_path(cls, value: str | Path) -> Path. Log levels normalize by upper()
and accept only DEBUG/INFO/WARNING/ERROR/CRITICAL. All four paths convert to Path;
relative/nonexistent paths are valid and no directory is created. Timezone is a
descriptive string; no timezone-database validation is promised. All fields have
defaults: missing/empty .env and unknown extra keys are accepted.


Exact [KR-002 contract](../wave1/KR-002_CONFIGURATION.md) defines signatures,
construction, validation, cache and errors. Four module-owned symbols, not a
dataclass/four-loader API. Imported vendor symbols are not AURORA-owned exports.

# KR-003 Symbol Index — APPROVED ADR-009

| Owner file | Public symbol |

| --- | --- |
| logger.py | get_logger(name: str, config: LoggingConfig \| None = None) -> logging.Logger |
| logger.py | LOGGER: Final[logging.Logger] |
| logging_config.py | LoggingConfig |
| logging_config.py | RuntimeContextFilter.filter(record: logging.LogRecord) -> bool |
| logging_config.py | ConsoleFormatter.format(record: logging.LogRecord) -> str |
| logging_config.py | JsonFormatter.format(record: logging.LogRecord) -> str |
| logging_config.py | set_correlation_id(correlation_id: str \| None) -> None |
| logging_config.py | get_correlation_id() -> str \| None |
| logging_config.py | clear_correlation_id() -> None |
| logging_config.py | set_session_id(session_id: str \| None) -> None |
| logging_config.py | get_session_id() -> str \| None |
| logging_config.py | clear_session_id() -> None |
| logging_config.py | clear_logging_context() -> None |
| logging_config.py | DEFAULT_LOGGING_CONFIG: Final[LoggingConfig] |
| logging_config.py | DEFAULT_CONTEXT_FILTER: Final[RuntimeContextFilter] |


Eight functions, four classes and three constants: 15 module-owned symbols.
Verify three formatter/filter member methods and LoggingConfig's exact field
schema as member APIs too. Exact [KR-003 contract](../wave1/KR-003_LOGGING.md).
Foundation constants remain KR-001, not logging-owned symbols. All legacy
cumulative core counts/index duplicates are superseded by these scoped tables.

<!-- M-03A PART 3 — KR-004 Kernel Contracts Symbol Index -->
<!-- ========================================================================= -->

# KR-004 Symbol Index

**Directory**

`src/kernel/contracts/`

**Runtime Layer**

L0

**Owner KR**

KR-004 Kernel Contracts

---

# DATACLASS Registry

## TraceContext

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-004 |
| Owner File | src/kernel/contracts/context.py |
| Export Path | src.kernel.contracts.context.TraceContext |
| API Registry | CONTRACT-001 |
| Module Spec | CONTRACT-001 |
| Test Owner | KR-004 TraceContext Tests |

**Purpose**

Canonical immutable distributed trace context.

**Public Fields**

- trace_id
- parent_trace_id
- root_trace_id
- depth
- created_at

**Derived Properties**

- is_root
- has_parent

**Imported By**

- RuntimeContext
- RuntimeEvent
- PublisherRuntime
- ContextRuntime

---

## RuntimeContext

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-004 |
| Owner File | src/kernel/contracts/context.py |
| Export Path | src.kernel.contracts.context.RuntimeContext |
| API Registry | CONTRACT-002 |
| Module Spec | CONTRACT-002 |
| Test Owner | KR-004 RuntimeContext Tests |

**Purpose**

Canonical immutable execution context.

**Public Fields**

- session_id
- pipeline_id
- runtime_layer
- trace
- metadata
- created_at
- expires_at

**Derived Properties**

- trace_id
- root_trace_id
- depth
- is_expired

**Imported By**

- ContextRuntime
- SessionRuntime
- ExecutorRuntime
- EventBusRuntime
- LifecycleRuntime

---

## RuntimeEvent

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-004 |
| Owner File | src/kernel/contracts/events.py |
| Export Path | src.kernel.contracts.events.RuntimeEvent |
| API Registry | CONTRACT-003 |
| Module Spec | CONTRACT-003 |
| Test Owner | KR-004 RuntimeEvent Tests |

**Purpose**

Canonical immutable runtime event.

**Public Fields**

### Identity

- event_id
- event_type
- priority

### Context

- session_id
- pipeline_id
- trace

### Payload

- payload
- headers

### Lifecycle

- phase
- created_at

**Derived Properties**

- trace_id
- root_trace_id
- is_critical

**Imported By**

- PublisherRuntime
- DispatcherRuntime
- SubscriberRuntime
- ExecutorRuntime

---

## LifecycleState

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-004 |
| Owner File | src/kernel/contracts/lifecycle.py |
| Export Path | src.kernel.contracts.lifecycle.LifecycleState |
| API Registry | CONTRACT-004 |
| Module Spec | CONTRACT-004 |
| Test Owner | KR-004 Lifecycle Tests |

**Purpose**

Immutable lifecycle state snapshot.

**Public Fields**

- current
- previous
- entered_at
- transition_count

**Derived Properties**

- is_running
- is_ready
- is_failed
- is_terminal

**Imported By**

- StateRuntime
- LifecycleRuntime
- RuntimeKernel

---

## RuntimeModuleManifest

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-004 |
| Owner File | src/kernel/contracts/module.py |
| Export Path | src.kernel.contracts.module.RuntimeModuleManifest |
| API Registry | CONTRACT-005 |
| Module Spec | CONTRACT-005 |
| Test Owner | KR-004 Manifest Tests |

**Purpose**

Canonical runtime module descriptor.

**Public Fields**

### Identity

- module_id
- module_name
- runtime_layer

### Dependency Graph

- provides
- depends_on

### Lifecycle

- enabled
- version

### Metadata

- metadata

**Derived Properties**

- has_dependencies
- dependency_count
- provides_count

**Imported By**

- ManifestRuntime
- OrchestratorRuntime
- BootstrapRuntime

---

## ServiceDescriptor

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-004 |
| Owner File | src/kernel/contracts/service.py |
| Export Path | src.kernel.contracts.service.ServiceDescriptor |
| API Registry | CONTRACT-006 |
| Module Spec | CONTRACT-006 |
| Test Owner | KR-004 ServiceDescriptor Tests |

**Purpose**

Canonical Dependency Injection registration descriptor.

**Public Fields**

### Identity

- service_id
- implementation

### Dependency Injection

- scope
- dependencies

### Hooks

- initialize
- shutdown

### Metadata

- metadata

**Derived Properties**

- dependency_count
- is_singleton
- has_initialize_hook
- has_shutdown_hook

**Imported By**

- RegistryRuntime
- ResolverRuntime
- ProviderRuntime
- ContainerRuntime

---

# PROTOCOL Registry

## RuntimeContract

| Field | Value |
|-------|-------|
| Category | PROTOCOL |
| KR Owner | KR-004 |
| Owner File | src/kernel/contracts/runtime.py |
| Export Path | src.kernel.contracts.runtime.RuntimeContract |
| API Registry | CONTRACT-007 |
| Module Spec | CONTRACT-007 |
| Test Owner | KR-004 RuntimeContract Tests |

**Purpose**

Canonical runtime protocol implemented by every runtime.

### Required Properties

- runtime_name
- runtime_layer

### Required Methods

- initialize()
- shutdown()
- health()

**Implemented By**

- ContainerRuntime
- LifecycleRuntime
- EventBusRuntime
- ContextRuntime
- OrchestratorRuntime
- RuntimeKernel

---

# KR-004 Symbol Dependency Matrix

| Symbol | Depends On |
|--------|------------|
| TraceContext | TraceId |
| RuntimeContext | TraceContext, Metadata, RuntimeLayer |
| RuntimeEvent | RuntimeContext, TraceContext, Payload, Headers |
| LifecycleState | RuntimeStatus |
| RuntimeModuleManifest | RuntimeLayer, ModuleId, Metadata |
| ServiceDescriptor | ServiceId, DIScope, Metadata |
| RuntimeContract | RuntimeLayer, HealthStatus |

This dependency graph is immutable.

---

# KR-004 Symbol Import Matrix

| Consumer Runtime | Imported Symbols |
|------------------|------------------|
| ContextRuntime | TraceContext, RuntimeContext |
| EventBusRuntime | RuntimeEvent, TraceContext |
| LifecycleRuntime | LifecycleState |
| ContainerRuntime | ServiceDescriptor |
| ManifestRuntime | RuntimeModuleManifest |
| BootstrapRuntime | RuntimeContract, RuntimeModuleManifest |

Only immutable contracts cross runtime boundaries.

---

# KR-004 Symbol Statistics

| Category | Count |
|----------|------:|
| Dataclasses | 6 |
| Protocols | 1 |
| Total Symbols Indexed | 7 |

---

# Cumulative Symbol Index Progress

| KR | Indexed Symbols |
|----|----------------:|
| KR-001 | 17 |
| KR-002 | 5 |
| KR-003 | 11 |
| KR-004 | 7 |

**Total Indexed So Far:** **40 public symbols**

---

**Document Status:** IN PROGRESS (Part 3 of 6)

<!-- ========================================================================= -->
<!-- M-03A PART 4 — KR-005 + KR-006 + KR-007 Runtime Symbol Index -->
<!-- ========================================================================= -->

# KR-005 Symbol Index

**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-005 Dependency Injection Runtime

---

# RUNTIME_CLASS Registry

## ContainerRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-005 |
| Owner File | src/kernel/runtime/container.py |
| Export Path | src.kernel.runtime.container.ContainerRuntime |
| API Registry | DI-API-001 |
| Module Spec | KR-005 ContainerRuntime |
| Test Owner | KR-005 ContainerRuntime Tests |

**Purpose**

Public Dependency Injection container.

**Public Properties**

- registry
- resolver
- provider
- scope

**Public Methods**

- initialize()
- shutdown()
- register()
- unregister()
- resolve()
- contains()
- descriptors()
- health()

**Depends On**

- RegistryRuntime
- ResolverRuntime
- ProviderRuntime
- ScopeRuntime

**Imported By**

- RuntimeKernel
- BootstrapRuntime

---

## RegistryRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-005 |
| Owner File | src/kernel/runtime/registry.py |
| Export Path | src.kernel.runtime.registry.RegistryRuntime |
| API Registry | DI-API-002 |
| Module Spec | KR-005 RegistryRuntime |
| Test Owner | KR-005 Registry Tests |

**Purpose**

Immutable ServiceDescriptor registry.

**Public Methods**

- register()
- remove()
- descriptor()
- contains()
- list()

**Depends On**

- ServiceDescriptor

**Imported By**

- ContainerRuntime
- ResolverRuntime

---

## ResolverRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-005 |
| Owner File | src/kernel/runtime/resolver.py |
| Export Path | src.kernel.runtime.resolver.ResolverRuntime |
| API Registry | DI-API-003 |
| Module Spec | KR-005 ResolverRuntime |
| Test Owner | KR-005 Resolver Tests |

**Purpose**

Dependency graph resolver.

**Public Methods**

- resolve()
- dependencies()

**Depends On**

- RegistryRuntime
- ProviderRuntime
- ScopeRuntime

**Imported By**

- ContainerRuntime

---

## ProviderRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-005 |
| Owner File | src/kernel/runtime/provider.py |
| Export Path | src.kernel.runtime.provider.ProviderRuntime |
| API Registry | DI-API-004 |
| Module Spec | KR-005 ProviderRuntime |
| Test Owner | KR-005 Provider Tests |

**Purpose**

Service constructor runtime.

**Public Methods**

- build()
- initialize()
- shutdown()

**Depends On**

- ServiceDescriptor

**Imported By**

- ResolverRuntime

---

## ScopeRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-005 |
| Owner File | src/kernel/runtime/scope.py |
| Export Path | src.kernel.runtime.scope.ScopeRuntime |
| API Registry | DI-API-005 |
| Module Spec | KR-005 ScopeRuntime |
| Test Owner | KR-005 Scope Tests |

**Purpose**

Owner of all DI scope caches.

**Public Methods**

- get()
- store()
- clear_pipeline()
- clear_session()
- clear_application()
- clear_all()

**Depends On**

- DIScope

**Imported By**

- ResolverRuntime
- ContainerRuntime

---

# KR-005 Runtime Dependency Matrix

| Runtime | Depends On |
|---------|------------|
| ContainerRuntime | RegistryRuntime, ResolverRuntime, ProviderRuntime, ScopeRuntime |
| RegistryRuntime | ServiceDescriptor |
| ResolverRuntime | RegistryRuntime, ProviderRuntime, ScopeRuntime |
| ProviderRuntime | ServiceDescriptor |
| ScopeRuntime | DIScope |

Dependency graph is acyclic.

---

# KR-006 Symbol Index

**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-006 Lifecycle Runtime

---

# RUNTIME_CLASS Registry

## LifecycleRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-006 |
| Owner File | src/kernel/runtime/lifecycle.py |
| Export Path | src.kernel.runtime.lifecycle.LifecycleRuntime |
| API Registry | LIFECYCLE-API-001 |
| Module Spec | KR-006 LifecycleRuntime |
| Test Owner | KR-006 Lifecycle Tests |

**Purpose**

Public lifecycle coordinator.

**Public Methods**

- initialize()
- start()
- stop()
- shutdown()
- status()
- state()
- health()

**Depends On**

- StateRuntime
- HookRuntime

**Imported By**

- RuntimeKernel
- BootstrapRuntime

---

## StateRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-006 |
| Owner File | src/kernel/runtime/state.py |
| Export Path | src.kernel.runtime.state.StateRuntime |
| API Registry | LIFECYCLE-API-002 |
| Module Spec | KR-006 StateRuntime |
| Test Owner | KR-006 State Tests |

**Purpose**

Canonical RuntimeStatus state machine owner.

**Public Methods**

- current()
- previous()
- snapshot()
- transition()
- can_transition()
- reset()

**Depends On**

- LifecycleState
- RuntimeStatus

**Imported By**

- LifecycleRuntime

---

## HookRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-006 |
| Owner File | src/kernel/runtime/hooks.py |
| Export Path | src.kernel.runtime.hooks.HookRuntime |
| API Registry | LIFECYCLE-API-003 |
| Module Spec | KR-006 HookRuntime |
| Test Owner | KR-006 Hook Tests |

**Purpose**

Lifecycle callback registry.

**Public Methods**

- register_initialize()
- register_start()
- register_stop()
- register_shutdown()
- run_initialize()
- run_start()
- run_stop()
- run_shutdown()
- clear()

**Imported By**

- LifecycleRuntime

---

# KR-006 Runtime Dependency Matrix

| Runtime | Depends On |
|---------|------------|
| LifecycleRuntime | StateRuntime, HookRuntime |
| StateRuntime | LifecycleState |
| HookRuntime | None |

---

# KR-007 Symbol Index

**Authority:** APPROVED ADR-005 E-01–E-04, ADR-004 P-04 and AB-00C/D (2026-10-06).
The exact signatures and acceptance contract are `../wave1/KR-007_EVENT_BUS.md`.
Only KR-007 entries are reconciled; other module contracts remain unchanged.

| File | Export | Responsibility | Concrete dependencies |
| --- | --- | --- | --- |
| bus.py | EventBusRuntime | Public facade/composition | Publisher, Dispatcher, Subscriber |
| publisher.py | PublisherRuntime | Sole new event factory, validation, publication | Dispatcher |
| dispatcher.py | DispatcherRuntime | Sequential snapshot delivery | Subscriber |
| subscriber.py | SubscriberRuntime | Instance-local registry | None |

Canonical exports are `src.kernel.runtime.<file>.<listed class>` for all four
existing files. Category: RUNTIME_CLASS; owner: KR-007/L0. Test owner: KR-011,
canonical path tests/kernel/test_event_bus.py (ADR-004/005 adjustment authority).
API IDs: EVENT-API-001 Bus, 002 Publisher, 003 Dispatcher, 004 Subscriber.

| Class | Exact method names |
| --- | --- |
| EventBusRuntime | subscribe, unsubscribe, async publish, async publish_many, create_for_runtime, handlers, contains, clear; async initialize/start/stop/shutdown, health; runtime_name/runtime_layer properties |
| PublisherRuntime | create, validate, async publish, async publish_many |
| DispatcherRuntime | async dispatch, async dispatch_many |
| SubscriberRuntime | subscribe, unsubscribe, handlers, contains, clear |

Publisher depends on RuntimeEvent/RuntimeContext and Dispatcher; Dispatcher depends
on Subscriber/RuntimeEvent; Subscriber on EventHandlerContract; Bus on all three.
Dispatcher is consumed by Publisher/Bus/tests, never imports Publisher. Runtime
consumers use the Bus facade. No handlers_for, dispatch_sync/async or new symbols.

# Runtime Layer Ownership Matrix (KR-005 → KR-007)

| Runtime Class | Owner Runtime |
|--------------|---------------|
| ContainerRuntime | Dependency Injection Runtime |
| RegistryRuntime | Dependency Injection Runtime |
| ResolverRuntime | Dependency Injection Runtime |
| ProviderRuntime | Dependency Injection Runtime |
| ScopeRuntime | Dependency Injection Runtime |
| LifecycleRuntime | Lifecycle Runtime |
| StateRuntime | Lifecycle Runtime |
| HookRuntime | Lifecycle Runtime |
| EventBusRuntime | Event Bus Runtime |
| PublisherRuntime | Event Bus Runtime |
| DispatcherRuntime | Event Bus Runtime |
| SubscriberRuntime | Event Bus Runtime |

Every runtime class has exactly one runtime owner.

---

# KR-005/006/007 Symbol Statistics

| KR | Runtime Classes |
|----|----------------:|
| KR-005 | 5 |
| KR-006 | 3 |
| KR-007 | 4 |

**Total Runtime Classes Indexed:** **12**

---

# Cumulative Symbol Index Progress

| KR | Indexed Symbols |
|----|----------------:|
| KR-001 | 17 |
| KR-002 | 5 |
| KR-003 | 11 |
| KR-004 | 7 |
| KR-005–007 | 12 Runtime Classes |

**Total Indexed So Far:** **52 primary public symbols**

---

**Document Status:** IN PROGRESS (Part 4 of 6)

<!-- ========================================================================= -->
<!-- M-03A PART 5 — KR-008 + KR-009 + KR-010 Runtime Symbol Index -->
<!-- ========================================================================= -->

# KR-008 Symbol Index

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

# KR-009 Symbol Index

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

# KR-010 Symbol Index

**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-010 Bootstrap Runtime

---

# RUNTIME_CLASS Registry

## BootstrapRuntime

**Status:** APPROVED — ADR-008 B-01–B-05, 2026-10-06.
Exact contract: [KR-010](../wave1/KR-010_RUNNER_BOOTSTRAP.md).
Authority: [ADR-008](../ADR-008_KR010_Bootstrap_Reconciliation_Proposal_v1.0.md).

Owner/export: src/kernel/runtime/bootstrap.py / src.kernel.runtime.bootstrap.BootstrapRuntime.
Existing seven public methods: build (async), validate_environment, build_context,
build_container, build_event_bus, build_orchestrator(event_bus),
build_lifecycle(container, event_bus, context, orchestrator). Exact signatures in KR-010.
Dependencies: Configuration/Logging, public five collaborators, Kernel;
SessionRuntime only explicit approved construction. Imported by Main/canonical tests.

## RuntimeKernel

Owner/export: src/kernel/runtime/runtime.py / src.kernel.runtime.runtime.RuntimeKernel.
Implements existing RuntimeContract, not another protocol. Constructor explicitly
requires six keyword-only references including session: SessionRuntime.
Ten read-only properties: container, lifecycle, event_bus, context, orchestrator,
session, runtime_name, runtime_layer, version, architecture_version.
Ten public methods: async initialize/start/stop/shutdown/execute/remove_session;
sync status/state/health/diagnostics. No new universal contract member/compatibility alias.
Dependencies: Foundation/version/contracts, PipelineDefinition, five public facades
and narrowly permitted Session composition. Imported by Bootstrap/canonical tests.

## main

Owner/export: src/main.py / src.main.main; async main() -> None.
Build once, initialize, start, immediately bounded finally stop/shutdown through
Kernel; no invented pipeline/inputless execute or signal server. Both cleanup
attempts independent; first error/cancellation survives. Single asyncio.run entry.
Dependencies: Bootstrap, Foundation vocabulary, optional existing Logger, asyncio.

## KR-010 Ownership and Counts

Two existing runtime classes, one entry function; 17 domain/public methods across
both classes (constructors excluded), ten Kernel properties. SessionRuntime remains
KR-008's storage owner; Kernel only holds its explicit read-only reference/composes DI.
All canonical acceptance is in the two KR-010 test files with KR-011 ownership.

---

# KR-008/009/010 Symbol Statistics

| KR | Public Symbols |
|----|---------------:|
| KR-008 | 3 Runtime Classes |
| KR-009 | 2 Dataclasses + 3 Runtime Classes |
| KR-010 | 2 Runtime Classes + 1 Function |

**Total Symbols Indexed:** **11**

---

# Cumulative Symbol Index Progress

| KR | Indexed Symbols |
|----|----------------:|
| KR-001 | 17 |
| KR-002 | 5 |
| KR-003 | 11 |
| KR-004 | 7 |
| KR-005–007 | 12 |
| KR-008–010 | 11 |

**Total Indexed So Far:** **63 primary public symbols**

---

Document Status: CANONICAL COMPLETE
Version: 1.1 Canonical

<!-- ========================================================================= -->
<!-- M-03A PART 6 — Alphabetical Index + Lookup Tables + Definition of Done -->
<!-- ========================================================================= -->

# Runtime Filename Disambiguation

Status: CANONICAL

Authority:
- AB-00 Development Constitution
- M-00 Canonical Index
- M-03 API Registry
- M-04 Import Graph
- M-06 Module Specifications

---

## Purpose

Wave 1 intentionally contains two different files named `runtime.py`.

They belong to different architectural layers and represent different concepts.

These files must never be confused during implementation.

---

## Canonical Runtime Files

| Canonical File | Layer | Purpose |
|----------------|------|---------|
| `src/kernel/contracts/runtime.py` | Contracts Layer | Defines `RuntimeContract` protocol only. |
| `src/kernel/runtime/runtime.py` | Runtime Layer | Implements `RuntimeKernel` public runtime facade. |

The filename is identical.

The architectural ownership is different.

---

## Canonical Export Paths

### RuntimeContract

```python
from src.kernel.contracts.runtime import RuntimeContract
```

Owner:

KR-004

Category:

Protocol.

---

### RuntimeKernel

```python
from src.kernel.runtime.runtime import RuntimeKernel
```

Owner:

KR-010

Category:

Runtime Class.

---

## Import Disambiguation Rules

### Allowed

```python
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.runtime import RuntimeKernel
```

### Forbidden

```python
from src.kernel.runtime import RuntimeContract
```

```python
from src.kernel.contracts import RuntimeKernel
```

```python
from src.kernel.runtime.runtime import RuntimeContract
```

```python
from src.kernel.contracts.runtime import RuntimeKernel
```

Every forbidden example is an Architecture Conflict.

---

## Ownership Matrix

| Symbol | Owner File | Owner KR |
|--------|------------|----------|
| RuntimeContract | src/kernel/contracts/runtime.py | KR-004 |
| RuntimeKernel | src/kernel/runtime/runtime.py | KR-010 |

Ownership is immutable.

---

## Runtime Layer Boundary

```text
RuntimeKernel
      │ implements
      ▼
RuntimeContract
```

The implementation depends on the protocol.

The protocol never references the implementation.

Dependency direction is immutable.

---

## Import Graph Rule

```text
src/kernel/runtime/runtime.py
            │
            ▼
src/kernel/contracts/runtime.py
```

Reverse dependency is forbidden.

---

## Codex Resolution Rule

When resolving an import named `runtime.py`, Codex must first determine symbol ownership.

Resolution algorithm:

1. If symbol == `RuntimeContract`
   → `src/kernel/contracts/runtime.py`

2. If symbol == `RuntimeKernel`
   → `src/kernel/runtime/runtime.py`

3. Never infer ownership from filename alone.

4. Always resolve by canonical export path.

This rule has higher priority than filename similarity.

---

## Definition of Done

The repository is GREEN only if:

- [x] RuntimeContract imported only from contracts/runtime.py.
- [x] RuntimeKernel imported only from runtime/runtime.py.
- [x] No wildcard imports reference runtime modules.
- [x] No ambiguous `runtime` imports exist anywhere in Wave 1.

Violations are Architecture Conflicts.

# Context Filename Disambiguation

Status: CANONICAL

---

## Purpose

Wave 1 contains two different files named `context.py`.

They belong to different architectural layers.

---

## Canonical Context Files

| Canonical File | Layer | Purpose |
|----------------|------|---------|
| `src/kernel/contracts/context.py` | Contracts | Defines `TraceContext` and `RuntimeContext` dataclasses. |
| `src/kernel/runtime/context.py` | Runtime | Implements `ContextRuntime`. |

---

## Canonical Export Paths

### RuntimeContext

```python
from src.kernel.contracts.context import RuntimeContext
```

### TraceContext

```python
from src.kernel.contracts.context import TraceContext
```

### ContextRuntime

```python
from src.kernel.runtime.context import ContextRuntime
```

---

## Allowed Imports

```python
from src.kernel.contracts.context import RuntimeContext
from src.kernel.runtime.context import ContextRuntime
```

---

## Forbidden Imports

```python
from src.kernel.runtime import RuntimeContext
```

```python
from src.kernel.contracts import ContextRuntime
```

```python
from src.kernel.runtime.context import RuntimeContext
```

```python
from src.kernel.contracts.context import ContextRuntime
```

---

## Ownership Matrix

| Symbol | Owner File | KR |
|--------|------------|----|
| TraceContext | contracts/context.py | KR-004 |
| RuntimeContext | contracts/context.py | KR-004 |
| ContextRuntime | runtime/context.py | KR-008 |

---

## Import Direction

```text
ContextRuntime
      │
      ▼
RuntimeContext
```

Reverse dependency is forbidden.

---

## Codex Resolution Rule

When resolving `context.py`:

1. RuntimeContext / TraceContext → `contracts/context.py`
2. ContextRuntime → `runtime/context.py`
3. Never resolve by filename alone.

# Lifecycle Filename Disambiguation

Status: CANONICAL

---

## Purpose

Wave 1 contains two different files named `lifecycle.py`.

---

## Canonical Lifecycle Files

| File | Layer | Purpose |
|------|------|---------|
| `src/kernel/contracts/lifecycle.py` | Contracts | Defines `LifecycleState`. |
| `src/kernel/runtime/lifecycle.py` | Runtime | Implements `LifecycleRuntime`. |

---

## Canonical Export Paths

### LifecycleState

```python
from src.kernel.contracts.lifecycle import LifecycleState
```

### LifecycleRuntime

```python
from src.kernel.runtime.lifecycle import LifecycleRuntime
```

---

## Forbidden Imports

```python
from src.kernel.runtime.lifecycle import LifecycleState
```

```python
from src.kernel.contracts.lifecycle import LifecycleRuntime
```

---

## Ownership Matrix

| Symbol | Owner File | KR |
|--------|------------|----|
| LifecycleState | contracts/lifecycle.py | KR-004 |
| LifecycleRuntime | runtime/lifecycle.py | KR-006 |

---

## Dependency Rule

```text
LifecycleRuntime
      │
      ▼
LifecycleState
```

Reverse dependency is forbidden.


# Module Filename Disambiguation

Status: CANONICAL

---

## Purpose

Wave 1 contains `module.py` and runtime modules that consume manifests.

---

## Canonical File

| File | Purpose |
|------|---------|
| `src/kernel/contracts/module.py` | Defines `RuntimeModuleManifest`. |

---

## Export Path

```python
from src.kernel.contracts.module import RuntimeModuleManifest
```

---

## Forbidden Imports

```python
from src.kernel.runtime.module import RuntimeModuleManifest
```

---

## Ownership Matrix

| Symbol | Owner File | KR |
|--------|------------|----|
| RuntimeModuleManifest | contracts/module.py | KR-004 |

ManifestRuntime consumes this contract.

The contract never imports ManifestRuntime.

# Service Filename Disambiguation

Status: CANONICAL

---

## Canonical File

| File | Purpose |
|------|---------|
| `src/kernel/contracts/service.py` | Defines `ServiceDescriptor`. |

---

## Export Path

```python
from src.kernel.contracts.service import ServiceDescriptor
```

---

## Forbidden Imports

```python
from src.kernel.runtime.service import ServiceDescriptor
```

---

## Ownership Matrix

| Symbol | Owner File | KR |
|--------|------------|----|
| ServiceDescriptor | contracts/service.py | KR-004 |

ContainerRuntime, RegistryRuntime and ResolverRuntime consume the descriptor.

The descriptor never imports runtime implementations.
# Events Filename Disambiguation

Status: CANONICAL

---

## Canonical File

| File | Purpose |
|------|---------|
| `src/kernel/contracts/events.py` | Defines immutable `RuntimeEvent`. |

---

## Export Path

```python
from src.kernel.contracts.events import RuntimeEvent
```

---

## Forbidden Imports

```python
from src.kernel.runtime.events import RuntimeEvent
```

---

## Ownership Matrix

| Symbol | Owner File | KR |
|--------|------------|----|
| RuntimeEvent | contracts/events.py | KR-004 |

PublisherRuntime creates RuntimeEvents.

DispatcherRuntime dispatches RuntimeEvents.

SubscriberRuntime consumes RuntimeEvents.

RuntimeEvent never imports runtime implementations.

# Pipeline Filename Disambiguation

Status: CANONICAL

---

## Purpose

Pipeline dataclasses live in `runtime/pipeline.py`.

Pipeline execution lives in separate runtime modules.

---

## Canonical File Ownership

| Symbol | Owner File | KR |
|--------|------------|----|
| PipelineDefinition | runtime/pipeline.py | KR-009 |
| PipelineStage | runtime/pipeline.py | KR-009 |
| ManifestRuntime | runtime/manifest.py | KR-009 |
| ExecutorRuntime | runtime/executor.py | KR-009 |
| OrchestratorRuntime | runtime/orchestrator.py | KR-009 |

---

## Canonical Export Paths

```python
from src.kernel.runtime.pipeline import PipelineDefinition
from src.kernel.runtime.pipeline import PipelineStage
from src.kernel.runtime.manifest import ManifestRuntime
from src.kernel.runtime.executor import ExecutorRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
```

---

## Forbidden Imports

```python
from src.kernel.runtime.pipeline import ExecutorRuntime
```

```python
from src.kernel.runtime.pipeline import OrchestratorRuntime
```

---

## Dependency Rule

```text
PipelineDefinition
        │
        ▼
ManifestRuntime
        │
        ▼
ExecutorRuntime
        │
        ▼
OrchestratorRuntime
```

Reverse dependency is forbidden.

# Alphabetical Public Symbol Index

This section provides canonical O(1) lookup for every public symbol exported by Wave 1.

Symbols are indexed alphabetically.

---

# A–C

| Symbol | Category | Owner File | KR |
|--------|----------|------------|----|
| ARCHITECTURE_VERSION | CONSTANT | src/core/version.py | KR-001 |
| BootstrapRuntime | RUNTIME_CLASS | src/kernel/runtime/bootstrap.py | KR-010 |
| ConsoleFormatter | UTILITY_CLASS | src/core/logging_config.py | KR-003 |
| ContainerRuntime | RUNTIME_CLASS | src/kernel/runtime/container.py | KR-005 |
| ContextRuntime | RUNTIME_CLASS | src/kernel/runtime/context.py | KR-008 |

---

# D–H

| Symbol | Category | Owner File | KR |
|--------|----------|------------|----|
| DEFAULT_LOG_LEVEL | CONSTANT | src/core/constants.py | KR-001 |
| DEFAULT_TIMEZONE | CONSTANT | src/core/constants.py | KR-001 |
| DispatcherRuntime | RUNTIME_CLASS | src/kernel/runtime/dispatcher.py | KR-007 |
| DIScope | ENUM | src/core/types.py | KR-001 |
| EventId | TYPE_ALIAS | src/core/types.py | KR-001 |
| EventBusRuntime | RUNTIME_CLASS | src/kernel/runtime/bus.py | KR-007 |
| EventPhase | ENUM | src/core/types.py | KR-001 |
| EventPriority | ENUM | src/core/types.py | KR-001 |
| ExecutorRuntime | RUNTIME_CLASS | src/kernel/runtime/executor.py | KR-009 |
| get_logger | FUNCTION | src/core/logger.py | KR-003 |
| get_settings | FUNCTION | src/core/config.py | KR-002 |
| Headers | TYPE_ALIAS | src/core/types.py | KR-001 |
| HealthStatus | ENUM | src/core/types.py | KR-001 |
| HookRuntime | RUNTIME_CLASS | src/kernel/runtime/hooks.py | KR-006 |

---

# J–P

| Symbol | Category | Owner File | KR |
|--------|----------|------------|----|
| JSONDict | TYPE_ALIAS | src/core/types.py | KR-001 |
| JSONPrimitive | TYPE_ALIAS | src/core/types.py | KR-001 |
| JSONValue | TYPE_ALIAS | src/core/types.py | KR-001 |
| JsonFormatter | UTILITY_CLASS | src/core/logging_config.py | KR-003 |
| LifecycleRuntime | RUNTIME_CLASS | src/kernel/runtime/lifecycle.py | KR-006 |
| LifecycleState | DATACLASS | src/kernel/contracts/lifecycle.py | KR-004 |
| main | FUNCTION | src/main.py | KR-010 |
| ManifestRuntime | RUNTIME_CLASS | src/kernel/runtime/manifest.py | KR-009 |
| Metadata | TYPE_ALIAS | src/core/types.py | KR-001 |
| MetadataRuntime | RUNTIME_CLASS | src/kernel/runtime/metadata.py | KR-008 |
| ModuleId | TYPE_ALIAS | src/core/types.py | KR-001 |
| OrchestratorRuntime | RUNTIME_CLASS | src/kernel/runtime/orchestrator.py | KR-009 |
| Payload | TYPE_ALIAS | src/core/types.py | KR-001 |
| PipelineDefinition | DATACLASS | src/kernel/runtime/pipeline.py | KR-009 |
| PipelineId | TYPE_ALIAS | src/core/types.py | KR-001 |
| PipelineStage | DATACLASS | src/kernel/runtime/pipeline.py | KR-009 |
| PROJECT_NAME | CONSTANT | src/core/constants.py | KR-001 |
| ProviderRuntime | RUNTIME_CLASS | src/kernel/runtime/provider.py | KR-005 |
| PublisherRuntime | RUNTIME_CLASS | src/kernel/runtime/publisher.py | KR-007 |

---

# R–Z

| Symbol | Category | Owner File | KR |
|--------|----------|------------|----|
| RegistryRuntime | RUNTIME_CLASS | src/kernel/runtime/registry.py | KR-005 |
| ResolverRuntime | RUNTIME_CLASS | src/kernel/runtime/resolver.py | KR-005 |
| RuntimeContext | DATACLASS | src/kernel/contracts/context.py | KR-004 |
| RuntimeContract | PROTOCOL | src/kernel/contracts/runtime.py | KR-004 |
| RuntimeEvent | DATACLASS | src/kernel/contracts/events.py | KR-004 |
| RuntimeKernel | RUNTIME_CLASS | src/kernel/runtime/runtime.py | KR-010 |
| RuntimeLayer | ENUM | src/core/types.py | KR-001 |
| RuntimeModuleManifest | DATACLASS | src/kernel/contracts/module.py | KR-004 |
| RuntimeStatus | ENUM | src/core/types.py | KR-001 |
| ScopeRuntime | RUNTIME_CLASS | src/kernel/runtime/scope.py | KR-005 |
| ServiceDescriptor | DATACLASS | src/kernel/contracts/service.py | KR-004 |
| ServiceId | TYPE_ALIAS | src/core/types.py | KR-001 |
| SessionId | TYPE_ALIAS | src/core/types.py | KR-001 |
| SessionRuntime | RUNTIME_CLASS | src/kernel/runtime/session.py | KR-008 |
| Settings | BASE_SETTINGS | src/core/settings.py | KR-002 |
| StateRuntime | RUNTIME_CLASS | src/kernel/runtime/state.py | KR-006 |
| SubscriberRuntime | RUNTIME_CLASS | src/kernel/runtime/subscriber.py | KR-007 |
| TraceContext | DATACLASS | src/kernel/contracts/context.py | KR-004 |
| TraceId | TYPE_ALIAS | src/core/types.py | KR-001 |

---

# Lookup Index by File

## src/core/

<table>
  <table-row>
    <table-cell width="220">**File**</table-cell>
    <table-cell>**Public Symbols**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`types.py`</table-cell>
    <table-cell>11 Type Aliases, 6 Enums</table-cell>
  </table-row>
  <table-row>
    <table-cell>`settings.py`</table-cell>
    <table-cell>Settings</table-cell>
  </table-row>
  <table-row>
    <table-cell>`config.py`</table-cell>
    <table-cell>get_settings, validate_configuration</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logger.py`</table-cell>
    <table-cell>get_logger, LOGGER</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logging_config.py`</table-cell>
    <table-cell>LoggingConfig, RuntimeContextFilter, ConsoleFormatter, JsonFormatter, seven context functions, DEFAULT_LOGGING_CONFIG, DEFAULT_CONTEXT_FILTER</table-cell>
  </table-row>
  <table-row>
    <table-cell>`constants.py`</table-cell>
    <table-cell>PROJECT_NAME, ARCHITECTURE_VERSION, DEFAULT_LOG_LEVEL, DEFAULT_TIMEZONE, DEFAULT_LOCALE</table-cell>
  </table-row>
</table>

---

## src/kernel/contracts/

<table>
  <table-row>
    <table-cell width="220">**File**</table-cell>
    <table-cell>**Public Symbols**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`context.py`</table-cell>
    <table-cell>TraceContext, RuntimeContext</table-cell>
  </table-row>
  <table-row>
    <table-cell>`events.py`</table-cell>
    <table-cell>RuntimeEvent</table-cell>
  </table-row>
  <table-row>
    <table-cell>`lifecycle.py`</table-cell>
    <table-cell>LifecycleState</table-cell>
  </table-row>
  <table-row>
    <table-cell>`module.py`</table-cell>
    <table-cell>RuntimeModuleManifest</table-cell>
  </table-row>
  <table-row>
    <table-cell>`service.py`</table-cell>
    <table-cell>ServiceDescriptor</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.py`</table-cell>
    <table-cell>RuntimeContract</table-cell>
  </table-row>
</table>

---

## src/kernel/runtime/

<table>
  <table-row>
    <table-cell width="220">**File**</table-cell>
    <table-cell>**Public Symbol**</table-cell>
  </table-row>
  <table-row><table-cell>`container.py`</table-cell><table-cell>ContainerRuntime</table-cell></table-row>
  <table-row><table-cell>`registry.py`</table-cell><table-cell>RegistryRuntime</table-cell></table-row>
  <table-row><table-cell>`resolver.py`</table-cell><table-cell>ResolverRuntime</table-cell></table-row>
  <table-row><table-cell>`provider.py`</table-cell><table-cell>ProviderRuntime</table-cell></table-row>
  <table-row><table-cell>`scope.py`</table-cell><table-cell>ScopeRuntime</table-cell></table-row>
  <table-row><table-cell>`lifecycle.py`</table-cell><table-cell>LifecycleRuntime</table-cell></table-row>
  <table-row><table-cell>`state.py`</table-cell><table-cell>StateRuntime</table-cell></table-row>
  <table-row><table-cell>`hooks.py`</table-cell><table-cell>HookRuntime</table-cell></table-row>
  <table-row><table-cell>`bus.py`</table-cell><table-cell>EventBusRuntime</table-cell></table-row>
  <table-row><table-cell>`publisher.py`</table-cell><table-cell>PublisherRuntime</table-cell></table-row>
  <table-row><table-cell>`dispatcher.py`</table-cell><table-cell>DispatcherRuntime</table-cell></table-row>
  <table-row><table-cell>`subscriber.py`</table-cell><table-cell>SubscriberRuntime</table-cell></table-row>
  <table-row><table-cell>`context.py`</table-cell><table-cell>ContextRuntime</table-cell></table-row>
  <table-row><table-cell>`metadata.py`</table-cell><table-cell>MetadataRuntime</table-cell></table-row>
  <table-row><table-cell>`session.py`</table-cell><table-cell>SessionRuntime</table-cell></table-row>
  <table-row><table-cell>`pipeline.py`</table-cell><table-cell>PipelineDefinition, PipelineStage</table-cell></table-row>
  <table-row><table-cell>`manifest.py`</table-cell><table-cell>ManifestRuntime</table-cell></table-row>
  <table-row><table-cell>`executor.py`</table-cell><table-cell>ExecutorRuntime</table-cell></table-row>
  <table-row><table-cell>`orchestrator.py`</table-cell><table-cell>OrchestratorRuntime</table-cell></table-row>
  <table-row><table-cell>`bootstrap.py`</table-cell><table-cell>BootstrapRuntime</table-cell></table-row>
  <table-row><table-cell>`runtime.py`</table-cell><table-cell>RuntimeKernel</table-cell></table-row>
</table>

---

# Lookup Index by Kernel Requirement

| KR | Public Symbols |
|----|----------------|
| KR-001 | Type aliases, enums |
| KR-002 | Settings + configuration API |
| KR-003 | Logging API + constants |
| KR-004 | Immutable contracts + protocol |
| KR-005 | Dependency Injection runtime classes |
| KR-006 | Lifecycle runtime classes |
| KR-007 | Event runtime classes |
| KR-008 | Context runtime classes |
| KR-009 | Pipeline runtime + pipeline dataclasses |
| KR-010 | BootstrapRuntime, RuntimeKernel, main |

---

# Lookup Index by Category

## TYPE_ALIAS

11 symbols.

## ENUM

6 symbols.

## CONSTANT

5 symbols.

## FUNCTION

8 symbols.

## DATACLASS

9 symbols.

## PROTOCOL

1 symbol.

## UTILITY_CLASS

3 symbols.

## RUNTIME_CLASS

22 symbols.

---

# Runtime Facade Lookup Table

| Runtime Facade | Owner File | Implements RuntimeContract |
|---------------|------------|----------------------------|
| ContainerRuntime | container.py | Yes |
| LifecycleRuntime | lifecycle.py | Yes |
| EventBusRuntime | bus.py | Yes |
| ContextRuntime | context.py | Yes |
| OrchestratorRuntime | orchestrator.py | Yes |
| RuntimeKernel | runtime.py | Yes |

These six classes form the public runtime surface of Wave 1.

---

# Symbol Resolution Rules

When referencing a public symbol:

1. Import using its canonical export path.
2. Never alias public symbol names.
3. Never duplicate symbol definitions.
4. Never re-export from another module.

Example:

```python
from src.kernel.runtime.container import ContainerRuntime
```

Canonical export paths are immutable.

---

# Global Public Symbol Statistics

| Category | Count |
|----------|------:|
| Type Aliases | 11 |
| Enums | 6 |
| Constants | 5 |
| Dataclasses | 9 |
| Protocols | 1 |
| Utility Classes | 3 |
| Runtime Classes | 22 |
| Public Functions | 8 |

## Total Indexed Public Symbols

**65 canonical exported symbols**

> These 65 symbols define the public surface of Wave 1.
>
> Internal helper methods, private utilities and non-exported implementation classes are intentionally excluded.

---

# Public Symbol Integrity Rules

A public symbol is considered canonical only if:

- It exists in M-01 File Registry.
- It is defined in M-03 API Registry.
- It is indexed here.
- It has an implementation owner in M-06.
- It has test ownership in M-09.

Missing any reference is an Architecture Conflict.

---

# Public Symbol Definition of Done

The Public Symbol Index is GREEN only if:

- [x] Every exported symbol indexed exactly once.
- [x] Every symbol has one canonical owner file.
- [x] Every symbol has one canonical export path.
- [x] Every symbol references one KR owner.
- [x] Every symbol references M-03 API definition.
- [x] Every symbol references M-06 implementation owner.
- [x] Every symbol references M-09 test owner.
- [x] Alphabetical lookup complete.
- [x] File lookup complete.
- [x] Category lookup complete.
- [x] KR lookup complete.

---

# Canonical Completion Marker

**Document ID:** M-03A

**Document Name:** Public Symbol Index

**Version:** 1.0 Canonical

**Status:** COMPLETE

**Authority:** AURORA Engineering Bible v1.1

**Canonical Owner:** Architecture Authority

**Supersedes:** None (new canonical document)

**END OF DOCUMENT**
