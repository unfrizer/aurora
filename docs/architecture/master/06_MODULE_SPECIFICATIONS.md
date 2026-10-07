# AURORA MASTER HANDOFF v1.1

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

# KR-002 — Configuration Runtime — APPROVED ADR-009

The exact [KR-002 contract](../wave1/KR-002_CONFIGURATION.md) is normative for
the two owned files, complete fields/defaults/aliases/properties/validators,
signatures, imports, error boundaries and acceptance. Retain BaseSettings and
lru_cache(maxsize=1); no production edit in this reconciliation.

# KR-003 — Logging Runtime — APPROVED ADR-009

The exact [KR-003 contract](../wave1/KR-003_LOGGING.md) is normative for the two
owned files, public symbols, constructor compatibility, imports, cache/handler
behavior, context/formatters, safe admission errors and complete acceptance.
In this narrow task edit only logger.py and canonical test_logger.py; preserve
logging_config.py. Empty name, EXACT "root" and invalid levels reject before access.
No legacy configure_logging/reset_logging/ContextFilter/automatic-trace contract.

# KR-002 / KR-003 Definition of Done

All exact owner-contract APIs/behavior/acceptance and required gates must pass;
configuration/logging require measured 100% executable lines per owned file and
all public APIs asserted. Green regression alone is not acceptance. Current
KR-003 repair remains a separate reviewed task before KR-011.

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

Constructors and exact typed signatures are in the compiled module contract.
There are exactly four production files; no event.py or EventRuntime. Bus owns one
Subscriber, one Dispatcher(subscribers) and one Publisher(dispatcher). Publisher
creates UUID event_id and UTC timestamp and derives session/trace from context.
Private JSON validation helpers stay in Publisher; Dispatcher only copies already
validated events using the standard library, never importing Publisher.

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

Subscriber uses private lists and immutable returned tuples, not a global registry.
Registration error paths preserve it unchanged. No lifecycle transition/DI/context
mutation, network, persistence, queue, background work or new dependency.

DoD: exact owned files/API/import DAG, all ADR-004/005 canonical acceptance tests,
Ruff, strict Pyright, discovered Pytest, Kernel smoke and latest-head Windows/Linux
CI. Current passing regression tests alone do not prove these new requirements.

<!-- ========================================================================= -->
<!-- M-06 PART 7 — KR-008 Runtime Context Runtime -->
<!-- ========================================================================= -->

# KR-008 — Runtime Context Runtime

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

<!-- ========================================================================= -->
<!-- M-06 PART 8 — KR-009 Pipeline Runtime -->
<!-- ========================================================================= -->

# KR-009 — Pipeline Runtime

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
<!-- M-06 PART 9 — KR-010 Bootstrap Runtime -->
<!-- ========================================================================= -->

# KR-010 — Bootstrap Runtime

**Status:** APPROVED — ADR-008 B-01–B-05, 2026-10-06.
Exact contract: [KR-010](../wave1/KR-010_RUNNER_BOOTSTRAP.md).
Authority: [ADR-008](../ADR-008_KR010_Bootstrap_Reconciliation_Proposal_v1.0.md).

This exact compiled contract supersedes obsolete KR-010 private builders, creation
order, nonexistent logging/directory APIs, health vocabulary, wait/inputless execution,
exception suppression and unguarded/first-error teardown examples.

| Specification | File / purpose |
| --- | --- |
| BOOTSTRAP-001 | src/kernel/runtime/bootstrap.py: construction only, exact existing seven public builders |
| BOOTSTRAP-002 | src/kernel/runtime/runtime.py: RuntimeKernel(RuntimeContract), six explicit keyword-only references, guarded lifecycle/work/DI composition |
| BOOTSTRAP-003 | src/main.py: one bounded asynchronous process entrypoint and best-effort finalization |

Build validates existing immutable Settings, configures existing Logger with
Settings.log_level via LoggingConfig, then constructs Context and Session(context),
Container, EventBus, Orchestrator(event_bus), Lifecycle and Kernel. No initialization,
root context/event/trace, directory/service creation or business work. Configuration
errors propagate; other ordinary construction errors wrap with original cause in
RuntimeInitializationError; interruption remains interruption. Lifecycle registers
Context, Container, EventBus, Orchestrator; forward startup/reverse touched teardown.

Kernel read-only references and existing metadata/health/status/state APIs are retained;
new session reference/removal signatures are exactly B-02, no extra abstraction.
execute requires RUNNING/valid captured Pipeline ID, delegates Orchestrator work and
Container.clear_pipeline in finally; Session removal confirms existence then clears
matching DI before removing registry/context. Cancellation retains Session for retry.
Full admitted shutdown always drains Session registry after Lifecycle, not a closed
Container clear. Guard covers every mutation and cleanup, rejected calls have no DI
side effect. FAILED terminal/first-error/cause/cancellation preservation follow ADR-008.
Partial startup abort uses only existing legal FAILED transitions through Lifecycle.

main builds/initializes/starts then bounded finally independently attempts facade
stop/shutdown; error/cancellation can terminate process after cleanup. No wait task,
arbitrary execute, hidden service, reset, additional entrypoint or higher-layer import.
Exact APIs, error mapping, ownership and acceptance are in the linked KR-010 contract.
Three source files/two canonical tests only; all public APIs and 100% executable-line
target per source, required static/test/smoke/latest-head CI gates, one report/STOP.

---

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

Exactly eleven executable test modules plus one shared-fixture file (ADR-009).

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

All exact T-02 [KR-002 acceptance](../wave1/KR-002_CONFIGURATION.md):
isolated defaults/env/.env/aliases/extras, immutable assignment rejection,
relative Path conversion without I/O, helpers/validators, cache identity and
test-isolated invalidation, ValidationError/InvalidConfigurationError boundaries.

# TEST-003 — tests/core/test_logger.py

All exact T-03 [KR-003 acceptance](../wave1/KR-003_LOGGING.md): valid named
factory/cache/default/schema/constructor, empty/root/invalid-level pre-access
guards, root non-interference, first-installed handler/filter/formatters and
exception/missing-context branches, seven explicit context APIs and isolation.

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
- event priority ordering and insertion-ordered handlers (ADR-005);
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
