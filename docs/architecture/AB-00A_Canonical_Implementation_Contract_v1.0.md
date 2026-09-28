# AB-00A — Canonical Implementation Contract v1.0

**Document ID:** AB-00A  
**Status:** CANONICAL IMPLEMENTATION CONTRACT — WAVE 1  
**Authority:** Derived from the Frozen AURORA Engineering Architecture and approved architecture decisions  
**Purpose:** Convert frozen architecture into explicit implementation constraints for Codex / Build agents.  
**Scope:** AURORA Wave 1 — Kernel Runtime  
**Current Build State:** Repository frozen pending reconciliation and KR-004 restart.

---

# 1. PURPOSE

This document is the implementation-facing contract between the AURORA Frozen Architecture and source-code implementation.

The implementation agent MUST use this document together with:

1. `AGENTS.md`
2. `docs/architecture/AURORA_Wave1_Implementation_Handoff_v1.0.md`
3. the current repository state

The implementation agent MUST NOT reconstruct missing architecture from intuition.

Where this document is explicit, it is authoritative for Wave 1 implementation.

Where this document is intentionally silent, the implementation agent MUST NOT invent a new architectural rule.

A missing implementation detail is not permission to redesign the system.

---

# 2. AUTHORITY MODEL

The architecture authority chain is:

```text
Frozen Engineering Architecture
        ↓
Architecture Freeze / Approved ADRs
        ↓
AB-00A Canonical Implementation Contract
        ↓
AURORA Wave 1 Implementation Handoff
        ↓
AGENTS.md operational rules
        ↓
Current implementation
```

Lower layers cannot silently override higher layers.

Existing source code is implementation state, not architectural authority.

---

# 3. CURRENT REPOSITORY STATE

The current repository contains implementation attempts for:

- W1.01 Foundation Core
- W1.02 Configuration Runtime
- W1.03 Logging Runtime
- W1.04 Kernel Contracts

Current required state:

```text
KR-001  reconciliation required
KR-002  reconciliation required
KR-003  reconciliation required
KR-004  restart required
W1.11   tests missing
```

Until the reconciliation is complete:

- do not continue KR-004,
- do not begin KR-005,
- do not silently redesign earlier modules,
- do not apply automatic fixes that hide architectural problems.

---

# 4. AURORA RUNTIME CONSTITUTION

AURORA runtime layers are ordered:

```text
L0  Kernel
L1  State
L2  Layout
L3  Theme
L4  Motion
L5  Interaction
L6  Accessibility
L7  Platform Bridge
L8  Render
```

The dependency graph is directed downward through the runtime architecture.

Lower layers MUST NOT depend on higher layers.

Cyclic dependencies are forbidden.

---

# 5. GLOBAL RUNTIME INVARIANTS

## 5.1 Single Source of Truth

Runtime state has one authoritative owner.

Duplicated mutable runtime truth is forbidden.

## 5.2 Render Is Read-Only

Render consumes runtime state/snapshots.

Render MUST NOT mutate runtime state.

## 5.3 Diagnostics Are Read-Only

Diagnostics may inspect runtime state.

Diagnostics MUST NOT mutate runtime state.

## 5.4 Resolver Graphs Are DAGs

Resolver graphs MUST NOT contain cycles.

## 5.5 No Hidden Mutable Global Runtime Ownership

Runtime state and runtime services MUST NOT rely on uncontrolled mutable process-global ownership.

Where an Application-scoped resource exists, its ownership must be explicit.

## 5.6 Explicit Dependency Ownership

Dependencies must have an identifiable owner.

Hidden service locators and uncontrolled global registries are forbidden.

---

# 6. DI SCOPE MODEL

The frozen DI scope model contains exactly:

```text
Application
Session
Pipeline
Transient
```

No additional scope is authorized by this contract.

Scope semantics:

| Scope | Lifetime / Owner |
|---|---|
| Application | Application-wide runtime lifetime |
| Session | One runtime session |
| Pipeline | One pipeline execution |
| Transient | Single transient resolution / use |

Implementation requirements:

- scope must be explicit;
- scope ownership must be deterministic;
- scope behavior must not be inferred from module-global state;
- a later stage must not silently redefine scope semantics.

---

# 7. TYPED EVENT RUNTIME

AURORA Event Bus is a Typed Event Runtime.

Every runtime event contains these mandatory fields:

```text
event_id
event_type
session_id
timestamp
payload
trace
```

These are required contract fields.

The event contract must remain typed.

Public event contracts MUST NOT use unparameterized collections.

Preferred examples:

```python
dict[str, object]
list[str]
tuple[str, ...]
```

or a more specific canonical project type when defined.

Do not use bare:

```python
dict
list
set
```

in public contracts.

Do not use `dict[str, Any]` in a public canonical contract when a narrower type is available.

---

# 8. RUNTIME MODULE MANIFEST

Every runtime module participating in the runtime module system has a manifest containing:

```text
module_id
runtime_layer
depends_on
provides
version
```

All five fields are mandatory.

Required semantics:

| Field | Responsibility |
|---|---|
| `module_id` | Unique runtime module identity |
| `runtime_layer` | Runtime layer ownership |
| `depends_on` | Declared module dependencies |
| `provides` | Capabilities / services exposed by the module |
| `version` | Module contract/version identity |

`provides` MUST NOT be omitted.

The manifest is a runtime contract, not an informational comment.

---

# 9. WAVE 1 OWNERSHIP MATRIX

## W1.01 — Foundation Core

Canonical files:

```text
src/core/__init__.py
src/core/constants.py
src/core/exceptions.py
src/core/types.py
src/core/version.py
```

Responsibility:

- foundational types;
- foundational constants;
- foundational exceptions;
- project version metadata.

Must NOT implement:

- configuration runtime;
- logging runtime;
- dependency injection;
- event dispatch;
- pipeline orchestration;
- runtime bootstrapping.

---

## W1.02 — Configuration Runtime

Canonical files:

```text
src/core/settings.py
src/core/config.py
```

Responsibility:

- configuration models;
- environment/configuration loading;
- configuration access as defined by the architecture.

Must NOT implement:

- DI container;
- Event Bus;
- Pipeline orchestration.

---

## W1.03 — Logging Runtime

Canonical files:

```text
src/core/logging_config.py
src/core/logger.py
```

Responsibility:

- logging configuration;
- project logging API;
- log context behavior required by the architecture.

Logging implementation MUST remain explicit and testable.

No new generic logging helper package may be created without architecture approval.

---

## W1.04 — Kernel Contracts

Canonical files:

```text
src/kernel/contracts/__init__.py
src/kernel/contracts/context.py
src/kernel/contracts/events.py
src/kernel/contracts/lifecycle.py
src/kernel/contracts/module.py
src/kernel/contracts/runtime.py
src/kernel/contracts/service.py
```

Responsibility:

- define contracts;
- define type boundaries;
- define manifest/event/lifecycle/service/runtime interfaces.

Must NOT implement:

- concrete DI container;
- event dispatch engine;
- runtime bootstrap;
- filesystem/network I/O;
- subprocesses;
- background workers;
- provider execution.

---

## W1.05 — Dependency Injection

Implementation is not authorized until W1.04 is approved.

Responsibility:

- container/runtime registration;
- explicit scope ownership;
- service resolution.

---

## W1.06 — Lifecycle

Responsibility:

- concrete lifecycle runtime;
- lifecycle transitions;
- lifecycle coordination.

The exact implementation must respect the approved lifecycle contract.

---

## W1.07 — Event Bus

Responsibility:

- concrete typed event runtime;
- registration;
- dispatch;
- delivery semantics.

It must consume the W1.04 event contracts rather than redefining them.

---

## W1.08 — Pipeline Context

Responsibility:

- concrete pipeline execution context.

It must not redefine the kernel contract types.

---

## W1.09 — Pipeline Orchestrator

Responsibility:

- pipeline orchestration.

It must not be implemented in W1.04 or W1.05.

---

## W1.10 — Runner / Bootstrap

Responsibility:

- application/runtime bootstrap;
- composition of previously implemented runtime pieces.

Bootstrap must not leak into contracts.

---

## W1.11 — Kernel Test Suite

Responsibility:

- actual executable tests for Wave 1.

A test directory existing without test files does not satisfy W1.11.

---

# 10. KR-004 CONTRACT REGISTRY

KR-004 is a contract-only package.

No concrete runtime implementation is allowed.

## 10.1 `context.py`

Defines the runtime execution/context contract.

Requirements:

- contract-only;
- explicit typed fields;
- immutable contract representation where the contract specifies immutability;
- mutable defaults must use factories;
- no I/O;
- no orchestration.

Metadata must be explicitly typed.

A public contract must not expose `dict[str, Any]` merely for convenience.

---

## 10.2 `events.py`

Defines the typed event contract.

The canonical event contains:

```text
event_id
event_type
session_id
timestamp
payload
trace
```

All required event fields must be represented explicitly.

Dataclass implementations must satisfy:

- required fields before defaulted fields;
- mutable values through factories;
- explicit typing;
- no implicit `Any`;
- no concrete dispatch behavior.

---

## 10.3 `lifecycle.py`

Defines lifecycle contract boundaries.

The contract must be explicit and non-empty.

Lifecycle behavior belongs here at the interface/contract level only.

Concrete lifecycle execution belongs to W1.06.

Do not invent new states or transitions solely for implementation convenience.

---

## 10.4 `module.py`

Defines the runtime module manifest contract.

The manifest must include:

```text
module_id
runtime_layer
depends_on
provides
version
```

Dependencies and provided capabilities must be represented explicitly.

---

## 10.5 `runtime.py`

Defines the runtime contract boundary.

The module must remain contract-only.

No bootstrap logic.

No concrete runtime startup sequence.

No process-level runtime singleton.

Concrete runtime behavior belongs to later implementation stages.

---

## 10.6 `service.py`

Defines the service boundary.

The service contract must explicitly expose initialization and shutdown behavior.

The service abstraction must be non-empty.

The implementation type, where represented in a public descriptor, must be parameterized sufficiently to express compatibility with the service contract.

---

# 11. RUNTIME EVENT CONTRACT

Canonical runtime event data:

```text
event_id    : typed event identifier
event_type  : typed event category
session_id  : typed session identifier
timestamp   : datetime
payload     : typed payload
trace       : typed trace context
```

Required invariants:

- all mandatory fields are present;
- the event is immutable when modeled as a frozen dataclass;
- timestamp uses an explicit default factory when defaulted;
- trace uses an explicit default factory when defaulted;
- payload is explicitly typed;
- the event carries no dispatch behavior.

---

# 12. TYPE SAFETY CONTRACT

Python:

```text
3.13
```

Static analysis:

```text
Pyright
```

Typing requirements:

- public collections must be parameterized;
- avoid implicit `Any`;
- avoid `Unknown`;
- avoid bare `type`;
- avoid mutable dataclass defaults;
- use `field(default_factory=...)` for mutable values;
- required fields precede defaulted fields.

Modern Python 3.13 typing syntax is preferred where consistent with the project.

Do not introduce a new type abstraction solely to silence Pyright.

---

# 13. CANONICAL TYPE BOUNDARIES

The project uses typed identifiers and contract-specific types where required.

Examples of canonical conceptual categories include:

```text
ModuleId
SessionId
PipelineId
EventId
TraceId
Metadata
Payload
Headers
```

The exact Python representation of any type alias MUST only be changed through the canonical contract.

Do not introduce competing identifiers such as:

```text
RuntimeId
ContextId
ExecutionId
RequestId
```

for the same architectural concept without explicit approval.

---

# 14. IMPORT BOUNDARIES

## Foundation

May depend on:

- Python standard library;
- explicitly approved foundational dependencies.

## Configuration

May depend on:

- Foundation.

## Logging

May depend on:

- Foundation;
- Configuration where required by the approved contract.

## Kernel Contracts

May depend on:

- Foundation;
- sibling contract modules.

Must NOT depend on:

- DI implementation;
- Event Bus implementation;
- Pipeline implementation;
- Renderer;
- Theme;
- Layout;
- higher runtime layers.

## Implementations

Concrete implementation stages may consume approved lower-level contracts according to the runtime DAG.

They must not modify those contracts implicitly.

---

# 15. FILE CREATION RULE

A production file must satisfy all of the following:

1. canonical path;
2. canonical owner;
3. active implementation stage;
4. contract-defined responsibility;
5. allowed dependency direction.

If any condition fails:

**STOP.**

Do not create a convenience module.

Forbidden examples unless separately approved:

```text
src/utils/
src/utils/helpers.py
generic models.py
misc.py
common.py
shared_runtime.py
```

A generic dumping-ground module is not an acceptable substitute for proper ownership.

---

# 16. CONFIGURATION AND LOGGING OWNERSHIP

Configuration and logging are Wave 1 runtime foundations.

The no-hidden-global-state invariant applies to mutable runtime ownership.

This does NOT automatically prohibit every use of:

- standard-library caching;
- `ContextVar`;
- logger registries;
- immutable process-level configuration.

Instead, implementation must distinguish:

1. immutable configuration data;
2. process-wide infrastructure state;
3. mutable runtime state;
4. DI-owned runtime resources.

A mechanism is forbidden when it creates uncontrolled mutable runtime ownership or bypasses the DI/lifecycle model.

Do not classify a particular technique as an Architecture Conflict without comparing its actual semantics with the frozen ownership model.

---

# 17. LIFECYCLE CONTRACT

The lifecycle model is explicit.

The implementation must preserve the approved lifecycle vocabulary and transition rules.

No additional lifecycle state is authorized merely to simplify code.

Where lifecycle behavior is not specified in the current implementation-facing contract, the agent must not invent an architectural state.

---

# 18. CONTRACT-ONLY PACKAGE RULE

KR-004 source files must not:

- perform I/O;
- open network connections;
- create threads;
- create subprocesses;
- dispatch events;
- resolve application services;
- bootstrap runtime;
- mutate global runtime state;
- perform business logic;
- contain concrete provider integrations.

The package describes contracts.

Later stages implement behavior.

---

# 19. TEST CONTRACT

Wave 1 testing must contain actual executable tests.

Canonical minimum coverage:

```text
tests/core/test_types.py
tests/core/test_settings.py
tests/core/test_logger.py
tests/kernel/test_contracts.py
```

Tests may be split or expanded where necessary, but the module owner must remain clear.

Testing requirements:

- pytest must discover tests;
- tests must execute;
- tests must pass.

This is NOT acceptable evidence:

```text
collected 0 items
```

A successful process exit with zero collected tests is not a completed test gate.

---

# 20. VALIDATION GATE

The required local validation sequence is:

```powershell
uv run pyright
uv run ruff check .
uv run pytest
```

All three gates must pass before module approval.

## Pyright

Target:

```text
0 errors
0 warnings
0 informations
```

## Ruff

Target:

```text
0 violations
```

## Pytest

Required:

- tests collected;
- tests executed;
- tests passed.

---

# 21. AUTOMATIC FIX POLICY

Automatic tooling may be used for mechanical corrections such as:

- import ordering;
- formatting.

Automatic fixes MUST NOT be used to:

- restructure architecture;
- rename ownership;
- introduce compatibility layers;
- alter contracts;
- add new abstractions;
- move files between stages.

When a lint error exposes a contract problem, address the contract issue rather than mechanically hiding the symptom.

---

# 22. ERROR CLASSIFICATION

## Mechanical

Examples:

- import order;
- formatting.

May be fixed locally.

## Local Implementation Defect

Examples:

- incorrect annotation;
- missing default factory;
- invalid dataclass ordering;
- missing abstract implementation required by the already-approved contract.

May be repaired in the current module.

## Contract Conflict

Examples:

- missing mandatory field;
- wrong public field type;
- file ownership mismatch;
- dependency outside the allowed boundary.

Requires reconciliation before implementation proceeds.

## Architecture Conflict

Examples:

- new dependency direction;
- new DI scope;
- new runtime layer;
- new event semantics;
- changed ownership model.

Requires RFC/ADR.

The implementation agent must not silently change architecture.

---

# 23. BUILD PRECHECK

Before implementing a file, the Build agent must verify:

```text
[ ] active stage
[ ] canonical owner
[ ] canonical path
[ ] approved public contract
[ ] allowed imports
[ ] no higher-layer dependency
[ ] no duplicate abstraction
[ ] typing rules satisfied
[ ] test requirement identified
```

If any item cannot be established:

**STOP and report the missing contract.**

---

# 24. ONE-FILE IMPLEMENTATION RULE

The build workflow uses one production file or one test file at a time.

For each file:

```text
read contract
    ↓
implement
    ↓
validate
    ↓
report
```

Do not batch unrelated production files.

Do not advance to the next file while the current file is red.

---

# 25. MODULE RESTART RULE

A module requires clean restart when:

- an architecture conflict is found;
- the public contract is materially wrong;
- implementation has accumulated repeated incompatible patches;
- ownership has become unclear;
- the module can no longer be explained cleanly from the canonical contract.

KR-004 currently satisfies the restart condition.

KR-004 must therefore be regenerated cleanly rather than endlessly patched.

---

# 26. CURRENT KR-004 RESTART TARGET

The target package is:

```text
src/kernel/contracts/
├── __init__.py
├── context.py
├── events.py
├── lifecycle.py
├── module.py
├── runtime.py
└── service.py
```

The restart must:

1. preserve the contract-only boundary;
2. include the full mandatory event schema;
3. include the complete runtime module manifest schema;
4. maintain the DI scope vocabulary;
5. use strict typing;
6. use valid dataclass ordering;
7. avoid mutable defaults;
8. expose explicit lifecycle/service behavior;
9. avoid concrete runtime implementation.

---

# 27. TECH LEAD REVIEW GATE

A module is not approved because commands happened to exit successfully.

Tech Lead review must verify:

```text
Architecture
Ownership
Dependencies
Contract Surface
Typing
Testing
Stage Isolation
Runtime Invariants
```

Approval means all of those are coherent.

---

# 28. FREEZE RULE

After Tech Lead approval:

- module contract is treated as frozen;
- implementation proceeds only within that contract;
- architectural changes require RFC/ADR;
- downstream modules consume the frozen interface.

No informal redesign is permitted.

---

# 29. FORBIDDEN ARCHITECTURE CHANGES DURING IMPLEMENTATION

Without RFC/ADR, do not:

- add runtime layers;
- add DI scopes;
- alter event schema;
- remove mandatory manifest fields;
- change ownership model;
- introduce global runtime state;
- create cross-layer cycles;
- introduce a new canonical abstraction for an existing concept.

---

# 30. CODEx / BUILD EXECUTION PROTOCOL

Every Wave 1 implementation cycle is:

```text
1. Read AGENTS.md
2. Read AB-00A
3. Read Wave 1 Implementation Handoff
4. Inspect repository
5. Preflight active module
6. Select exactly one file
7. Verify contract
8. Implement
9. Run Pyright
10. Run Ruff
11. Run Pytest
12. Report result
13. Stop
14. Tech Lead review
15. Continue only after approval
```

The agent must never skip directly from architecture reading to uncontrolled multi-file implementation.

---

# 31. CURRENT AUTHORIZATION

At the moment this document is established:

```text
Repository: FROZEN
KR-004: RESTART REQUIRED
KR-005: NOT AUTHORIZED
W1.11: REQUIRED
```

The next permitted implementation action is:

```text
KR-004 contract reconciliation
        ↓
clean regeneration
        ↓
tests
        ↓
validation
        ↓
Tech Lead approval
```

---

# 32. FINAL IMPLEMENTATION PRINCIPLE

AURORA implementation is not:

```text
code → lint → patch → patch → patch
```

It is:

```text
architecture
    ↓
explicit implementation contract
    ↓
owned file
    ↓
typed implementation
    ↓
tests
    ↓
validation
    ↓
Tech Lead approval
    ↓
freeze
```

The implementation agent is not authorized to fill architectural gaps with invention.

The purpose of AB-00A is to make the intended architecture executable as a deterministic implementation contract.
