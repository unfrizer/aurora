# AURORA — File / API / Dependency Registry v1.0

**Status:** ACTIVE IMPLEMENTATION REGISTRY  
**Scope:** Wave 1  
**Purpose:** Make every source-file boundary explicit before Codex implementation.

---

# 1. Registry Semantics

Every production file must have:

```text
File ID
Path
Module
Stage
Runtime Layer
Owner
Purpose
Public Symbols
Public Signatures
Consumed Symbols
Dependencies
Allowed Imports
Forbidden Imports
State Ownership
Lifecycle
Events
DI Scope
Exceptions
Tests
Acceptance Criteria
```

Values marked `UNSPECIFIED` are intentionally unresolved and MUST NOT be invented by Codex.

---

# 2. W1.01 — FOUNDATION CORE

## F-W101-01

Path:
```text
src/core/__init__.py
```

Owner:
```text
W1.01 Foundation Core
```

Purpose:
Public Foundation Core package surface.

Consumes:
```text
src.core.types
src.core.version
```

Must not contain:
```text
configuration implementation
logging implementation
DI implementation
Event Bus implementation
pipeline implementation
bootstrap
```

Public API:
Must export only symbols whose ownership is explicitly established by KR-001.

Exact final export list:
**Derived from current reconciled implementation; no new exports may be introduced.**

Tests:
```text
tests/core/test_types.py
```

---

## F-W101-02

Path:
```text
src/core/constants.py
```

Purpose:
Foundational constants and canonical constant re-exports.

Required manifest fields:
```text
module_id
runtime_layer
depends_on
provides
version
```

Runtime-layer semantic values:
```text
L0 Kernel
L1 State
L2 Layout
L3 Theme
L4 Motion
L5 Interaction
L6 Accessibility
L7 Platform Bridge
L8 Render
```

Version ownership:
`version.py` is canonical.

Rule:
Do not duplicate canonical version facts.

---

## F-W101-03

Path:
```text
src/core/exceptions.py
```

Purpose:
Foundational exception taxonomy.

Constraint:
Existing approved exception concepts may be preserved only where already established by the project contract.

Do not create convenience exception classes to compensate for missing later-stage APIs.

---

## F-W101-04

Path:
```text
src/core/types.py
```

Purpose:
Canonical Foundation type system.

Confirmed public concepts:
```text
ModuleId
SessionId
PipelineId
ServiceId
EventId
TraceId

JSONPrimitive
JSONValue
JSONDict
Payload
Metadata
Headers

RuntimeLayer
DIScope
RuntimeStatus
HealthStatus
EventPhase
EventPriority
```

Forbidden:
```text
RuntimeId
```

Canonical Metadata:
```text
Metadata = JSONDict
```

Canonical JSON semantics:
```text
JSONPrimitive =
    str | int | float | bool | None

JSONValue =
    JSONPrimitive
    | list[JSONValue]
    | dict[str, JSONValue]

JSONDict =
    dict[str, JSONValue]
```

Unresolved:
Exact public semantics of EventPhase/EventPriority/RuntimeStatus beyond currently preserved vocabulary.

---

## F-W101-05

Path:
```text
src/core/version.py
```

Purpose:
Single canonical owner of project/version/architecture version facts.

Canonical owner for duplicated facts:
```text
PROJECT_NAME
PROJECT_DISPLAY_NAME
ARCHITECTURE_VERSION
ARCHITECTURE_FREEZE
PYTHON_VERSION
ENGINE_VERSION
ENGINE_STAGE
```

Additional current version facts may remain where they are already canonical.

No competing definitions in `constants.py`.

---

# 3. W1.02 — CONFIGURATION

## F-W102-01

Path:
```text
src/core/settings.py
```

Purpose:
Immutable configuration model.

Constraints:
- configuration only;
- immutable semantics;
- explicit types;
- no DI container;
- no Event Bus;
- no pipeline orchestration.

Public API:
**EXACT SIGNATURES MUST BE EXTRACTED FROM THE CURRENT APPROVED SOURCE BEFORE FINAL FREEZE.**

Tests:
```text
tests/core/test_settings.py
```

---

## F-W102-02

Path:
```text
src/core/config.py
```

Purpose:
Configuration/environment loading and access.

Approved caching:
Application-wide caching of immutable configuration is allowed.

Do not remove `lru_cache` solely because it is process-level.

Forbidden:
- DI container;
- Event Bus;
- pipeline orchestration.

---

# 4. W1.03 — LOGGING

## F-W103-01

Path:
```text
src/core/logging_config.py
```

Purpose:
Logging configuration and execution/log context behavior.

Allowed infrastructure:
```text
ContextVar
standard logging registry
logger caching
module-level standard-library logger
```

provided these are not authoritative mutable AURORA runtime-state ownership.

---

## F-W103-02

Path:
```text
src/core/logger.py
```

Purpose:
AURORA logging API.

Must remain:
- explicit;
- typed;
- testable;
- free of runtime-state ownership.

Tests:
```text
tests/core/test_logger.py
```

---

# 5. W1.04 — KERNEL CONTRACTS

## F-W104-01

Path:
```text
src/kernel/contracts/__init__.py
```

Purpose:
Contract package exports.

Only contract symbols may be exported.

---

## F-W104-02

Path:
```text
src/kernel/contracts/context.py
```

Purpose:
Kernel execution/context contract.

Requirements:
- contract-only;
- immutable contract representation where specified;
- canonical Metadata type;
- safe defaults;
- no I/O;
- no orchestration.

Consumers:
Later runtime infrastructure.

---

## F-W104-03

Path:
```text
src/kernel/contracts/events.py
```

Purpose:
Typed Event Runtime contract.

Mandatory fields:
```text
event_id
event_type
session_id
timestamp
payload
trace
```

Dataclass requirements:
- valid required/default field ordering;
- explicit typing;
- factory defaults for mutable structures;
- no dispatch implementation.

---

## F-W104-04

Path:
```text
src/kernel/contracts/lifecycle.py
```

Purpose:
Lifecycle contract boundary.

Constraint:
Do not invent lifecycle states/transitions.

Exact final API:
**MUST COME FROM AUTHORITATIVE LIFECYCLE CONTRACT.**

---

## F-W104-05

Path:
```text
src/kernel/contracts/module.py
```

Purpose:
Runtime module manifest contract.

Required:
```text
module_id
runtime_layer
depends_on
provides
version
```

`provides` is mandatory.

---

## F-W104-06

Path:
```text
src/kernel/contracts/runtime.py
```

Purpose:
Runtime contract boundary.

Must not:
- bootstrap;
- perform concrete runtime startup;
- contain provider logic;
- mutate global state.

Exact final API:
**MUST COME FROM AUTHORITATIVE RUNTIME CONTRACT.**

---

## F-W104-07

Path:
```text
src/kernel/contracts/service.py
```

Purpose:
Service contract and descriptor boundary.

Required service lifecycle:
```text
initialize()
shutdown()
```

Implementation type boundary:
Must express compatibility with `ServiceContract`.

Bare:
```python
type
```
is forbidden.

---

# 6. W1.05 — DEPENDENCY INJECTION

Status:
```text
CONTRACT MUST BE COMPLETED BEFORE IMPLEMENTATION
```

Known constraints:
```text
Application
Session
Pipeline
Transient
```

Required unknowns to resolve before implementation:
```text
exact file set
container class
registration API
resolution API
scope storage representation
provider contract
disposal semantics
circular dependency behavior
scope violation behavior
exception taxonomy
tests
```

---

# 7. W1.06 — LIFECYCLE

Status:
```text
CONTRACT MUST BE COMPLETED BEFORE IMPLEMENTATION
```

Known responsibility:
- concrete lifecycle runtime;
- lifecycle transitions;
- lifecycle coordination.

Unknowns to resolve:
```text
exact file set
exact public API
authoritative states
transition matrix
failure semantics
restart semantics
shutdown semantics
tests
```

---

# 8. W1.07 — EVENT BUS

Status:
```text
CONTRACT MUST BE COMPLETED BEFORE IMPLEMENTATION
```

Known responsibility:
- typed event runtime;
- registration;
- dispatch;
- delivery semantics.

Frozen input event schema:
```text
event_id
event_type
session_id
timestamp
payload
trace
```

Unknowns:
```text
exact file set
handler protocol
subscription identity
publish API
dispatch ordering
error propagation
handler lifecycle
concurrency model
tests
```

No invention is permitted.

---

# 9. W1.08 — PIPELINE CONTEXT

Status:
```text
CONTRACT MUST BE COMPLETED BEFORE IMPLEMENTATION
```

Known:
Concrete pipeline execution context.

Unknown:
exact file/API/ownership/lifecycle/dependencies/tests.

---

# 10. W1.09 — PIPELINE ORCHESTRATOR

Status:
```text
CONTRACT MUST BE COMPLETED BEFORE IMPLEMENTATION
```

Known:
Pipeline orchestration.

Must not be implemented in W1.04 or W1.05.

Unknown:
exact file/API/state machine/dependencies/tests.

---

# 11. W1.10 — RUNNER / BOOTSTRAP

Status:
```text
CONTRACT MUST BE COMPLETED BEFORE IMPLEMENTATION
```

Known:
- application/runtime bootstrap;
- composition of previously approved runtime pieces.

Must not leak into contracts.

Unknown:
exact entrypoints/composition API/lifecycle/error semantics/tests.

---

# 12. W1.11 — TEST SUITE

Required minimum:
```text
tests/core/test_types.py
tests/core/test_settings.py
tests/core/test_logger.py
tests/kernel/test_contracts.py
```

The exact assertions must be derived from the corresponding module contracts.

`pytest` must discover and execute tests.

---

# 13. FILE LINKAGE RULE

Every source file must declare its direct consumers.

Every consumer must reference exact public symbols rather than broad module access.

Conceptually:

```text
producer file
    ↓ exposes
public symbol
    ↓ consumed by
consumer file
```

A dependency must never exist merely because an import "might be useful."

---

# 14. IMPLEMENTATION RULE

If an exact API/signature is not in the authoritative registry:

```text
STOP
```

Do not infer it from naming conventions.
Do not infer it from a neighboring module.
Do not infer it from an old implementation.
