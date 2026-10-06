# AURORA ENGINEERING BIBLE v1.1

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

# KR-002 Symbol Index

**Directory**

`src/core/`

**Runtime Layer**

L0

**Owner KR**

KR-002 Configuration Runtime

---

# DATACLASS Registry

## Settings

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-002 |
| Owner File | src/core/settings.py |
| Export Path | src.core.settings.Settings |
| API Registry | CONFIG-001 |
| Module Spec | CONFIG-001 |
| Test Owner | KR-002 Settings Tests |

**Purpose**

Canonical immutable runtime configuration snapshot.

**Public Fields**

- project_name
- project_version
- architecture_version
- environment
- debug
- log_level
- timezone
- locale
- root_dir
- src_dir
- docs_dir
- tests_dir
- cache_dir
- temp_dir
- openrouter_api_key
- openrouter_base_url
- openrouter_timeout
- default_language
- default_pipeline_timeout
- default_event_priority
- metadata

---

# FUNCTION Registry

## get_settings

| Field | Value |
|-------|-------|
| Category | FUNCTION |
| KR Owner | KR-002 |
| Owner File | src/core/config.py |
| Export Path | src.core.config.get_settings |
| API Registry | CONFIG-002 |
| Module Spec | CONFIG-002 |
| Test Owner | KR-002 Config Tests |

**Returns**

Settings

**Behavior**

Returns canonical immutable Settings snapshot.

---

## reload_settings

| Field | Value |
|-------|-------|
| Category | FUNCTION |
| KR Owner | KR-002 |
| Owner File | src/core/config.py |
| Export Path | src.core.config.reload_settings |
| API Registry | CONFIG-003 |
| Module Spec | CONFIG-003 |
| Test Owner | KR-002 Config Tests |

**Returns**

Settings

**Behavior**

Rebuilds immutable Settings snapshot from environment.

---

## clear_settings_cache

| Field | Value |
|-------|-------|
| Category | FUNCTION |
| KR Owner | KR-002 |
| Owner File | src/core/config.py |
| Export Path | src.core.config.clear_settings_cache |
| API Registry | CONFIG-004 |
| Module Spec | CONFIG-004 |
| Test Owner | KR-002 Config Tests |

**Returns**

None

**Behavior**

Testing helper that clears Settings cache.

---

## validate_settings

| Field | Value |
|-------|-------|
| Category | FUNCTION |
| KR Owner | KR-002 |
| Owner File | src/core/config.py |
| Export Path | src.core.config.validate_settings |
| API Registry | CONFIG-005 |
| Module Spec | CONFIG-005 |
| Test Owner | KR-002 Validation Tests |

**Returns**

None

**Behavior**

Validates immutable Settings snapshot.

---

# KR-002 Symbol Statistics

| Category | Count |
|----------|------:|
| Dataclasses | 1 |
| Functions | 4 |
| Total Symbols Indexed | 5 |

---

# KR-003 Symbol Index

**Directory**

`src/core/`

**Runtime Layer**

L0

**Owner KR**

KR-003 Logging Runtime

---

# FUNCTION Registry

## get_logger

| Field | Value |
|-------|-------|
| Category | FUNCTION |
| KR Owner | KR-003 |
| Owner File | src/core/logger.py |
| Export Path | src.core.logger.get_logger |
| API Registry | LOG-001 |
| Module Spec | LOG-001 |
| Test Owner | KR-003 Logger Tests |

**Returns**

logging.Logger

**Behavior**

Returns canonical cached logger instance.

---

## configure_logging

| Field | Value |
|-------|-------|
| Category | FUNCTION |
| KR Owner | KR-003 |
| Owner File | src/core/logging_config.py |
| Export Path | src.core.logging_config.configure_logging |
| API Registry | LOG-002 |
| Module Spec | LOG-002 |
| Test Owner | KR-003 Logging Config Tests |

**Returns**

None

**Behavior**

Initializes global logging runtime.

---

## reset_logging

| Field | Value |
|-------|-------|
| Category | FUNCTION |
| KR Owner | KR-003 |
| Owner File | src/core/logging_config.py |
| Export Path | src.core.logging_config.reset_logging |
| API Registry | LOG-003 |
| Module Spec | LOG-003 |
| Test Owner | KR-003 Logging Config Tests |

**Returns**

None

**Behavior**

Resets logging runtime (tests only).

---

# UTILITY_CLASS Registry

## ContextFilter

| Field | Value |
|-------|-------|
| Category | UTILITY_CLASS |
| KR Owner | KR-003 |
| Owner File | src/core/logging_config.py |
| Export Path | src.core.logging_config.ContextFilter |
| API Registry | LOG-004 |
| Module Spec | LOG-004 |
| Test Owner | KR-003 Context Filter Tests |

**Purpose**

Injects RuntimeContext into log records.

**Public Methods**

- filter()

---

## ConsoleFormatter

| Field | Value |
|-------|-------|
| Category | UTILITY_CLASS |
| KR Owner | KR-003 |
| Owner File | src/core/logging_config.py |
| Export Path | src.core.logging_config.ConsoleFormatter |
| API Registry | LOG-005 |
| Module Spec | LOG-005 |
| Test Owner | KR-003 Formatter Tests |

**Purpose**

Canonical console formatter.

**Public Methods**

- format()

---

## JsonFormatter

| Field | Value |
|-------|-------|
| Category | UTILITY_CLASS |
| KR Owner | KR-003 |
| Owner File | src/core/logging_config.py |
| Export Path | src.core.logging_config.JsonFormatter |
| API Registry | LOG-006 |
| Module Spec | LOG-006 |
| Test Owner | KR-003 Formatter Tests |

**Purpose**

Canonical structured JSON formatter.

**Public Methods**

- format()

---

# Logging Public Constants

These constants are exported publicly from `src/core/constants.py`.

## PROJECT_NAME

| Field | Value |
|-------|-------|
| Category | CONSTANT |
| KR Owner | KR-003 |
| Owner File | src/core/constants.py |
| Export Path | src.core.constants.PROJECT_NAME |
| API Registry | CONSTANT-001 |
| Module Spec | CONSTANT-001 |
| Test Owner | KR-003 Constants Tests |

**Purpose**

Canonical repository name.

---

## ARCHITECTURE_VERSION

| Field | Value |
|-------|-------|
| Category | CONSTANT |
| KR Owner | KR-003 |
| Owner File | src/core/constants.py |
| Export Path | src.core.constants.ARCHITECTURE_VERSION |
| API Registry | CONSTANT-002 |
| Module Spec | CONSTANT-002 |
| Test Owner | KR-003 Constants Tests |

**Purpose**

Canonical Engineering Bible architecture version.

---

## DEFAULT_LOG_LEVEL

| Field | Value |
|-------|-------|
| Category | CONSTANT |
| KR Owner | KR-003 |
| Owner File | src/core/constants.py |
| Export Path | src.core.constants.DEFAULT_LOG_LEVEL |
| API Registry | CONSTANT-003 |
| Module Spec | CONSTANT-003 |
| Test Owner | KR-003 Constants Tests |

**Purpose**

Canonical runtime default log level.

---

## DEFAULT_TIMEZONE

| Field | Value |
|-------|-------|
| Category | CONSTANT |
| KR Owner | KR-003 |
| Owner File | src/core/constants.py |
| Export Path | src.core.constants.DEFAULT_TIMEZONE |
| API Registry | CONSTANT-004 |
| Module Spec | CONSTANT-004 |
| Test Owner | KR-003 Constants Tests |

**Purpose**

Canonical runtime timezone.

---

## DEFAULT_LOCALE

| Field | Value |
|-------|-------|
| Category | CONSTANT |
| KR Owner | KR-003 |
| Owner File | src/core/constants.py |
| Export Path | src.core.constants.DEFAULT_LOCALE |
| API Registry | CONSTANT-005 |
| Module Spec | CONSTANT-005 |
| Test Owner | KR-003 Constants Tests |

**Purpose**

Canonical runtime locale.

---

# KR-003 Symbol Statistics

| Category | Count |
|----------|------:|
| Functions | 3 |
| Utility Classes | 3 |
| Constants | 5 |
| Total Symbols Indexed | 11 |

---

# Cumulative Symbol Index Progress

| KR | Indexed Symbols |
|----|----------------:|
| KR-001 | 17 |
| KR-002 | 5 |
| KR-003 | 11 |

**Total Indexed So Far:** **33 public symbols**

---

**Document Status:** IN PROGRESS (Part 2 of 6)

<!-- ========================================================================= -->
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

**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-009 Pipeline Runtime

---

# DATACLASS Registry

## PipelineStage

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-009 |
| Owner File | src/kernel/runtime/pipeline.py |
| Export Path | src.kernel.runtime.pipeline.PipelineStage |
| API Registry | PIPELINE-API-001 |
| Module Spec | KR-009 PipelineStage |
| Test Owner | KR-009 PipelineStage Tests |

**Purpose**

Immutable executable pipeline stage.

### Public Fields

- stage_id
- module_id
- depends_on

### Derived Properties

- dependency_count
- has_dependencies

### Imported By

- PipelineDefinition
- ManifestRuntime
- ExecutorRuntime

---

## PipelineDefinition

| Field | Value |
|-------|-------|
| Category | DATACLASS |
| KR Owner | KR-009 |
| Owner File | src/kernel/runtime/pipeline.py |
| Export Path | src.kernel.runtime.pipeline.PipelineDefinition |
| API Registry | PIPELINE-API-002 |
| Module Spec | KR-009 PipelineDefinition |
| Test Owner | KR-009 Pipeline Tests |

**Purpose**

Immutable pipeline execution graph.

### Public Fields

- pipeline_id
- stages

### Derived Properties

- stage_count
- is_empty

### Imported By

- ManifestRuntime
- ExecutorRuntime
- OrchestratorRuntime
- RuntimeKernel

---

# RUNTIME_CLASS Registry

## ManifestRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-009 |
| Owner File | src/kernel/runtime/manifest.py |
| Export Path | src.kernel.runtime.manifest.ManifestRuntime |
| API Registry | PIPELINE-API-003 |
| Module Spec | KR-009 ManifestRuntime |
| Test Owner | KR-009 Manifest Tests |

**Purpose**

Pipeline validation runtime.

### Public Methods

- validate()
- validate_stage_ids()
- validate_dependencies()
- validate_dag()

### Depends On

- PipelineDefinition
- PipelineStage

### Imported By

- OrchestratorRuntime

---

## ExecutorRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-009 |
| Owner File | src/kernel/runtime/executor.py |
| Export Path | src.kernel.runtime.executor.ExecutorRuntime |
| API Registry | PIPELINE-API-004 |
| Module Spec | KR-009 ExecutorRuntime |
| Test Owner | KR-009 Executor Tests |

**Purpose**

Pipeline execution runtime.

### Public Methods

- execute()
- execute_stage()
- execution_order()
- health()

### Depends On

- PipelineDefinition
- PipelineStage
- RuntimeContext
- EventBusRuntime

### Imported By

- OrchestratorRuntime
- RuntimeKernel

---

## OrchestratorRuntime

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-009 |
| Owner File | src/kernel/runtime/orchestrator.py |
| Export Path | src.kernel.runtime.orchestrator.OrchestratorRuntime |
| API Registry | PIPELINE-API-005 |
| Module Spec | KR-009 OrchestratorRuntime |
| Test Owner | KR-009 Orchestrator Tests |

**Purpose**

Coordinates runtime modules and pipeline execution.

### Public Methods

- register_module()
- unregister_module()
- modules()
- execute()
- contains()
- health()

### Depends On

- ManifestRuntime
- ExecutorRuntime
- RuntimeModuleManifest

### Imported By

- RuntimeKernel
- BootstrapRuntime

---

# KR-009 Runtime Dependency Matrix

| Runtime | Depends On |
|---------|------------|
| ManifestRuntime | PipelineDefinition, PipelineStage |
| ExecutorRuntime | PipelineDefinition, RuntimeContext, EventBusRuntime |
| OrchestratorRuntime | ManifestRuntime, ExecutorRuntime, RuntimeModuleManifest |

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

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-010 |
| Owner File | src/kernel/runtime/bootstrap.py |
| Export Path | src.kernel.runtime.bootstrap.BootstrapRuntime |
| API Registry | BOOTSTRAP-API-001 |
| Module Spec | KR-010 BootstrapRuntime |
| Test Owner | KR-010 Bootstrap Tests |

**Purpose**

Constructs the RuntimeKernel graph.

### Public Methods

- build()
- validate_environment()
- build_context()
- build_container()
- build_event_bus()
- build_orchestrator()
- build_lifecycle()

### Depends On

- ContainerRuntime
- LifecycleRuntime
- EventBusRuntime
- ContextRuntime
- OrchestratorRuntime

### Imported By

- src/main.py
- Integration Tests

---

## RuntimeKernel

| Field | Value |
|-------|-------|
| Category | RUNTIME_CLASS |
| KR Owner | KR-010 |
| Owner File | src/kernel/runtime/runtime.py |
| Export Path | src.kernel.runtime.runtime.RuntimeKernel |
| API Registry | BOOTSTRAP-API-002 |
| Module Spec | KR-010 RuntimeKernel |
| Test Owner | KR-010 RuntimeKernel Tests |

**Purpose**

Public runtime facade for Wave 1.

### Public Properties

- container
- lifecycle
- event_bus
- context
- orchestrator
- version
- runtime_layer
- architecture_version

### Public Methods

- initialize()
- start()
- stop()
- shutdown()
- execute()
- status()
- state()
- health()
- diagnostics()

### Depends On

- ContainerRuntime
- LifecycleRuntime
- EventBusRuntime
- ContextRuntime
- OrchestratorRuntime

### Imported By

- src/main.py
- BootstrapRuntime

---

# FUNCTION Registry

## main

| Field | Value |
|-------|-------|
| Category | FUNCTION |
| KR Owner | KR-010 |
| Owner File | src/main.py |
| Export Path | src.main.main |
| API Registry | BOOTSTRAP-API-003 |
| Module Spec | KR-010 Main Entrypoint |
| Test Owner | KR-010 Integration Tests |

**Purpose**

Canonical asynchronous process entrypoint.

### Signature

`async def main() -> None`

### Execution Sequence

1. BootstrapRuntime.build()
2. RuntimeKernel.initialize()
3. RuntimeKernel.start()
4. RuntimeKernel.execute()
5. RuntimeKernel.stop()
6. RuntimeKernel.shutdown()

### Imported By

Python process only.

---

# KR-010 Runtime Dependency Matrix

| Runtime | Depends On |
|---------|------------|
| BootstrapRuntime | ContainerRuntime, LifecycleRuntime, EventBusRuntime, ContextRuntime, OrchestratorRuntime |
| RuntimeKernel | All public runtime facades |
| main() | BootstrapRuntime |

---

# Runtime Kernel Ownership Matrix

| Runtime Facade | Owned By |
|---------------|----------|
| ContainerRuntime | RuntimeKernel |
| LifecycleRuntime | RuntimeKernel |
| EventBusRuntime | RuntimeKernel |
| ContextRuntime | RuntimeKernel |
| OrchestratorRuntime | RuntimeKernel |

RuntimeKernel owns references only, never implementations.

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
| ARCHITECTURE_VERSION | CONSTANT | src/core/constants.py | KR-003 |
| BootstrapRuntime | RUNTIME_CLASS | src/kernel/runtime/bootstrap.py | KR-010 |
| clear_settings_cache | FUNCTION | src/core/config.py | KR-002 |
| configure_logging | FUNCTION | src/core/logging_config.py | KR-003 |
| ConsoleFormatter | UTILITY_CLASS | src/core/logging_config.py | KR-003 |
| ContainerRuntime | RUNTIME_CLASS | src/kernel/runtime/container.py | KR-005 |
| ContextFilter | UTILITY_CLASS | src/core/logging_config.py | KR-003 |
| ContextRuntime | RUNTIME_CLASS | src/kernel/runtime/context.py | KR-008 |

---

# D–H

| Symbol | Category | Owner File | KR |
|--------|----------|------------|----|
| DEFAULT_LOCALE | CONSTANT | src/core/constants.py | KR-003 |
| DEFAULT_LOG_LEVEL | CONSTANT | src/core/constants.py | KR-003 |
| DEFAULT_TIMEZONE | CONSTANT | src/core/constants.py | KR-003 |
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
| PROJECT_NAME | CONSTANT | src/core/constants.py | KR-003 |
| ProviderRuntime | RUNTIME_CLASS | src/kernel/runtime/provider.py | KR-005 |
| PublisherRuntime | RUNTIME_CLASS | src/kernel/runtime/publisher.py | KR-007 |

---

# R–Z

| Symbol | Category | Owner File | KR |
|--------|----------|------------|----|
| RegistryRuntime | RUNTIME_CLASS | src/kernel/runtime/registry.py | KR-005 |
| reload_settings | FUNCTION | src/core/config.py | KR-002 |
| ResolverRuntime | RUNTIME_CLASS | src/kernel/runtime/resolver.py | KR-005 |
| reset_logging | FUNCTION | src/core/logging_config.py | KR-003 |
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
| Settings | DATACLASS | src/core/settings.py | KR-002 |
| StateRuntime | RUNTIME_CLASS | src/kernel/runtime/state.py | KR-006 |
| SubscriberRuntime | RUNTIME_CLASS | src/kernel/runtime/subscriber.py | KR-007 |
| TraceContext | DATACLASS | src/kernel/contracts/context.py | KR-004 |
| TraceId | TYPE_ALIAS | src/core/types.py | KR-001 |
| validate_settings | FUNCTION | src/core/config.py | KR-002 |

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
    <table-cell>get_settings, reload_settings, clear_settings_cache, validate_settings</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logger.py`</table-cell>
    <table-cell>get_logger</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logging_config.py`</table-cell>
    <table-cell>configure_logging, reset_logging, ContextFilter, ConsoleFormatter, JsonFormatter</table-cell>
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
