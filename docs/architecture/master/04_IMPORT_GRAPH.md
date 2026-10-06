# AURORA ENGINEERING BIBLE v1.1

## Approved KR-009 Precedence — ADR-007, 2026-10-06

The compiled KR-009 section below and exact wave1/KR-009 contract supersede
all retained historical KR-009 summaries/examples in this document, including
Executor health/lifecycle, unbound stage execution, ContextRuntime access,
queue/DI acquisition and Orchestrator event production. Reserved event vocabulary
and other modules' ownership remain unchanged. Only MetadataRuntime's public
stateless transformations are permitted for detached context JSON. Bootstrap uses
only OrchestratorRuntime(event_bus); full KR-010 cleanup remains deferred.

Document ID: M-04

Document Name: Import Graph

Path:
docs/architecture/master/04_IMPORT_GRAPH.md

Status: CANONICAL SOURCE OF TRUTH

Authority:
- AB-00 Development Constitution
- AB-00A Architecture Reconciliation
- M-00 Canonical Index
- M-01 File Registry
- M-02 Runtime Graph
- M-03 API Registry

Version: 1.1 Canonical

---

# Purpose

This document defines the canonical import dependency graph of AURORA Wave 1.

It specifies:

- allowed imports,
- forbidden imports,
- dependency direction,
- runtime layer visibility,
- circular dependency prevention,
- module ownership boundaries.

No implementation appears in this document.

Implementation belongs to M-06.

---

# Import Graph Constitution

The repository import graph is deterministic.

Every production import must satisfy all rules below.

## Import Invariants

1. Every production file has one canonical import set.
2. Every import follows runtime layer direction.
3. Cyclic imports are forbidden.
4. Private modules are imported only inside their owner runtime.
5. Cross-runtime imports follow ownership boundaries.
6. Tests may import public APIs only.

Violating any invariant is an Architecture Conflict.

---

# Runtime Layer Import Model

Wave 1 contains one implemented runtime layer.

Future layers are reserved.

| Runtime Layer | Status |
|---------------|--------|
| L0 Kernel Runtime | IMPLEMENTED |
| L1 Shared State Runtime | RESERVED |
| L2 Layout Runtime | RESERVED |
| L3 Theme Runtime | RESERVED |
| L4 Motion Runtime | RESERVED |
| L5 Interaction Runtime | RESERVED |
| L6 Accessibility Runtime | RESERVED |
| L7 Platform Runtime | RESERVED |
| L8 Render Runtime | RESERVED |

---

## Canonical Layer Dependency Graph

```text
L8 Render
    │
L7 Platform
    │
L6 Accessibility
    │
L5 Interaction
    │
L4 Motion
    │
L3 Theme
    │
L2 Layout
    │
L1 Shared State
    │
L0 Kernel
```

Dependencies flow downward only.

Lower layers never import higher layers.

---

# Repository Import Direction

Imports are evaluated in three dimensions.

| Dimension | Rule |
|----------|------|
| Layer | Downward only. |
| Runtime | Ownership only. |
| Module | DAG only. |

All three must succeed simultaneously.

---

# Canonical Repository Import DAG

```text
src/core/
      │
      ▼
src/kernel/contracts/
      │
      ▼
src/kernel/runtime/
      │
      ▼
src/main.py
```

No reverse dependency exists.

---

# Runtime Import Vocabulary

Every production import belongs to exactly one category.

| Category | Description |
|----------|-------------|
| FOUNDATION_IMPORT | src/core imports. |
| CONTRACT_IMPORT | src/kernel/contracts imports. |
| RUNTIME_IMPORT | src/kernel/runtime imports. |
| ENTRY_IMPORT | src/main.py imports. |
| TEST_IMPORT | tests imports. |

Vocabulary is frozen.

---

# Public Import Boundary

Public imports are imported from canonical owner modules only.

## Allowed

```python
from src.core.logger import get_logger
```

## Forbidden

```python
from src.core.logging_config import _LOGGER_CACHE
```

Private symbols never cross module boundaries.

---

# Absolute Import Policy

Wave 1 uses absolute imports only.

## Allowed

```python
from src.kernel.runtime.container import ContainerRuntime
```

## Forbidden

```python
from ..runtime.container import ContainerRuntime
```

Relative imports are forbidden across the repository.

---

# Runtime Import Ownership

Every runtime imports contracts instead of implementation.

| Runtime | Imports |
|---------|---------|
| ContainerRuntime | contracts + core |
| LifecycleRuntime | contracts + core |
| EventBusRuntime | contracts + core |
| ContextRuntime | contracts + core |
| OrchestratorRuntime | contracts + core |
| RuntimeKernel | runtime public APIs only |

Implementation-to-implementation imports follow ownership matrix later in this document.

---

# Import Visibility Model

Visibility is independent from ownership.

| Visibility | Accessible By |
|------------|---------------|
| Public | Entire repository |
| Runtime Internal | Same runtime only |
| Private | Same file only |

Visibility rules are immutable.

---

# Import Naming Rules

Every import follows canonical naming.

## Classes

```python
from src.kernel.runtime.container import ContainerRuntime
```

## Functions

```python
from src.core.config import get_settings
```

## Constants

```python
from src.core.constants import PROJECT_NAME
```

## Types

```python
from src.core.types import RuntimeLayer
```

Wildcard imports are forbidden.

---

# Import Aliasing Rules

Aliasing is restricted.

## Allowed

```python
from src.core.types import RuntimeLayer as RuntimeLayer
```

(no-op aliasing for formatting tools only)

## Forbidden

```python
from src.core.types import RuntimeLayer as Layer
```

Public API names must remain canonical.

---

# Import Categories Summary

| Category | Canonical Directory |
|----------|---------------------|
| Foundation | src/core |
| Contracts | src/kernel/contracts |
| Runtime | src/kernel/runtime |
| Entry | src/main.py |
| Tests | tests |

Every production import belongs to exactly one category.

---

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

Document Status:

IN PROGRESS (Part 1 of 10)

<!-- ========================================================================= -->
<!-- M-04 PART 2 — KR-001 Foundation Core Import Graph -->
<!-- ========================================================================= -->

# KR-001 Import Graph

**Directory**

`src/core/`

**Runtime Layer**

L0

**Owner KR**

KR-001 Foundation Core

---

# Foundation Core Import Graph

Foundation Core is the lowest dependency layer of the repository.

Every production module may import Foundation Core.

Foundation Core imports **nothing** from runtime implementations.

---

# Foundation Core Module Inventory

| Module | Category | Public |
|--------|----------|--------|
| types.py | Type System | Yes |
| constants.py | Constants | Yes |
| exceptions.py | Exception Base | Yes |

These three files form the immutable foundation layer.

---

# FOUNDATION-001 — types.py

### Module Category

Foundation Type System

### Runtime Layer

L0

### Allowed Imports

```python
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Mapping
```

Only Python standard library imports are allowed.

---

## Public Exports

| Category | Symbols |
|----------|---------|
| Type Aliases | ModuleId, SessionId, PipelineId, EventId, TraceId, ServiceId, JSONPrimitive, JSONValue, JSONDict, Payload, Metadata, Headers |
| Enums | RuntimeLayer, RuntimeStatus, HealthStatus, DIScope, EventPriority, EventPhase |

---

## Forbidden Imports

`types.py` must never import:

- `src.core.config`
- `src.core.logger`
- `src.kernel.contracts`
- `src.kernel.runtime`
- `src.main`

Reason: type system must remain dependency-free.

---

## Imported By

<table columnSizing="equal">
  <table-row>
    <table-cell>**Directory**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`src/core/*`</table-cell>
    <table-cell>Shared vocabulary.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`src/kernel/contracts/*`</table-cell>
    <table-cell>Contract field types.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`src/kernel/runtime/*`</table-cell>
    <table-cell>Runtime APIs.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`tests/*`</table-cell>
    <table-cell>Assertions and fixtures.</table-cell>
  </table-row>
</table>

---

## Import Degree

| Metric | Count |
|--------|------:|
| Incoming Imports | Repository-wide |
| Outgoing Imports | Standard Library Only |

---

# FOUNDATION-002 — constants.py

### Module Category

Foundation Constants

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from pathlib import Path

from src.core.types import RuntimeLayer
```

Imports only Foundation modules.

---

## Public Exports

| Category | Symbols |
|----------|---------|
| Project | PROJECT_NAME, PROJECT_VERSION, ARCHITECTURE_VERSION |
| Locale | DEFAULT_LOCALE, DEFAULT_TIMEZONE |
| Logging | DEFAULT_LOG_LEVEL |
| Runtime | DEFAULT_RUNTIME_LAYER |
| Paths | ROOT_DIRECTORY_NAME, SRC_DIRECTORY_NAME, DOCS_DIRECTORY_NAME, TESTS_DIRECTORY_NAME |

---

## Forbidden Imports

constants.py must never import:

- config.py
- logger.py
- settings.py
- runtime modules
- contracts

Constants cannot depend on configuration.

---

## Imported By

<table columnSizing="equal">
  <table-row>
    <table-cell>**Module**</table-cell>
    <table-cell>**Purpose**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`config.py`</table-cell>
    <table-cell>Default configuration values.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logger.py`</table-cell>
    <table-cell>Logger defaults.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`runtime.py`</table-cell>
    <table-cell>Runtime metadata.</table-cell>
  </table-row>
</table>

---

# FOUNDATION-003 — exceptions.py

### Module Category

Foundation Exceptions

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from src.core.types import RuntimeStatus
```

Only Foundation imports.

---

## Public Exports

### Base Exceptions

- AuroraError
- ValidationError
- ConfigurationError
- RuntimeErrorBase

### Runtime Exceptions

- RuntimeInitializationError
- RuntimeShutdownError
- RuntimeStateError
- RuntimeHealthError

### Context Exceptions

- ContextNotAvailableError
- SessionNotFoundError
- MetadataValidationError

### Event Exceptions

- EventValidationError
- EventDispatchError
- EventHandlerError

### Dependency Injection Exceptions

- DuplicateServiceError
- UnknownServiceError
- ServiceResolutionError
- CircularDependencyError
- ScopeError

### Pipeline Exceptions

- PipelineExecutionError
- PipelineCycleError
- DuplicateModuleError
- UnknownModuleError

---

## Forbidden Imports

Exceptions must never import:

- runtime implementations;
- contracts;
- configuration runtime;
- logging runtime.

Exception hierarchy must remain dependency-free.

---

## Imported By

Every runtime module imports canonical exceptions.

---

# Foundation Core Dependency Graph

```text
types.py
    │
    ├────────────┐
    ▼            ▼
constants.py   exceptions.py
```

No reverse dependency exists.

---

# Foundation Import Matrix

<table columnSizing="equal">
  <table-row>
    <table-cell>**Module**</table-cell>
    <table-cell>**May Import**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`types.py`</table-cell>
    <table-cell>Standard Library only.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`constants.py`</table-cell>
    <table-cell>`types.py` + Standard Library.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`exceptions.py`</table-cell>
    <table-cell>`types.py` + Standard Library.</table-cell>
  </table-row>
</table>

---

# Foundation Reverse Import Matrix

<table columnSizing="equal">
  <table-row>
    <table-cell>**Target Module**</table-cell>
    <table-cell>**Allowed Importers**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`types.py`</table-cell>
    <table-cell>Entire repository.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`constants.py`</table-cell>
    <table-cell>Configuration Runtime, Logging Runtime, RuntimeKernel.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`exceptions.py`</table-cell>
    <table-cell>Entire runtime layer.</table-cell>
  </table-row>
</table>

---

# Foundation Import Integrity Rules

Foundation modules guarantee:

1. No runtime imports.
2. No contract imports.
3. No configuration imports.
4. No logger imports.
5. No circular imports.
6. Only standard-library outbound imports.
7. Entire repository may depend on Foundation.

Violating any rule is an Architecture Conflict.

---

# KR-001 Import Statistics

| Metric | Value |
|--------|------:|
| Modules | 3 |
| Internal Dependencies | 2 |
| Runtime Dependencies | 0 |
| Contract Dependencies | 0 |
| Cycles | 0 |

Foundation Core is a directed acyclic graph.

---

**Document Status:** IN PROGRESS (Part 2 of 10)

<!-- ========================================================================= -->
<!-- M-04 PART 3 — KR-002 Configuration Runtime + KR-003 Logging Import Graph -->
<!-- ========================================================================= -->

# KR-002 Import Graph

**Directory**

`src/core/`

**Runtime Layer**

L0

**Owner KR**

KR-002 Configuration Runtime

---

# Configuration Import Graph

Configuration Runtime owns runtime configuration loading, validation and immutable Settings construction.

Configuration Runtime depends only on Foundation Core.

---

# Configuration Runtime Module Inventory

| Module | Category | Public |
|--------|----------|--------|
| settings.py | Immutable Settings Dataclass | Yes |
| config.py | Settings Loader Runtime | Yes |

---

# CONFIG-IMPORT-001 — settings.py

### Module Category

Configuration Dataclass

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.core.constants import (
    PROJECT_NAME,
    PROJECT_VERSION,
    ARCHITECTURE_VERSION,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOCALE,
    DEFAULT_TIMEZONE,
)

from src.core.types import (
    Metadata,
    RuntimeLayer,
    EventPriority,
)
```

Imports only Foundation modules.

---

## Public Export

`Settings`

---

## Forbidden Imports

settings.py must never import:

- config.py
- logger.py
- logging_config.py
- kernel contracts
- runtime implementations

Settings must remain immutable and dependency-free.

---

## Imported By

| Importer | Purpose |
|----------|---------|
| config.py | Construct immutable Settings snapshot. |
| RuntimeKernel | Read runtime metadata. |
| Tests | Configuration assertions. |

---

## Import Degree

| Metric | Count |
|--------|------:|
| Incoming Imports | 3 |
| Outgoing Imports | Foundation only |

---

# CONFIG-IMPORT-002 — config.py

### Module Category

Configuration Runtime

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from src.core.constants import *
from src.core.exceptions import (
    ConfigurationError,
    ValidationError,
)
from src.core.settings import Settings
from src.core.types import Metadata
```

Configuration Runtime imports Foundation only.

---

## Public Exports

| Category | Symbols |
|----------|---------|
| Functions | get_settings, reload_settings, clear_settings_cache, validate_settings |

---

## Forbidden Imports

config.py must never import:

- logger.py
- logging_config.py
- runtime modules
- contracts
- main.py

Reason: configuration cannot depend on logging runtime.

---

## Imported By

| Importer | Purpose |
|----------|---------|
| logger.py | Read log configuration. |
| logging_config.py | Configure handlers. |
| BootstrapRuntime | Load runtime configuration. |
| RuntimeKernel | Read Settings snapshot. |
| Tests | Configuration runtime tests. |

---

## Internal Dependency Rules

config.py owns:

- cache creation;
- environment loading;
- validation;
- Settings construction.

settings.py owns immutable Settings structure only.

---

## Cache Ownership Rule

Only config.py owns `_SETTINGS_CACHE`.

settings.py never stores cache.

---

# Configuration Runtime Dependency Graph

```text
types.py
     │
constants.py
     │
exceptions.py
     │
settings.py
     │
config.py
```

No reverse dependency exists.

---

# Configuration Runtime Import Matrix

| Module | May Import |
|--------|------------|
| settings.py | constants.py, types.py |
| config.py | settings.py, constants.py, exceptions.py |

---

# Configuration Runtime Reverse Import Matrix

| Target Module | Allowed Importers |
|--------------|-------------------|
| settings.py | config.py, RuntimeKernel, tests |
| config.py | logger.py, BootstrapRuntime, RuntimeKernel, tests |

---

# Configuration Runtime Anti-Cycle Rules

Forbidden dependency pairs:

| Forbidden Pair | Reason |
|----------------|--------|
| settings.py ↔ config.py | Immutable dataclass must not depend on loader. |
| config.py ↔ logger.py | Logging cannot configure configuration runtime. |
| config.py ↔ runtime.py | Runtime construction happens after configuration. |

These cycles are architecture violations.

---

# KR-002 Import Statistics

| Metric | Value |
|--------|------:|
| Modules | 2 |
| Internal Dependencies | 1 |
| Runtime Dependencies | 0 |
| Contract Dependencies | 0 |
| Cycles | 0 |

Configuration Runtime remains acyclic.

---

# KR-003 Import Graph

**Directory**

`src/core/`

**Runtime Layer**

L0

**Owner KR**

KR-003 Logging Runtime

---

# Logging Import Graph

Logging Runtime owns logger creation, formatter construction and RuntimeContext injection.

Logging Runtime depends on Configuration Runtime.

Configuration Runtime never depends on Logging Runtime.

---

# Logging Runtime Module Inventory

| Module | Category | Public |
|--------|----------|--------|
| logger.py | Logger Factory | Yes |
| logging_config.py | Logging Runtime | Yes |

---

# LOG-IMPORT-001 — logger.py

### Module Category

Logger Factory

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

import logging

from src.core.config import get_settings
from src.core.constants import PROJECT_NAME
```

Imports configuration only.

---

## Public Export

`get_logger`

---

## Forbidden Imports

logger.py must never import:

- logging_config.py
- runtime modules
- contracts
- ContextRuntime

Logger factory cannot initialize runtime logging.

---

## Imported By

Entire repository imports `get_logger()`.

---

## Logger Cache Rule

logger.py owns `_LOGGER_CACHE`.

No other module mutates logger cache.

---

# LOG-IMPORT-002 — logging_config.py

### Module Category

Logging Runtime

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

import logging
import json

from src.core.config import get_settings
from src.core.constants import DEFAULT_LOG_LEVEL
from src.core.types import Metadata
```

Logging Runtime imports Configuration Runtime and Foundation only.

---

## Public Exports

### Functions

- configure_logging
- reset_logging

### Classes

- ContextFilter
- ConsoleFormatter
- JsonFormatter

---

## Forbidden Imports

logging_config.py must never import:

- logger.py
- RuntimeKernel
- LifecycleRuntime
- EventBusRuntime
- ContextRuntime implementation

Context information arrives through ContextFilter interface only.

---

## Imported By

| Importer | Purpose |
|----------|---------|
| BootstrapRuntime | Initialize logging runtime. |
| RuntimeKernel | Startup logging configuration. |
| Tests | Logging runtime tests. |

---

## Formatter Ownership Rules

ContextFilter injects runtime metadata.

ConsoleFormatter owns console formatting.

JsonFormatter owns structured formatting.

No formatter owns logger creation.

---

# Logging Runtime Dependency Graph

```text
Foundation
    │
settings.py
    │
config.py
   ├──────► logger.py
   │
   └──────► logging_config.py
```

logger.py and logging_config.py never import each other.

---

# Logging Runtime Import Matrix

| Module | May Import |
|--------|------------|
| logger.py | config.py, constants.py |
| logging_config.py | config.py, constants.py, types.py |

---

# Logging Runtime Reverse Import Matrix

| Target Module | Allowed Importers |
|--------------|-------------------|
| logger.py | Entire repository |
| logging_config.py | BootstrapRuntime, RuntimeKernel, tests |

---

# Logging Runtime Anti-Cycle Rules

Forbidden dependency pairs:

| Forbidden Pair | Reason |
|----------------|--------|
| logger.py ↔ logging_config.py | Factory/runtime separation. |
| logging_config.py ↔ ContextRuntime | Runtime abstraction boundary. |
| logger.py ↔ RuntimeKernel | Logger available before runtime construction. |

All logging dependencies remain one-directional.

---

# Core Runtime Dependency DAG

```text
types.py
    │
constants.py
    │
exceptions.py
    │
settings.py
    │
config.py
   ├────────► logger.py
   │
   └────────► logging_config.py
```

Every edge is directed downward.

---

# Core Layer Import Integrity Rules

Core layer guarantees:

1. Foundation has no runtime imports.
2. Settings never imports config.
3. Config never imports logger.
4. Logger never imports logging runtime.
5. Logging runtime never imports runtime implementations.
6. Runtime metadata enters logging only through ContextFilter.
7. Core dependency graph contains zero cycles.

Violating any rule is an Architecture Conflict.

---

# KR-002 + KR-003 Import Statistics

| Runtime | Modules | Internal Edges | Cycles |
|---------|--------:|---------------:|-------:|
| Configuration Runtime | 2 | 1 | 0 |
| Logging Runtime | 2 | 2 | 0 |

Entire `src/core/` remains a directed acyclic graph.

---

**Document Status:** IN PROGRESS (Part 3 of 10)

<!-- ========================================================================= -->
<!-- M-04 PART 4 — KR-004 Kernel Contracts Import Graph -->
<!-- ========================================================================= -->

# KR-004 Import Graph

**Directory**

`src/kernel/contracts/`

**Runtime Layer**

L0

**Owner KR**

KR-004 Kernel Contracts

---

# Kernel Contracts Import Graph

Kernel Contracts define immutable runtime contracts shared by every runtime.

Contracts import Foundation Core only.

Runtime implementations import Contracts.

Contracts never import Runtime implementations.

---

# Kernel Contracts Module Inventory

| Module | Category | Public |
|--------|----------|--------|
| context.py | Runtime Context Contracts | Yes |
| events.py | Runtime Event Contracts | Yes |
| lifecycle.py | Lifecycle Contracts | Yes |
| module.py | Runtime Module Contracts | Yes |
| service.py | Dependency Injection Contracts | Yes |
| runtime.py | Runtime Protocol | Yes |

---

# CONTRACT-IMPORT-001 — context.py

### Module Category

Runtime Context Contracts

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.types import (
    Metadata,
    PipelineId,
    RuntimeLayer,
    SessionId,
    TraceId,
)
```

Only Foundation imports.

---

## Public Exports

- TraceContext
- RuntimeContext

---

## Forbidden Imports

context.py must never import:

- runtime modules;
- EventBusRuntime;
- LifecycleRuntime;
- ContextRuntime implementation;
- BootstrapRuntime.

Contracts remain implementation-free.

---

## Imported By

| Runtime | Reason |
|---------|--------|
| ContextRuntime | Active runtime context. |
| SessionRuntime | Session snapshots. |
| EventBusRuntime | Event context propagation. |
| ExecutorRuntime | Pipeline execution context. |
| RuntimeKernel | Runtime snapshot aggregation. |

---

## Import Degree

| Metric | Value |
|--------|------:|
| Incoming Imports | Runtime-wide |
| Outgoing Imports | Foundation only |

---

# CONTRACT-IMPORT-002 — events.py

### Module Category

Runtime Event Contracts

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.types import (
    EventId,
    EventPhase,
    EventPriority,
    Headers,
    Payload,
    PipelineId,
    SessionId,
)

from src.kernel.contracts.context import TraceContext
```

Imports Foundation and sibling contracts only.

---

## Public Export

RuntimeEvent

---

## Forbidden Imports

events.py must never import:

- PublisherRuntime;
- DispatcherRuntime;
- EventBusRuntime;
- RuntimeKernel.

Event contract never depends on Event Runtime.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| PublisherRuntime | Event creation. |
| DispatcherRuntime | Event dispatch. |
| SubscriberRuntime | Handler registry. |
| ExecutorRuntime | Stage events. |

---

## Internal Dependency Rule

events.py may import context.py.

context.py may never import events.py.

Dependency direction is immutable.

---

# CONTRACT-IMPORT-003 — lifecycle.py

### Module Category

Lifecycle Contracts

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.types import RuntimeStatus
```

Foundation only.

---

## Public Export

LifecycleState

---

## Forbidden Imports

lifecycle.py must never import:

- LifecycleRuntime;
- StateRuntime;
- HookRuntime.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| StateRuntime | State snapshots. |
| LifecycleRuntime | Public lifecycle API. |
| RuntimeKernel | Runtime status aggregation. |

---

# CONTRACT-IMPORT-004 — module.py

### Module Category

Runtime Module Contracts

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from dataclasses import dataclass

from src.core.types import (
    Metadata,
    ModuleId,
    RuntimeLayer,
    ServiceId,
)
```

Foundation only.

---

## Public Export

RuntimeModuleManifest

---

## Forbidden Imports

module.py must never import:

- OrchestratorRuntime;
- ManifestRuntime;
- RuntimeKernel.

Manifest contract cannot depend on pipeline runtime.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| ManifestRuntime | Validation. |
| OrchestratorRuntime | Module registry. |
| BootstrapRuntime | Runtime construction. |

---

# CONTRACT-IMPORT-005 — service.py

### Module Category

Dependency Injection Contracts

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from dataclasses import dataclass

from src.core.types import (
    DIScope,
    Metadata,
    ServiceId,
)
```

Foundation only.

---

## Public Export

ServiceDescriptor

---

## Forbidden Imports

service.py must never import:

- ContainerRuntime;
- RegistryRuntime;
- ResolverRuntime;
- ProviderRuntime.

Descriptor cannot depend on Dependency Injection implementation.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| RegistryRuntime | Registry storage. |
| ResolverRuntime | Dependency traversal. |
| ProviderRuntime | Service construction. |
| ContainerRuntime | Public API. |

---

# CONTRACT-IMPORT-006 — runtime.py

### Module Category

Runtime Protocol

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from typing import Protocol

from src.core.types import (
    HealthStatus,
    RuntimeLayer,
)
```

Foundation only.

---

## Public Export

RuntimeContract

---

## Forbidden Imports

runtime.py must never import:

- RuntimeKernel;
- ContainerRuntime;
- LifecycleRuntime;
- EventBusRuntime;
- ContextRuntime;
- OrchestratorRuntime.

Protocol cannot reference implementations.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| ContainerRuntime | RuntimeContract implementation. |
| LifecycleRuntime | RuntimeContract implementation. |
| EventBusRuntime | RuntimeContract implementation. |
| ContextRuntime | RuntimeContract implementation. |
| OrchestratorRuntime | RuntimeContract implementation. |
| RuntimeKernel | RuntimeContract implementation. |

---

# Kernel Contracts Internal DAG

```text
Foundation
     │
context.py
     │
events.py

Foundation
 ├────────► lifecycle.py
 ├────────► module.py
 ├────────► service.py
 └────────► runtime.py
```

Only one internal dependency exists:

events.py → context.py

No reverse dependency exists.

---

# Kernel Contracts Import Matrix

| Contract Module | May Import |
|-----------------|------------|
| context.py | Foundation only |
| events.py | Foundation + context.py |
| lifecycle.py | Foundation only |
| module.py | Foundation only |
| service.py | Foundation only |
| runtime.py | Foundation only |

---

# Kernel Contracts Reverse Import Matrix

| Target Module | Allowed Importers |
|--------------|-------------------|
| context.py | Context Runtime, Event Runtime, Pipeline Runtime |
| events.py | Event Runtime, Pipeline Runtime |
| lifecycle.py | Lifecycle Runtime, RuntimeKernel |
| module.py | Pipeline Runtime, BootstrapRuntime |
| service.py | Dependency Injection Runtime |
| runtime.py | Every RuntimeContract implementation |

Contracts are imported read-only.

---

# Contract Boundary Rules

## Contracts May Import

- Foundation (`src/core/*`)
- Sibling contracts (when explicitly documented)

## Contracts May Not Import

- Runtime implementations
- Configuration runtime
- Logging runtime
- `src/main.py`
- Tests

Contracts remain independent from runtime execution.

---

# Runtime-to-Contract Direction

Canonical dependency direction:

```text
Runtime Implementation
        │
        ▼
Kernel Contracts
        │
        ▼
Foundation Core
```

Reverse dependency is forbidden.

---

# Contract Replacement Rules

Runtime implementations never mutate contract objects.

Allowed:

```python
new_context = replace(old_context, metadata=new_metadata)
```

Forbidden:

```python
old_context.metadata["language"] = "en"
```

Contracts remain immutable.

---

# Anti-Cycle Registry (KR-004)

| Forbidden Cycle | Reason |
|-----------------|--------|
| context.py ↔ events.py | Events depend on context only. |
| runtime.py ↔ RuntimeKernel | Protocol cannot reference implementation. |
| service.py ↔ ContainerRuntime | Descriptor/implementation separation. |
| module.py ↔ ManifestRuntime | Contract/runtime separation. |
| lifecycle.py ↔ LifecycleRuntime | Snapshot/runtime separation. |

Every forbidden cycle is architecture-breaking.

---

# Kernel Contracts Import Integrity Rules

Kernel Contracts guarantee:

1. Imports Foundation only.
2. Imports sibling contracts only when explicitly documented.
3. Zero runtime implementation imports.
4. Zero configuration imports.
5. Zero logging imports.
6. Zero circular dependencies.
7. Immutable dependency graph.

Violating any rule is an Architecture Conflict.

---

# KR-004 Import Statistics

| Metric | Value |
|--------|------:|
| Modules | 6 |
| Internal Dependencies | 1 |
| Foundation Imports | 6 |
| Runtime Imports | 0 |
| Cycles | 0 |

Kernel Contracts remain a directed acyclic graph.

---

**Document Status:** IN PROGRESS (Part 4 of 10)

<!-- ========================================================================= -->
<!-- M-04 PART 5 — KR-005 Dependency Injection Import Graph -->
<!-- ========================================================================= -->

# KR-005 Import Graph

## Approved ADR-004 import reconciliation

`../wave1/KR-005_DI.md` is the current APPROVED implementation contract.
Container composes Registry/Resolver/Provider/Scope; Resolver imports the latter
three plus Foundation/Contracts. Registry and Provider import Foundation/Contracts
only. Scope imports Foundation and standard-library types only: its async disposal
callback replaces the forbidden Scope-to-Provider edge. A private construction
notification callback does not import Resolver into Provider. Legacy signatures
and exception aliases below are superseded for KR-005 only by ADR-004's existing
Foundation exceptions. Frozen ownership and the acyclic dependency DAG remain.


**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-005 Dependency Injection Runtime

---

# Dependency Injection Import Graph

Dependency Injection Runtime owns service registration, dependency resolution,
service construction and scope lifetime management.

The runtime is intentionally split into five independent modules.

Only `ContainerRuntime` is public.

---

# Dependency Injection Module Inventory

| Module | Category | Public |
|--------|----------|--------|
| container.py | Public Runtime Facade | Yes |
| registry.py | Descriptor Registry | Internal Runtime |
| resolver.py | Dependency Resolver | Internal Runtime |
| provider.py | Service Provider | Internal Runtime |
| scope.py | Scope Cache Runtime | Internal Runtime |

---

# Canonical Dependency Injection DAG

```text
                 contracts/service.py
                         │
                         ▼
                  RegistryRuntime
                         │
                         ▼
                  ResolverRuntime
                  │            │
                  ▼            ▼
          ProviderRuntime   ScopeRuntime
                  │            │
                  └──────┬─────┘
                         ▼
                 ContainerRuntime
```

The graph is acyclic.

Only ContainerRuntime exposes the public DI API.

---

# DI-IMPORT-001 — registry.py

### Module Category

Descriptor Registry Runtime

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from src.core.exceptions import (
    DuplicateServiceError,
    UnknownServiceError,
    ValidationError,
)

from src.kernel.contracts.service import ServiceDescriptor
```

Registry imports Foundation + Contracts only.

---

## Public Export

RegistryRuntime

---

## Forbidden Imports

registry.py must never import:

- ContainerRuntime
- ResolverRuntime
- ProviderRuntime
- ScopeRuntime
- RuntimeKernel

Registry owns descriptors only.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| ResolverRuntime | Read descriptors. |
| ContainerRuntime | Registration API. |
| Tests | Registry validation. |

---

## Ownership Rule

RegistryRuntime owns:

- descriptor storage
- duplicate validation
- descriptor lookup

RegistryRuntime never constructs services.

---

# DI-IMPORT-002 — provider.py

### Module Category

Provider Runtime

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from src.core.exceptions import (
    ServiceInitializationError,
    ServiceShutdownError,
    ValidationError,
)

from src.kernel.contracts.service import ServiceDescriptor
```

Provider imports Foundation + Contracts only.

---

## Public Export

ProviderRuntime

---

## Forbidden Imports

provider.py must never import:

- ContainerRuntime
- RegistryRuntime
- ResolverRuntime
- ScopeRuntime
- RuntimeKernel

Provider performs construction only.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| ResolverRuntime | Construct resolved services. |
| Tests | Provider runtime tests. |

---

## Ownership Rule

ProviderRuntime owns:

- constructor injection
- initialize hook execution
- shutdown hook execution

ProviderRuntime never stores instances.

---

# DI-IMPORT-003 — scope.py

### Module Category

Scope Cache Runtime

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from src.core.exceptions import ScopeError
from src.core.types import DIScope, PipelineId, ServiceId, SessionId
```

ScopeRuntime imports Foundation only.

---

## Public Export

ScopeRuntime

---

## Forbidden Imports

scope.py must never import:

- ContainerRuntime
- RegistryRuntime
- ResolverRuntime
- ProviderRuntime
- RuntimeKernel

Scope cache is independent.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| ResolverRuntime | Cache lookup/store. |
| ContainerRuntime | Cache shutdown. |
| Tests | Scope lifetime tests. |

---

## Ownership Rule

ScopeRuntime owns every cached instance.

No other runtime stores service instances.

---

# DI-IMPORT-004 — resolver.py

### Module Category

Dependency Resolver Runtime

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from src.core.exceptions import (
    CircularDependencyError,
    ServiceResolutionError,
    UnknownServiceError,
    ValidationError,
)

from src.core.types import ServiceId

from src.kernel.runtime.registry import RegistryRuntime
from src.kernel.runtime.provider import ProviderRuntime
from src.kernel.runtime.scope import ScopeRuntime
```

Resolver imports runtime internals only.

---

## Public Export

ResolverRuntime

---

## Forbidden Imports

resolver.py must never import:

- ContainerRuntime
- RuntimeKernel
- BootstrapRuntime
- LifecycleRuntime
- EventBusRuntime

Resolver never exposes public API.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| ContainerRuntime | Public resolve(). |
| Tests | Dependency graph tests. |

---

## Ownership Rule

ResolverRuntime owns:

- dependency traversal
- cycle detection
- dependency ordering
- scope lookup coordination

ResolverRuntime never exposes caches publicly.

---

# DI-IMPORT-005 — container.py

### Module Category

Public Dependency Injection Runtime

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from src.core.exceptions import (
    DuplicateServiceError,
    ServiceResolutionError,
    UnknownServiceError,
)

from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.contracts.service import ServiceDescriptor

from src.kernel.runtime.provider import ProviderRuntime
from src.kernel.runtime.registry import RegistryRuntime
from src.kernel.runtime.resolver import ResolverRuntime
from src.kernel.runtime.scope import ScopeRuntime
```

Container imports contracts plus internal DI runtimes.

---

## Public Export

ContainerRuntime

---

## Forbidden Imports

container.py must never import:

- RuntimeKernel
- BootstrapRuntime
- LifecycleRuntime
- ContextRuntime
- EventBusRuntime
- PipelineRuntime

ContainerRuntime is runtime-independent.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| BootstrapRuntime | Runtime construction. |
| RuntimeKernel | Public runtime facade. |
| Tests | Container integration tests. |

---

## Ownership Rule

ContainerRuntime owns:

- public registration API
- public resolution API
- runtime initialization
- runtime shutdown

ContainerRuntime delegates implementation internally.

---

# Internal Runtime Import Matrix

| Runtime Module | May Import |
|---------------|------------|
| registry.py | Contracts + Foundation |
| provider.py | Contracts + Foundation |
| scope.py | Foundation |
| resolver.py | registry.py, provider.py, scope.py |
| container.py | registry.py, resolver.py, provider.py, scope.py |

No other imports are allowed.

---

# Reverse Import Matrix

| Target Module | Allowed Importers |
|--------------|-------------------|
| registry.py | ResolverRuntime, ContainerRuntime |
| provider.py | ResolverRuntime, ContainerRuntime |
| scope.py | ResolverRuntime, ContainerRuntime |
| resolver.py | ContainerRuntime |
| container.py | RuntimeKernel, BootstrapRuntime, Tests |

ContainerRuntime is the only externally imported runtime.

---

# Dependency Injection Ownership Boundary

## Public Boundary

```text
RuntimeKernel
      │
      ▼
ContainerRuntime
```

Everything below ContainerRuntime is internal.

---

## Internal Boundary

```text
ContainerRuntime
 ├── RegistryRuntime
 ├── ResolverRuntime
 ├── ProviderRuntime
 └── ScopeRuntime
```

Internal runtimes never expose APIs directly outside DI Runtime.

---

# Scope Lifetime Dependency Rules

| Scope | Owner Runtime |
|-------|---------------|
| APPLICATION | ScopeRuntime |
| SESSION | ScopeRuntime |
| PIPELINE | ScopeRuntime |
| TRANSIENT | ResolverRuntime |

Scope ownership is exclusive.

---

# Dependency Resolution Direction

Canonical resolution flow:

```text
ContainerRuntime.resolve()
          │
          ▼
ResolverRuntime
      │
      ▼
RegistryRuntime
      │
      ▼
ProviderRuntime
      │
      ▼
ScopeRuntime
```

Construction occurs after validation.

---

# Anti-Cycle Registry (KR-005)

| Forbidden Cycle | Reason |
|-----------------|--------|
| ContainerRuntime ↔ ResolverRuntime | Public/internal separation. |
| RegistryRuntime ↔ ResolverRuntime | Registry cannot resolve dependencies. |
| ProviderRuntime ↔ RegistryRuntime | Construction cannot mutate registry. |
| ScopeRuntime ↔ ProviderRuntime | Cache cannot construct services. |
| ScopeRuntime ↔ RegistryRuntime | Cache independent from descriptors. |

Every listed cycle is architecture-breaking.

---

# Dependency Injection Import Integrity Rules

Dependency Injection Runtime guarantees:

1. ContainerRuntime is the only public DI runtime.
2. RegistryRuntime imports contracts only.
3. ProviderRuntime imports contracts only.
4. ScopeRuntime imports Foundation only.
5. ResolverRuntime imports internal DI runtimes only.
6. RuntimeKernel imports ContainerRuntime only.
7. Internal DI modules are never imported by unrelated runtimes.

Violating any rule is an Architecture Conflict.

---

# KR-005 Import Statistics

| Metric | Value |
|--------|------:|
| Modules | 5 |
| Internal Runtime Edges | 7 |
| Contract Imports | 4 |
| Foundation Imports | 5 |
| External Runtime Imports | 0 |
| Cycles | 0 |

Dependency Injection Runtime forms a directed acyclic graph.

---

**Document Status:** IN PROGRESS (Part 5 of 10)

<!-- ========================================================================= -->
<!-- M-04 PART 6 — KR-006 Lifecycle Runtime + KR-007 Event Bus Import Graph -->
<!-- ========================================================================= -->

# KR-006 Import Graph

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

# Lifecycle Import Graph

Lifecycle Runtime owns runtime lifecycle orchestration.

It consists of three independent runtime modules.

Only `LifecycleRuntime` is imported outside Lifecycle Runtime.

---

# Lifecycle Runtime Module Inventory

| Module | Category | Public |
|--------|----------|--------|
| lifecycle.py | Public Lifecycle Facade | Yes |
| state.py | Runtime State Machine | Internal Runtime |
| hooks.py | Lifecycle Hook Registry | Internal Runtime |

---

# Canonical Lifecycle Runtime DAG

```text
contracts/lifecycle.py
          │
          ▼
      StateRuntime
          │
          ▼
LifecycleRuntime
          ▲
          │
      HookRuntime
```

No reverse dependency exists.

---

# LIFE-IMPORT-001 — state.py

### Module Category

Runtime State Machine

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from src.core.exceptions import RuntimeStateError
from src.core.types import RuntimeStatus

from src.kernel.contracts.lifecycle import LifecycleState
```

Imports Foundation + Lifecycle contract only.

---

## Public Export

`StateRuntime`

---

## Forbidden Imports

state.py must never import:

- LifecycleRuntime
- HookRuntime
- RuntimeKernel
- BootstrapRuntime
- EventBusRuntime

StateRuntime owns RuntimeStatus only.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| LifecycleRuntime | Runtime transitions. |
| Tests | State machine tests. |

---

## Ownership Rule

StateRuntime owns:

- RuntimeStatus transitions.
- LifecycleState snapshot creation.
- Transition validation.

---

# LIFE-IMPORT-002 — hooks.py

### Module Category

Lifecycle Hook Registry

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from typing import Callable
```

Standard Library only.

---

## Public Export

`HookRuntime`

---

## Forbidden Imports

hooks.py must never import:

- LifecycleRuntime
- StateRuntime
- RuntimeKernel
- EventBusRuntime
- ContextRuntime

HookRuntime stores callbacks only.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| LifecycleRuntime | Hook execution. |
| Tests | Hook ordering tests. |

---

## Ownership Rule

HookRuntime owns:

- initialize hook registry.
- startup hook registry.
- stop hook registry.
- shutdown hook registry.

Hooks know nothing about runtime state.

---

# LIFE-IMPORT-003 — lifecycle.py

### Module Category

Public Lifecycle Runtime

### Runtime Layer

L0

---

## Allowed Imports

```python
from __future__ import annotations

from src.core.exceptions import (
    RuntimeInitializationError,
    RuntimeShutdownError,
    RuntimeStateError,
)

from src.kernel.contracts.runtime import RuntimeContract

from src.kernel.runtime.state import StateRuntime
from src.kernel.runtime.hooks import HookRuntime
```

LifecycleRuntime imports contracts and internal lifecycle runtimes only.

---

## Public Export

`LifecycleRuntime`

---

## Forbidden Imports

lifecycle.py must never import:

- RuntimeKernel
- BootstrapRuntime
- EventBusRuntime
- ContextRuntime
- OrchestratorRuntime

Lifecycle Runtime remains runtime-independent.

---

## Imported By

| Runtime | Purpose |
|---------|---------|
| BootstrapRuntime | Startup lifecycle. |
| RuntimeKernel | Public runtime lifecycle facade. |
| Tests | Lifecycle integration tests. |

---

## Ownership Rule

LifecycleRuntime owns:

- initialize/start/stop/shutdown orchestration.
- hook execution order.
- public lifecycle API.

State mutation is delegated to StateRuntime.

---

# Lifecycle Runtime Import Matrix

| Runtime Module | May Import |
|---------------|------------|
| state.py | contracts/lifecycle.py + Foundation |
| hooks.py | Standard Library only |
| lifecycle.py | state.py, hooks.py, contracts/runtime.py |

---

# Lifecycle Reverse Import Matrix

| Target Module | Allowed Importers |
|--------------|-------------------|
| state.py | LifecycleRuntime |
| hooks.py | LifecycleRuntime |
| lifecycle.py | RuntimeKernel, BootstrapRuntime |

---

# Lifecycle Anti-Cycle Registry

| Forbidden Cycle | Reason |
|-----------------|--------|
| LifecycleRuntime ↔ StateRuntime | Coordinator/state separation. |
| LifecycleRuntime ↔ HookRuntime | Coordinator/registry separation. |
| HookRuntime ↔ StateRuntime | Hooks cannot mutate lifecycle state. |

---

# Lifecycle Runtime Integrity Rules

Lifecycle Runtime guarantees:

1. LifecycleRuntime is the only public lifecycle facade.
2. StateRuntime owns RuntimeStatus exclusively.
3. HookRuntime owns callbacks exclusively.
4. No lifecycle implementation imports RuntimeKernel.
5. Lifecycle dependency graph is acyclic.

---

# KR-007 Import Graph

**Authority:** APPROVED ADR-005 E-01–E-04, ADR-004 P-04 and AB-00C/D (2026-10-06).
The exact signatures and acceptance contract are `../wave1/KR-007_EVENT_BUS.md`.
Only KR-007 entries are reconciled; other module contracts remain unchanged.

## Allowed Import Edges

| File | Export | Responsibility | Concrete dependencies |
| --- | --- | --- | --- |
| bus.py | EventBusRuntime | Public facade/composition | Publisher, Dispatcher, Subscriber |
| publisher.py | PublisherRuntime | Sole new event factory, validation, publication | Dispatcher |
| dispatcher.py | DispatcherRuntime | Sequential snapshot delivery | Subscriber |
| subscriber.py | SubscriberRuntime | Instance-local registry | None |

All four may use their necessary existing Foundation types/exceptions and frozen
KR-004 event/context/runtime contracts. Subscriber has no concrete runtime import.
Dispatcher must not import Publisher, EventBus, Lifecycle or RuntimeKernel.
Publisher may import Dispatcher solely for its existing constructor/publication
delegation (explicit ADR-005 E-01); never Subscriber, EventBus or RuntimeKernel.
Bus imports only its three existing event internals, Foundation and contracts.
Standard-library copy/dataclasses support existing-event snapshots; Publisher's
private typed JSON validator uses datetime/uuid/math/typing. No higher-layer import,
reverse edge, callback abstraction or cross-owner utility is permitted.

The acyclic concrete graph is Bus -> Publisher -> Dispatcher -> Subscriber,
with Bus also constructing Dispatcher and Subscriber. Runtime consumers access
only EventBusRuntime; tests may access all four existing exported classes.

Publication is Bus.publish -> Publisher.validate/capture -> Dispatcher.dispatch
-> Subscriber.handlers -> await EventHandlerContract.handle. Construction is a
separate Publisher.create operation, not a new factory invoked on each publish.

No circular import. No concrete event runtime may import Bootstrap, RuntimeKernel,
Container, Lifecycle, ContextRuntime, Executor or a higher layer. Test consumption
of existing internals does not expose them as production facades.

# Lifecycle ↔ Event Runtime Boundary Rules

Lifecycle Runtime may publish events **only through EventBusRuntime**.

Forbidden:

```text
LifecycleRuntime
        │
        ▼
PublisherRuntime
```

Required:

```text
LifecycleRuntime
        │
        ▼
EventBusRuntime
        │
        ▼
PublisherRuntime
```

This boundary is immutable.

---

# KR-006 + KR-007 Import Integrity Rules

Lifecycle and Event Runtime guarantee:

1. LifecycleRuntime is the only lifecycle facade.
2. EventBusRuntime is the only event facade.
3. Internal runtimes never import RuntimeKernel.
4. PublisherRuntime imports contracts only.
5. DispatcherRuntime imports SubscriberRuntime only.
6. LifecycleRuntime communicates with Event Runtime through EventBusRuntime only.
7. Both runtime graphs remain acyclic.

Violating any rule is an Architecture Conflict.

---

# KR-006 + KR-007 Import Statistics

| Runtime | Modules | Internal Edges | Cycles |
|---------|--------:|---------------:|-------:|
| Lifecycle Runtime | 3 | 3 | 0 |
| Event Runtime | 4 | 5 | 0 |

Combined runtime graph contains **zero circular dependencies**.

---

**Document Status:** IN PROGRESS (Part 6 of 10)

<!-- ========================================================================= -->
<!-- M-04 PART 7 — KR-008 Runtime Context Runtime + KR-009 Pipeline Import Graph -->
<!-- ========================================================================= -->

# KR-008 Import Graph

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

# KR-009 Import Graph

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
<!-- M-04 PART 8 — KR-010 Bootstrap Runtime + RuntimeKernel + Entry Point Import Graph -->
<!-- ========================================================================= -->

# KR-010 Import Graph

**Directory**

`src/kernel/runtime/`

**Runtime Layer**

L0

**Owner KR**

KR-010 Bootstrap Runtime

---

# Bootstrap Import Graph — Approved KR-010

**Status:** APPROVED — ADR-008 B-01–B-05, 2026-10-06.
Exact contract: [KR-010](../wave1/KR-010_RUNNER_BOOTSTRAP.md).
Authority: [ADR-008](../ADR-008_KR010_Bootstrap_Reconciliation_Proposal_v1.0.md).

Allowed directed edges:

| Consumer | Allowed project imports |
| --- | --- |
| bootstrap.py | Existing Configuration/Logging APIs and LoggingConfig; ContainerRuntime, LifecycleRuntime, EventBusRuntime from bus.py, ContextRuntime, OrchestratorRuntime, RuntimeKernel; SessionRuntime only B-02 construction |
| runtime/runtime.py | Existing Foundation exceptions/types/logger/version; RuntimeContract, RuntimeContext, LifecycleState; PipelineDefinition; five public runtime facades; SessionRuntime only B-02 typed reference/public composition |
| src/main.py | BootstrapRuntime; existing Foundation status/error vocabulary and optional get_logger only |

SessionRuntime is an explicit narrow exception to legacy internal-runtime bans
below for these TWO KR-010 files only. It does not permit Metadata/DI/Lifecycle/
Event/Pipeline internals, private Session APIs or reverse imports. Session remains
KR-008; it imports no Container/Kernel/Bootstrap. Kernel never constructs Session
or another runtime. Main imports no RuntimeKernel/collaborator/contract/service.
Existing stateless PipelineDefinition/contract annotations do not authorize executors.

Canonical construction: Settings -> Logging -> Context -> Session(context) storage
collaborator -> Container -> EventBus -> Orchestrator(event_bus) -> Lifecycle -> Kernel.
Lifecycle participant registration: Context, Container, EventBus, Orchestrator;
reverse touched cleanup. This approved order supersedes the contradictory legacy
KR-010 order; no Bootstrap-to-Executor construction/import is restored.

Main -> Bootstrap -> Kernel -> existing collaborators -> contracts/Foundation
remains acyclic/downward. The Main flow is bounded build/initialize/start/finally
stop/shutdown, not a mandatory inputless execute/signal wait. Only Kernel composes
Pipeline/Session DI cleanup through Container and existing Session public methods.
No business logic, runtime globals, new layer/scope or ownership transfer.

---

<!-- ========================================================================= -->
<!-- M-04 PART 9 — Global Forbidden Import Registry -->
<!-- ========================================================================= -->

# Global Forbidden Import Registry

**Document Scope**

Entire Wave 1 Repository

**Runtime Layer**

L0

**Authority**

Import Constitution (Part 1)

---

# Purpose

This section defines every forbidden import relationship inside Wave 1.

Unlike previous sections that define allowed dependency graphs, this registry defines repository-wide import violations.

Every forbidden import is an Architecture Conflict.

---

# Forbidden Import Categories

| Category | Meaning |
|----------|---------|
| LAYER_VIOLATION | Higher layer imported by lower layer. |
| CONTRACT_VIOLATION | Contract imports implementation. |
| FACADE_VIOLATION | Internal runtime imported outside owner runtime. |
| ENTRY_VIOLATION | `main.py` bypasses BootstrapRuntime. |
| CYCLE_VIOLATION | Creates circular dependency. |
| PRIVATE_VIOLATION | Imports private runtime module. |

Vocabulary is immutable.

---

# Foundation Layer Violations

Foundation (`src/core/`) is the lowest dependency layer.

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`src.core.types → src.kernel.*`</table-cell>
    <table-cell>Foundation cannot depend on kernel.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`src.core.constants → src.core.config`</table-cell>
    <table-cell>Constants cannot depend on configuration.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`src.core.constants → src.core.logger`</table-cell>
    <table-cell>Constants cannot depend on logging runtime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`src.core.exceptions → src.kernel.runtime.*`</table-cell>
    <table-cell>Exceptions remain implementation-free.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`src.core.settings → src.core.config`</table-cell>
    <table-cell>Immutable Settings cannot depend on loader.</table-cell>
  </table-row>
</table>

---

# Configuration Runtime Violations

Configuration Runtime may import Foundation only.

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`config.py → logger.py`</table-cell>
    <table-cell>No configuration/logging cycle.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`config.py → logging_config.py`</table-cell>
    <table-cell>Logging initializes after configuration.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`settings.py → RuntimeKernel`</table-cell>
    <table-cell>Configuration independent from runtime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`settings.py → BootstrapRuntime`</table-cell>
    <table-cell>Settings remain immutable.</table-cell>
  </table-row>
</table>

---

# Logging Runtime Violations

Logging Runtime depends on Configuration Runtime only.

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logger.py → logging_config.py`</table-cell>
    <table-cell>Factory/runtime separation.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logging_config.py → logger.py`</table-cell>
    <table-cell>No logger initialization cycle.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logging_config.py → ContextRuntime`</table-cell>
    <table-cell>Logging receives metadata through filter abstraction.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`logger.py → RuntimeKernel`</table-cell>
    <table-cell>Logger available before runtime exists.</table-cell>
  </table-row>
</table>

---

# Contract Layer Violations

Contracts never import runtime implementations.

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`contracts/context.py → runtime/context.py`</table-cell>
    <table-cell>Contract/runtime separation.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`contracts/events.py → runtime/bus.py`</table-cell>
    <table-cell>Event contract independent from runtime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`contracts/lifecycle.py → runtime/lifecycle.py`</table-cell>
    <table-cell>Lifecycle snapshot independent.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`contracts/service.py → runtime/container.py`</table-cell>
    <table-cell>ServiceDescriptor independent.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`contracts/module.py → runtime/orchestrator.py`</table-cell>
    <table-cell>Manifest independent.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`contracts/runtime.py → runtime/runtime.py`</table-cell>
    <table-cell>Protocol independent.</table-cell>
  </table-row>
</table>

---

# Dependency Injection Violations

Internal DI runtimes are private.

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`RuntimeKernel → RegistryRuntime`</table-cell>
    <table-cell>Facade imports only ContainerRuntime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`RuntimeKernel → ResolverRuntime`</table-cell>
    <table-cell>Internal runtime hidden.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`LifecycleRuntime → ScopeRuntime`</table-cell>
    <table-cell>Runtime ownership violation.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`EventBusRuntime → RegistryRuntime`</table-cell>
    <table-cell>Cross-runtime private import.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`ContextRuntime → ResolverRuntime`</table-cell>
    <table-cell>Context runtime independent.</table-cell>
  </table-row>
</table>

---

# Lifecycle Runtime Violations

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`StateRuntime → LifecycleRuntime`</table-cell>
    <table-cell>No reverse coordinator dependency.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`HookRuntime → StateRuntime`</table-cell>
    <table-cell>Hook registry independent from state.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`HookRuntime → RuntimeKernel`</table-cell>
    <table-cell>Internal runtime hidden.</table-cell>
  </table-row>
</table>

---

# Event Runtime Violations

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`PublisherRuntime → DispatcherRuntime`</table-cell>
    <table-cell>Create/dispatch separation.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`DispatcherRuntime → EventBusRuntime`</table-cell>
    <table-cell>No reverse facade dependency.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`SubscriberRuntime → PublisherRuntime`</table-cell>
    <table-cell>Registry independent from publishing.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`SubscriberRuntime → RuntimeKernel`</table-cell>
    <table-cell>Internal runtime hidden.</table-cell>
  </table-row>
</table>

---

# Context Runtime Violations

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`MetadataRuntime → ContextRuntime`</table-cell>
    <table-cell>Metadata runtime independent.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`ContextRuntime → SessionRuntime`</table-cell>
    <table-cell>Reverse edge forbidden; Session-to-Context is explicitly approved by ADR-006 C-01.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`ContextRuntime → RuntimeKernel`</table-cell>
    <table-cell>No upward dependency.</table-cell>
  </table-row>
</table>

---

# Pipeline Runtime Violations

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`ExecutorRuntime → RuntimeKernel`</table-cell>
    <table-cell>Executor independent from kernel.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`ManifestRuntime → ExecutorRuntime`</table-cell>
    <table-cell>Validation/execution separation.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`PipelineDefinition → ManifestRuntime`</table-cell>
    <table-cell>Dataclasses independent from runtime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`OrchestratorRuntime → BootstrapRuntime`</table-cell>
    <table-cell>Pipeline independent from bootstrap.</table-cell>
  </table-row>
</table>

---

# Bootstrap Runtime Violations

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`BootstrapRuntime → RegistryRuntime`</table-cell>
    <table-cell>Bootstrap imports facades only.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`BootstrapRuntime → PublisherRuntime`</table-cell>
    <table-cell>No internal runtime imports.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`BootstrapRuntime → ExecutorRuntime`</table-cell>
    <table-cell>Pipeline internals hidden.</table-cell>
  </table-row>
</table>

---

# RuntimeKernel Violations

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`RuntimeKernel → BootstrapRuntime`</table-cell>
    <table-cell>Kernel cannot build itself.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`RuntimeKernel → PublisherRuntime`</table-cell>
    <table-cell>Event internals hidden.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`RuntimeKernel → StateRuntime`</table-cell>
    <table-cell>Lifecycle internals hidden.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`RuntimeKernel → MetadataRuntime`</table-cell>
    <table-cell>Context internals hidden.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`RuntimeKernel → ManifestRuntime`</table-cell>
    <table-cell>Pipeline internals hidden.</table-cell>
  </table-row>
</table>

---

# Entry Layer Violations

## Forbidden Imports

<table columnSizing="equal">
  <table-row>
    <table-cell>**Forbidden Import**</table-cell>
    <table-cell>**Reason**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`main.py → RuntimeKernel`</table-cell>
    <table-cell>Must go through BootstrapRuntime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`main.py → ContainerRuntime`</table-cell>
    <table-cell>No runtime bypass.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`main.py → EventBusRuntime`</table-cell>
    <table-cell>No direct runtime ownership.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`main.py → contracts/*`</table-cell>
    <table-cell>Entry layer imports runtime only.</table-cell>
  </table-row>
</table>

---

# Private Runtime Import Registry

The following runtime modules are **private**.

They may never be imported outside their owner runtime.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Private Runtime**</table-cell>
    <table-cell>**Owner Runtime**</table-cell>
  </table-row>
  <table-row><table-cell>RegistryRuntime</table-cell><table-cell>Dependency Injection Runtime</table-cell></table-row>
  <table-row><table-cell>ResolverRuntime</table-cell><table-cell>Dependency Injection Runtime</table-cell></table-row>
  <table-row><table-cell>ProviderRuntime</table-cell><table-cell>Dependency Injection Runtime</table-cell></table-row>
  <table-row><table-cell>ScopeRuntime</table-cell><table-cell>Dependency Injection Runtime</table-cell></table-row>
  <table-row><table-cell>StateRuntime</table-cell><table-cell>Lifecycle Runtime</table-cell></table-row>
  <table-row><table-cell>HookRuntime</table-cell><table-cell>Lifecycle Runtime</table-cell></table-row>
  <table-row><table-cell>PublisherRuntime</table-cell><table-cell>Event Runtime</table-cell></table-row>
  <table-row><table-cell>DispatcherRuntime</table-cell><table-cell>Event Runtime</table-cell></table-row>
  <table-row><table-cell>SubscriberRuntime</table-cell><table-cell>Event Runtime</table-cell></table-row>
  <table-row><table-cell>MetadataRuntime</table-cell><table-cell>Context Runtime</table-cell></table-row>
  <table-row><table-cell>SessionRuntime</table-cell><table-cell>Context Runtime</table-cell></table-row>
  <table-row><table-cell>ManifestRuntime</table-cell><table-cell>Pipeline Runtime</table-cell></table-row>
  <table-row><table-cell>ExecutorRuntime</table-cell><table-cell>Pipeline Runtime</table-cell></table-row>
</table>

Private runtime visibility is immutable.

---

# Repository-Wide Cycle Registry

These cycles are explicitly forbidden.

<table columnSizing="equal">
  <table-row>
    <table-cell>**Cycle**</table-cell>
    <table-cell>**Status**</table-cell>
  </table-row>
  <table-row><table-cell>Configuration ↔ Logging</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
  <table-row><table-cell>Contracts ↔ Runtime</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
  <table-row><table-cell>Container ↔ Resolver</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
  <table-row><table-cell>Lifecycle ↔ State</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
  <table-row><table-cell>Publisher ↔ Dispatcher</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
  <table-row><table-cell>Context ↔ Session</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
  <table-row><table-cell>Manifest ↔ Executor</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
  <table-row><table-cell>RuntimeKernel ↔ Bootstrap</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
  <table-row><table-cell>main ↔ RuntimeKernel</table-cell><table-cell>FORBIDDEN</table-cell></table-row>
</table>

Every listed cycle is architecture-breaking.

---

# Repository Import Integrity Rules

The repository is GREEN only if:

- [x] Layer direction never violated.
- [x] Contracts never import implementations.
- [x] Public facades hide internal runtimes.
- [x] Private runtimes remain private.
- [x] Entry layer imports BootstrapRuntime only.
- [x] Repository contains zero circular imports.
- [x] Every import follows M-02 Runtime Graph.

Violating any rule is an Architecture Conflict.

---

# Global Forbidden Import Statistics

| Metric | Value |
|--------|------:|
| Forbidden Layer Imports | 18 |
| Forbidden Contract Imports | 6 |
| Forbidden Runtime Imports | 27 |
| Private Runtime Modules | 13 |
| Explicit Forbidden Cycles | 9 |

This registry is exhaustive for Wave 1.

---

**Document Status:** IN PROGRESS (Part 9 of 10)

<!-- ========================================================================= -->
<!-- M-04 PART 10 — Repository Import Matrix, Layer Visibility Matrix & DoD -->
<!-- ========================================================================= -->

# Repository Import Matrix

**Document Scope**

Entire Wave 1 Repository

**Status**

CANONICAL

**Authority**

AB-00 Development Constitution

---

# Repository Layer Matrix

This matrix defines every dependency direction between architectural layers.

| From / To | Foundation | Contracts | Runtime Facades | Runtime Internals | Bootstrap | Entry |
|------------|------------|-----------|-----------------|-------------------|-----------|-------|
| **Foundation** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Contracts** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Runtime Facades** | ✅ | ✅ | ✅ | ✅ (own runtime only) | ❌ | ❌ |
| **Runtime Internals** | ✅ | ✅ | ✅ (own facade only) | ✅ (own runtime only) | ❌ | ❌ |
| **Bootstrap Runtime** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Entry Layer (`main.py`)** | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |

This table is immutable.

---

# Canonical Dependency Direction

The repository dependency graph is strictly top-down.

```text
main.py
    │
    ▼
Bootstrap Runtime
    │
    ▼
Runtime Kernel
    │
    ▼
Runtime Facades
    │
    ▼
Runtime Internals
    │
    ▼
Kernel Contracts
    │
    ▼
Foundation Core
```

No dependency may point upward.

---

# Runtime Visibility Matrix

## Public Runtime Modules

These modules may be imported outside their runtime package.

| Runtime | Public Module |
|----------|---------------|
| Dependency Injection | `ContainerRuntime` |
| Lifecycle | `LifecycleRuntime` |
| Event Bus | `EventBusRuntime` |
| Runtime Context | `ContextRuntime` |
| Pipeline Runtime | `OrchestratorRuntime` |
| Runtime Kernel | `RuntimeKernel` |
| Bootstrap Runtime | `BootstrapRuntime` |

Everything else is internal.

---

## Internal Runtime Modules

Internal modules may only be imported inside their owner runtime.

| Runtime | Internal Modules |
|----------|------------------|
| Dependency Injection | RegistryRuntime, ResolverRuntime, ProviderRuntime, ScopeRuntime |
| Lifecycle | StateRuntime, HookRuntime |
| Event Runtime | PublisherRuntime, DispatcherRuntime, SubscriberRuntime |
| Runtime Context | MetadataRuntime, SessionRuntime |
| Pipeline Runtime | ManifestRuntime, ExecutorRuntime |

Importing an internal runtime from another runtime is forbidden.

---

# Repository Public Import Matrix

<table columnSizing="equal">
  <table-row>
    <table-cell>**Importer**</table-cell>
    <table-cell>**Public Runtime Allowed**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`main.py`</table-cell>
    <table-cell>`BootstrapRuntime` only.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`BootstrapRuntime`</table-cell>
    <table-cell>All runtime facades.</table-cell>
  </table-row>
  <table-row>
    <table-cell>`RuntimeKernel`</table-cell>
    <table-cell>Runtime facades only.</table-cell>
  </table-row>
  <table-row>
    <table-cell>Business Modules</table-cell>
    <table-cell>`RuntimeKernel` only.</table-cell>
  </table-row>
  <table-row>
    <table-cell>Tests</table-cell>
    <table-cell>Public facades and explicitly documented internals.</table-cell>
  </table-row>
</table>

---

# Repository Internal Import Matrix

<table columnSizing="equal">
  <table-row>
    <table-cell>**Owner Runtime**</table-cell>
    <table-cell>**Allowed Internal Imports**</table-cell>
  </table-row>
  <table-row>
    <table-cell>Dependency Injection</table-cell>
    <table-cell>Registry ↔ Resolver ↔ Provider ↔ Scope according to KR-005 DAG.</table-cell>
  </table-row>
  <table-row>
    <table-cell>Lifecycle</table-cell>
    <table-cell>LifecycleRuntime → StateRuntime + HookRuntime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>Event Runtime</table-cell>
    <table-cell>EventBusRuntime → PublisherRuntime / DispatcherRuntime / SubscriberRuntime.</table-cell>
  </table-row>
  <table-row>
    <table-cell>Runtime Context</table-cell>
    <table-cell>SessionRuntime → ContextRuntime → MetadataRuntime; SessionRuntime → MetadataRuntime (ADR-006 C-01).</table-cell>
  </table-row>
  <table-row>
    <table-cell>Pipeline Runtime</table-cell>
    <table-cell>OrchestratorRuntime → ManifestRuntime → ExecutorRuntime.</table-cell>
  </table-row>
</table>

Cross-runtime internal imports are forbidden.

---

# Import Decision Algorithm

Every new import must pass this algorithm before implementation.

## Step 1 — Identify Symbol Owner

Determine the canonical owner module.

| Symbol Category | Owner |
|-----------------|-------|
| Type Alias | Foundation |
| Exception | Foundation |
| Runtime Contract | Contracts |
| Runtime Facade | Runtime |
| Runtime Internal | Runtime Owner |
| Bootstrap | Bootstrap Runtime |

---

## Step 2 — Check Layer Direction

The importer must belong to the same or a higher runtime layer.

If dependency points upward:

**Architecture Conflict**

---

## Step 3 — Check Runtime Visibility

If target module is internal:

Importer must belong to the same runtime package.

Otherwise:

**Private Runtime Violation**

---

## Step 4 — Check Cycle Registry

If import creates a documented forbidden cycle:

Reject implementation.

---

## Step 5 — Validate Against Repository Matrix

Import must exist inside the Repository Layer Matrix.

Otherwise:

**Import Validation Failed**

---

# Import Validation Checklist

Every production import must satisfy all conditions.

- [ ] Correct canonical owner.
- [ ] Correct runtime layer direction.
- [ ] Correct public/internal visibility.
- [ ] No forbidden cycle introduced.
- [ ] No wildcard import used.
- [ ] No runtime internal imported outside owner runtime.
- [ ] Import documented inside M-04.

---

# Wildcard Import Policy

Wildcard imports are forbidden.

## Forbidden

```python
from src.kernel.runtime.container import *
```

```python
from src.core.types import *
```

```python
from src.kernel.contracts.events import *
```

## Required

```python
from src.kernel.runtime.container import ContainerRuntime
```

Explicit imports are mandatory.

---

# Relative Import Policy

Relative imports are forbidden across the repository.

## Forbidden

```python
from .container import ContainerRuntime
```

```python
from ..contracts.context import RuntimeContext
```

## Required

```python
from src.kernel.runtime.container import ContainerRuntime
```

Absolute imports are mandatory.

---

# Canonical Import Style

Imports must be grouped in this exact order.

```python
from __future__ import annotations

# Standard Library

# Third Party

# Foundation

# Contracts

# Runtime

# Local Package
```

Import ordering is deterministic.

---

# Repository Import Style Rules

Every module must satisfy:

1. `__future__` import first.
2. Standard Library second.
3. Third-party packages third.
4. Foundation imports.
5. Contract imports.
6. Runtime imports.
7. Local package imports.
8. No wildcard imports.
9. No relative imports.

---

# Layer Ownership Summary

| Layer | Owns |
|--------|------|
| Foundation | Types, constants, exceptions, configuration, logging primitives. |
| Contracts | Immutable runtime contracts and protocols. |
| Runtime Internals | Implementation details of each runtime subsystem. |
| Runtime Facades | Public runtime APIs. |
| Bootstrap Runtime | Runtime construction. |
| Entry Layer | Process lifecycle only. |

Ownership never overlaps.

---

# Import Compliance Levels

| Level | Meaning |
|-------|---------|
| GREEN | Fully compliant with M-04. |
| YELLOW | Temporary implementation exception documented in Architecture Decision Record. |
| RED | Architecture Conflict — implementation rejected. |

Wave 1 production code must remain GREEN.

---

# Repository Import Metrics

| Metric | Value |
|--------|------:|
| Architectural Layers | 6 |
| Public Runtime Facades | 7 |
| Internal Runtime Modules | 13 |
| Foundation Modules | 7 |
| Contract Modules | 6 |
| Bootstrap Modules | 2 |
| Entry Modules | 1 |
| Explicit Forbidden Cycles | 9 |
| Wildcard Imports Allowed | 0 |
| Relative Imports Allowed | 0 |

These metrics are canonical.

---

# Definition of Done — M-04 Import Graph

M-04 is COMPLETE only if:

- [x] Every Wave 1 module has an owner runtime layer.
- [x] Every public symbol has a canonical owner file.
- [x] Every runtime has a complete DAG.
- [x] Every forbidden cycle is documented.
- [x] Every public facade is documented.
- [x] Every internal runtime visibility rule is documented.
- [x] Repository Layer Matrix is complete.
- [x] Repository Import Matrix is complete.
- [x] Import Decision Algorithm is defined.
- [x] Wildcard and relative import policies are defined.

---

# Completion Marker

**Document ID**

M-04

**Document Name**

Import Graph

**Version**

1.1 Canonical

**Status**

COMPLETE

**Canonical Authority**

Wave 1 Import Source of Truth

No document may redefine import ownership established by M-04.
