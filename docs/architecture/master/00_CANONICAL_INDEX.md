# AURORA ENGINEERING BIBLE v1.1

Document ID: M-00

Document Name: Canonical Architecture Index

Path:
docs/architecture/master/00_CANONICAL_INDEX.md

Status: CANONICAL SOURCE OF TRUTH

Authority:
- AB-00 Development Constitution
- Architecture Freeze v1.0
- All Master Documents M-01…M-11 (+ M-03A)

Version: 1.1 Canonical

---

# Purpose

This document is the navigation root of the entire AURORA Engineering Bible.

Every implementation session MUST begin with this document.

The purpose of M-00 is to:

- define the complete documentation hierarchy;
- define the document loading order;
- define ownership of every document;
- define which documents are authoritative for each engineering task;
- minimize Codex context usage by allowing selective loading.

Codex must never scan documentation arbitrarily.

Codex loads documents according to this index only.

---

# Engineering Bible Hierarchy

The Engineering Bible consists of canonical master documents.

| ID | Document | Owner | Status |
|----|----------|-------|--------|
| AB-00 | Development Constitution | Tech Lead | Canonical |
| AB-00A | Architecture Reconciliation | Tech Lead | Canonical |
| M-00 | Canonical Index | Tech Lead | Canonical |
| M-01 | File Registry | Architecture | Canonical |
| M-02 | Runtime Graph | Architecture | Canonical |
| M-03 | Public API Registry | Architecture | Canonical |
| M-04 | Import Graph | Architecture | Canonical |
| M-05 | State event di lifecycle registry | Architecture | Canonical |
| M-06 | Module Specifications | Engineering | Canonical |
| M-07 | Implementation Rules | Engineering | Canonical |
| M-08 | Codex Master Prompt | Engineering | Canonical |
| M-09 | Build Validation Protocol | Engineering | Canonical |
| M-10 | ADR Registry | Architecture | Canonical |

No additional master documents may exist.

---

# Canonical Loading Order

Codex loads documentation in deterministic order.

## Stage 0 — Constitution

Always read:

1. AGENTS.md
2. AB-00
3. AB-00A
4. M-00

These documents define repository law.

---

## Stage 1 — Repository Structure

Read only when repository structure is required.

- M-01
- M-02

---

## Stage 2 — Public Interfaces

Read only when APIs or imports are required.

- M-03
- M-03A
- M-04

---

## Stage 3 — Runtime Architecture

Read only when runtime ownership is required.

- M-05

---

## Stage 4 — Implementation

Read before generating code.

- M-06
- M-07

---

## Stage 5 — Generation Protocol

Read immediately before implementation.

- M-08

---

## Stage 6 — Validation

Read before Postflight.

- M-09

---

## Stage 7 — Architecture Decisions

Read only if referenced.

- M-10

---

# Repository Navigation Map

```
docs/
└── architecture/
    ├── AGENTS.md
    ├── AB-00_Development_Constitution.md
    ├── AB-00A_Architecture_Reconciliation.md
    └── master/
        ├── 00_CANONICAL_INDEX.md
        ├── 01_FILE_REGISTRY.md
        ├── 02_DIRECTORY_BLUEPRINT.md
        ├── 03_PUBLIC_API_REGISTRY.md
        ├── 04_IMPORT_GRAPH.md
        ├── 05_RUNTIME_REGISTRY.md
        ├── 06_MODULE_SPECIFICATIONS.md
        ├── 07_IMPLEMENTATION_RULES.md
        ├── 08_CODEX_MASTER_PROMPT.md
        ├── 09_BUILD_VALIDATION_PROTOCOL.md
        └── 10_ADR_REGISTRY.md
```

Directory names are frozen.

---

# Runtime Layer Index

AURORA runtime hierarchy is frozen.

| Layer | Name | Description |
|-------|------|-------------|
| L0 | Kernel | Runtime infrastructure. |
| L1 | State | Shared runtime state. |
| L2 | Layout | Layout engine. |
| L3 | Theme | Theme engine. |
| L4 | Motion | Animation runtime. |
| L5 | Interaction | User interaction runtime. |
| L6 | Accessibility | Accessibility runtime. |
| L7 | Platform | Browser/platform integration. |
| L8 | Render | Rendering runtime. |

No additional runtime layers exist.

---

# Kernel Runtime Index

Wave 1 consists of eleven KR modules.

| KR | Runtime | Owner Document |
|----|---------|----------------|
| KR-001 | Foundation Core | M-06 |
| KR-002 | Configuration Runtime | M-06 |
| KR-003 | Logging Runtime | M-06 |
| KR-004 | Kernel Contracts | M-06 |
| KR-005 | DI Runtime | M-06 |
| KR-006 | Lifecycle Runtime | M-06 |
| KR-007 | Event Bus Runtime | M-06 |
| KR-008 | Runtime Context Runtime | M-06 |
| KR-009 | Pipeline Runtime | M-06 |
| KR-010 | Bootstrap Runtime | M-06 |
| KR-011 | Test Suite | M-06 |

Implementation order is frozen.

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

# Document Responsibility Matrix

## M-01 — File Registry

Defines:

- every production file;
- owner KR;
- exports;
- dependencies.

Does NOT define implementation.

---

## M-02 — Runtime Graph

Defines:

- repository folders;
- allowed contents;
- forbidden contents;
- ownership boundaries.

Does NOT define APIs.

---

## M-03 — Public API Registry

Defines:

- every public function;
- every public class;
- every dataclass;
- every exported symbol.

No implementation.

---

## M-04 — Import Graph

Defines:

- allowed imports;
- forbidden imports;
- dependency direction;
- circular dependency prevention.

---

## M-05 —  State event di lifecycle registry

Defines:

- runtime ownership;
- runtime lifecycle;
- runtime communication;
- runtime creation/destruction.

---

## M-06 — Module Specifications

Defines implementation contracts for every production file.

Contains:

- file blueprint;
- methods;
- dataclasses;
- constants;
- exceptions;
- validation rules.

---

## M-07 — Implementation Rules

Defines coding constitution.

Contains:

- typing rules;
- dataclass rules;
- logging rules;
- DI rules;
- event rules;
- testing rules;
- Ruff/Pyright constitution.

---

## M-08 — Codex Master Prompt

Defines implementation protocol.

Contains:

- preflight;
- generation rules;
- self-validation;
- postflight.

---

## M-09 — Build Validation Protocol

Defines repository validation pipeline.

Contains:

- Ruff;
- Pyright;
- Pytest;
- Build Report;
- DoD validation.

---

## M-10 — ADR Registry

Defines architecture decisions.

Every ADR has immutable ID.

No implementation inside ADRs.

---

# Engineering Task → Required Documents

| Task | Required Documents |
|------|--------------------|
| New file implementation | M-01, M-03, M-04, M-06, M-07 |
| Repository audit | AB-00, AB-00A, M-00, M-01, M-04, M-05 |
| Typing fix | M-03, M-06, M-07 |
| Import fix | M-04, M-07 |
| Runtime implementation | M-05, M-06 |
| Test implementation | M-06, M-07, M-09 |
| Bootstrap implementation | M-05, M-06, M-07 |
| Full Wave implementation | M-00…M-09 |

Codex loads only required documents.

---

# Repository Validation Order

Every build validates in this order.

## Phase 1

Architecture Validation

- ownership;
- directories;
- imports.

## Phase 2

Static Validation

- Ruff.
- Ruff Format.
- Pyright.

## Phase 3

Runtime Validation

- lifecycle;
- DI;
- EventBus;
- Context;
- Pipeline.

## Phase 4

Testing Validation

- unit tests;
- integration tests.

## Phase 5

Definition of Done Validation.

---

# Canonical Runtime Ownership Summary

| Runtime | Created By | Destroyed By |
|----------|------------|--------------|
| Settings | BootstrapRuntime | Process exit |
| Logger | BootstrapRuntime | Process exit |
| Container | BootstrapRuntime | Lifecycle shutdown |
| Lifecycle | BootstrapRuntime | Bootstrap shutdown |
| EventBus | BootstrapRuntime | Lifecycle shutdown |
| Context | BootstrapRuntime | Session shutdown |
| Pipeline | OrchestratorRuntime | Pipeline completion |
| RuntimeKernel | BootstrapRuntime | Process shutdown |

Ownership is unique.

---

# Global Invariants

The following invariants are repository law.

## Architecture Invariants

- One KR owns one runtime.
- One runtime owns one responsibility.
- One public API owner.
- One implementation owner.

## Typing Invariants

- No Any in public APIs.
- JSON-compatible payloads.
- Immutable contracts.

## Runtime Invariants

- No hidden mutable globals.
- No circular dependencies.
- No runtime created outside Bootstrap.

## Validation Invariants

Repository is considered valid only if:

- Ruff passes.
- Pyright passes.
- Pytest passes.
- Definition of Done passes.

---

# Canonical Completion Marker

Document ID: M-00

Document Name: Canonical Architecture Index

Version: 1.1 Canonical

Status: COMPLETE

Authority: AURORA Engineering Bible v1.1

END OF DOCUMENT