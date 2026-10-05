# AURORA MASTER HANDOFF v1.1

**Document ID:** M-06

**Document Name:** Module Specifications

**Path:** `docs/architecture/master/06_MODULE_SPECIFICATIONS.md`

**Status:** CANONICAL SOURCE OF TRUTH

**Authority:**
- AB-00A Development Constitution
- Architecture Freeze v1.0
- Wave 1 Implementation Handoff
- M-01 File Registry
- M-03 API Registry
- M-04 Import Graph
- M-05 State / Event / DI Registry

---

# Purpose

This document is the canonical implementation specification for every Wave 1 production file.

Every production file has:

- single owner KR;
- fixed public API;
- fixed imports;
- fixed exports;
- fixed dataclass rules;
- fixed typing rules;
- fixed exception contract;
- fixed dependency contract.

Codex must never invent APIs outside this document.

---

# Global Module Rules

## Ownership

Every production file belongs to exactly one KR.

No file may be implemented outside its owning KR.

## File Blueprint

Every specification follows exactly this structure:

1. Purpose
2. Imports
3. Public Types / Classes
4. Public Functions
5. Private Helpers
6. Public Constants
7. Raises
8. Imported By
9. __all__
10. Validation Rules

## Dataclass Rules

Unless explicitly overridden:

- `slots=True`
- `kw_only=True`
- `repr=True`
- `eq=True`

Use `frozen=True` only where specified.

## Typing Rules

Public APIs may only use types defined in `src.core.types`.

No `Any` in public APIs.

No untyped containers.

## Export Rules

Every file exposes explicit `__all__`.

Wildcard exports are forbidden.

---

# KR-001 — Foundation Core

Runtime Layer: **L0 Kernel**

Foundation Core contains immutable runtime definitions only.

No runtime logic.

No filesystem operations.

No IO.

---

## CORE-001 — src/core/types.py

### Purpose

Canonical runtime typing definitions.

### Imports

```python
from __future__ import annotations

from enum import StrEnum
from typing import NewType
from uuid import UUID
```

No additional imports.

### Public Type Aliases

```python
ModuleId = NewType("ModuleId", str)
ServiceId = NewType("ServiceId", str)

SessionId = NewType("SessionId", UUID)
PipelineId = NewType("PipelineId", UUID)
EventId = NewType("EventId", UUID)
TraceId = NewType("TraceId", UUID)

type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | list[JSONValue] | dict[str, JSONValue]
type JSONDict = dict[str, JSONValue]

type Payload = JSONDict
type Metadata = JSONDict
type Headers = dict[str, str]
```

### RuntimeLayer

Only canonical runtime layers exist.

| Enum | Meaning |
|------|---------|
| L0_KERNEL | Kernel Runtime |
| L1_STATE | State Runtime |
| L2_LAYOUT | Layout Runtime |
| L3_THEME | Theme Runtime |
| L4_MOTION | Motion Runtime |
| L5_INTERACTION | Interaction Runtime |
| L6_ACCESSIBILITY | Accessibility Runtime |
| L7_PLATFORM | Platform Runtime |
| L8_RENDER | Render Runtime |

No additional layers.

### DIScope

Exactly four scopes.

| Scope | Lifetime |
|-------|----------|
| APPLICATION | Entire runtime |
| SESSION | User session |
| PIPELINE | Pipeline execution |
| TRANSIENT | Single resolution |

### RuntimeStatus

Canonical lifecycle vocabulary.

- CREATED
- INITIALIZING
- READY
- STARTING
- RUNNING
- STOPPING
- STOPPED
- SHUTTING_DOWN
- TERMINATED
- FAILED

Vocabulary is frozen.

### HealthStatus

- HEALTHY
- DEGRADED
- FAILED

### EventPriority

- LOW
- NORMAL
- HIGH
- CRITICAL

Vocabulary frozen.

### EventPhase

- CREATED
- PUBLISHED
- HANDLED
- FAILED

Vocabulary frozen.

### Derived Constants

```python
RUNTIME_LAYER_VALUES
DI_SCOPE_VALUES
RUNTIME_STATUS_VALUES
HEALTH_STATUS_VALUES
EVENT_PRIORITY_VALUES
EVENT_PHASE_VALUES
```

Generated only from enums.

### __all__

Exports exactly:

- RuntimeLayer
- DIScope
- RuntimeStatus
- HealthStatus
- EventPriority
- EventPhase
- ModuleId
- ServiceId
- SessionId
- PipelineId
- EventId
- TraceId
- JSONPrimitive
- JSONValue
- JSONDict
- Payload
- Metadata
- Headers

### Raises

Never raises exceptions.

### Imported By

Every production runtime module.

### Validation Rules

- Ruff clean.
- Pyright strict clean.
- No mutable globals.
- No helper functions.
- No dataclasses.
- No runtime state.

---

## CORE-002 — src/core/constants.py

### Purpose

Canonical immutable runtime constants.

### Imports

```python
from __future__ import annotations

from typing import Final

from src.core.version import (
    ARCHITECTURE_FREEZE,
    ARCHITECTURE_VERSION,
    ENGINE_STAGE,
    ENGINE_VERSION,
    KERNEL_RUNTIME_VERSION,
    PROJECT_DISPLAY_NAME,
    PROJECT_NAME,
    PYTHON_VERSION,
)
```

No runtime imports.

### Manifest Constants

```python
MANIFEST_FIELD_MODULE_ID
MANIFEST_FIELD_RUNTIME_LAYER
MANIFEST_FIELD_DEPENDS_ON
MANIFEST_FIELD_PROVIDES
MANIFEST_FIELD_VERSION

MANIFEST_REQUIRED_FIELDS
```

`MANIFEST_REQUIRED_FIELDS` contains exactly five fields.

### Event Constants

```python
EVENT_VERSION

EVENT_FIELD_EVENT_ID
EVENT_FIELD_EVENT_TYPE
EVENT_FIELD_SESSION_ID
EVENT_FIELD_TIMESTAMP
EVENT_FIELD_PAYLOAD
EVENT_FIELD_TRACE

EVENT_REQUIRED_FIELDS
```

Field order is canonical.

### Runtime Identifiers

```python
RUNTIME_KERNEL_ID
RUNTIME_CONTAINER
RUNTIME_EVENT_BUS
RUNTIME_CONFIG
RUNTIME_LOGGER
RUNTIME_PIPELINE
```

### Scope Constants

```python
SCOPE_APPLICATION
SCOPE_SESSION
SCOPE_PIPELINE
SCOPE_TRANSIENT
```

### Environment Constants

```python
ENV_FILENAME

ENV_APP_ENV
ENV_LOG_LEVEL
ENV_CONFIG_PATH
ENV_SESSION_ID
```

### Directory Constants

```python
CONFIG_DIRECTORY
CACHE_DIRECTORY
DATA_DIRECTORY
LOG_DIRECTORY
```

### Default Constants

```python
DEFAULT_ENCODING
DEFAULT_LOG_LEVEL
DEFAULT_TIMEZONE

TRACE_ROOT_ID
UUID_VERSION
```

### Exit Codes

```python
EXIT_SUCCESS
EXIT_FAILURE

EXIT_CONFIGURATION_ERROR
EXIT_RUNTIME_ERROR
EXIT_DEPENDENCY_ERROR
EXIT_VALIDATION_ERROR
```

### __all__

Exports every constant group above.

Version metadata is re-exported only.

### Raises

Never raises.

### Validation Rules

- Immutable only.
- No duplicated version values.
- No computed runtime state.

<!-- ========================================================================= -->
<!-- M-06 PART 2 — KR-002 Configuration Runtime + KR-003 Logging Runtime -->
<!-- ========================================================================= -->

# KR-002 — Configuration Runtime

**Runtime Layer:** L0 Kernel

Configuration Runtime is the only owner of application configuration loading.

It is responsible for:

- loading `.env`;
- validating configuration;
- exposing immutable runtime settings.

It never owns runtime state beyond immutable configuration.

---

## CONFIG-001 — src/core/settings.py

### Owner

KR-002 Configuration Runtime

### Purpose

Immutable validated application configuration model.

---

### File Blueprint

```
settings.py
├── imports
├── Environment type alias
├── Settings class
├── validators
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import (...)
from src.core.exceptions import (...)
```

No logging imports.

No runtime imports.

No DI imports.

---

### Public Types

```python
Environment = Literal[
    "development",
    "testing",
    "production",
]
```

Frozen vocabulary.

---

### Public Class

```python
class Settings(BaseSettings):
```

Configuration:

| Property | Value |
|----------|-------|
| frozen | True |
| validate_assignment | False |
| extra | forbid |
| env_file | `.env` |
| env_prefix | empty |
| case_sensitive | False |

---

### Public Fields

<table><table-row><table-cell width="220">**Field**</table-cell><table-cell width="180">**Type**</table-cell><table-cell>**Description**</table-cell></table-row><table-row><table-cell>`app_env`</table-cell><table-cell>`Environment`</table-cell><table-cell>Runtime environment.</table-cell></table-row><table-row><table-cell>`log_level`</table-cell><table-cell>`str`</table-cell><table-cell>Logging level.</table-cell></table-row><table-row><table-cell>`config_path`</table-cell><table-cell>`Path`</table-cell><table-cell>Root configuration directory.</table-cell></table-row><table-row><table-cell>`cache_directory`</table-cell><table-cell>`Path`</table-cell><table-cell>Cache directory.</table-cell></table-row><table-row><table-cell>`data_directory`</table-cell><table-cell>`Path`</table-cell><table-cell>Runtime data directory.</table-cell></table-row><table-row><table-cell>`timezone`</table-cell><table-cell>`str`</table-cell><table-cell>Default runtime timezone.</table-cell></table-row></table>

All fields are required.

---

### Validators

#### validate_environment

```python
@field_validator("app_env")
def validate_environment(cls, value: Environment) -> Environment
```

Rules:

- must be one of Environment values;
- raises InvalidConfigurationError otherwise.

---

#### validate_directory

```python
@field_validator(
    "config_path",
    "cache_directory",
    "data_directory",
)
def validate_directory(cls, value: Path) -> Path
```

Rules:

- absolute path;
- existing parent directory;
- normalized path.

---

### Public API

No public methods besides validators.

---

### Raises

<table><table-row><table-cell width="260">**Exception**</table-cell><table-cell>**When**</table-cell></table-row><table-row><table-cell>MissingConfigurationError</table-cell><table-cell>Required environment variable missing.</table-cell></table-row><table-row><table-cell>InvalidConfigurationError</table-cell><table-cell>Invalid value or invalid directory.</table-cell></table-row></table>

---

### Imported By

- config.py
- bootstrap.py
- logger.py
- container.py

---

### __all__

```python
__all__ = [
    "Environment",
    "Settings",
]
```

---

### Validation Rules

- Frozen model.
- No mutable defaults.
- No runtime methods.
- Ruff clean.
- Pyright strict clean.

---

## CONFIG-002 — src/core/config.py

### Owner

KR-002 Configuration Runtime

### Purpose

Immutable settings loader.

Single application owner of Settings lifecycle.

---

### File Blueprint

```
config.py
├── imports
├── _load_settings()
├── get_settings()
├── reload_settings()
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from functools import cache

from src.core.settings import Settings
from src.core.exceptions import (...)
```

No logging.

No runtime.

No container.

---

### Private Functions

#### _load_settings

```python
def _load_settings() -> Settings
```

Responsibilities:

- instantiate Settings;
- validate configuration;
- wrap pydantic validation errors.

Not exported.

---

### Public Functions

#### get_settings

```python
@cache
def get_settings() -> Settings
```

Returns immutable Application-scoped Settings instance.

Cache policy:

- process-local;
- immutable;
- recreated only by reload_settings.

---

#### reload_settings

```python
def reload_settings() -> Settings
```

Responsibilities:

1. clear cache;
2. reload Settings;
3. return new immutable instance.

---

### Raises

<table><table-row><table-cell width="260">**Exception**</table-cell><table-cell>**When**</table-cell></table-row><table-row><table-cell>MissingConfigurationError</table-cell><table-cell>Environment variable missing.</table-cell></table-row><table-row><table-cell>InvalidConfigurationError</table-cell><table-cell>Configuration invalid.</table-cell></table-row></table>

---

### Imported By

- logger.py
- bootstrap.py
- container.py

---

### __all__

```python
__all__ = [
    "get_settings",
    "reload_settings",
]
```

---

### Validation Rules

- Only immutable cache.
- No mutable globals.
- No runtime ownership.
- Ruff clean.
- Pyright strict clean.

---

# KR-003 — Logging Runtime

**Runtime Layer:** L0 Kernel

Logging Runtime owns logging configuration only.

It never owns runtime lifecycle.

---

## LOG-001 — src/core/logging_config.py

### Owner

KR-003 Logging Runtime

### Purpose

Logging configuration primitives.

---

### File Blueprint

```
logging_config.py
├── imports
├── LoggingConfig
├── ContextFilter
├── JsonFormatter
├── ConsoleFormatter
└── __all__
```

---

### Imports

```python
from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from dataclasses import dataclass
```

No container imports.

No runtime imports.

---

### Public Dataclass

#### LoggingConfig

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class LoggingConfig
```

Fields:

<table><table-row><table-cell width="220">**Field**</table-cell><table-cell width="180">**Type**</table-cell><table-cell>**Default**</table-cell></table-row><table-row><table-cell>`level`</table-cell><table-cell>`str`</table-cell><table-cell>DEFAULT_LOG_LEVEL</table-cell></table-row><table-row><table-cell>`json_logs`</table-cell><table-cell>`bool`</table-cell><table-cell>False</table-cell></table-row><table-row><table-cell>`console_logs`</table-cell><table-cell>`bool`</table-cell><table-cell>True</table-cell></table-row><table-row><table-cell>`include_trace`</table-cell><table-cell>`bool`</table-cell><table-cell>True</table-cell></table-row><table-row><table-cell>`include_session`</table-cell><table-cell>`bool`</table-cell><table-cell>True</table-cell></table-row></table>

Immutable.

---

### Public Classes

#### ContextFilter(logging.Filter)

Responsibilities:

Inject:

- trace_id
- session_id
- pipeline_id

Public method:

```python
def filter(self, record: logging.LogRecord) -> bool
```

Returns boolean only.

---

#### JsonFormatter(logging.Formatter)

Public API:

```python
def format(self, record: logging.LogRecord) -> str
```

Produces canonical JSON log.

Required keys:

- timestamp
- level
- logger
- message
- trace_id
- session_id
- pipeline_id

---

#### ConsoleFormatter(logging.Formatter)

Public API:

```python
def format(self, record: logging.LogRecord) -> str
```

Produces human-readable colored log.

No JSON.

---

### Private Runtime State

Only ContextVar objects.

Never exported.

---

### __all__

```python
__all__ = [
    "LoggingConfig",
    "ContextFilter",
    "JsonFormatter",
    "ConsoleFormatter",
]
```

---

### Imported By

- logger.py

---

### Validation Rules

- No print().
- No basicConfig().
- Immutable configuration.
- Ruff clean.
- Pyright strict clean.

---

## LOG-002 — src/core/logger.py

### Owner

KR-003 Logging Runtime

### Purpose

Canonical logger factory.

---

### File Blueprint

```
logger.py
├── imports
├── _build_logger()
├── _create_console_handler()
├── _create_json_handler()
├── configure_logging()
├── get_logger()
└── __all__
```

---

### Imports

```python
from __future__ import annotations

import logging
from functools import cache

from src.core.logging_config import (...)
```

No container imports.

---

### Private Functions

#### _create_console_handler

```python
def _create_console_handler(
    config: LoggingConfig,
) -> logging.Handler
```

---

#### _create_json_handler

```python
def _create_json_handler(
    config: LoggingConfig,
) -> logging.Handler
```

---

#### _build_logger

```python
def _build_logger(
    name: str,
    config: LoggingConfig,
) -> logging.Logger
```

Private only.

---

### Public Functions

#### configure_logging

```python
def configure_logging(
    config: LoggingConfig,
) -> None
```

Responsibilities:

- configure handlers;
- configure formatters;
- install ContextFilter.

May be called once during bootstrap.

---

#### get_logger

```python
@cache
def get_logger(
    name: str,
) -> logging.Logger
```

Returns Application-scoped logger instance.

Never returns root logger.

---

### Raises

<table><table-row><table-cell width="260">**Exception**</table-cell><table-cell>**When**</table-cell></table-row><table-row><table-cell>InvalidConfigurationError</table-cell><table-cell>Logging configuration invalid.</table-cell></table-row></table>

---

### Imported By

- container.py
- lifecycle.py
- event_bus.py
- bootstrap.py
- runtime.py

---

### __all__

```python
__all__ = [
    "configure_logging",
    "get_logger",
]
```

---

### Validation Rules

- Logger cache only.
- No mutable exported globals.
- Structured logging only.
- Ruff clean.
- Pyright strict clean.

---

# KR-002 / KR-003 Definition of Done

KR-002 is GREEN only if:

- immutable Settings model exists;
- configuration validation passes;
- get_settings cache works;
- reload_settings recreates immutable settings;
- tests pass.

KR-003 is GREEN only if:

- configure_logging configures runtime logging;
- get_logger returns cached named logger;
- JSON formatter works;
- Console formatter works;
- Context filter injects runtime context;
- tests pass.

<!-- ========================================================================= -->
<!-- M-06 PART 3 — KR-004 Kernel Contracts -->
<!-- ========================================================================= -->

# KR-004 — Kernel Contracts

**Runtime Layer:** L0 Kernel

Kernel Contracts define immutable runtime interfaces.

They contain **zero implementation**.

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

Authority:
- AB-00 Development Constitution
- M-00 Canonical Index
- M-03 API Registry
- M-04 Import Graph
- M-06 Module Specifications

---

## Purpose

Wave 1 contains two different files named `context.py`.

Although they share a filename, they belong to different architectural layers and export different symbols.

Codex must always resolve imports by canonical symbol ownership, never by filename similarity.

---

## Canonical Context Files

| Canonical File | Runtime Layer | Owner KR | Public Symbols |
|----------------|---------------|----------|----------------|
| `src/kernel/contracts/context.py` | Contracts Layer | KR-004 | `TraceContext`, `RuntimeContext` |
| `src/kernel/runtime/context.py` | Runtime Layer | KR-008 | `ContextRuntime` |

These files represent different architectural responsibilities.

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

These export paths are immutable.

---

## Ownership Matrix

| Symbol | Owner File | Runtime Layer |
|--------|------------|---------------|
| TraceContext | `contracts/context.py` | Contracts |
| RuntimeContext | `contracts/context.py` | Contracts |
| ContextRuntime | `runtime/context.py` | Runtime |

Ownership is unique.

---

## Import Direction

Canonical dependency:

```text
ContextRuntime
      │
      ▼
RuntimeContext
      │
      ▼
TraceContext
```

Reverse dependency is forbidden.

---

## Allowed Imports

```python
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.context import TraceContext
from src.kernel.runtime.context import ContextRuntime
```

---

## Forbidden Imports

```python
from src.kernel.runtime.context import RuntimeContext
```

```python
from src.kernel.runtime.context import TraceContext
```

```python
from src.kernel.contracts.context import ContextRuntime
```

```python
from src.kernel.runtime import RuntimeContext
```

Every forbidden example is an Architecture Conflict.

---

## Runtime Boundary Rule

`RuntimeContext` is an immutable contract.

`ContextRuntime` owns creation, storage and propagation of `RuntimeContext`.

The contract never references the runtime implementation.

---

## Codex Resolution Rule

Resolution algorithm:

1. `RuntimeContext` → `src/kernel/contracts/context.py`
2. `TraceContext` → `src/kernel/contracts/context.py`
3. `ContextRuntime` → `src/kernel/runtime/context.py`

Filename similarity must never influence import resolution.

---

## Definition of Done

The repository is GREEN only if:

- [x] `RuntimeContext` imported only from `contracts/context.py`.
- [x] `TraceContext` imported only from `contracts/context.py`.
- [x] `ContextRuntime` imported only from `runtime/context.py`.
- [x] No ambiguous `context.py` imports exist anywhere in Wave 1.

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

Forbidden inside KR-004:

- IO
- filesystem
- logging
- threading
- asyncio tasks
- service registration
- dependency resolution
- event dispatching
- runtime bootstrap

Contracts describe behaviour only.

---

## CONTRACT-001 — src/kernel/contracts/runtime.py

### Owner

KR-004 Kernel Contracts

### Purpose

Defines the lifecycle contract implemented by every runtime module.

### File Blueprint

runtime.py

- imports
- RuntimeContract
- __all__

### Imports

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.types import HealthStatus, RuntimeStatus
```

No runtime imports.

### Public Abstract Class

```python
class RuntimeContract(ABC)
```

### Required Methods

```python
@abstractmethod
async def initialize(self) -> None

@abstractmethod
async def start(self) -> None

@abstractmethod
async def stop(self) -> None

@abstractmethod
async def shutdown(self) -> None

@abstractmethod
def health(self) -> HealthStatus
```

### Runtime Contract Rules

| Method | Requirement |
|--------|-------------|
| initialize | Allocate resources only. |
| start | Begin runtime execution. |
| stop | Stop execution gracefully. |
| shutdown | Release owned resources. |
| health | Never mutate runtime state. |

### Raises

Only subclasses define exceptions.

### __all__

```python
__all__ = ["RuntimeContract"]
```

### Imported By

- lifecycle runtime
- container runtime
- pipeline runtime
- bootstrap runtime

### Validation Rules

- ABC only.
- No implementation.
- No fields.
- No dataclasses.

---

## CONTRACT-002 — src/kernel/contracts/module.py

### Owner

KR-004 Kernel Contracts

### Purpose

Defines immutable runtime module metadata.

### File Blueprint

module.py

- imports
- RuntimeModuleManifest
- __all__

### Imports

```python
from __future__ import annotations

from dataclasses import dataclass

from src.core.types import ModuleId, RuntimeLayer
```

### Public Dataclass

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class RuntimeModuleManifest
```

### Fields

| Field | Type | Required |
|-------|------|----------|
| module_id | ModuleId | Yes |
| runtime_layer | RuntimeLayer | Yes |
| depends_on | tuple[ModuleId, ...] | Yes |
| provides | tuple[str, ...] | Yes |
| version | str | Yes |

### Rules

- immutable
- tuple only
- no mutable collections
- no helper methods

### __all__

```python
__all__ = ["RuntimeModuleManifest"]
```

### Imported By

Container runtime.

### Validation Rules

Manifest contains exactly five canonical fields.

---

## CONTRACT-003 — src/kernel/contracts/service.py

### Owner

KR-004 Kernel Contracts

### Purpose

Defines dependency injection service contracts.

### File Blueprint

service.py

- imports
- ServiceDescriptor
- ServiceContract
- __all__

### Imports

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.core.types import DIScope, ServiceId
```

### Public Dataclass

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class ServiceDescriptor
```

### Fields

| Field | Type |
|-------|------|
| service_id | ServiceId |
| scope | DIScope |
| implementation | type[ServiceContract] |
| eager | bool |
| dependencies | tuple[tuple[str, ServiceId], ...] |

### Rules

- immutable
- eager defaults False
- ADR-004: dependencies defaults (); each pair binds a constructor keyword to a ServiceId
- constructor, dependency graph and scope validation remain in KR-005
- descriptor construction has no service construction/initialization side effects

### Public Abstract Class

```python
class ServiceContract(ABC)
```

### Required Methods

```python
@abstractmethod
async def initialize(self) -> None

@abstractmethod
async def shutdown(self) -> None
```

### Rules

Every service owns initialization/shutdown lifecycle.

### __all__

```python
__all__ = [
    "ServiceContract",
    "ServiceDescriptor",
]
```

### Imported By

DI Container.

### Validation Rules

No implementation logic.

---

## CONTRACT-004 — src/kernel/contracts/lifecycle.py

### Owner

KR-004 Kernel Contracts

### Purpose

Defines lifecycle state transitions.

### File Blueprint

lifecycle.py

- imports
- LifecycleState
- LifecycleContract
- __all__

### Imports

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.core.types import RuntimeStatus
```

### Public Dataclass

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class LifecycleState
```

### Fields

| Field | Type |
|-------|------|
| current | RuntimeStatus |
| previous | RuntimeStatus \| None |

### Public Abstract Class

```python
class LifecycleContract(ABC)
```

### Required Methods

```python
@abstractmethod
async def transition(
    self,
    target: RuntimeStatus,
) -> None

@abstractmethod
def state(self) -> LifecycleState
```

### Rules

Lifecycle vocabulary comes only from RuntimeStatus.

### __all__

```python
__all__ = [
    "LifecycleContract",
    "LifecycleState",
]
```

---

## CONTRACT-005 — src/kernel/contracts/context.py

### Owner

KR-004 Kernel Contracts

### Purpose

Defines immutable runtime context.

### File Blueprint

context.py

- imports
- TraceContext
- RuntimeContext
- __all__

### Imports

```python
from __future__ import annotations

from dataclasses import dataclass, field

from src.core.types import (
    Metadata,
    PipelineId,
    SessionId,
    TraceId,
)
```

### Public Dataclass

#### TraceContext

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class TraceContext
```

Fields:

| Field | Type |
|-------|------|
| trace_id | TraceId |
| parent_trace_id | TraceId \| None |

### Public Dataclass

#### RuntimeContext

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class RuntimeContext
```

Fields:

| Field | Type |
|-------|------|
| session_id | SessionId |
| pipeline_id | PipelineId |
| trace | TraceContext |
| metadata | Metadata = field(default_factory=dict) |

### Rules

- metadata is JSON-compatible.
- metadata default uses default_factory.
- frozen.
- slots.

### __all__

```python
__all__ = [
    "RuntimeContext",
    "TraceContext",
]
```

### Validation Rules

No mutable default dictionaries.

---

## CONTRACT-006 — src/kernel/contracts/events.py

### Owner

KR-004 Kernel Contracts

### Purpose

Defines canonical runtime events.

### File Blueprint

events.py

- imports
- RuntimeEvent
- EventHandlerContract
- __all__

### Imports

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.core.types import EventId, Payload, SessionId
from src.kernel.contracts.context import TraceContext
```

### Public Dataclass

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class RuntimeEvent
```

### Canonical Field Order

**Required fields first.**

| Order | Field | Type |
|------|------|------|
| 1 | event_id | EventId |
| 2 | event_type | str |
| 3 | session_id | SessionId |
| 4 | trace | TraceContext |
| 5 | timestamp | datetime |
| 6 | payload | Payload |

### Defaults

Only these defaults exist.

```python
timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
payload: Payload = field(default_factory=dict)
```

### Rules

- trace has no default.
- payload default_factory only.
- timestamp UTC only.
- immutable.
- JSON-compatible payload.

### Public Abstract Class

```python
class EventHandlerContract(ABC)
```

### Required Method

```python
@abstractmethod
async def handle(
    self,
    event: RuntimeEvent,
) -> None
```

### __all__

```python
__all__ = [
    "RuntimeEvent",
    "EventHandlerContract",
]
```

### Validation Rules

This ordering must satisfy Pyright dataclass rules.

---

## CONTRACT-007 — src/kernel/contracts/__init__.py

### Owner

KR-004 Kernel Contracts

### Purpose

Canonical export gateway for all contracts.

### Imports

Only sibling contract modules.

### __all__

Exports exactly:

Runtime

- RuntimeContract

Lifecycle

- LifecycleContract
- LifecycleState

Module

- RuntimeModuleManifest

Service

- ServiceContract
- ServiceDescriptor

Context

- RuntimeContext
- TraceContext

Events

- RuntimeEvent
- EventHandlerContract

### Validation Rules

Alphabetically sorted __all__.

No wildcard exports.

---

# KR-004 Definition of Done

KR-004 is GREEN only if:

- every contract is abstract or immutable;
- RuntimeEvent field ordering passes Pyright;
- RuntimeModuleManifest contains provides;
- RuntimeContext metadata is JSON-compatible;
- ServiceDescriptor implementation is typed as type[ServiceContract];
- Ruff clean;
- Pyright clean;
- contracts tests pass.

<!-- ========================================================================= -->
<!-- M-06 PART 4 — KR-005 Dependency Injection Runtime -->
<!-- ========================================================================= -->

# KR-005 — Dependency Injection Runtime

## Approved ADR-004 implementation reconciliation

Apply exact APPROVED `../wave1/KR-005_DI.md` instead of the obsolete sync methods,
public properties, descriptor/context Scope API and bare implementation typing
in this section. Five production files and one canonical test file are authorized.
Private iterative graph/build working records and a typed construction callback
track partial initialization before awaiting hooks; they introduce no public
contract, cache owner, Runtime or dependency direction. Ready cached instances
belong only to Scope; transient/pending acquisition records belong to Resolver.
ADR-004 P-01/P-02/P-05 define lifecycle, rollback, removal and cancellation behavior.


**Runtime Layer:** L0 Kernel

Dependency Injection Runtime owns service registration, dependency resolution and scope lifetimes.

It is the **only** runtime allowed to create service instances.

Forbidden:

- business logic;
- filesystem IO;
- HTTP requests;
- event publishing;
- lifecycle transitions.

DI Runtime owns object lifetime only.

---

## DI Architecture

Container Runtime consists of five production files.

| File | Responsibility |
|------|----------------|
| `container.py` | Public DI container API and runtime owner. |
| `registry.py` | Immutable descriptor registry. |
| `resolver.py` | Dependency graph construction and constructor injection. |
| `provider.py` | Service provider abstraction. |
| `scope.py` | Scope lifetime storage and disposal. |

Dependency direction:

```
container
   │
   ├── registry
   ├── resolver
   ├── scope
   └── provider
```

No circular imports.

---

## DI-001 — src/kernel/runtime/container.py

### Owner

KR-005 DI Runtime

### Purpose

Canonical dependency injection container.

### File Blueprint

```
container.py
├── imports
├── ContainerRuntime
├── private helpers
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.core.types import ServiceId
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.service import (
    ServiceContract,
    ServiceDescriptor,
)
from src.kernel.runtime.provider import ProviderRuntime
from src.kernel.runtime.registry import RegistryRuntime
from src.kernel.runtime.resolver import ResolverRuntime
from src.kernel.runtime.scope import ScopeRuntime
```

### Public Class

```python
class ContainerRuntime
```

Container owns:

- registry
- resolver
- provider
- scope runtime

### Constructor

```python
def __init__(self) -> None
```

Creates empty runtime.

No eager services started.

---

### Public API

#### register

```python
def register(
    self,
    descriptor: ServiceDescriptor,
) -> None
```

Registers service descriptor.

Raises duplicate registration error.

---

#### remove

```python
def remove(
    self,
    service_id: ServiceId,
) -> None
```

Removes descriptor and cached instances.

---

#### resolve

```python
def resolve(
    self,
    service_id: ServiceId,
    *,
    context: RuntimeContext | None = None,
) -> ServiceContract
```

Returns service instance respecting DI scope.

Never returns `None`.

---

#### contains

```python
def contains(
    self,
    service_id: ServiceId,
) -> bool
```

---

#### descriptors

```python
def descriptors(self) -> tuple[ServiceDescriptor, ...]
```

Returns immutable descriptor snapshot.

---

#### shutdown

```python
async def shutdown(self) -> None
```

Disposes every active scope.

Calls shutdown on initialized services.

---

### Private Helpers

```python
_create_service(...)
_dispose_service(...)
```

Private only.

---

### Raises

<table><table-row><table-cell width="260">**Exception**</table-cell><table-cell>**Condition**</table-cell></table-row><table-row><table-cell>ServiceRegistrationError</table-cell><table-cell>Duplicate registration.</table-cell></table-row><table-row><table-cell>ServiceResolutionError</table-cell><table-cell>Service missing.</table-cell></table-row><table-row><table-cell>CircularDependencyError</table-cell><table-cell>Dependency cycle detected.</table-cell></table-row><table-row><table-cell>ScopeViolationError</table-cell><table-cell>Invalid scope resolution.</table-cell></table-row></table>

---

### Imported By

- bootstrap runtime
- pipeline runtime

---

### __all__

```python
__all__ = ["ContainerRuntime"]
```

### Validation Rules

- Container owns lifetime.
- Resolver owns graph.
- Registry owns descriptors.

---

## DI-002 — src/kernel/runtime/registry.py

### Owner

KR-005 DI Runtime

### Purpose

Immutable service descriptor registry.

### File Blueprint

```
registry.py
├── imports
├── RegistryRuntime
└── __all__
```

### Public Class

```python
class RegistryRuntime
```

### Public API

#### register

```python
def register(
    self,
    descriptor: ServiceDescriptor,
) -> None
```

---

#### unregister

```python
def unregister(
    self,
    service_id: ServiceId,
) -> None
```

---

#### get

```python
def get(
    self,
    service_id: ServiceId,
) -> ServiceDescriptor
```

---

#### contains

```python
def contains(
    self,
    service_id: ServiceId,
) -> bool
```

---

#### list

```python
def list(self) -> tuple[ServiceDescriptor, ...]
```

### Internal Storage

```python
dict[ServiceId, ServiceDescriptor]
```

Private only.

---

### Raises

- ServiceRegistrationError
- ServiceResolutionError

---

### __all__

```python
__all__ = ["RegistryRuntime"]
```

---

## DI-003 — src/kernel/runtime/resolver.py

### Owner

KR-005 DI Runtime

### Purpose

Dependency graph resolver.

### File Blueprint

```
resolver.py
├── imports
├── ResolverRuntime
└── __all__
```

### Public Class

```python
class ResolverRuntime
```

### Public API

#### resolve

```python
def resolve(
    self,
    descriptor: ServiceDescriptor,
    *,
    context: RuntimeContext | None,
) -> ServiceContract
```

Creates service respecting scope.

---

#### validate

```python
def validate(
    self,
    descriptor: ServiceDescriptor,
) -> None
```

Validates dependency graph before construction.

---

### Private Helpers

#### _collect_dependencies

```python
def _collect_dependencies(
    self,
    implementation: type[ServiceContract],
) -> tuple[ServiceId, ...]
```

---

#### _detect_cycle

```python
def _detect_cycle(
    self,
    root: ServiceId,
) -> None
```

Depth-first dependency validation.

---

### Raises

- CircularDependencyError
- ServiceResolutionError

---

### Validation Rules

- Constructor injection only.
- No property injection.
- No setter injection.

---

### __all__

```python
__all__ = ["ResolverRuntime"]
```

---

## DI-004 — src/kernel/runtime/provider.py

### Owner

KR-005 DI Runtime

### Purpose

Factory abstraction for service creation.

### File Blueprint

```
provider.py
├── imports
├── ProviderRuntime
└── __all__
```

### Public Class

```python
class ProviderRuntime
```

### Public API

#### provide

```python
def provide(
    self,
    descriptor: ServiceDescriptor,
    *,
    context: RuntimeContext | None,
) -> ServiceContract
```

Returns initialized service instance.

---

#### dispose

```python
async def dispose(
    self,
    service: ServiceContract,
) -> None
```

Invokes shutdown contract.

---

### Raises

- ServiceResolutionError

---

### __all__

```python
__all__ = ["ProviderRuntime"]
```

---

## DI-005 — src/kernel/runtime/scope.py

### Owner

KR-005 DI Runtime

### Purpose

Owns scope caches and lifetime disposal.

### File Blueprint

```
scope.py
├── imports
├── ScopeRuntime
└── __all__
```

### Public Class

```python
class ScopeRuntime
```

### Internal Storage

| Scope | Storage |
|-------|---------|
| APPLICATION | `dict[ServiceId, ServiceContract]` |
| SESSION | `dict[SessionId, dict[ServiceId, ServiceContract]]` |
| PIPELINE | `dict[PipelineId, dict[ServiceId, ServiceContract]]` |
| TRANSIENT | no cache |

Storage is private.

---

### Public API

#### get

```python
def get(
    self,
    service_id: ServiceId,
    *,
    context: RuntimeContext | None,
) -> ServiceContract | None
```

---

#### put

```python
def put(
    self,
    service_id: ServiceId,
    service: ServiceContract,
    *,
    context: RuntimeContext | None,
) -> None
```

---

#### remove

```python
def remove(
    self,
    service_id: ServiceId,
    *,
    context: RuntimeContext | None,
) -> None
```

---

#### clear_session

```python
async def clear_session(
    self,
    session_id: SessionId,
) -> None
```

---

#### clear_pipeline

```python
async def clear_pipeline(
    self,
    pipeline_id: PipelineId,
) -> None
```

---

#### clear_application

```python
async def clear_application(self) -> None
```

Disposes every cached Application-scoped service.

---

### Lifetime Rules

<table><table-row><table-cell width="160">**Scope**</table-cell><table-cell>**Lifetime**</table-cell></table-row><table-row><table-cell>APPLICATION</table-cell><table-cell>Created once. Destroyed during runtime shutdown.</table-cell></table-row><table-row><table-cell>SESSION</table-cell><table-cell>Created per session. Destroyed when session ends.</table-cell></table-row><table-row><table-cell>PIPELINE</table-cell><table-cell>Created per pipeline execution. Destroyed after pipeline completion.</table-cell></table-row><table-row><table-cell>TRANSIENT</table-cell><table-cell>Never cached. New instance every resolution.</table-cell></table-row></table>

---

### Raises

- ScopeViolationError

---

### __all__

```python
__all__ = ["ScopeRuntime"]
```

---

# KR-005 Definition of Done

KR-005 is GREEN only if:

- ContainerRuntime owns all scopes.
- RegistryRuntime owns descriptors only.
- ResolverRuntime performs constructor injection only.
- ProviderRuntime creates and disposes services only.
- ScopeRuntime owns cache lifetime only.
- Circular dependency detection works.
- Scope disposal works.
- Ruff clean.
- Pyright clean.
- DI tests pass.

<!-- ========================================================================= -->
<!-- M-06 PART 5 — KR-006 Lifecycle Runtime -->
<!-- ========================================================================= -->

# KR-006 — Lifecycle Runtime

**Runtime Layer:** L0 Kernel

Lifecycle Runtime is the only owner of runtime state transitions.

It coordinates initialization, startup, graceful shutdown and failure transitions for every runtime module.

Lifecycle Runtime **does not** own:

- dependency injection,
- event dispatch,
- configuration,
- logging,
- pipeline execution.

It owns **state transitions only**.

---

# Lifecycle Architecture

Lifecycle Runtime consists of three production files.

| File | Responsibility |
|------|----------------|
| `lifecycle.py` | Lifecycle manager and transition coordinator. |
| `state.py` | Runtime state machine and transition validation. |
| `hooks.py` | Lifecycle hook registry and execution. |

Dependency graph:

```
lifecycle
├── state
└── hooks
```

No circular imports.

---

## LIFECYCLE-001 — src/kernel/runtime/lifecycle.py

### Owner

KR-006 Lifecycle Runtime

### Purpose

Coordinates lifecycle transitions for RuntimeContract implementations.

---

### File Blueprint

```
lifecycle.py
├── imports
├── LifecycleRuntime
├── private helpers
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from src.core.types import RuntimeStatus
from src.kernel.contracts.lifecycle import (
    LifecycleContract,
    LifecycleState,
)
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.hooks import HookRuntime
from src.kernel.runtime.state import StateRuntime
```

---

### Public Class

```python
class LifecycleRuntime(LifecycleContract)
```

Owns:

- runtime state machine,
- hook runtime,
- registered runtime modules.

---

### Constructor

```python
def __init__(self) -> None
```

Creates empty lifecycle manager.

No runtime initialized.

---

### Public API

#### register

```python
def register(
    self,
    runtime: RuntimeContract,
) -> None
```

Registers runtime participant.

Order of registration defines startup/shutdown order.

---

#### initialize

```python
async def initialize(self) -> None
```

Sequence:

1. BEFORE_INITIALIZE hooks.
2. Initialize registered runtimes.
3. AFTER_INITIALIZE hooks.
4. Transition to READY.

---

#### start

```python
async def start(self) -> None
```

Sequence:

1. BEFORE_START hooks.
2. Start runtimes.
3. AFTER_START hooks.
4. Transition to RUNNING.

---

#### stop

```python
async def stop(self) -> None
```

Sequence:

1. BEFORE_STOP hooks.
2. Stop runtimes in reverse registration order.
3. AFTER_STOP hooks.
4. Transition to STOPPED.

---

#### shutdown

```python
async def shutdown(self) -> None
```

Calls runtime shutdown in reverse order.

State remains STOPPED.

---

#### transition

```python
async def transition(
    self,
    target: RuntimeStatus,
) -> None
```

Delegates validation to StateRuntime.

---

#### state

```python
def state(self) -> LifecycleState
```

Returns immutable snapshot.

---

### Private Helpers

```python
_run_initialize()

_run_start()

_run_stop()

_run_shutdown()
```

Private only.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeInitializationError | Runtime initialization failed. |
| RuntimeShutdownError | Shutdown failed. |
| RuntimeStateError | Illegal transition attempted. |

---

### Imported By

- bootstrap runtime.

---

### __all__

```python
__all__ = ["LifecycleRuntime"]
```

---

### Validation Rules

- Reverse shutdown order.
- No direct state mutation.
- StateRuntime validates every transition.

---

## LIFECYCLE-002 — src/kernel/runtime/state.py

### Owner

KR-006 Lifecycle Runtime

### Purpose

Canonical runtime state machine.

---

### File Blueprint

```
state.py
├── imports
├── StateRuntime
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from src.core.types import RuntimeStatus
from src.kernel.contracts.lifecycle import LifecycleState
```

---

### Public Class

```python
class StateRuntime
```

Owns current lifecycle state only.

---

### Internal State

Private fields:

| Field | Type |
|-------|------|
| `_current` | RuntimeStatus |
| `_previous` | RuntimeStatus \| None |

No public mutation.

---

### Public API

#### current

```python
def current(self) -> RuntimeStatus
```

---

#### previous

```python
def previous(self) -> RuntimeStatus | None
```

---

#### snapshot

```python
def snapshot(self) -> LifecycleState
```

Immutable dataclass snapshot.

---

#### transition

```python
def transition(
    self,
    target: RuntimeStatus,
) -> LifecycleState
```

Validates transition.

Updates previous/current.

Returns snapshot.

---

#### can_transition

```python
def can_transition(
    self,
    target: RuntimeStatus,
) -> bool
```

Validation only.

---

### Canonical Transition Matrix

| From | Allowed To |
|------|------------|
| CREATED | INITIALIZING |
| INITIALIZING | READY |
| INITIALIZING | FAILED |
| READY | RUNNING |
| RUNNING | STOPPED |
| RUNNING | FAILED |
| FAILED | STOPPED |
| STOPPED | *(terminal state)* |

Every other transition raises RuntimeStateError.

---

### Forbidden Transitions

Examples:

- CREATED → RUNNING
- READY → CREATED
- FAILED → RUNNING
- STOPPED → RUNNING

No restart inside Wave 1.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeStateError | Illegal transition. |

---

### __all__

```python
__all__ = ["StateRuntime"]
```

---

### Validation Rules

- Transition matrix immutable.
- Snapshot immutable.
- No lifecycle hooks.

---

## LIFECYCLE-003 — src/kernel/runtime/hooks.py

### Owner

KR-006 Lifecycle Runtime

### Purpose

Lifecycle hook registry.

---

### File Blueprint

```
hooks.py
├── imports
├── LifecycleHook
├── HookRuntime
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from collections.abc import Awaitable, Callable
from enum import StrEnum
```

---

### Public Enum

```python
class LifecycleHook(StrEnum)
```

Vocabulary is frozen.

Values:

| Hook |
|------|
| BEFORE_INITIALIZE |
| AFTER_INITIALIZE |
| BEFORE_START |
| AFTER_START |
| BEFORE_STOP |
| AFTER_STOP |

---

### Public Class

```python
class HookRuntime
```

Owns hook registration only.

---

### Internal Storage

```python
dict[
    LifecycleHook,
    list[Callable[[], Awaitable[None]]],
]
```

Private only.

---

### Public API

#### register

```python
def register(
    self,
    hook: LifecycleHook,
    callback: Callable[[], Awaitable[None]],
) -> None
```

---

#### unregister

```python
def unregister(
    self,
    hook: LifecycleHook,
    callback: Callable[[], Awaitable[None]],
) -> None
```

---

#### execute

```python
async def execute(
    self,
    hook: LifecycleHook,
) -> None
```

Executes callbacks in registration order.

---

#### clear

```python
def clear(self) -> None
```

Removes all callbacks.

---

### Hook Execution Rules

- Registration order preserved.
- Await callbacks sequentially.
- Exception aborts lifecycle transition.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeInitializationError | Hook failed during initialize. |
| RuntimeShutdownError | Hook failed during shutdown. |

---

### __all__

```python
__all__ = [
    "LifecycleHook",
    "HookRuntime",
]
```

---

### Validation Rules

- No duplicate callback execution.
- No background execution.
- No threading.

---

# KR-006 Runtime Guarantees

## Startup Order

```
CREATED
      │
      ▼
INITIALIZING
      │
      ▼
READY
      │
      ▼
RUNNING
```

---

## Failure Path

```
INITIALIZING
      │
      ▼
FAILED
      │
      ▼
STOPPED
```

```
RUNNING
      │
      ▼
FAILED
      │
      ▼
STOPPED
```

---

## Shutdown Order

Registered runtimes stop in reverse registration order.

Example:

```
Register:

Config
Logger
Container
EventBus
Pipeline

Shutdown:

Pipeline
EventBus
Container
Logger
Config
```

---

# KR-006 Definition of Done

KR-006 is GREEN only if:

- LifecycleRuntime coordinates transitions.
- StateRuntime validates every transition.
- HookRuntime executes hooks in deterministic order.
- Illegal transitions raise RuntimeStateError.
- Shutdown executes in reverse registration order.
- Ruff clean.
- Pyright clean.
- Lifecycle tests pass.

<!-- ========================================================================= -->
<!-- M-06 PART 6 — KR-007 Event Bus Runtime -->
<!-- ========================================================================= -->

# KR-007 — Event Bus Runtime

**Runtime Layer:** L0 Kernel

Event Bus Runtime is the only owner of runtime event publication and dispatch.

It is responsible for:

- publishing runtime events;
- subscriber registration;
- dispatch ordering;
- synchronous and asynchronous dispatch;
- event routing.

It never owns:

- lifecycle;
- DI container;
- configuration;
- pipeline execution.

---

# Event Bus Architecture

Event Runtime consists of five production files.

| File | Responsibility |
|------|----------------|
| `bus.py` | Public Event Bus API. |
| `dispatcher.py` | Dispatch engine. |
| `publisher.py` | Event publication entrypoint. |
| `subscriber.py` | Subscriber registry. |
| `event.py` | Event factory and validation helpers. |

Dependency graph:

```
bus
├── dispatcher
├── publisher
├── subscriber
└── event
```

No circular imports.

---

## EVENT-001 — src/kernel/runtime/event.py

### Owner

KR-007 Event Runtime

### Purpose

Canonical RuntimeEvent construction and validation.

---

### File Blueprint

```
event.py
├── imports
├── EventRuntime
└── __all__
```

### Imports

```python
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from src.core.types import EventId
from src.kernel.contracts.context import TraceContext
from src.kernel.contracts.events import RuntimeEvent
```

---

### Public Class

```python
class EventRuntime
```

Stateless helper.

---

### Public API

#### create

```python
def create(
    self,
    *,
    event_type: str,
    session_id: SessionId,
    trace: TraceContext,
    payload: Payload | None = None,
) -> RuntimeEvent
```

Responsibilities:

- generate EventId,
- generate UTC timestamp,
- normalize payload,
- validate required fields.

---

#### validate

```python
def validate(
    self,
    event: RuntimeEvent,
) -> None
```

Validation only.

---

### Validation Rules

Required fields:

- event_id
- event_type
- session_id
- trace
- timestamp
- payload

Timestamp must be UTC.

Payload must be JSON-compatible.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| InvalidEventError | Required field missing. |
| EventValidationError | Invalid payload. |

---

### __all__

```python
__all__ = ["EventRuntime"]
```

---

## EVENT-002 — src/kernel/runtime/subscriber.py

### Owner

KR-007 Event Runtime

### Purpose

Subscriber registry.

---

### File Blueprint

```
subscriber.py
├── imports
├── SubscriberRuntime
└── __all__
```

### Imports

```python
from __future__ import annotations

from collections.abc import Awaitable, Callable

from src.kernel.contracts.events import (
    EventHandlerContract,
    RuntimeEvent,
)
```

---

### Public Class

```python
class SubscriberRuntime
```

Owns subscriber registration.

---

### Internal Storage

```python
dict[
    str,
    list[EventHandlerContract],
]
```

Key = event_type.

Private only.

---

### Public API

#### subscribe

```python
def subscribe(
    self,
    event_type: str,
    handler: EventHandlerContract,
) -> None
```

---

#### unsubscribe

```python
def unsubscribe(
    self,
    event_type: str,
    handler: EventHandlerContract,
) -> None
```

---

#### handlers

```python
def handlers(
    self,
    event_type: str,
) -> tuple[EventHandlerContract, ...]
```

Returns immutable handler snapshot.

---

#### contains

```python
def contains(
    self,
    event_type: str,
) -> bool
```

---

#### clear

```python
def clear(self) -> None
```

Removes all subscribers.

---

### Registration Rules

- duplicate handler forbidden.
- insertion order preserved.
- event_type is case-sensitive.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| EventHandlerError | Duplicate handler registration. |

---

### __all__

```python
__all__ = ["SubscriberRuntime"]
```

---

## EVENT-003 — src/kernel/runtime/publisher.py

### Owner

KR-007 Event Runtime

### Purpose

Public event publication API.

---

### File Blueprint

```
publisher.py
├── imports
├── PublisherRuntime
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.kernel.contracts.events import RuntimeEvent
from src.kernel.runtime.dispatcher import DispatcherRuntime
```

---

### Public Class

```python
class PublisherRuntime
```

Owns publication only.

---

### Public API

#### publish

```python
async def publish(
    self,
    event: RuntimeEvent,
) -> None
```

Publishes validated event.

---

#### publish_many

```python
async def publish_many(
    self,
    events: tuple[RuntimeEvent, ...],
) -> None
```

Sequential publication.

---

### Publication Rules

- validate event before dispatch;
- preserve publication order;
- never bypass dispatcher.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| EventPublishError | Publication failed. |
| InvalidEventError | Event invalid. |

---

### __all__

```python
__all__ = ["PublisherRuntime"]
```

---

## EVENT-004 — src/kernel/runtime/dispatcher.py

### Owner

KR-007 Event Runtime

### Purpose

Dispatch runtime events to subscribers.

---

### File Blueprint

```
dispatcher.py
├── imports
├── DispatcherRuntime
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.core.types import EventPriority
from src.kernel.contracts.events import RuntimeEvent
from src.kernel.runtime.subscriber import SubscriberRuntime
```

---

### Public Class

```python
class DispatcherRuntime
```

Owns dispatch execution.

---

### Public API

#### dispatch

```python
async def dispatch(
    self,
    event: RuntimeEvent,
) -> None
```

Dispatches to subscribers.

---

#### dispatch_many

```python
async def dispatch_many(
    self,
    events: tuple[RuntimeEvent, ...],
) -> None
```

Sequential dispatch.

---

### Private Helpers

#### _ordered_handlers

```python
def _ordered_handlers(
    self,
    event: RuntimeEvent,
) -> tuple[EventHandlerContract, ...]
```

Returns handlers ordered by priority.

---

### Dispatch Rules

Handlers execute:

1. HIGH
2. NORMAL
3. LOW

Handlers of equal priority preserve registration order.

Dispatch waits (`await`) every handler sequentially.

No background execution.

---

### Failure Rules

- first handler exception stops dispatch;
- remaining handlers do not execute;
- exception propagates.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| EventHandlerError | Subscriber failed. |

---

### __all__

```python
__all__ = ["DispatcherRuntime"]
```

---

## EVENT-005 — src/kernel/runtime/bus.py

### Owner

KR-007 Event Runtime

### Purpose

Canonical Event Bus facade.

---

### File Blueprint

```
bus.py
├── imports
├── EventBusRuntime
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.kernel.contracts.events import (
    EventHandlerContract,
    RuntimeEvent,
)
from src.kernel.runtime.dispatcher import DispatcherRuntime
from src.kernel.runtime.publisher import PublisherRuntime
from src.kernel.runtime.subscriber import SubscriberRuntime
```

---

### Public Class

```python
class EventBusRuntime
```

Owns:

- subscriber runtime,
- dispatcher runtime,
- publisher runtime.

---

### Constructor

```python
def __init__(self) -> None
```

Creates empty event bus.

---

### Public API

#### subscribe

```python
def subscribe(
    self,
    event_type: str,
    handler: EventHandlerContract,
) -> None
```

---

#### unsubscribe

```python
def unsubscribe(
    self,
    event_type: str,
    handler: EventHandlerContract,
) -> None
```

---

#### publish

```python
async def publish(
    self,
    event: RuntimeEvent,
) -> None
```

Delegates to PublisherRuntime.

---

#### publish_many

```python
async def publish_many(
    self,
    events: tuple[RuntimeEvent, ...],
) -> None
```

---

#### contains

```python
def contains(
    self,
    event_type: str,
) -> bool
```

---

#### clear

```python
def clear(self) -> None
```

Removes every subscriber.

---

### Event Bus Rules

- publish always validates RuntimeEvent;
- publish always dispatches through DispatcherRuntime;
- subscribers are immutable during active dispatch.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| InvalidEventError | Invalid RuntimeEvent. |
| EventPublishError | Publication failed. |
| EventHandlerError | Handler execution failed. |

---

### __all__

```python
__all__ = ["EventBusRuntime"]
```

---

# Event Dispatch Flow

## Publication Pipeline

```
RuntimeEvent
      │
      ▼
PublisherRuntime
      │
      ▼
DispatcherRuntime
      │
      ▼
SubscriberRuntime
      │
      ▼
EventHandlerContract.handle()
```

Every event follows this pipeline.

---

## Subscriber Execution Order

```
Priority HIGH
      │
Priority NORMAL
      │
Priority LOW
```

Registration order preserved within same priority.

---

## Event Validation Pipeline

```
create()
      │
validate()
      │
publish()
      │
dispatch()
```

Validation always happens before publication.

---

# KR-007 Definition of Done

KR-007 is GREEN only if:

- EventRuntime creates canonical RuntimeEvent objects.
- SubscriberRuntime manages immutable subscriptions.
- PublisherRuntime publishes validated events only.
- DispatcherRuntime dispatches sequentially by priority.
- EventBusRuntime is the only public Event Bus API.
- Ruff clean.
- Pyright clean.
- Event tests pass.

<!-- ========================================================================= -->
<!-- M-06 PART 7 — KR-008 Runtime Context Runtime -->
<!-- ========================================================================= -->

# KR-008 — Runtime Context Runtime

**Runtime Layer:** L0 Kernel

Runtime Context Runtime owns execution context propagation.

It is responsible for:

- current RuntimeContext ownership;
- session context lifecycle;
- metadata storage and updates;
- trace propagation.

It never owns:

- dependency injection;
- lifecycle transitions;
- event dispatch;
- pipeline execution.

RuntimeContext is immutable. Runtime Context Runtime manages immutable snapshots.

---

# Runtime Context Architecture

Runtime Context Runtime consists of three production files.

| File | Responsibility |
|------|----------------|
| `context.py` | Runtime context manager. |
| `metadata.py` | Metadata manipulation utilities. |
| `session.py` | Session lifecycle manager. |

Dependency graph:

```
context
├── metadata
└── session
```

No circular imports.

---

## CONTEXT-001 — src/kernel/runtime/context.py

### Owner

KR-008 Runtime Context Runtime

### Purpose

Canonical RuntimeContext manager.

### File Blueprint

```
context.py
├── imports
├── ContextRuntime
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.core.types import Metadata
from src.kernel.contracts.context import RuntimeContext
from src.kernel.runtime.metadata import MetadataRuntime
```

### Public Class

```python
class ContextRuntime
```

Owns current RuntimeContext snapshot.

### Internal State

Private field:

```python
_context: RuntimeContext | None
```

Never exported.

---

### Public API

#### create

```python
def create(
    self,
    *,
    session_id: SessionId,
    pipeline_id: PipelineId,
    trace: TraceContext,
    metadata: Metadata | None = None,
) -> RuntimeContext
```

Creates immutable RuntimeContext.

---

#### current

```python
def current(self) -> RuntimeContext
```

Returns active RuntimeContext.

---

#### replace

```python
def replace(
    self,
    context: RuntimeContext,
) -> None
```

Replaces active RuntimeContext snapshot.

---

#### clear

```python
def clear(self) -> None
```

Removes current RuntimeContext.

---

#### has_context

```python
def has_context(self) -> bool
```

Returns whether runtime context exists.

---

### Runtime Context Rules

- RuntimeContext immutable.
- ContextRuntime owns mutable reference only.
- Replacement produces a new immutable snapshot.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeStateError | Current context missing. |

---

### Imported By

- Container Runtime.
- Pipeline Runtime.
- Event Runtime.
- Bootstrap Runtime.

---

### __all__

```python
__all__ = ["ContextRuntime"]
```

### Validation Rules

- Never mutate RuntimeContext fields.
- No global context object.
- Snapshot replacement only.

---

## CONTEXT-002 — src/kernel/runtime/metadata.py

### Owner

KR-008 Runtime Context Runtime

### Purpose

Metadata manipulation runtime.

### File Blueprint

```
metadata.py
├── imports
├── MetadataRuntime
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.core.types import JSONValue, Metadata
```

### Public Class

```python
class MetadataRuntime
```

Stateless metadata utility.

---

### Public API

#### merge

```python
def merge(
    self,
    base: Metadata,
    update: Metadata,
) -> Metadata
```

Returns new metadata dictionary.

---

#### put

```python
def put(
    self,
    metadata: Metadata,
    *,
    key: str,
    value: JSONValue,
) -> Metadata
```

Returns new metadata snapshot.

---

#### remove

```python
def remove(
    self,
    metadata: Metadata,
    *,
    key: str,
) -> Metadata
```

Returns new metadata snapshot.

---

#### contains

```python
def contains(
    self,
    metadata: Metadata,
    *,
    key: str,
) -> bool
```

---

#### get

```python
def get(
    self,
    metadata: Metadata,
    *,
    key: str,
    default: JSONValue | None = None,
) -> JSONValue | None
```

---

### Metadata Rules

- Metadata immutable.
- No in-place mutation.
- JSON-compatible values only.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| ValidationError | Invalid metadata value. |

---

### __all__

```python
__all__ = ["MetadataRuntime"]
```

### Validation Rules

- No mutable defaults.
- No nested Any.
- Preserve JSON compatibility.

---

## CONTEXT-003 — src/kernel/runtime/session.py

### Owner

KR-008 Runtime Context Runtime

### Purpose

Session lifecycle manager.

### File Blueprint

```
session.py
├── imports
├── SessionRuntime
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.core.types import Metadata, SessionId
from src.kernel.contracts.context import RuntimeContext
from src.kernel.runtime.context import ContextRuntime
```

### Public Class

```python
class SessionRuntime
```

Owns session context lifecycle.

### Internal Storage

```python
dict[SessionId, RuntimeContext]
```

Private only.

---

### Public API

#### create

```python
def create(
    self,
    *,
    session_id: SessionId,
    trace: TraceContext,
    metadata: Metadata | None = None,
) -> RuntimeContext
```

Creates session RuntimeContext.

---

#### get

```python
def get(
    self,
    session_id: SessionId,
) -> RuntimeContext
```

Returns immutable RuntimeContext.

---

#### update_metadata

```python
def update_metadata(
    self,
    session_id: SessionId,
    metadata: Metadata,
) -> RuntimeContext
```

Returns new immutable RuntimeContext snapshot.

---

#### remove

```python
def remove(
    self,
    session_id: SessionId,
) -> None
```

Destroys session context.

---

#### contains

```python
def contains(
    self,
    session_id: SessionId,
) -> bool
```

---

#### list

```python
def list(self) -> tuple[SessionId, ...]
```

Returns immutable snapshot of active sessions.

---

### Session Rules

- SessionRuntime owns session storage.
- RuntimeContext immutable.
- Metadata updates replace snapshot.
- Session removal disposes context.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeStateError | Session missing. |

---

### __all__

```python
__all__ = ["SessionRuntime"]
```

### Validation Rules

- No mutable RuntimeContext.
- Session ownership only.
- Snapshot replacement only.

---

# Runtime Context Ownership Matrix

| Object | Owner |
|--------|-------|
| RuntimeContext | ContextRuntime |
| Metadata | MetadataRuntime |
| Session RuntimeContext | SessionRuntime |
| TraceContext | RuntimeContext |
| Session metadata updates | MetadataRuntime |

No object has multiple owners.

---

# Runtime Context Flow

## Context Creation

```
SessionRuntime
      │
      ▼
ContextRuntime.create()
      │
      ▼
RuntimeContext
```

---

## Metadata Update

```
RuntimeContext
      │
      ▼
MetadataRuntime.put()
      │
      ▼
New Metadata
      │
      ▼
New RuntimeContext Snapshot
```

No mutation occurs.

---

## Session Removal

```
SessionRuntime.remove()
      │
      ▼
Context removed
      │
      ▼
Metadata released
```

---

# KR-008 Definition of Done

KR-008 is GREEN only if:

- ContextRuntime owns RuntimeContext snapshots.
- MetadataRuntime performs immutable metadata operations.
- SessionRuntime owns session lifecycle.
- RuntimeContext is never mutated.
- Metadata remains JSON-compatible.
- Ruff clean.
- Pyright clean.
- Runtime Context tests pass.

<!-- ========================================================================= -->
<!-- M-06 PART 8 — KR-009 Pipeline Runtime -->
<!-- ========================================================================= -->

# KR-009 — Pipeline Runtime

**Runtime Layer:** L0 Kernel

Pipeline Runtime owns execution of module pipelines.

It is responsible for:

- pipeline definitions;
- DAG validation;
- stage execution;
- module orchestration;
- execution context creation.

It never owns:

- DI container internals;
- lifecycle transitions;
- logging configuration;
- event bus implementation.

Pipeline Runtime coordinates already-initialized runtimes.

---

# Pipeline Architecture

Pipeline Runtime consists of four production files.

| File | Responsibility |
|------|----------------|
| `pipeline.py` | Pipeline model and stage definitions. |
| `manifest.py` | Pipeline manifest validation. |
| `executor.py` | Runtime stage executor. |
| `orchestrator.py` | Pipeline orchestration runtime. |

Dependency graph:

```
orchestrator
├── manifest
├── executor
└── pipeline
```

No circular imports.

---

## PIPELINE-001 — src/kernel/runtime/pipeline.py

### Owner

KR-009 Pipeline Runtime

### Purpose

Canonical pipeline definition.

---

### File Blueprint

```
pipeline.py
├── imports
├── PipelineStage
├── PipelineDefinition
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from dataclasses import dataclass, field

from src.core.types import ModuleId, PipelineId
```

No runtime imports.

---

### Public Dataclass

#### PipelineStage

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class PipelineStage
```

Fields:

| Field | Type |
|-------|------|
| stage_id | str |
| module_id | ModuleId |
| depends_on | tuple[str, ...] |

Rules:

- immutable;
- stage_id unique within pipeline;
- depends_on references stage_id only.

---

### Public Dataclass

#### PipelineDefinition

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class PipelineDefinition
```

Fields:

| Field | Type |
|-------|------|
| pipeline_id | PipelineId |
| stages | tuple[PipelineStage, ...] |

Rules:

- immutable;
- stage order preserved;
- stages cannot be empty.

---

### Pipeline Rules

- Directed acyclic graph.
- Duplicate stage IDs forbidden.
- Self-dependency forbidden.
- Dependency references existing stage only.

---

### __all__

```python
__all__ = [
    "PipelineDefinition",
    "PipelineStage",
]
```

---

### Imported By

- manifest.py
- executor.py
- orchestrator.py

---

### Validation Rules

- Immutable dataclasses.
- No execution logic.
- No mutable collections.

---

## PIPELINE-002 — src/kernel/runtime/manifest.py

### Owner

KR-009 Pipeline Runtime

### Purpose

Pipeline manifest validation.

---

### File Blueprint

```
manifest.py
├── imports
├── ManifestRuntime
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from src.kernel.runtime.pipeline import (
    PipelineDefinition,
    PipelineStage,
)
```

---

### Public Class

```python
class ManifestRuntime
```

Stateless validator.

---

### Public API

#### validate

```python
def validate(
    self,
    pipeline: PipelineDefinition,
) -> None
```

Runs every validation step.

---

#### validate_stage_ids

```python
def validate_stage_ids(
    self,
    pipeline: PipelineDefinition,
) -> None
```

Ensures uniqueness.

---

#### validate_dependencies

```python
def validate_dependencies(
    self,
    pipeline: PipelineDefinition,
) -> None
```

Ensures referenced stages exist.

---

#### validate_dag

```python
def validate_dag(
    self,
    pipeline: PipelineDefinition,
) -> None
```

Detects cycles.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| InvalidManifestError | Manifest invalid. |
| RuntimeDependencyError | Cycle detected. |

---

### __all__

```python
__all__ = ["ManifestRuntime"]
```

---

### Validation Rules

- No pipeline execution.
- Validation only.

---

## PIPELINE-003 — src/kernel/runtime/executor.py

### Owner

KR-009 Pipeline Runtime

### Purpose

Execute validated pipeline stages.

---

### File Blueprint

```
executor.py
├── imports
├── ExecutorRuntime
├── private helpers
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from src.kernel.contracts.context import RuntimeContext
from src.kernel.runtime.event_bus import EventBusRuntime
from src.kernel.runtime.pipeline import (
    PipelineDefinition,
    PipelineStage,
)
```

---

### Public Class

```python
class ExecutorRuntime
```

Owns execution flow only.

---

### Public API

#### execute

```python
async def execute(
    self,
    pipeline: PipelineDefinition,
    *,
    context: RuntimeContext,
) -> None
```

Executes complete pipeline.

---

#### execute_stage

```python
async def execute_stage(
    self,
    stage: PipelineStage,
    *,
    context: RuntimeContext,
) -> None
```

Executes one stage.

---

### Private Helpers

#### _execution_order

```python
def _execution_order(
    self,
    pipeline: PipelineDefinition,
) -> tuple[PipelineStage, ...]
```

Returns topological order.

---

#### _publish_stage_event

```python
async def _publish_stage_event(...)
```

Publishes lifecycle events.

Private only.

---

### Execution Rules

Execution order:

1. topological sort;
2. dependency completion required;
3. one stage at a time.

Wave 1 execution is sequential.

---

### Failure Rules

- First stage failure aborts pipeline.
- Remaining stages skipped.
- Failure event published.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeError | Stage execution failed. |

---

### __all__

```python
__all__ = ["ExecutorRuntime"]
```

---

### Validation Rules

- Sequential execution.
- Context immutable.
- No DAG mutation.

---

## PIPELINE-004 — src/kernel/runtime/orchestrator.py

### Owner

KR-009 Pipeline Runtime

### Purpose

Coordinates runtime modules and pipeline execution.

---

### File Blueprint

```
orchestrator.py
├── imports
├── OrchestratorRuntime
└── __all__
```

---

### Imports

```python
from __future__ import annotations

from src.kernel.contracts.module import RuntimeModuleManifest
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.executor import ExecutorRuntime
from src.kernel.runtime.manifest import ManifestRuntime
from src.kernel.runtime.pipeline import PipelineDefinition
```

---

### Public Class

```python
class OrchestratorRuntime
```

Owns:

- module manifests,
- executor,
- manifest validator.

---

### Internal Storage

```python
dict[ModuleId, RuntimeModuleManifest]
```

Private only.

---

### Public API

#### register_module

```python
def register_module(
    self,
    manifest: RuntimeModuleManifest,
) -> None
```

Registers runtime module.

---

#### unregister_module

```python
def unregister_module(
    self,
    module_id: ModuleId,
) -> None
```

---

#### modules

```python
def modules(
    self,
) -> tuple[RuntimeModuleManifest, ...]
```

Returns immutable snapshot.

---

#### execute

```python
async def execute(
    self,
    pipeline: PipelineDefinition,
    *,
    context: RuntimeContext,
) -> None
```

Validation then execution.

---

### Orchestration Rules

Execution flow:

1. validate manifest;
2. validate pipeline;
3. create execution order;
4. execute pipeline;
5. publish completion event.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| InvalidManifestError | Module invalid. |
| RuntimeDependencyError | Dependency graph invalid. |
| RuntimeError | Pipeline execution failed. |

---

### __all__

```python
__all__ = ["OrchestratorRuntime"]
```

---

### Validation Rules

- No DI logic.
- No lifecycle logic.
- Pipeline owner only.

---

# Pipeline DAG Rules

## Valid DAG

```
Stage A
   │
   ▼
Stage B
   │
   ▼
Stage C
```

---

## Branching DAG

```
      Stage A
      /     \
     ▼       ▼
Stage B   Stage C
      \     /
       ▼   ▼
      Stage D
```

Allowed.

---

## Invalid DAG

```
A → B → C
↑       │
└───────┘
```

Cycle forbidden.

---

# Execution State Machine

| State | Meaning |
|-------|---------|
| CREATED | Pipeline exists. |
| VALIDATED | Manifest validated. |
| RUNNING | Stage execution started. |
| COMPLETED | Pipeline finished successfully. |
| FAILED | Pipeline aborted. |

Pipeline state belongs to ExecutorRuntime.

---

# Pipeline Event Sequence

During execution:

```
PIPELINE_STARTED

STAGE_STARTED

STAGE_COMPLETED

...

PIPELINE_COMPLETED
```

Failure sequence:

```
PIPELINE_STARTED

STAGE_STARTED

STAGE_FAILED

PIPELINE_FAILED
```

Event types are frozen.

---

# KR-009 Definition of Done

KR-009 is GREEN only if:

- PipelineDefinition is immutable.
- ManifestRuntime validates DAG and dependencies.
- ExecutorRuntime executes sequentially in topological order.
- OrchestratorRuntime validates before execution.
- Pipeline events follow canonical sequence.
- Ruff clean.
- Pyright clean.
- Pipeline tests pass.

<!-- ========================================================================= -->
<!-- M-06 PART 9 — KR-010 Bootstrap Runtime -->
<!-- ========================================================================= -->

# KR-010 — Bootstrap Runtime

**Runtime Layer:** L0 Kernel

Bootstrap Runtime is the only owner of application startup and shutdown.

It wires together every completed Kernel Runtime (KR-001 → KR-009) into one executable runtime.

Bootstrap Runtime **never** implements business logic.

---

# Bootstrap Architecture

Bootstrap Runtime consists of three production files.

| File | Responsibility |
|------|----------------|
| `bootstrap.py` | Runtime assembly and dependency wiring. |
| `runtime.py` | High-level Runtime facade. |
| `main.py` | Process entrypoint. |

Dependency graph:

```
main
 │
 ▼
runtime
 │
 ▼
bootstrap
 │
 ├── ContainerRuntime
 ├── LifecycleRuntime
 ├── EventBusRuntime
 ├── ContextRuntime
 └── OrchestratorRuntime
```

No circular imports.

---

## BOOTSTRAP-001 — src/kernel/runtime/bootstrap.py

### Owner

KR-010 Bootstrap Runtime

### Purpose

Construct every runtime subsystem in canonical order.

### File Blueprint

```
bootstrap.py
├── imports
├── BootstrapRuntime
├── private builders
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.core.config import get_settings
from src.core.logger import configure_logging
from src.core.logging_config import LoggingConfig

from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
```

### Public Class

```python
class BootstrapRuntime
```

Owns runtime assembly only.

### Public API

#### build

```python
async def build(self) -> RuntimeKernel
```

Creates every runtime subsystem.

Sequence:

1. Settings.
2. Logging.
3. Context.
4. Container.
5. EventBus.
6. Orchestrator.
7. Lifecycle.
8. RuntimeKernel.

Returns initialized RuntimeKernel.

---

### Private Builders

```python
_build_logging()

_build_context()

_build_container()

_build_event_bus()

_build_orchestrator()

_build_lifecycle()
```

Private only.

---

### Bootstrap Order

```
Settings
   │
Logging
   │
Context
   │
Container
   │
EventBus
   │
Orchestrator
   │
Lifecycle
   │
RuntimeKernel
```

Order is frozen.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeInitializationError | Bootstrap failed. |
| ConfigurationError | Invalid configuration. |

---

### __all__

```python
__all__ = ["BootstrapRuntime"]
```

---

## BOOTSTRAP-002 — src/kernel/runtime/runtime.py

### Owner

KR-010 Bootstrap Runtime

### Purpose

Public runtime facade.

### File Blueprint

```
runtime.py
├── imports
├── RuntimeKernel
└── __all__
```

### Imports

```python
from __future__ import annotations

from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
```

### Public Class

```python
class RuntimeKernel
```

### Owned Runtimes

| Property | Type |
|----------|------|
| container | ContainerRuntime |
| lifecycle | LifecycleRuntime |
| event_bus | EventBusRuntime |
| context | ContextRuntime |
| orchestrator | OrchestratorRuntime |

Immutable references.

---

### Public API

#### initialize

```python
async def initialize(self) -> None
```

Delegates to LifecycleRuntime.initialize.

---

#### start

```python
async def start(self) -> None
```

Delegates to LifecycleRuntime.start.

---

#### stop

```python
async def stop(self) -> None
```

Delegates to LifecycleRuntime.stop.

---

#### shutdown

```python
async def shutdown(self) -> None
```

Delegates to LifecycleRuntime.shutdown.

---

#### health

```python
def health(self) -> HealthStatus
```

Aggregates runtime health.

---

### Health Aggregation Rules

- Every runtime healthy → HEALTHY.
- Any degraded runtime → DEGRADED.
- Any failed runtime → FAILED.

---

### Raises

| Exception | Condition |
|-----------|-----------|
| RuntimeInitializationError | Runtime initialization failed. |
| RuntimeShutdownError | Runtime shutdown failed. |

---

### __all__

```python
__all__ = ["RuntimeKernel"]
```

---

## BOOTSTRAP-003 — src/main.py

### Owner

KR-010 Bootstrap Runtime

### Purpose

Application process entrypoint.

### File Blueprint

```
main.py
├── imports
├── main()
└── __main__
```

### Imports

```python
from __future__ import annotations

import asyncio

from src.kernel.runtime.bootstrap import BootstrapRuntime
```

No runtime imports besides BootstrapRuntime.

---

### Public Function

#### main

```python
async def main() -> None
```

Sequence:

1. BootstrapRuntime.build().
2. RuntimeKernel.initialize().
3. RuntimeKernel.start().
4. Wait for shutdown signal.
5. RuntimeKernel.stop().
6. RuntimeKernel.shutdown().

---

### Process Entry

```python
if __name__ == "__main__":
    asyncio.run(main())
```

Exactly one process entrypoint.

---

### Shutdown Guarantees

Shutdown sequence is always executed inside `finally`.

Graceful shutdown is mandatory.

---

### Raises

Never propagates uncaught runtime exceptions outside `asyncio.run`.

---

### Validation Rules

- No business logic.
- No print().
- No environment loading.
- No service registration.

---

# Canonical Startup Sequence

```
Process Start
      │
      ▼
BootstrapRuntime.build()
      │
      ▼
RuntimeKernel.initialize()
      │
      ▼
Lifecycle.initialize()
      │
      ▼
Runtime READY
      │
      ▼
RuntimeKernel.start()
      │
      ▼
RUNNING
```

---

# Canonical Shutdown Sequence

```
Shutdown Signal
      │
      ▼
RuntimeKernel.stop()
      │
      ▼
Lifecycle.stop()
      │
      ▼
RuntimeKernel.shutdown()
      │
      ▼
Container shutdown
      │
      ▼
STOPPED
```

Reverse runtime shutdown order is mandatory.

---

# Runtime Ownership Matrix

| Runtime | Owner KR |
|---------|----------|
| Settings | KR-002 |
| Logger | KR-003 |
| Contracts | KR-004 |
| Container | KR-005 |
| Lifecycle | KR-006 |
| EventBus | KR-007 |
| Context | KR-008 |
| Pipeline | KR-009 |
| Bootstrap | KR-010 |

No runtime has multiple owners.

---

# KR-010 Definition of Done

KR-010 is GREEN only if:

- BootstrapRuntime builds every runtime subsystem.
- RuntimeKernel exposes canonical runtime API.
- main.py is the only executable entrypoint.
- Startup order matches this document.
- Shutdown order matches this document.
- Ruff clean.
- Pyright clean.
- Bootstrap integration tests pass.

<!-- ========================================================================= -->
<!-- M-06 PART 10 — KR-011 Wave 1 Test Suite + Global Definition of Done -->
<!-- ========================================================================= -->

# KR-011 — Wave 1 Test Suite

**Runtime Layer:** Validation Layer

KR-011 owns every executable validation artifact for Wave 1.

Production code never imports tests.

Tests validate only public APIs.

---

# Test Architecture

```
tests/
├── core/
│   ├── test_types.py
│   ├── test_settings.py
│   └── test_logger.py
├── kernel/
│   ├── test_contracts.py
│   ├── test_container.py
│   ├── test_lifecycle.py
│   ├── test_event_bus.py
│   ├── test_context.py
│   ├── test_pipeline.py
│   └── test_bootstrap.py
├── integration/
│   └── test_runtime_startup.py
└── conftest.py
```

Exactly ten executable test files.

---

# TEST-001 — tests/core/test_types.py

### Owner

KR-011

### Purpose

Validate Foundation Core typing contracts.

### Required Tests

| Test | Validates |
|------|-----------|
| test_runtime_layers | RuntimeLayer L0–L8 vocabulary. |
| test_di_scope_values | DIScope values. |
| test_runtime_status_values | RuntimeStatus vocabulary. |
| test_health_status_values | HealthStatus vocabulary. |
| test_event_priority_values | EventPriority vocabulary unchanged. |
| test_event_phase_values | EventPhase vocabulary unchanged. |
| test_metadata_jsondict | Metadata is JSON-compatible. |

---

# TEST-002 — tests/core/test_settings.py

### Purpose

Validate immutable Settings model.

### Required Tests

- loads `.env`;
- validates environment values;
- validates directories;
- immutable model (`frozen=True`);
- reload_settings recreates settings;
- cache invalidation works.

---

# TEST-003 — tests/core/test_logger.py

### Purpose

Validate Logging Runtime.

### Required Tests

- logger caching;
- configure_logging installs handlers;
- JSON formatter output;
- Console formatter output;
- Context filter injects trace/session IDs.

---

# TEST-004 — tests/kernel/test_contracts.py

### Purpose

Validate KR-004 contracts.

### Required Tests

- RuntimeModuleManifest fields.
- RuntimeEvent field ordering.
- RuntimeEvent UTC timestamp.
- RuntimeContext immutable.
- ServiceDescriptor typing.
- LifecycleState immutable.
- Contract exports.

---

# TEST-005 — tests/kernel/test_container.py

### Purpose

Validate KR-005 DI Runtime.

### Required Tests

- service registration;
- duplicate registration fails;
- dependency resolution;
- constructor injection;
- Application scope reuse;
- Session scope isolation;
- Pipeline scope isolation;
- Transient creates new instance;
- circular dependency detection;
- shutdown disposes services.

---

# TEST-006 — tests/kernel/test_lifecycle.py

### Purpose

Validate KR-006 Lifecycle Runtime.

### Required Tests

- CREATED → INITIALIZING.
- INITIALIZING → READY.
- READY → RUNNING.
- RUNNING → STOPPED.
- FAILED transitions.
- invalid transitions raise RuntimeStateError.
- reverse shutdown order.
- lifecycle hooks execute correctly.

---

# TEST-007 — tests/kernel/test_event_bus.py

### Purpose

Validate KR-007 Event Runtime.

### Required Tests

- subscribe;
- unsubscribe;
- duplicate handler rejected;
- publish event;
- publish_many;
- dispatch ordering;
- handler priority ordering;
- handler failure propagation;
- invalid event rejection.

---

# TEST-008 — tests/kernel/test_context.py

### Purpose

Validate KR-008 Runtime Context.

### Required Tests

- RuntimeContext creation;
- metadata merge;
- metadata put/remove;
- metadata immutable replacement;
- session create/remove;
- session metadata update;
- context replacement;
- context clear.

---

# TEST-009 — tests/kernel/test_pipeline.py

### Purpose

Validate KR-009 Pipeline Runtime.

### Required Tests

- pipeline manifest validation;
- duplicate stage IDs;
- dependency validation;
- DAG validation;
- cycle detection;
- execution order;
- stage events;
- pipeline failure abort.

---

# TEST-010 — tests/kernel/test_bootstrap.py

### Purpose

Validate KR-010 Bootstrap Runtime.

### Required Tests

- bootstrap builds runtime;
- startup sequence;
- shutdown sequence;
- runtime health aggregation;
- runtime owns expected subsystems.

---

# TEST-011 — tests/integration/test_runtime_startup.py

### Purpose

End-to-end Wave 1 integration.

### Required Tests

- Runtime bootstraps successfully.
- Container initialized.
- EventBus initialized.
- Lifecycle reaches RUNNING.
- Pipeline executes.
- Runtime shuts down cleanly.

---

# Shared Test Infrastructure

## tests/conftest.py

Provides only shared fixtures.

### Required Fixtures

| Fixture | Purpose |
|---------|---------|
| settings | Immutable Settings instance. |
| runtime_context | RuntimeContext fixture. |
| trace_context | TraceContext fixture. |
| container | Fresh ContainerRuntime. |
| event_bus | Fresh EventBusRuntime. |
| lifecycle | Fresh LifecycleRuntime. |
| orchestrator | Fresh OrchestratorRuntime. |

No business fixtures.

---

# Required Toolchain Validation

Every implementation must pass all quality gates.

## Ruff

Command:

```bash
uv run ruff check .
```

Required result:

```
All checks passed!
```

---

## Ruff Format

Command:

```bash
uv run ruff format .
```

Repository formatted.

---

## Pyright

Command:

```bash
uv run pyright
```

Required result:

```
0 errors
0 warnings
```

Strict mode.

---

## Pytest

Command:

```bash
uv run pytest
```

Required result:

- Tests collected.
- All tests passed.
- Zero skipped.
- Zero xfailed.

Collection of zero tests is a hard failure.

---

# Repository Quality Gates

Wave 1 cannot be considered complete unless every gate passes.

| Gate | Requirement |
|------|-------------|
| Architecture | All modules match M-01…M-06. |
| Imports | M-04 import graph satisfied. |
| Public API | M-03 registry satisfied. |
| Typing | Pyright strict clean. |
| Style | Ruff clean. |
| Formatting | Ruff format clean. |
| Tests | All KR tests pass. |
| Integration | Runtime startup integration passes. |

Every gate is mandatory.

---

# Global Forbidden Rules

Codex must never generate:

## Architecture

- additional runtime layers;
- additional DI scopes;
- additional lifecycle states;
- additional EventPhase values;
- additional EventPriority values.

## Code Structure

- wildcard imports;
- wildcard exports;
- mutable globals;
- singleton runtime objects outside Bootstrap;
- Any in public APIs;
- print() in production code.

## Runtime

- hidden caches except approved immutable configuration/logger caches;
- filesystem access outside configuration runtime;
- HTTP clients;
- subprocesses;
- threads;
- background workers.

## Testing

- skipped Wave 1 tests;
- placeholder tests;
- empty tests.

---

# Wave 1 Global Definition of Done

Wave 1 is COMPLETE only when:

## KR Status

| KR | Status |
|----|--------|
| KR-001 | GREEN |
| KR-002 | GREEN |
| KR-003 | GREEN |
| KR-004 | GREEN |
| KR-005 | GREEN |
| KR-006 | GREEN |
| KR-007 | GREEN |
| KR-008 | GREEN |
| KR-009 | GREEN |
| KR-010 | GREEN |
| KR-011 | GREEN |

Every KR must satisfy its own Definition of Done.

---

## Runtime Validation

The runtime must successfully execute:

1. Bootstrap.
2. Initialize.
3. Start.
4. Execute pipeline.
5. Stop.
6. Shutdown.

Without architecture violations.

---

## Static Validation

- Ruff clean.
- Ruff formatted.
- Pyright strict clean.

---

## Dynamic Validation

- All unit tests pass.
- All integration tests pass.
- Zero failing tests.
- Zero skipped tests.

---

## Documentation Validation

The implementation must conform exactly to:

- M-01 File Registry.
- M-02 Runtime Graph.
- M-03 Public API Registry.
- M-04 Import Graph.
- M-05 Runtime Registry.
- M-06 Module Specifications.

No undocumented public API may exist.

---

# Canonical Completion Marker

**Document:** `06_MODULE_SPECIFICATIONS.md`

**Version:** 1.1 Canonical

**Status:** COMPLETE

**Authority:** AURORA Engineering Bible v1.1

**End of Document**
