# AURORA ENGINEERING BIBLE v1.1

## Approved KR-009 Precedence — ADR-007, 2026-10-06

The compiled KR-009 section below and exact wave1/KR-009 contract supersede
all retained historical KR-009 summaries/examples in this document, including
Executor health/lifecycle, unbound stage execution, ContextRuntime access,
queue/DI acquisition and Orchestrator event production. Reserved event vocabulary
and other modules' ownership remain unchanged. Only MetadataRuntime's public
stateless transformations are permitted for detached context JSON. Bootstrap uses
only OrchestratorRuntime(event_bus); full KR-010 cleanup remains deferred.

Document ID: M-03

Document Name: API Registry

Path:
docs/architecture/master/03_API_REGISTRY.md

Status: CANONICAL SOURCE OF TRUTH

Authority:
- AB-00 Development Constitution
- AB-00A Architecture Reconciliation
- M-00 Canonical Index
- M-01 File Registry
- M-02 Runtime Graph

Version: 1.1 Canonical

---

# Purpose

This document defines the complete public API surface of Wave 1.

It is the single source of truth for every exported:

- class;
- dataclass;
- protocol;
- enum;
- function;
- type alias;
- constant export.

Implementation is forbidden here.

Implementation belongs exclusively to M-06.

---

# API Registry Constitution

Every public symbol inside AURORA satisfies immutable API invariants.

## API Invariants

1. Every public symbol has exactly one owner file.
2. Every public symbol appears exactly once inside this registry.
3. Every public symbol has one responsibility.
4. Every public symbol has an immutable signature.
5. Every public symbol has documented import ownership.
6. Every public symbol documents raised exceptions.

Violating any invariant is an Architecture Conflict.

---

# Public API Categories

Wave 1 exposes seven categories of public symbols.

| Category | Examples |
|----------|----------|
| Type Alias | ModuleId, SessionId |
| Enum | RuntimeLayer |
| Dataclass | RuntimeContext |
| Protocol | RuntimeContract |
| Runtime Class | ContainerRuntime |
| Public Function | get_settings |
| Constant Export | PROJECT_NAME |

Private symbols never appear here.

---

# API Ownership Rule

Every symbol belongs to one production file.

Example:

| Symbol | Owner |
|--------|-------|
| RuntimeLayer | src/core/types.py |
| RuntimeContext | src/kernel/contracts/context.py |
| RuntimeKernel | src/kernel/runtime/runtime.py |
| get_logger | src/core/logger.py |

Duplicate ownership is forbidden.

---

# KR-001 Public API Registry

Directory:

`src/core/`

Runtime Layer:

L0

---

# CORE-001 — src/core/types.py

Canonical owner of the repository typing vocabulary.

---

## Type Alias — ModuleId

### Owner File

`src/core/types.py`

### Category

Public Type Alias.

### Definition

Unique runtime module identifier.

### Canonical Type

```python
type ModuleId = str
```

### Used By

- RuntimeModuleManifest
- OrchestratorRuntime
- ManifestRuntime

### Imported By

KR-004

KR-005

KR-009

### Raised Exceptions

None.

---

## Type Alias — SessionId

### Purpose

Unique session identifier.

### Canonical Type

```python
type SessionId = str
```

### Used By

RuntimeContext

RuntimeEvent

SessionRuntime

---

## Type Alias — PipelineId

### Purpose

Unique pipeline identifier.

### Used By

PipelineDefinition

RuntimeContext

ExecutorRuntime

---

## Type Alias — EventId

### Purpose

Unique runtime event identifier.

### Used By

RuntimeEvent

PublisherRuntime

DispatcherRuntime

---

## Type Alias — TraceId

### Purpose

Distributed trace identifier.

### Used By

TraceContext

EventTrace

RuntimeContext

---

## Type Alias — ServiceId

### Purpose

Dependency Injection service identifier.

### Used By

ServiceDescriptor

ContainerRuntime

ResolverRuntime

---

## Type Alias — JSONPrimitive

### Canonical Definition

```python
None | bool | int | float | str
```

### Purpose

Atomic JSON-compatible value.

---

## Type Alias — JSONValue

### Purpose

Recursive JSON value.

### Used By

Payload

Metadata

Headers

---

## Type Alias — JSONDict

### Purpose

Canonical immutable JSON dictionary representation.

### Used By

Metadata

Payload

Settings metadata

---

## Type Alias — Payload

### Purpose

Runtime event payload.

### Canonical Constraints

- JSON-compatible.
- Immutable by convention.

### Used By

RuntimeEvent

PublisherRuntime

ExecutorRuntime

---

## Type Alias — Metadata

### Purpose

Runtime metadata snapshot.

### Canonical Type

```python
type Metadata = JSONDict
```

### Used By

RuntimeContext

SessionRuntime

MetadataRuntime

### Architecture Rule

Metadata never aliases `dict[str, Any]`.

---

## Type Alias — Headers

### Purpose

Canonical immutable header dictionary.

### Used By

Future Platform Runtime.

Reserved in Wave 1.

---

# Enum Registry — RuntimeLayer

### Owner File

`src/core/types.py`

### Category

Public Enum.

### Canonical Vocabulary

| Member | Meaning |
|--------|---------|
| L0_KERNEL | Kernel Runtime |
| L1_STATE | Shared State Runtime |
| L2_LAYOUT | Layout Runtime |
| L3_THEME | Theme Runtime |
| L4_MOTION | Motion Runtime |
| L5_INTERACTION | Interaction Runtime |
| L6_ACCESSIBILITY | Accessibility Runtime |
| L7_PLATFORM | Platform Runtime |
| L8_RENDER | Render Runtime |

Vocabulary frozen.

### Used By

RuntimeModuleManifest

ManifestRuntime

BootstrapRuntime

---

# Enum Registry — RuntimeStatus

### Canonical Vocabulary

| Member |
|--------|
| CREATED |
| INITIALIZING |
| READY |
| RUNNING |
| FAILED |
| STOPPED |

### Owner

StateRuntime.

### Consumers

LifecycleRuntime

RuntimeKernel

Health Runtime

Vocabulary immutable.

---

# Enum Registry — HealthStatus

### Vocabulary

| Member |
|--------|
| OK |
| WARNING |
| ERROR |

### Used By

RuntimeKernel.health()

Diagnostics snapshots.

---

# Enum Registry — DIScope

### Vocabulary

| Member |
|--------|
| APPLICATION |
| SESSION |
| PIPELINE |
| TRANSIENT |

### Owner Runtime

ScopeRuntime.

### Used By

ServiceDescriptor

ContainerRuntime

ResolverRuntime

---

# Enum Registry — EventPriority

### Vocabulary

| Member |
|--------|
| LOW |
| NORMAL |
| HIGH |
| CRITICAL |

Vocabulary frozen pending Architecture Authority.

### Used By

DispatcherRuntime

PublisherRuntime

---

# Enum Registry — EventPhase

### Vocabulary

| Member |
|--------|
| CREATED |
| PUBLISHED |
| HANDLED |
| FAILED |

Vocabulary frozen pending Architecture Authority.

### Used By

RuntimeEvent diagnostics.

---

# Enum Export Matrix

| Enum | Owner File |
|------|------------|
| RuntimeLayer | types.py |
| RuntimeStatus | types.py |
| HealthStatus | types.py |
| DIScope | types.py |
| EventPriority | types.py |
| EventPhase | types.py |

No enum has multiple owners.

---

# KR-001 API Summary

| Category | Count |
|----------|------:|
| Type Aliases | 11 |
| Enums | 6 |
| Public Symbols | 17 |

Foundation Core exports only immutable vocabulary.

No runtime implementation appears in KR-001.

---

Document Status:

IN PROGRESS (Part 1 of 12)

<!-- ========================================================================= -->
<!-- M-03 PART 2 — KR-002 Configuration Runtime Public API -->
<!-- ========================================================================= -->

# KR-002 Public API Registry

**Directory**

`src/core/`

**Runtime Layer**

L0

**Owner KR**

KR-002 Configuration Runtime

---

# Configuration Runtime Public API

Configuration Runtime exposes exactly one public dataclass and four public functions.

| Symbol | Category | Owner File |
|--------|----------|------------|
| Settings | Frozen Dataclass | settings.py |
| get_settings | Public Function | config.py |
| reload_settings | Public Function | config.py |
| clear_settings_cache | Public Function | config.py |
| validate_settings | Public Function | config.py |

No additional public exports exist.

---

# CONFIG-001 — Settings Dataclass

**Owner File**

`src/core/settings.py`

**Category**

Frozen Public Dataclass

**Runtime Owner**

Configuration Runtime

**Mutability**

Immutable (`frozen=True`).

---

## Purpose

Represents the canonical runtime configuration snapshot.

Exactly one immutable `Settings` instance exists during runtime execution.

---

## Construction Rules

Settings are created:

- once during bootstrap;
- from environment variables;
- after validation succeeds.

Direct manual construction outside Configuration Runtime is forbidden.

---

## Public Fields

### Project Metadata

| Field | Type | Required |
|-------|------|----------|
| project_name | str | Yes |
| project_version | str | Yes |
| architecture_version | str | Yes |
| environment | str | Yes |

---

### Runtime Environment

| Field | Type | Required |
|-------|------|----------|
| debug | bool | Yes |
| log_level | str | Yes |
| timezone | str | Yes |
| locale | str | Yes |

---

### Filesystem

| Field | Type |
|-------|------|
| root_dir | Path |
| src_dir | Path |
| docs_dir | Path |
| tests_dir | Path |
| cache_dir | Path |
| temp_dir | Path |

All paths are absolute.

---

### OpenRouter

| Field | Type |
|-------|------|
| openrouter_api_key | str \| None |
| openrouter_base_url | str |
| openrouter_timeout | int |

---

### Runtime Defaults

| Field | Type |
|-------|------|
| default_language | str |
| default_pipeline_timeout | int |
| default_event_priority | EventPriority |
| metadata | Metadata |

---

## Derived Properties

### is_debug

Returns runtime debug mode.

### is_production

Returns production environment flag.

### has_openrouter_key

Returns whether API key exists.

Derived properties never mutate Settings.

---

## Validation Rules

Settings validates:

- required environment variables;
- directory existence;
- timeout ranges;
- log level vocabulary;
- locale format.

Validation occurs before RuntimeKernel initialization.

---

## Raised Exceptions

| Exception | Condition |
|-----------|-----------|
| ConfigurationError | Invalid configuration |
| EnvironmentVariableError | Missing required environment variable |
| DirectoryValidationError | Invalid repository path |

---

## Imported By

- BootstrapRuntime
- Logging Runtime
- RuntimeKernel
- Tests

Settings are imported read-only.

---

# CONFIG-002 — get_settings()

**Owner File**

`src/core/config.py`

**Category**

Public Function

---

## Signature

```python
def get_settings() -> Settings
```

---

## Purpose

Returns the canonical immutable Settings instance.

---

## Behavior

1. Returns cached Settings.
2. Loads Settings if cache empty.
3. Never creates multiple instances.
4. Thread-safe.

---

## Return Type

Settings

---

## Side Effects

None after cache initialization.

---

## Raises

- ConfigurationError
- EnvironmentVariableError
- DirectoryValidationError

---

## Imported By

Entire runtime.

---

# CONFIG-003 — reload_settings()

**Owner File**

`src/core/config.py`

**Category**

Public Function

---

## Signature

```python
def reload_settings() -> Settings
```

---

## Purpose

Invalidates configuration cache and reloads environment.

---

## Behavior

1. Clears cached Settings.
2. Reloads .env.
3. Validates configuration.
4. Returns new immutable Settings.

---

## Usage Rules

Allowed:

- tests;
- development reload.

Forbidden:

- production pipeline execution.

---

## Raises

Same exceptions as `get_settings()`.

---

# CONFIG-004 — clear_settings_cache()

**Owner File**

`src/core/config.py`

**Category**

Public Function

---

## Signature

```python
def clear_settings_cache() -> None
```

---

## Purpose

Clears internal configuration cache.

---

## Behavior

- Removes cached Settings instance.
- Does not reload configuration.
- Used only by tests and reload_settings.

---

## Imported By

Tests only.

Production runtime must not call this function.

---

# CONFIG-005 — validate_settings()

**Owner File**

`src/core/config.py`

**Category**

Public Function

---

## Signature

```python
def validate_settings(settings: Settings) -> None
```

---

## Purpose

Performs canonical Settings validation.

---

## Validation Coverage

### Environment

- project name
- architecture version
- runtime environment

### Filesystem

- repository root
- docs directory
- src directory
- tests directory

### Runtime Values

- timeout greater than zero
- supported locale
- supported timezone
- supported log level

### Metadata

- JSON compatibility
- immutable snapshot

---

## Return Value

None.

Validation succeeds silently.

---

## Raises

- ConfigurationError
- EnvironmentVariableError
- DirectoryValidationError

---

# Configuration Cache API

The configuration cache is private.

## Private Runtime API

| Symbol | Visibility |
|--------|------------|
| _settings_cache | Private |
| _settings_lock | Private |
| _load_environment | Private |
| _build_settings | Private |

Private symbols are forbidden outside config.py.

---

# Configuration Import Matrix

| Consumer | Allowed API |
|----------|-------------|
| BootstrapRuntime | get_settings |
| Logging Runtime | get_settings |
| RuntimeKernel | get_settings |
| Tests | get_settings, reload_settings, clear_settings_cache |
| Production Modules | get_settings only |

---

# Configuration Lifecycle API

```text
BootstrapRuntime
        │
        ▼
get_settings()
        │
        ▼
Settings Cache
        │
        ▼
Immutable Settings Snapshot
```

`reload_settings()` exists outside the production lifecycle.

---

# Configuration Exception Matrix

| Public API | Raises |
|------------|--------|
| Settings | ConfigurationError |
| get_settings | ConfigurationError |
| reload_settings | ConfigurationError |
| clear_settings_cache | None |
| validate_settings | ConfigurationError |

---

# Configuration API Invariants

Configuration Runtime guarantees:

1. Settings are immutable.
2. Exactly one cached Settings instance exists.
3. Reload always creates a new immutable snapshot.
4. Production runtime never mutates Settings.
5. Configuration validation completes before runtime startup.
6. All filesystem paths are absolute Path objects.

Violating any invariant is an Architecture Conflict.

---

# KR-002 API Summary

| Category | Count |
|----------|------:|
| Public Dataclasses | 1 |
| Public Functions | 4 |
| Public Symbols | 5 |

Configuration Runtime exports exactly five public API symbols.

---

Document Status:

**IN PROGRESS (Part 2 of 12)**

<!-- ========================================================================= -->
<!-- M-03 PART 3 — KR-003 Logging Runtime Public API -->
<!-- ========================================================================= -->

# KR-003 Public API Registry

**Directory**

`src/core/`

**Runtime Layer**

L0

**Owner KR**

KR-003 Logging Runtime

---

# Logging Runtime Public API

Logging Runtime exposes exactly six public API symbols.

| Symbol | Category | Owner File |
|--------|----------|------------|
| get_logger | Public Function | logger.py |
| configure_logging | Public Function | logging_config.py |
| reset_logging | Public Function | logging_config.py |
| ContextFilter | Public Class | logging_config.py |
| ConsoleFormatter | Public Class | logging_config.py |
| JsonFormatter | Public Class | logging_config.py |

No additional public logging exports exist.

---

# LOG-001 — get_logger()

### Owner File

`src/core/logger.py`

### Category

Public Function

### Signature

```python
def get_logger(name: str) -> logging.Logger
```

### Purpose

Returns the canonical logger for a runtime module.

### Behavior

1. Returns cached logger if it already exists.
2. Creates logger on first request.
3. Applies canonical configuration automatically.
4. Logger identity is stable for identical names.

### Parameters

| Parameter | Type | Required |
|-----------|------|----------|
| name | str | Yes |

### Returns

`logging.Logger`

### Raises

None.

### Imported By

Entire production repository.

### Usage Rules

Allowed:

```python
logger = get_logger(__name__)
```

Forbidden:

```python
logging.getLogger(...)
```

Production code always uses `get_logger()`.

---

# LOG-002 — configure_logging()

### Owner File

`src/core/logging_config.py`

### Category

Public Function

### Signature

```python
def configure_logging(settings: Settings) -> None
```

### Purpose

Initializes the global logging system.

### Responsibilities

- configure root logger;
- configure handlers;
- configure formatters;
- configure filters;
- configure propagation policy.

### Execution Rules

Called exactly once during Bootstrap.

Repeated execution is idempotent.

### Parameters

| Parameter | Type |
|-----------|------|
| settings | Settings |

### Raises

| Exception | Condition |
|-----------|-----------|
| LoggingConfigurationError | Invalid logging configuration. |

### Imported By

BootstrapRuntime only.

---

# LOG-003 — reset_logging()

### Owner File

`src/core/logging_config.py`

### Category

Public Function

### Signature

```python
def reset_logging() -> None
```

### Purpose

Resets global logging state.

### Intended Usage

- tests;
- development reload.

### Production Usage

Forbidden.

### Behavior

- removes handlers;
- clears logger cache;
- restores clean logging runtime.

### Raises

None.

---

# LOG-004 — ContextFilter

### Owner File

`src/core/logging_config.py`

### Category

Public Class

### Purpose

Injects runtime context into log records.

### Base Class

```python
logging.Filter
```

### Public Methods

| Method | Signature |
|--------|-----------|
| filter | `(record: LogRecord) -> bool` |

### Injected Fields

| Field | Source |
|-------|--------|
| session_id | RuntimeContext |
| pipeline_id | RuntimeContext |
| trace_id | TraceContext |
| runtime | RuntimeLayer |

### Behavior

Missing context produces empty values.

Never raises exceptions.

### Imported By

`configure_logging()` only.

---

# LOG-005 — ConsoleFormatter

### Owner File

`src/core/logging_config.py`

### Category

Public Class

### Purpose

Human-readable console formatter.

### Base Class

```python
logging.Formatter
```

### Public Methods

| Method | Signature |
|--------|-----------|
| format | `(record: LogRecord) -> str` |

### Output Format

Canonical console structure:

```text
[2026-09-12 21:04:15]
INFO
kernel.runtime.container
Session=...
Trace=...
Message
```

### Rules

- multiline safe;
- UTF-8 output;
- deterministic timestamp formatting.

### Imported By

`configure_logging()`.

---

# LOG-006 — JsonFormatter

### Owner File

`src/core/logging_config.py`

### Category

Public Class

### Purpose

Structured JSON formatter.

### Base Class

```python
logging.Formatter
```

### Public Methods

| Method | Signature |
|--------|-----------|
| format | `(record: LogRecord) -> str` |

### JSON Fields

| Field | Type |
|-------|------|
| timestamp | str |
| level | str |
| logger | str |
| runtime | str |
| session_id | str \| null |
| pipeline_id | str \| null |
| trace_id | str \| null |
| message | str |

### Rules

- valid JSON output;
- deterministic field order;
- UTF-8 encoded.

### Imported By

`configure_logging()`.

---

# Logger Cache API

The logger cache is private.

### Private Symbols

| Symbol | Visibility |
|--------|------------|
| _LOGGER_CACHE | Private |
| _LOGGER_LOCK | Private |
| _ROOT_CONFIGURED | Private |

Private symbols never leave Logging Runtime.

---

# Logging Configuration API

### Root Logger Policy

| Property | Value |
|----------|-------|
| propagate | False |
| level | Settings.log_level |
| handlers | Canonical handlers only |

### Handler Policy

| Handler | Purpose |
|---------|---------|
| ConsoleHandler | Development output |
| JsonHandler | Structured runtime output (reserved) |

Only canonical handlers may be registered.

---

# Logging Context API

Every log record contains runtime context fields.

| Context Field | Source Runtime |
|--------------|----------------|
| session_id | ContextRuntime |
| pipeline_id | ContextRuntime |
| trace_id | ContextRuntime |
| runtime | RuntimeLayer |

Context injection is automatic.

---

# Logging Import Matrix

| Consumer | Allowed API |
|----------|-------------|
| BootstrapRuntime | configure_logging |
| Production Modules | get_logger |
| Tests | get_logger, reset_logging |
| Logging Runtime | ContextFilter, Formatters |

No production module imports formatter classes directly.

---

# Logging Lifecycle API

```text
BootstrapRuntime
        │
        ▼
configure_logging()
        │
        ▼
Root Logger Configured
        │
        ▼
get_logger(__name__)
        │
        ▼
Cached Logger Returned
```

Logging is initialized before RuntimeKernel.

---

# Logging Exception Matrix

| API | Raises |
|-----|--------|
| get_logger | None |
| configure_logging | LoggingConfigurationError |
| reset_logging | None |
| ContextFilter.filter | None |
| ConsoleFormatter.format | None |
| JsonFormatter.format | None |

Logging failures never crash formatter execution.

---

# Logging API Invariants

Logging Runtime guarantees:

1. Every production module uses `get_logger(__name__)`.
2. Root logger is configured exactly once.
3. Logger cache guarantees identity stability.
4. Runtime context is injected automatically.
5. No production code uses `print()`.
6. Logging configuration occurs before runtime startup.
7. Formatter output is deterministic.

Violating any invariant is an Architecture Conflict.

---

# KR-003 API Summary

| Category | Count |
|----------|------:|
| Public Functions | 3 |
| Public Classes | 3 |
| Public Symbols | 6 |

Logging Runtime exports exactly six public API symbols.

---

**Document Status:** IN PROGRESS (Part 3 of 12)

<!-- ========================================================================= -->
<!-- M-03 PART 4 — KR-004 Kernel Contracts Public API (Context + Event Contracts) -->
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

# KR-004 Public API Registry (Part 1)

**Directory**

`src/kernel/contracts/`

**Runtime Layer**

L0

**Owner KR**

KR-004 Kernel Contracts

---

# Kernel Contracts Public API

Kernel Contracts expose immutable contracts only.

This part covers:

| Symbol | Category | Owner File |
|--------|----------|------------|
| TraceContext | Frozen Dataclass | context.py |
| RuntimeContext | Frozen Dataclass | context.py |
| RuntimeEvent | Frozen Dataclass | events.py |

All contracts are immutable (`frozen=True`).

---

# CONTRACT-001 — TraceContext

### Owner File

`src/kernel/contracts/context.py`

### Category

Frozen Public Dataclass

### Runtime Owner

Context Runtime

### Mutability

Immutable.

---

## Purpose

Represents the canonical execution trace.

Every RuntimeContext owns exactly one TraceContext.

Every RuntimeEvent references one TraceContext.

---

## Construction Rules

Created only by:

- BootstrapRuntime (root trace).
- ContextRuntime (session trace).
- PublisherRuntime (child event traces).

Manual mutation is forbidden.

---

## Public Fields

| Field | Type | Required |
|-------|------|----------|
| trace_id | TraceId | Yes |
| parent_trace_id | TraceId \| None | Yes |
| root_trace_id | TraceId | Yes |
| depth | int | Yes |
| created_at | datetime | Yes |

---

## Semantic Rules

### trace_id

Unique identifier of the current trace.

Never reused.

---

### parent_trace_id

Parent trace reference.

`None` only for root trace.

---

### root_trace_id

Identifier shared by the entire execution tree.

Never changes across descendants.

---

### depth

Depth inside trace tree.

Root depth is zero.

---

### created_at

UTC timestamp.

Immutable.

---

## Derived Properties

| Property | Returns |
|----------|---------|
| is_root | bool |
| has_parent | bool |

Derived properties never mutate TraceContext.

---

## Validation Rules

TraceContext validates:

- UUID format.
- non-negative depth.
- root consistency.
- parent/root relationship.

---

## Imported By

- RuntimeContext
- RuntimeEvent
- PublisherRuntime
- ContextRuntime
- Tests

---

## Raised Exceptions

| Exception | Condition |
|-----------|-----------|
| ValidationError | Invalid trace hierarchy. |

---

# CONTRACT-002 — RuntimeContext

### Owner File

`src/kernel/contracts/context.py`

### Category

Frozen Public Dataclass

### Runtime Owner

Context Runtime

### Mutability

Immutable.

---

## Purpose

Represents the canonical execution context of the runtime.

Every pipeline executes inside one RuntimeContext.

---

## Construction Rules

Created only by ContextRuntime.

Replacement creates a new immutable snapshot.

Mutation is forbidden.

---

## Public Fields

### Identity

| Field | Type |
|-------|------|
| session_id | SessionId |
| pipeline_id | PipelineId |
| runtime_layer | RuntimeLayer |

---

### Trace

| Field | Type |
|-------|------|
| trace | TraceContext |

---

### Metadata

| Field | Type |
|-------|------|
| metadata | Metadata |

---

### Timing

| Field | Type |
|-------|------|
| created_at | datetime |
| expires_at | datetime \| None |

---

## Derived Properties

| Property | Returns |
|----------|---------|
| is_expired | bool |
| trace_id | TraceId |
| root_trace_id | TraceId |
| depth | int |

Properties proxy TraceContext where appropriate.

---

## Semantic Rules

### session_id

Stable during session lifetime.

---

### pipeline_id

Stable during pipeline lifetime.

---

### runtime_layer

Current execution layer.

Wave 1 always begins in `L0_KERNEL`.

---

### metadata

Immutable metadata snapshot.

JSON-compatible only.

---

### trace

Immutable TraceContext reference.

---

## Validation Rules

RuntimeContext validates:

- session identifier format.
- pipeline identifier format.
- metadata JSON compatibility.
- trace validity.
- expiration consistency.

---

## Replacement Rules

Updates create a new RuntimeContext.

Allowed operations:

- metadata replacement.
- trace replacement.
- expiration replacement.

In-place mutation is forbidden.

---

## Imported By

- ContextRuntime
- SessionRuntime
- ExecutorRuntime
- EventBusRuntime
- LifecycleRuntime
- Tests

---

## Raised Exceptions

| Exception | Condition |
|-----------|-----------|
| ValidationError | Invalid RuntimeContext. |

---

# CONTRACT-003 — RuntimeEvent

### Owner File

`src/kernel/contracts/events.py`

### Category

Frozen Public Dataclass

### Runtime Owner

Event Bus Runtime

### Mutability

Immutable.

---

## Purpose

Represents the canonical runtime event transported through EventBusRuntime.

---

## Construction Rules

Created only through PublisherRuntime.

Direct construction is forbidden outside tests.

---

## Public Fields

### Identity

| Field | Type |
|-------|------|
| event_id | EventId |
| event_type | str |
| priority | EventPriority |

---

### Context

| Field | Type |
|-------|------|
| session_id | SessionId |
| pipeline_id | PipelineId |
| trace | TraceContext |

---

### Payload

| Field | Type |
|-------|------|
| payload | Payload |
| headers | Headers |

---

### Lifecycle

| Field | Type |
|-------|------|
| phase | EventPhase |
| created_at | datetime |

---

## Derived Properties

| Property | Returns |
|----------|---------|
| trace_id | TraceId |
| root_trace_id | TraceId |
| is_critical | bool |

---

## Event Identity Rules

### event_id

Globally unique.

Never reused.

---

### event_type

Canonical event vocabulary.

Examples:

- PIPELINE_STARTED
- STAGE_COMPLETED
- SESSION_CREATED
- RUNTIME_STARTED

Vocabulary is defined in M-05.

---

### priority

Immutable dispatch priority.

---

### phase

Lifecycle of event.

Updated by PublisherRuntime through immutable replacement.

---

## Payload Rules

Payload must satisfy:

- JSON-compatible.
- Immutable by convention.
- Serializable.

---

## Header Rules

Headers contain transport metadata.

Reserved fields:

| Header | Purpose |
|--------|---------|
| runtime | RuntimeLayer |
| source | ModuleId |
| correlation_id | TraceId |

Headers are immutable.

---

## Validation Rules

RuntimeEvent validates:

- event identifier.
- priority vocabulary.
- phase vocabulary.
- trace validity.
- payload compatibility.
- header compatibility.

---

## Imported By

- PublisherRuntime
- DispatcherRuntime
- SubscriberRuntime
- ExecutorRuntime
- Tests

---

## Raised Exceptions

| Exception | Condition |
|-----------|-----------|
| ValidationError | Invalid RuntimeEvent. |

---

# Context Contract Export Matrix

| Contract | Owner File |
|----------|------------|
| TraceContext | context.py |
| RuntimeContext | context.py |
| RuntimeEvent | events.py |

No duplicated ownership.

---

# Context Contract Import Matrix

| Consumer | Allowed Contracts |
|----------|-------------------|
| ContextRuntime | TraceContext, RuntimeContext |
| EventBusRuntime | RuntimeEvent, TraceContext |
| PipelineRuntime | RuntimeContext, RuntimeEvent |
| LifecycleRuntime | RuntimeContext |
| Tests | All contracts |

Contracts are imported read-only.

---

# Context Contract API Invariants

Kernel Contracts guarantee:

1. TraceContext is immutable.
2. RuntimeContext is immutable.
3. RuntimeEvent is immutable.
4. Trace hierarchy is preserved.
5. Metadata is immutable.
6. Payload is JSON-compatible.
7. Headers are immutable.

Violating any invariant is an Architecture Conflict.

---

# KR-004 Progress Summary

| Category | Count |
|----------|------:|
| Public Dataclasses | 3 |
| Public Symbols Documented | 3 |

Remaining KR-004 contracts are documented in **Part 5**.

---

Document Status:

**IN PROGRESS (Part 4 of 12)**

<!-- ========================================================================= -->
<!-- M-03 PART 5 — KR-004 Kernel Contracts Public API (Lifecycle + Module + DI) -->
<!-- ========================================================================= -->

# KR-004 Public API Registry (Part 2)

**Directory**

`src/kernel/contracts/`

**Runtime Layer**

L0

**Owner KR**

KR-004 Kernel Contracts

---

# Remaining Kernel Contracts

This section completes the public API of KR-004.

| Symbol | Category | Owner File |
|--------|----------|------------|
| LifecycleState | Frozen Dataclass | lifecycle.py |
| RuntimeModuleManifest | Frozen Dataclass | module.py |
| ServiceDescriptor | Frozen Dataclass | service.py |
| RuntimeContract | Protocol | runtime.py |

---

# CONTRACT-004 — LifecycleState

### Owner File

`src/kernel/contracts/lifecycle.py`

### Category

Frozen Public Dataclass

### Runtime Owner

Lifecycle Runtime

### Mutability

Immutable.

---

## Purpose

Represents the immutable snapshot of the runtime lifecycle state.

The lifecycle state machine owns exactly one active LifecycleState at any moment.

---

## Public Fields

| Field | Type |
|-------|------|
| current | RuntimeStatus |
| previous | RuntimeStatus \| None |
| entered_at | datetime |
| transition_count | int |

---

## Field Semantics

### current

Current RuntimeStatus.

### previous

Previous RuntimeStatus.

`None` only immediately after runtime creation.

### entered_at

UTC timestamp when `current` state became active.

### transition_count

Number of successful transitions since runtime creation.

Always non-negative.

---

## Derived Properties

| Property | Returns |
|----------|---------|
| is_running | bool |
| is_ready | bool |
| is_failed | bool |
| is_terminal | bool |

---

## Validation Rules

LifecycleState validates:

- transition count ≥ 0;
- current RuntimeStatus exists;
- previous RuntimeStatus consistency;
- timestamp validity.

---

## Imported By

- StateRuntime
- LifecycleRuntime
- RuntimeKernel
- Tests

---

## Raised Exceptions

| Exception | Condition |
|-----------|-----------|
| ValidationError | Invalid lifecycle snapshot. |

---

# CONTRACT-005 — RuntimeModuleManifest

### Owner File

`src/kernel/contracts/module.py`

### Category

Frozen Public Dataclass

### Runtime Owner

Pipeline Runtime

### Mutability

Immutable.

---

## Purpose

Canonical description of one runtime module inside AURORA.

Every executable runtime module is represented by exactly one manifest.

---

## Public Fields

### Identity

| Field | Type |
|-------|------|
| module_id | ModuleId |
| module_name | str |
| runtime_layer | RuntimeLayer |

---

### Runtime Registration

| Field | Type |
|-------|------|
| provides | tuple[ServiceId, ...] |
| depends_on | tuple[ModuleId, ...] |

---

### Lifecycle

| Field | Type |
|-------|------|
| enabled | bool |
| version | str |

---

### Metadata

| Field | Type |
|-------|------|
| metadata | Metadata |

---

## Field Semantics

### module_id

Globally unique runtime module identifier.

Never changes.

---

### provides

Services exported by this runtime module.

Tuple is immutable.

Must not contain duplicates.

---

### depends_on

Runtime module dependencies.

Must reference existing ModuleIds.

Must form a DAG.

---

### runtime_layer

Layer that owns the module.

Wave 1 modules belong to `L0_KERNEL`.

---

### metadata

JSON-compatible immutable metadata.

---

## Derived Properties

| Property | Returns |
|----------|---------|
| has_dependencies | bool |
| provides_count | int |
| dependency_count | int |

---

## Validation Rules

RuntimeModuleManifest validates:

- unique module identifier;
- runtime layer vocabulary;
- dependency uniqueness;
- provides uniqueness;
- metadata compatibility.

---

## Imported By

- ManifestRuntime
- OrchestratorRuntime
- BootstrapRuntime
- Tests

---

## Raised Exceptions

| Exception | Condition |
|-----------|-----------|
| ValidationError | Invalid runtime module manifest. |

---

# CONTRACT-006 — ServiceDescriptor

### Owner File

`src/kernel/contracts/service.py`

### Category

Frozen Public Dataclass

### Runtime Owner

Dependency Injection Runtime

### Mutability

Immutable.

---

## Purpose

Canonical Dependency Injection service registration descriptor.

Every registered service has exactly one descriptor.

---

## Public Fields

Under the approved KR-004 reconciliation of ADR-004 P-01, exactly:

| Field | Type | Default |
| --- | --- | --- |
| service_id | ServiceId | required |
| scope | DIScope | required |
| implementation | type[ServiceContract] | required |
| eager | bool | False |
| dependencies | tuple[tuple[str, ServiceId], ...] | () |

---

## Field Semantics

### service_id

Registered service identifier; uniqueness is checked by KR-005 RegistryRuntime.

### implementation

Concrete ServiceContract implementation type, not a bare type or service factory.

### scope

Canonical DI scope.

### dependencies

Immutable explicit constructor keyword/ServiceId bindings. Different parameters
may refer to the same registered ID. No dependency lookup by inferred name/type.

### eager

Whether initialization prepares the service; KR-005 permits eager APPLICATION
services only. No initialization runs during descriptor construction.

Lifecycle remains ServiceContract's async initialize/shutdown, not string hooks.

---

## Derived Properties

None. Former hook names, metadata and derived properties are superseded by the
approved exact schema; no compatibility shim or replacement API is introduced.

---

## Validation Rules

ServiceDescriptor is a frozen, keyword-only, slotted contract without concrete
validation, construction, resolution or caching. KR-005 owns descriptor shape,
constructor compatibility, duplicate bindings, missing IDs, dependency cycles and
scope validation according to ADR-004. Defaults preserve old no-dependency callers.

---

## Imported By

- RegistryRuntime
- ResolverRuntime
- ProviderRuntime
- ContainerRuntime
- Tests

---

## Raised Exceptions

None from descriptor construction. KR-005 owns validation errors.

---

# CONTRACT-007 — RuntimeContract

### Owner File

`src/kernel/contracts/runtime.py`

### Category

Public Protocol

### Runtime Owner

Bootstrap Runtime

---

## Purpose

Defines the canonical interface implemented by every runtime.

All runtime implementations conform to RuntimeContract.

---

## Required Properties

| Property | Type |
|----------|------|
| runtime_name | str |
| runtime_layer | RuntimeLayer |

---

## Required Methods

| Method | Signature |
|--------|-----------|
| initialize | `() -> None` |
| shutdown | `() -> None` |
| health | `() -> HealthStatus` |

---

## Behavioral Guarantees

Every RuntimeContract implementation guarantees:

- deterministic initialization;
- deterministic shutdown;
- immutable runtime identity;
- health reporting.

---

## Implemented By

- ContainerRuntime
- LifecycleRuntime
- EventBusRuntime
- ContextRuntime
- OrchestratorRuntime
- RuntimeKernel

---

## Imported By

- BootstrapRuntime
- RuntimeKernel
- Tests

---

# Kernel Contract Export Matrix

| Contract | Owner File |
|----------|------------|
| TraceContext | context.py |
| RuntimeContext | context.py |
| RuntimeEvent | events.py |
| LifecycleState | lifecycle.py |
| RuntimeModuleManifest | module.py |
| ServiceDescriptor | service.py |
| RuntimeContract | runtime.py |

Every contract has exactly one canonical owner.

---

# Kernel Contract Import Matrix

| Consumer Runtime | Allowed Contracts |
|------------------|-------------------|
| ContainerRuntime | ServiceDescriptor |
| LifecycleRuntime | LifecycleState |
| EventBusRuntime | RuntimeEvent |
| ContextRuntime | RuntimeContext, TraceContext |
| PipelineRuntime | RuntimeModuleManifest, RuntimeContext |
| BootstrapRuntime | RuntimeContract, RuntimeModuleManifest |

Contracts are imported read-only.

---

# Kernel Contract Validation Matrix

| Contract | Validation Owner |
|----------|------------------|
| TraceContext | ContextRuntime |
| RuntimeContext | ContextRuntime |
| RuntimeEvent | PublisherRuntime |
| LifecycleState | StateRuntime |
| RuntimeModuleManifest | ManifestRuntime |
| ServiceDescriptor | RegistryRuntime |
| RuntimeContract | BootstrapRuntime |

---

# Kernel Contract API Invariants

Kernel Contracts guarantee:

1. Every contract is immutable.
2. Every contract is serializable when applicable.
3. Metadata is JSON-compatible.
4. No contract imports runtime implementation.
5. No contract owns mutable state.
6. RuntimeModuleManifest forms a DAG through `depends_on`.
7. ServiceDescriptor scope vocabulary is immutable.

Violating any invariant is an Architecture Conflict.

---

# KR-004 API Summary

| Category | Count |
|----------|------:|
| Public Dataclasses | 6 |
| Public Protocols | 1 |
| Total Public Symbols | 7 |

KR-004 exposes exactly seven canonical contracts.

---

**Document Status:** IN PROGRESS (Part 5 of 12)

<!-- ========================================================================= -->
<!-- M-03 PART 6 — KR-005 Dependency Injection Runtime Public API -->
<!-- ========================================================================= -->

# KR-005 Public API Registry (Part 1)

## Approved ADR-004 API replacement

For KR-005, the exact APPROVED signatures in `../wave1/KR-005_DI.md` supersede
the legacy signatures, properties, counts and sync examples below. Container
retains sync register/contains/descriptors, makes resolve/remove asynchronous,
and adds the approved async release/clear_session/clear_pipeline. Resolver receives
Registry/Provider/typed Scope and resolves asynchronously. Provider.provide receives
explicit dependency keywords and awaits initialize; dispose awaits shutdown.
ScopeRuntime[T] receives a typed async callback and explicit IDs/scope, not
descriptors, contexts or Provider. Registry's existing sync API is unchanged.
These are ADR-004-approved changes, not new facade identifiers by inference.


**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-005 Dependency Injection Runtime

---

# Dependency Injection Runtime Public API

DI Runtime exposes exactly five runtime classes.

| Symbol | Category | Owner File |
|--------|----------|------------|
| ContainerRuntime | Runtime Class | container.py |
| RegistryRuntime | Runtime Class | registry.py |
| ResolverRuntime | Runtime Class | resolver.py |
| ProviderRuntime | Runtime Class | provider.py |
| ScopeRuntime | Runtime Class | scope.py |

---

# DI-API-001 — ContainerRuntime

### Owner File

`src/kernel/runtime/container.py`

### Category

Runtime Class

### Implements

RuntimeContract

### Runtime Owner

Dependency Injection Runtime

---

## Purpose

ContainerRuntime is the only public Dependency Injection container.

All service registration and resolution flows through ContainerRuntime.

---

## Public Properties

| Property | Type | Description |
|----------|------|-------------|
| registry | RegistryRuntime | Descriptor registry. |
| resolver | ResolverRuntime | Dependency resolver. |
| provider | ProviderRuntime | Service constructor runtime. |
| scope | ScopeRuntime | Scope cache runtime. |

Properties are read-only after construction.

---

## Public Methods

### register()

```python
def register(descriptor: ServiceDescriptor) -> None
```

Registers a service descriptor.

#### Parameters

| Name | Type |
|------|------|
| descriptor | ServiceDescriptor |

#### Raises

- DuplicateServiceError
- ValidationError

---

### unregister()

```python
def unregister(service_id: ServiceId) -> None
```

Removes service descriptor.

#### Raises

- UnknownServiceError

---

### resolve()

```python
def resolve(service_id: ServiceId) -> object
```

Returns initialized service instance.

#### Behavior

- resolves dependencies recursively;
- respects DI scope cache;
- initializes service if required.

#### Raises

- ServiceResolutionError
- CircularDependencyError
- UnknownServiceError

---

### contains()

```python
def contains(service_id: ServiceId) -> bool
```

Returns whether descriptor exists.

---

### descriptors()

```python
def descriptors() -> tuple[ServiceDescriptor, ...]
```

Returns immutable descriptor snapshot.

---

### shutdown()

```python
def shutdown() -> None
```

Disposes cached scoped services.

Called only during runtime shutdown.

---

## Lifecycle Methods

Implements RuntimeContract.

| Method | Purpose |
|--------|---------|
| initialize() | Initialize internal runtimes. |
| shutdown() | Dispose services. |
| health() | Return HealthStatus. |

---

## Imported By

- RuntimeKernel
- BootstrapRuntime
- Tests

No runtime constructs ContainerRuntime directly.

---

# DI-API-002 — RegistryRuntime

### Owner File

`src/kernel/runtime/registry.py`

### Category

Runtime Class

### Runtime Owner

Dependency Injection Runtime

---

## Purpose

Stores immutable ServiceDescriptor objects.

RegistryRuntime never creates service instances.

---

## Public Methods

### register()

```python
def register(descriptor: ServiceDescriptor) -> None
```

Stores descriptor.

Raises DuplicateServiceError.

---

### remove()

```python
def remove(service_id: ServiceId) -> None
```

Deletes descriptor.

Raises UnknownServiceError.

---

### descriptor()

```python
def descriptor(service_id: ServiceId) -> ServiceDescriptor
```

Returns descriptor.

Raises UnknownServiceError.

---

### contains()

```python
def contains(service_id: ServiceId) -> bool
```

Descriptor existence check.

---

### list()

```python
def list() -> tuple[ServiceDescriptor, ...]
```

Immutable registry snapshot.

---

## Imported By

ResolverRuntime

ContainerRuntime

Tests

---

## Raised Exceptions

- DuplicateServiceError
- UnknownServiceError
- ValidationError

---

# DI-API-003 — ResolverRuntime

### Owner File

`src/kernel/runtime/resolver.py`

### Category

Runtime Class

### Runtime Owner

Dependency Injection Runtime

---

## Purpose

Resolves complete dependency graphs.

ResolverRuntime owns dependency traversal.

---

## Public Methods

### resolve()

```python
def resolve(service_id: ServiceId) -> object
```

Canonical dependency resolution entrypoint.

---

### dependencies()

```python
def dependencies(service_id: ServiceId) -> tuple[ServiceId, ...]
```

Returns immutable dependency graph for one service.

---

## Resolution Algorithm

1. Read descriptor.
2. Validate dependencies.
3. Detect cycles.
4. Resolve children.
5. Check scope cache.
6. Build missing instance.

Algorithm is deterministic.

---

## Raises

| Exception | Condition |
|-----------|-----------|
| UnknownServiceError | Missing descriptor |
| CircularDependencyError | Dependency cycle |
| ServiceResolutionError | Resolution failure |
| ValidationError | Invalid descriptor graph |

---

## Imported By

ContainerRuntime

Tests

---

# DI-API-004 — ProviderRuntime

### Owner File

`src/kernel/runtime/provider.py`

### Category

Runtime Class

### Runtime Owner

Dependency Injection Runtime

---

## Purpose

Constructs service instances.

ProviderRuntime owns constructor injection.

---

## Public Methods

### build()

```python
def build(descriptor: ServiceDescriptor, dependencies: tuple[object, ...]) -> object
```

Constructs implementation instance.

---

### initialize()

```python
def initialize(instance: object, descriptor: ServiceDescriptor) -> object
```

Executes initialization hook if present.

Returns initialized instance.

---

### shutdown()

```python
def shutdown(instance: object, descriptor: ServiceDescriptor) -> None
```

Executes shutdown hook if present.

---

## Hook Rules

Initialization hook:

- optional;
- executed once.

Shutdown hook:

- optional;
- executed once.

---

## Raises

- ServiceInitializationError
- ServiceShutdownError
- ValidationError

---

## Imported By

ResolverRuntime

ContainerRuntime

Tests

---

# DI-API-005 — ScopeRuntime

### Owner File

`src/kernel/runtime/scope.py`

### Category

Runtime Class

### Runtime Owner

Dependency Injection Runtime

---

## Purpose

Owns every DI scope cache.

No other runtime stores service instances.

---

## Public Methods

### get()

```python
def get(scope: DIScope, service_id: ServiceId) -> object | None
```

Returns cached instance.

---

### store()

```python
def store(scope: DIScope, service_id: ServiceId, instance: object) -> None
```

Caches instance.

---

### clear_pipeline()

```python
def clear_pipeline(pipeline_id: PipelineId) -> None
```

Clears pipeline scope.

---

### clear_session()

```python
def clear_session(session_id: SessionId) -> None
```

Clears session scope.

---

### clear_application()

```python
def clear_application() -> None
```

Clears application scope.

---

### clear_all()

```python
def clear_all() -> None
```

Clears every cache.

Tests only.

---

## Scope Ownership

| Scope | Lifetime |
|-------|----------|
| APPLICATION | Runtime lifetime |
| SESSION | Session lifetime |
| PIPELINE | Pipeline lifetime |
| TRANSIENT | No cache |

---

## Raises

- ValidationError
- ScopeError

---

# Dependency Injection Import Matrix

| Consumer Runtime | Allowed API |
|------------------|-------------|
| BootstrapRuntime | ContainerRuntime |
| RuntimeKernel | ContainerRuntime |
| ResolverRuntime | RegistryRuntime, ProviderRuntime, ScopeRuntime |
| ProviderRuntime | ServiceDescriptor |
| Tests | Entire DI public API |

---

# Dependency Injection Exception Matrix

| API | Raises |
|-----|--------|
| register | DuplicateServiceError, ValidationError |
| unregister | UnknownServiceError |
| resolve | ServiceResolutionError, CircularDependencyError |
| build | ServiceInitializationError |
| initialize | ServiceInitializationError |
| shutdown | ServiceShutdownError |
| store | ScopeError |
| get | ScopeError |

---

# Dependency Injection API Invariants

Dependency Injection Runtime guarantees:

1. ContainerRuntime is the only public DI container.
2. RegistryRuntime owns descriptors only.
3. ResolverRuntime owns dependency traversal only.
4. ProviderRuntime owns construction only.
5. ScopeRuntime owns caches only.
6. ServiceDescriptor is immutable.
7. Scope resolution is deterministic.
8. Circular dependencies are rejected before construction.

Violating any invariant is an Architecture Conflict.

---

# KR-005 API Summary

| Category | Count |
|----------|------:|
| Runtime Classes | 5 |
| Public Methods | 22 |
| Public Properties | 4 |

Dependency Injection Runtime exposes exactly **five runtime classes** and **twenty-two public methods**.

---

**Document Status:** IN PROGRESS (Part 6 of 12)

<!-- ========================================================================= -->
<!-- M-03 PART 7 — KR-006 Lifecycle Runtime + KR-007 Event Bus Runtime API -->
<!-- ========================================================================= -->

# KR-006 Public API Registry

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

**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-006 Lifecycle Runtime

---

# Lifecycle Runtime Public API

Lifecycle Runtime exposes three runtime classes.

| Symbol | Category | Owner File |
|--------|----------|------------|
| LifecycleRuntime | Runtime Class | lifecycle.py |
| StateRuntime | Runtime Class | state.py |
| HookRuntime | Runtime Class | hooks.py |

---

# LIFECYCLE-API-001 — LifecycleRuntime

### Owner File

`src/kernel/runtime/lifecycle.py`

### Category

Runtime Class

### Implements

RuntimeContract

### Purpose

Public lifecycle coordinator of the runtime.

Owns lifecycle orchestration but not lifecycle state storage.

---

## Public Methods

### initialize()

```python
def initialize() -> None
```

Initializes lifecycle subsystem.

Allowed only once.

Raises:

- RuntimeInitializationError

---

### start()

```python
def start() -> None
```

Transitions runtime into `RUNNING`.

#### Transition

READY → RUNNING

Raises:

- RuntimeStateError

---

### stop()

```python
def stop() -> None
```

Transitions runtime into `STOPPED`.

Runs stop hooks.

Raises:

- RuntimeShutdownError
- RuntimeStateError

---

### shutdown()

```python
def shutdown() -> None
```

Runs shutdown hooks.

Disposes lifecycle subsystem.

Raises:

- RuntimeShutdownError

---

### status()

```python
def status() -> RuntimeStatus
```

Returns current runtime status.

---

### state()

```python
def state() -> LifecycleState
```

Returns immutable LifecycleState snapshot.

---

### health()

```python
def health() -> HealthStatus
```

Returns runtime health.

---

## Imported By

- RuntimeKernel
- BootstrapRuntime
- Tests

---

# LIFECYCLE-API-002 — StateRuntime

### Owner File

`src/kernel/runtime/state.py`

### Category

Runtime Class

### Purpose

Canonical runtime state machine owner.

Only StateRuntime mutates RuntimeStatus.

---

## Public Methods

### current()

```python
def current() -> RuntimeStatus
```

Returns current runtime status.

---

### previous()

```python
def previous() -> RuntimeStatus | None
```

Returns previous runtime status.

---

### snapshot()

```python
def snapshot() -> LifecycleState
```

Returns immutable lifecycle snapshot.

---

### transition()

```python
def transition(next_state: RuntimeStatus) -> LifecycleState
```

Executes validated transition.

Returns updated immutable snapshot.

Raises:

- RuntimeStateError

---

### can_transition()

```python
def can_transition(next_state: RuntimeStatus) -> bool
```

Validates transition legality.

---

### reset()

```python
def reset() -> None
```

Testing-only helper.

Forbidden in production runtime.

---

## Imported By

LifecycleRuntime

Tests

---

# LIFECYCLE-API-003 — HookRuntime

### Owner File

`src/kernel/runtime/hooks.py`

### Category

Runtime Class

### Purpose

Registry of lifecycle callbacks.

---

## Public Methods

### register_initialize()

Registers initialize hook.

### register_start()

Registers startup hook.

### register_stop()

Registers stop hook.

### register_shutdown()

Registers shutdown hook.

### run_initialize()

Executes initialize hooks.

### run_start()

Executes startup hooks.

### run_stop()

Executes stop hooks.

### run_shutdown()

Executes shutdown hooks.

### clear()

Removes all registered hooks.

Testing only.

---

## Hook Registration Rules

Hooks execute:

- initialize → registration order
- start → registration order
- stop → reverse registration order
- shutdown → reverse registration order

Ordering is immutable.

---

## Raises

- HookRegistrationError
- HookExecutionError

---

# Lifecycle Import Matrix

| Consumer | Allowed API |
|----------|-------------|
| RuntimeKernel | LifecycleRuntime |
| BootstrapRuntime | LifecycleRuntime |
| Tests | Entire lifecycle API |

---

# Lifecycle API Invariants

1. LifecycleRuntime coordinates only.
2. StateRuntime owns RuntimeStatus.
3. HookRuntime owns callback registry.
4. State transitions are deterministic.
5. Shutdown hooks execute exactly once.

---

# KR-007 Public API Registry

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

Constructors remain Bus(), Subscriber(), Dispatcher(subscribers), Publisher(dispatcher).
Exact argument/return annotations are compiled in the referenced module contract;
no new public symbols or compatibility methods. No handlers_for, dispatch_sync,
dispatch_async, headers or handler-priority API. All publication/dispatch is async.
Runtime identity is event_bus/L0_KERNEL; health is OK. Four lifecycle methods retain
the AB-00D contract; shutdown clears registration without adding a status owner.

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

The only KR-007 custom failures are existing EventValidationError (invalid event
fields/data) and EventHandlerError (duplicate/missing registration, ordinary handler
failure). Original failure remains the cause; no EventDispatchError,
DuplicateSubscriberError or UnknownSubscriberError is added to Foundation.

# KR-006 + KR-007 API Summary

| Runtime | Classes | Public Methods |
|---------|--------:|---------------:|
| Lifecycle Runtime | 3 | 17 |
| Event Bus Runtime | 4 | 24 |

Total methods in the displayed module rows: **41** (constructors/properties excluded).

---

**Document Status:** IN PROGRESS (Part 7 of 12)

<!-- ========================================================================= -->
<!-- M-03 PART 8 — KR-008 Runtime Context Runtime + KR-009 Pipeline Runtime API -->
<!-- ========================================================================= -->

# KR-008 Public API Registry

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

# KR-009 Public API Registry

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
<!-- M-03 PART 9 — KR-010 Bootstrap Runtime Public API -->
<!-- ========================================================================= -->

# KR-010 Public API Registry

**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-010 Bootstrap Runtime

---

# Bootstrap Runtime Public API

Bootstrap Runtime exposes exactly three public API symbols.

| Symbol | Category | Owner File |
|--------|----------|------------|
| BootstrapRuntime | Runtime Class | bootstrap.py |
| RuntimeKernel | Runtime Class | runtime.py |
| main | Public Async Function | src/main.py |

Bootstrap Runtime owns runtime construction only.

---

# BOOTSTRAP-API-001 — BootstrapRuntime

### Owner File

`src/kernel/runtime/bootstrap.py`

### Category

Runtime Class

### Runtime Owner

Bootstrap Runtime

### Purpose

Constructs the complete RuntimeKernel graph.

BootstrapRuntime is the only authorized runtime constructor.

---

## Public Methods

### build()

```python
def build() -> RuntimeKernel
```

Builds and wires the complete runtime graph.

Returns initialized RuntimeKernel instance.

---

### validate_environment()

```python
def validate_environment() -> None
```

Validates repository environment before runtime construction.

Runs:

- configuration validation;
- directory validation;
- environment validation.

---

### build_context()

```python
def build_context() -> ContextRuntime
```

Creates ContextRuntime.

Used internally during build.

Public for tests only.

---

### build_container()

```python
def build_container() -> ContainerRuntime
```

Creates ContainerRuntime.

---

### build_event_bus()

```python
def build_event_bus() -> EventBusRuntime
```

Creates EventBusRuntime.

---

### build_orchestrator()

```python
def build_orchestrator() -> OrchestratorRuntime
```

Creates OrchestratorRuntime.

---

### build_lifecycle()

```python
def build_lifecycle() -> LifecycleRuntime
```

Creates LifecycleRuntime.

---

## Runtime Construction Guarantees

BootstrapRuntime guarantees:

1. construction order is deterministic;
2. every runtime constructed exactly once;
3. dependencies injected before RuntimeKernel creation;
4. RuntimeKernel returned fully wired.

---

## Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeInitializationError | Runtime construction failure. |
| ConfigurationError | Invalid Settings. |
| DirectoryValidationError | Invalid repository layout. |

---

## Imported By

- src/main.py
- integration tests

No runtime imports BootstrapRuntime after startup.

---

# BOOTSTRAP-API-002 — RuntimeKernel

### Owner File

`src/kernel/runtime/runtime.py`

### Category

Runtime Class

### Implements

RuntimeContract

### Purpose

Public runtime facade of Wave 1.

Owns references to every runtime subsystem.

---

## Public Properties

### Runtime References

| Property | Type |
|----------|------|
| container | ContainerRuntime |
| lifecycle | LifecycleRuntime |
| event_bus | EventBusRuntime |
| context | ContextRuntime |
| orchestrator | OrchestratorRuntime |

Properties are immutable after construction.

---

## Runtime Metadata

| Property | Type |
|----------|------|
| version | str |
| runtime_layer | RuntimeLayer |
| architecture_version | str |

Read-only.

---

## Public Methods

### initialize()

```python
def initialize() -> None
```

Initializes every runtime subsystem.

Transition:

CREATED → INITIALIZING → READY.

Raises:

- RuntimeInitializationError.

---

### start()

```python
def start() -> None
```

Transitions runtime into RUNNING.

Runs startup hooks.

Raises:

- RuntimeStateError.

---

### stop()

```python
def stop() -> None
```

Gracefully stops runtime.

Runs stop hooks.

Raises:

- RuntimeShutdownError.

---

### shutdown()

```python
def shutdown() -> None
```

Gracefully disposes every runtime subsystem.

Reverse shutdown order.

Raises:

- RuntimeShutdownError.

---

### execute()

```python
def execute(
    definition: PipelineDefinition,
    context: RuntimeContext,
) -> None
```

Delegates execution to OrchestratorRuntime.

Raises:

- PipelineExecutionError.

---

### status()

```python
def status() -> RuntimeStatus
```

Returns RuntimeStatus snapshot.

---

### state()

```python
def state() -> LifecycleState
```

Returns immutable LifecycleState snapshot.

---

### health()

```python
def health() -> HealthStatus
```

Aggregates runtime health snapshot.

Read-only aggregation.

---

### diagnostics()

```python
def diagnostics() -> Metadata
```

Returns immutable diagnostics snapshot.

Reserved public API for future Diagnostics Runtime.

Wave 1 returns runtime metadata only.

---

## Health Aggregation Rules

RuntimeKernel aggregates:

- ContainerRuntime.health()
- LifecycleRuntime.health()
- EventBusRuntime.health()
- ContextRuntime.health()
- OrchestratorRuntime.health()

Aggregation never mutates runtime health.

---

## Imported By

- src/main.py
- BootstrapRuntime
- Tests

---

## Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeInitializationError | Initialization failed. |
| RuntimeShutdownError | Shutdown failed. |
| RuntimeStateError | Invalid lifecycle transition. |
| PipelineExecutionError | Pipeline execution failed. |

---

# BOOTSTRAP-API-003 — main()

### Owner File

`src/main.py`

### Category

Public Async Function

### Signature

```python
async def main() -> None
```

### Purpose

Canonical asynchronous entrypoint of AURORA.

---

## Execution Sequence

1. BootstrapRuntime.build()
2. RuntimeKernel.initialize()
3. RuntimeKernel.start()
4. Await runtime completion.
5. RuntimeKernel.stop()
6. RuntimeKernel.shutdown()

Sequence is immutable.

---

## Runtime Guarantees

- exactly one RuntimeKernel exists;
- graceful shutdown in finally block;
- startup failures terminate process immediately.

---

## Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeInitializationError | Bootstrap failed. |
| RuntimeShutdownError | Graceful shutdown failed. |

Exceptions are allowed to terminate the process.

---

## Imported By

Python process only.

No production module imports `main()`.

---

# Bootstrap Runtime Lifecycle Matrix

| Public API | Runtime Phase |
|------------|---------------|
| build() | Runtime construction |
| initialize() | Runtime initialization |
| start() | Startup |
| execute() | Runtime execution |
| stop() | Graceful stop |
| shutdown() | Graceful shutdown |
| main() | Process lifecycle |

---

# Bootstrap Import Matrix

| Consumer | Allowed API |
|----------|-------------|
| src/main.py | BootstrapRuntime |
| RuntimeKernel | RuntimeContract |
| Tests | BootstrapRuntime, RuntimeKernel |

BootstrapRuntime is never imported by runtime implementation modules.

---

# Bootstrap Exception Matrix

| API | Raises |
|-----|--------|
| build | RuntimeInitializationError |
| validate_environment | ConfigurationError |
| initialize | RuntimeInitializationError |
| start | RuntimeStateError |
| stop | RuntimeShutdownError |
| shutdown | RuntimeShutdownError |
| execute | PipelineExecutionError |
| main | RuntimeInitializationError, RuntimeShutdownError |

---

# Bootstrap API Invariants

Bootstrap Runtime guarantees:

1. BootstrapRuntime is the only runtime constructor.
2. RuntimeKernel is created exactly once.
3. Runtime references are immutable.
4. Startup order is deterministic.
5. Shutdown order is reverse startup order.
6. RuntimeKernel aggregates but does not create runtime health.
7. main() is the only process entrypoint.

Violating any invariant is an Architecture Conflict.

---

# Wave 1 Runtime API Completion Matrix

| KR | Runtime Classes Documented |
|----|----------------------------|
| KR-005 | 5 |
| KR-006 | 3 |
| KR-007 | 4 |
| KR-008 | 3 |
| KR-009 | 5 |
| KR-010 | 2 |

Total runtime classes documented so far: **22**.

---

# KR-010 API Summary

| Category | Count |
|----------|------:|
| Runtime Classes | 2 |
| Public Functions | 1 |
| Public Methods | 16 |
| Public Properties | 8 |

Bootstrap Runtime exports exactly **three public API symbols**.

---

**Document Status:** IN PROGRESS (Part 9 of 12)

<!-- ========================================================================= -->
<!-- M-03 PART 11 — Public Function & Method Behavioral Registry -->
<!-- ========================================================================= -->

# Public Function & Method Behavioral Registry

This section defines behavioral contracts for every public API exported by Wave 1.

Unlike previous sections, this registry specifies **how APIs behave**, not only their signatures.

Behavior is immutable.

Implementation must conform exactly.

---

# Behavioral Classification Vocabulary

Every public function or method is classified using the following vocabulary.

## Purity Classification

| Classification | Meaning |
|----------------|---------|
| PURE | No side effects. Returns derived value only. |
| CONTEXT_READ | Reads runtime context only. |
| CACHE_READ | Reads cache only. |
| CACHE_WRITE | Mutates owned cache. |
| STATE_WRITE | Mutates owned runtime state. |
| IO_RUNTIME | Performs runtime initialization/shutdown or logging side effects. |

Vocabulary is frozen.

---

## Thread Safety Classification

| Value | Meaning |
|-------|---------|
| SAFE | Safe for concurrent callers. |
| GUARDED | Safe through internal locking. |
| SINGLE_THREAD | Must execute on runtime thread only. |

---

## Async Policy Classification

| Policy | Meaning |
|--------|---------|
| SYNC_ONLY | Must remain synchronous. |
| ASYNC_ALLOWED | Async wrapper permitted in future. |
| ASYNC_REQUIRED | Canonical async API. |

Wave 1 introduces only one ASYNC_REQUIRED public function: `main()`.

---

## Idempotency Classification

| Value | Meaning |
|-------|---------|
| YES | Multiple calls produce equivalent state. |
| NO | Multiple calls change runtime state. |
| CONDITIONAL | Depends on runtime lifecycle state. |

---

# KR-001 Behavioral Registry

<table><table-section header><table-row header><table-cell header>Public API</table-cell><table-cell header>Purity</table-cell><table-cell header>Thread Safety</table-cell><table-cell header>Idempotent</table-cell><table-cell header>Async</table-cell></table-row></table-section><table-row><table-cell>RuntimeLayer enum</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>RuntimeStatus enum</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>HealthStatus enum</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>DIScope enum</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>EventPriority enum</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row></table>

All type aliases and enums are compile-time immutable vocabulary.

---

# KR-002 Behavioral Registry

<table><table-section header><table-row header><table-cell header>API</table-cell><table-cell header>Purity</table-cell><table-cell header>Thread Safety</table-cell><table-cell header>Idempotent</table-cell><table-cell header>Async</table-cell></table-row></table-section><table-row><table-cell>get_settings()</table-cell><table-cell>CACHE_READ</table-cell><table-cell>GUARDED</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>reload_settings()</table-cell><table-cell>CACHE_WRITE</table-cell><table-cell>GUARDED</table-cell><table-cell>NO</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>clear_settings_cache()</table-cell><table-cell>CACHE_WRITE</table-cell><table-cell>GUARDED</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>validate_settings()</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row></table>

### Behavioral Rules

- `get_settings()` never mutates Settings.
- `reload_settings()` always returns a new immutable snapshot.
- `clear_settings_cache()` is forbidden during runtime execution.

---

# KR-003 Behavioral Registry

<table><table-section header><table-row header><table-cell header>API</table-cell><table-cell header>Purity</table-cell><table-cell header>Thread Safety</table-cell><table-cell header>Idempotent</table-cell><table-cell header>Async</table-cell></table-row></table-section><table-row><table-cell>get_logger()</table-cell><table-cell>CACHE_READ</table-cell><table-cell>GUARDED</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>configure_logging()</table-cell><table-cell>IO_RUNTIME</table-cell><table-cell>SINGLE_THREAD</table-cell><table-cell>CONDITIONAL</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>reset_logging()</table-cell><table-cell>IO_RUNTIME</table-cell><table-cell>SINGLE_THREAD</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>ContextFilter.filter()</table-cell><table-cell>CONTEXT_READ</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>ConsoleFormatter.format()</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>JsonFormatter.format()</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell><table-cell>SYNC_ONLY</table-cell></table-row></table>

---

# KR-004 Behavioral Registry

All contracts are immutable.

<table><table-section header><table-row header><table-cell header>Contract</table-cell><table-cell header>Mutable</table-cell><table-cell header>Serializable</table-cell><table-cell header>Replaceable</table-cell></table-row></table-section><table-row><table-cell>TraceContext</table-cell><table-cell>No</table-cell><table-cell>Yes</table-cell><table-cell>Yes (new instance)</table-cell></table-row><table-row><table-cell>RuntimeContext</table-cell><table-cell>No</table-cell><table-cell>Yes</table-cell><table-cell>Yes</table-cell></table-row><table-row><table-cell>RuntimeEvent</table-cell><table-cell>No</table-cell><table-cell>Yes</table-cell><table-cell>Yes</table-cell></table-row><table-row><table-cell>LifecycleState</table-cell><table-cell>No</table-cell><table-cell>Yes</table-cell><table-cell>Yes</table-cell></table-row><table-row><table-cell>RuntimeModuleManifest</table-cell><table-cell>No</table-cell><table-cell>Yes</table-cell><table-cell>No</table-cell></table-row><table-row><table-cell>ServiceDescriptor</table-cell><table-cell>No</table-cell><table-cell>Yes</table-cell><table-cell>No</table-cell></table-row></table>

Replacement always creates a new immutable instance.

---

# KR-005 Behavioral Registry (Dependency Injection)

ADR-004 P-01/P-02/P-05 and APPROVED `../wave1/KR-005_DI.md` supersede this
section's legacy sync-only, unregister, initialize and cleanup descriptions.
Resolution returns initialized services; constructor bindings are explicit and
graphs preflight before side effects. Transients have tracked release ownership.
Removal rejects consumers, detaches before best-effort reverse-order teardown,
and remains effective despite disposal errors. Cancellation preserves retryable
pending cleanup. No other module's API is changed by this replacement.


<table><table-section header><table-row header><table-cell header>API</table-cell><table-cell header>Purity</table-cell><table-cell header>Thread Safety</table-cell><table-cell header>Idempotent</table-cell></table-row></table-section><table-row><table-cell>register()</table-cell><table-cell>STATE_WRITE</table-cell><table-cell>SINGLE_THREAD</table-cell><table-cell>NO</table-cell></table-row><table-row><table-cell>unregister()</table-cell><table-cell>STATE_WRITE</table-cell><table-cell>SINGLE_THREAD</table-cell><table-cell>NO</table-cell></table-row><table-row><table-cell>resolve()</table-cell><table-cell>CACHE_WRITE</table-cell><table-cell>GUARDED</table-cell><table-cell>YES*</table-cell></table-row><table-row><table-cell>contains()</table-cell><table-cell>CACHE_READ</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell></table-row><table-row><table-cell>descriptors()</table-cell><table-cell>CACHE_READ</table-cell><table-cell>SAFE</table-cell><table-cell>YES</table-cell></table-row></table>

<caption>*For singleton scopes, repeated resolve returns the cached instance.</caption>

### DI Behavioral Guarantees

- resolution never mutates descriptors;
- construction occurs once per scope;
- circular dependency detection happens before construction.

---

# KR-006 Behavioral Registry (Lifecycle)

<table><table-section header><table-row header><table-cell header>API</table-cell><table-cell header>State Mutation</table-cell><table-cell header>Allowed States</table-cell></table-row></table-section><table-row><table-cell>initialize()</table-cell><table-cell>Yes</table-cell><table-cell>CREATED → READY</table-cell></table-row><table-row><table-cell>start()</table-cell><table-cell>Yes</table-cell><table-cell>READY → RUNNING</table-cell></table-row><table-row><table-cell>stop()</table-cell><table-cell>Yes</table-cell><table-cell>RUNNING → STOPPED</table-cell></table-row><table-row><table-cell>shutdown()</table-cell><table-cell>No RuntimeStatus mutation</table-cell><table-cell>STOPPED only</table-cell></table-row><table-row><table-cell>status()</table-cell><table-cell>No</table-cell><table-cell>Read-only</table-cell></table-row><table-row><table-cell>state()</table-cell><table-cell>No</table-cell><table-cell>Read-only snapshot</table-cell></table-row></table>

### Lifecycle Guarantees

- invalid transitions raise RuntimeStateError;
- snapshots are immutable.

---

# KR-007 Behavioral Registry (Event Bus)

Canonical clarification: APPROVED ADR-005 E-01–E-04 and the exact
`../wave1/KR-007_EVENT_BUS.md` contract supersede legacy sync-only publication,
obsolete method names and exception rows for KR-007 only. publish/publish_many
and dispatch/dispatch_many are async, awaited sequentially; subscription is sync.
Detached JSON/captured handler snapshots follow ADR-004 P-04. Existing
EventValidationError/EventHandlerError are the only KR-007 custom error mappings;
cancellation/BaseException propagate. No new Runtime, vocabulary or schema field.

<table><table-section header><table-row header><table-cell header>API</table-cell><table-cell header>Side Effects</table-cell><table-cell header>Thread Safety</table-cell></table-row></table-section><table-row><table-cell>publish()</table-cell><table-cell>Dispatch handlers</table-cell><table-cell>SINGLE_THREAD</table-cell></table-row><table-row><table-cell>publish_many()</table-cell><table-cell>Dispatch handlers</table-cell><table-cell>SINGLE_THREAD</table-cell></table-row><table-row><table-cell>create()</table-cell><table-cell>None</table-cell><table-cell>SAFE</table-cell></table-row><table-row><table-cell>dispatch()</table-cell><table-cell>Execute handlers</table-cell><table-cell>SINGLE_THREAD</table-cell></table-row><table-row><table-cell>subscribe()</table-cell><table-cell>Mutate registry</table-cell><table-cell>SINGLE_THREAD</table-cell></table-row><table-row><table-cell>unsubscribe()</table-cell><table-cell>Mutate registry</table-cell><table-cell>SINGLE_THREAD</table-cell></table-row></table>

### Event Guarantees

- RuntimeEvent is immutable;
- handler execution order is deterministic;
- subscriber registry snapshots are immutable.

---

# KR-008 Behavioral Registry (Context Runtime)

<table><table-section header><table-row header><table-cell header>API</table-cell><table-cell header>Purity</table-cell><table-cell header>Thread Safety</table-cell></table-row></table-section><table-row><table-cell>current()</table-cell><table-cell>CONTEXT_READ</table-cell><table-cell>SAFE</table-cell></table-row><table-row><table-cell>replace()</table-cell><table-cell>STATE_WRITE</table-cell><table-cell>SINGLE_THREAD</table-cell></table-row><table-row><table-cell>clear()</table-cell><table-cell>STATE_WRITE</table-cell><table-cell>SINGLE_THREAD</table-cell></table-row><table-row><table-cell>merge()</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell></table-row><table-row><table-cell>put()</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell></table-row><table-row><table-cell>remove()</table-cell><table-cell>PURE</table-cell><table-cell>SAFE</table-cell></table-row></table>

### Context Guarantees

- RuntimeContext replacement preserves trace hierarchy.
- MetadataRuntime never mutates dictionaries.

---

# KR-009 Behavioral Registry (Pipeline Runtime)

<table><table-section header><table-row header><table-cell header>API</table-cell><table-cell header>Side Effects</table-cell><table-cell header>Async Policy</table-cell></table-row></table-section><table-row><table-cell>validate()</table-cell><table-cell>None</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>validate_dag()</table-cell><table-cell>None</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>execute()</table-cell><table-cell>Publish events</table-cell><table-cell>SYNC_ONLY (Wave 1)</table-cell></table-row><table-row><table-cell>execute_stage()</table-cell><table-cell>Publish events</table-cell><table-cell>SYNC_ONLY</table-cell></table-row><table-row><table-cell>register_module()</table-cell><table-cell>Mutate manifest registry</table-cell><table-cell>SINGLE_THREAD</table-cell></table-row><table-row><table-cell>modules()</table-cell><table-cell>Read-only snapshot</table-cell><table-cell>SAFE</table-cell></table-row></table>

### Pipeline Guarantees

- validation precedes execution;
- execution order is deterministic;
- module registry is immutable by snapshot.

---

# KR-010 Behavioral Registry (Bootstrap)

<table><table-section header><table-row header><table-cell header>API</table-cell><table-cell header>Lifecycle Effect</table-cell><table-cell header>Idempotent</table-cell></table-row></table-section><table-row><table-cell>build()</table-cell><table-cell>Construct runtime graph</table-cell><table-cell>NO</table-cell></table-row><table-row><table-cell>initialize()</table-cell><table-cell>Transition to READY</table-cell><table-cell>CONDITIONAL</table-cell></table-row><table-row><table-cell>start()</table-cell><table-cell>Transition to RUNNING</table-cell><table-cell>NO</table-cell></table-row><table-row><table-cell>stop()</table-cell><table-cell>Transition to STOPPED</table-cell><table-cell>CONDITIONAL</table-cell></table-row><table-row><table-cell>shutdown()</table-cell><table-cell>Dispose runtime graph</table-cell><table-cell>CONDITIONAL</table-cell></table-row><table-row><table-cell>execute()</table-cell><table-cell>Execute pipeline</table-cell><table-cell>NO</table-cell></table-row><table-row><table-cell>health()</table-cell><table-cell>Read-only aggregation</table-cell><table-cell>YES</table-cell></table-row><table-row><table-cell>diagnostics()</table-cell><table-cell>Read-only snapshot</table-cell><table-cell>YES</table-cell></table-row><table-row><table-cell>main()</table-cell><table-cell>Owns process lifecycle</table-cell><table-cell>NO</table-cell></table-row></table>

### Bootstrap Guarantees

- exactly one RuntimeKernel;
- graceful shutdown always attempted;
- startup failures abort process.

---

# Exception Ownership Registry

Every public API raises only canonical exceptions owned by M-08.

<table><table-section header><table-row header><table-cell header>Exception Family</table-cell><table-cell header>Owner KR</table-cell></table-row></table-section><table-row><table-cell>ConfigurationError</table-cell><table-cell>KR-002</table-cell></table-row><table-row><table-cell>LoggingConfigurationError</table-cell><table-cell>KR-003</table-cell></table-row><table-row><table-cell>ValidationError</table-cell><table-cell>KR-004</table-cell></table-row><table-row><table-cell>DuplicateServiceError</table-cell><table-cell>KR-005</table-cell></table-row><table-row><table-cell>ServiceResolutionError</table-cell><table-cell>KR-005</table-cell></table-row><table-row><table-cell>RuntimeStateError</table-cell><table-cell>KR-006</table-cell></table-row><table-row><table-cell>EventDispatchError</table-cell><table-cell>KR-007</table-cell></table-row><table-row><table-cell>ContextNotAvailableError</table-cell><table-cell>KR-008</table-cell></table-row><table-row><table-cell>PipelineExecutionError</table-cell><table-cell>KR-009</table-cell></table-row><table-row><table-cell>RuntimeInitializationError</table-cell><table-cell>KR-010</table-cell></table-row></table>

No public API raises undocumented exceptions.

---

# Async Policy Registry

<table><table-section header><table-row header><table-cell header>Async Policy</table-cell><table-cell header>Public APIs</table-cell></table-row></table-section><table-row><table-cell>ASYNC_REQUIRED</table-cell><table-cell>main()</table-cell></table-row><table-row><table-cell>SYNC_ONLY</table-cell><table-cell>All remaining Wave 1 APIs.</table-cell></table-row></table>

Wave 1 runtime APIs remain synchronous unless explicitly documented.

---

# Thread Safety Rules

<table><table-section header><table-row header><table-cell header>Classification</table-cell><table-cell header>Applies To</table-cell></table-row></table-section><table-row><table-cell>SAFE</table-cell><table-cell>Immutable dataclasses, enums, snapshots.</table-cell></table-row><table-row><table-cell>GUARDED</table-cell><table-cell>Configuration cache, logger cache, scope cache.</table-cell></table-row><table-row><table-cell>SINGLE_THREAD</table-cell><table-cell>Lifecycle transitions, event dispatch, registry mutation.</table-cell></table-row></table>

Thread safety vocabulary is immutable.

---

# Behavioral Registry Invariants

The API Registry guarantees:

1. Every public API has one behavioral classification.
2. Every public API has one async policy.
3. Every public API has one thread-safety policy.
4. Every state-mutating API documents ownership.
5. Every cache-mutating API documents cache ownership.
6. Every exception belongs to one canonical owner.
7. Behavioral contracts are implementation-independent.

Violating any invariant is an Architecture Conflict.

---

**Document Status:** IN PROGRESS (Part 11 of 12)

<!-- ========================================================================= -->
<!-- M-03 PART 12 — API Integrity Rules + Cross Reference + Definition of Done -->
<!-- ========================================================================= -->

# API Integrity Rules

This section defines repository-wide API integrity requirements.

Every Wave 1 implementation must satisfy these rules before merge.

Failure to satisfy any rule is an Architecture Conflict.

---

## Public Symbol Ownership Rule

Every exported public symbol has exactly one canonical owner.

### Ownership Rules

| Rule | Requirement |
|------|-------------|
| One Symbol | One production owner file. |
| One Owner | One KR owns lifecycle of symbol. |
| One Export | Symbol exported exactly once. |
| One Definition | Signature defined exactly once. |

Duplicate ownership is forbidden.

---

## Import Integrity Rules

Public APIs may only be imported according to Runtime Layer rules.

### Import Matrix

| Source Layer | Allowed Target Layer |
|--------------|---------------------|
| L0 | L0 |
| L1 | L0–L1 |
| L2 | L0–L2 |
| L3 | L0–L3 |
| L4 | L0–L4 |
| L5 | L0–L5 |
| L6 | L0–L6 |
| L7 | L0–L7 |
| L8 | L0–L8 |

Higher layers may depend only downward.

Downward imports never reverse.

---

## Export Integrity Rules

Every exported symbol satisfies:

- documented signature;
- documented return type;
- documented exceptions;
- documented ownership;
- documented behavioral policy.

Undocumented exports are forbidden.

---

## Exception Integrity Rules

Every public API raises only canonical exception families.

### Exception Rules

- undocumented exceptions forbidden;
- generic Exception forbidden;
- RuntimeError forbidden unless wrapped;
- ValueError forbidden across runtime boundary.

Exception ownership belongs to M-08.

---

## Mutability Integrity Rules

| Symbol Category | Mutable |
|-----------------|---------|
| Enum | No |
| Type Alias | No |
| Frozen Dataclass | No |
| Protocol | No |
| Runtime Snapshot | No |
| Runtime Cache | Yes (owner runtime only) |
| Runtime State | Yes (owner runtime only) |

Mutation ownership is exclusive.

---

## Serialization Integrity Rules

Every public contract must satisfy serialization requirements.

### Serializable Contracts

| Contract | Serializable |
|----------|--------------|
| TraceContext | Yes |
| RuntimeContext | Yes |
| RuntimeEvent | Yes |
| LifecycleState | Yes |
| RuntimeModuleManifest | Yes |
| ServiceDescriptor | Yes |
| PipelineDefinition | Yes |
| PipelineStage | Yes |
| Settings | Yes |

Serialization format is JSON-compatible.

---

## Snapshot Integrity Rules

Immutable snapshots guarantee:

- structural sharing allowed;
- mutation forbidden;
- replacement required for updates.

Applies to:

- RuntimeContext
- Metadata
- RuntimeEvent
- LifecycleState

---

## Thread Safety Integrity Rules

### SAFE APIs

Immutable reads only.

### GUARDED APIs

Internal synchronization required.

### SINGLE_THREAD APIs

Only RuntimeKernel execution thread may invoke.

No undocumented synchronization exists.

---

## Async Integrity Rules

Wave 1 async policy is frozen.

| Policy | Allowed |
|--------|---------|
| SYNC_ONLY | Yes |
| ASYNC_REQUIRED | main() only |
| ASYNC_ALLOWED | Reserved Wave 2+ |

No runtime method becomes async without Architecture Authority.

---

## Runtime Boundary Rules

Runtime APIs cannot bypass runtime ownership.

Examples:

### Forbidden

- mutate RuntimeStatus directly;
- mutate RuntimeContext directly;
- publish raw dictionaries instead of RuntimeEvent;
- instantiate services outside ProviderRuntime.

### Required

- LifecycleRuntime → StateRuntime.
- EventBusRuntime → PublisherRuntime.
- ContainerRuntime → ResolverRuntime.
- ContextRuntime → MetadataRuntime.

---

# Global Public API Statistics

This table is canonical for Wave 1.

## Public Symbol Statistics

| Category | Count |
|----------|------:|
| Type Aliases | 11 |
| Enums | 6 |
| Frozen Dataclasses | 8 |
| Protocols | 1 |
| Runtime Classes | 22 |
| Public Utility Classes | 3 |
| Public Functions | 8 |
| Public Runtime Methods | 109 |
| Public Properties | 12 |

**Total Canonical Public Symbols: 171**

This number is frozen for Wave 1.

---

## KR Symbol Distribution

| KR | Public Symbols |
|----|---------------:|
| KR-001 Foundation Core | 17 |
| KR-002 Configuration Runtime | 5 |
| KR-003 Logging Runtime | 6 |
| KR-004 Kernel Contracts | 7 |
| KR-005 Dependency Injection Runtime | 27 |
| KR-006 Lifecycle Runtime | 20 |
| KR-007 Event Bus Runtime | 23 |
| KR-008 Runtime Context Runtime | 19 |
| KR-009 Pipeline Runtime | 24 |
| KR-010 Bootstrap Runtime | 23 |

Every symbol belongs to exactly one KR.

---

# Cross-Document Reference Matrix

Defines ownership of architectural information across the Engineering Bible.

## Canonical Ownership Matrix

| Architecture Topic | Canonical Document |
|--------------------|--------------------|
| Repository Inventory | M-01 File Registry |
| Runtime Topology | M-02 Runtime Graph |
| Public API Surface | M-03 API Registry |
| Import DAG | M-04 Import Graph |
| Runtime Vocabulary | M-05 State Event DI Lifecycle Registry |
| File Implementations | M-06 Module Specifications |
| Coding Rules | M-07 Implementation Rules |
| Exception Hierarchy | M-08 Exception Registry |
| Testing Ownership | M-09 Test Matrix |
| Build Validation | M-10 Build Checklist |
| Codex Execution Protocol | M-11 Codex Master Prompt |

No architectural concept has multiple owners.

---

## Symbol Reference Rule

Every public symbol must appear in exactly three places.

| Document | Responsibility |
|----------|----------------|
| M-03 | API signature |
| M-06 | Implementation specification |
| M-09 | Test ownership |

Missing any reference is an Architecture Conflict.

---

## Runtime Reference Rule

Every runtime class must appear in:

- M-02 topology.
- M-03 API.
- M-06 implementation.
- M-09 testing.

---

## Contract Reference Rule

Every immutable contract must appear in:

- M-03 API.
- M-05 vocabulary.
- M-06 implementation.
- M-08 validation exceptions.

---

# API Completeness Checklist

The API Registry is complete only if every checklist item is GREEN.

## Foundation

- [x] All type aliases documented.
- [x] All enums documented.
- [x] Ownership documented.

---

## Configuration Runtime

- [x] Settings documented.
- [x] Configuration functions documented.
- [x] Cache behavior documented.

---

## Logging Runtime

- [x] Logger API documented.
- [x] Formatter API documented.
- [x] Context injection documented.

---

## Kernel Contracts

- [x] TraceContext documented.
- [x] RuntimeContext documented.
- [x] RuntimeEvent documented.
- [x] LifecycleState documented.
- [x] RuntimeModuleManifest documented.
- [x] ServiceDescriptor documented.
- [x] RuntimeContract documented.

---

## Runtime APIs

- [x] ContainerRuntime.
- [x] RegistryRuntime.
- [x] ResolverRuntime.
- [x] ProviderRuntime.
- [x] ScopeRuntime.
- [x] LifecycleRuntime.
- [x] StateRuntime.
- [x] HookRuntime.
- [x] EventBusRuntime.
- [x] PublisherRuntime.
- [x] DispatcherRuntime.
- [x] SubscriberRuntime.
- [x] ContextRuntime.
- [x] MetadataRuntime.
- [x] SessionRuntime.
- [x] ManifestRuntime.
- [x] ExecutorRuntime.
- [x] OrchestratorRuntime.
- [x] BootstrapRuntime.
- [x] RuntimeKernel.

---

## Behavioral Registry

- [x] Purity documented.
- [x] Thread safety documented.
- [x] Async policy documented.
- [x] Idempotency documented.
- [x] Exception ownership documented.

---

## Integrity

- [x] Export matrix complete.
- [x] Import matrix complete.
- [x] Runtime ownership complete.
- [x] Cross-document references complete.

---

# API Definition of Done

`03_API_REGISTRY.md` is **GREEN** only if all conditions below are satisfied.

## Public API

- Every public symbol documented.
- Every signature immutable.
- Every return type documented.
- Every property documented.

---

## Ownership

- Every symbol has one owner.
- Every runtime has one owner.
- Every exception has one owner.

---

## Behavior

- Thread safety documented.
- Async policy documented.
- Purity documented.
- Side effects documented.

---

## Architecture

- Cross-document ownership complete.
- Runtime boundary rules documented.
- Import integrity documented.
- Export integrity documented.

---

## Statistics

- Public symbol inventory complete.
- KR ownership inventory complete.
- Runtime inventory complete.

---

# Canonical Completion Marker

**Document ID:** M-03

**Document Name:** API Registry

**Version:** 1.1 Canonical

**Status:** COMPLETE

**Authority:** AURORA Engineering Bible v1.1

**Supersedes:** API Registry v1.0

**Canonical Owner:** Architecture Authority

**END OF DOCUMENT**
