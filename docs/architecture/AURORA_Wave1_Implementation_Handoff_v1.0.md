# AURORA — Wave 1 Implementation Handoff Pack v1.0

**Document ID:** AURORA-IHP-W1-001  
**Status:** ACTIVE IMPLEMENTATION HANDOFF  
**Authority:** Frozen AURORA Engineering Bible v1.0 + Architecture Freeze v1.0  
**Phase:** Wave 1 — Kernel Runtime  
**Audience:** Codex / Build Chat / Implementation Agent  
**Purpose:** Eliminate architecture inference, stage mixing, accidental file creation, and preventable type/test failures before implementation.

---

## 1. EXECUTIVE DIRECTIVE

This document is an implementation contract and build-governance layer between the Frozen AURORA Architecture and source-code implementation.

The implementation agent MUST NOT invent architecture.

The implementation agent MUST NOT create files, directories, public APIs, dependencies, abstractions, or runtime behavior merely because they appear convenient.

The implementation agent MUST treat the Frozen Architecture as the source of truth and this document as the operational handoff for Wave 1.

When a requirement is missing or ambiguous:

1. Do not guess.
2. Do not silently redesign.
3. Do not create a workaround abstraction.
4. Report the contract conflict or missing specification.
5. Stop the affected module until the contract is resolved.

The goal is not merely "code that passes Ruff/Pyright".

The goal is:

**Frozen Architecture → Explicit Implementation Contract → Isolated Module → Local Validation → Tech Lead Approval**

---

# 2. CURRENT PROJECT IDENTITY

## 2.1 Product

**AURORA**

A runtime-first visual UI engine / AI-assisted UI system.

The current implementation phase is the **Kernel Runtime foundation**.

Do not introduce ORION concepts into AURORA.

The following ORION domains are forbidden in the AURORA kernel:

- News
- Research
- Media generation
- News ranking
- News providers
- ORION-specific AI pipelines
- ORION-specific source/provider abstractions

Any such code appearing in the repository is architectural contamination and must be reported.

---

# 3. ARCHITECTURE AUTHORITY

The architecture hierarchy is:

1. Architecture Freeze v1.0
2. Canonical Bible / Engineering Bible v1.0
3. Approved ADRs
4. This Implementation Handoff Pack
5. Existing implementation
6. Agent assumptions

A lower item MUST NOT override a higher item.

Existing code is not automatically authoritative.

If existing code conflicts with the frozen architecture:

- identify the conflict,
- do not normalize the conflict by silently changing architecture,
- do not add compatibility layers without approval.

---

# 4. FROZEN RUNTIME CONSTITUTION

The runtime layer hierarchy is:

- L0 — Kernel
- L1 — State
- L2 — Layout
- L3 — Theme
- L4 — Motion
- L5 — Interaction
- L6 — Accessibility
- L7 — Platform Bridge
- L8 — Render

## 4.1 Dependency direction

Lower layers MUST NOT depend on higher layers.

The dependency graph is a DAG.

Cyclic dependencies are forbidden.

A module may depend only on explicitly permitted lower-level contracts.

---

# 5. GLOBAL RUNTIME INVARIANTS

These are implementation invariants, not suggestions.

### 5.1 Single source of truth

There is exactly one authoritative runtime state owner.

Duplicated mutable runtime truth is forbidden.

### 5.2 Render is read-only

Render consumes runtime state/snapshots.

Render MUST NOT mutate runtime state.

### 5.3 Diagnostics are read-only

Diagnostics may observe runtime information.

Diagnostics MUST NOT mutate runtime state.

### 5.4 Resolver graphs are DAGs

Resolver systems MUST NOT introduce cycles.

### 5.5 No hidden globals

Runtime ownership MUST NOT depend on mutable process-global state.

### 5.6 Explicit dependency ownership

Dependencies must be injected or explicitly owned.

Hidden service locators and uncontrolled globals are forbidden.

---

# 6. DI SCOPE MODEL — FROZEN

The dependency-injection model contains exactly these scopes:

- Application
- Session
- Pipeline
- Transient

Implementations MUST preserve these scope semantics.

Do not introduce additional scopes unless the architecture is explicitly changed through RFC/ADR.

Do not collapse all scopes into a single singleton/container behavior.

Do not make scope behavior implicit.

---

# 7. TYPED EVENT RUNTIME — FROZEN

The Event Bus is a **Typed Event Runtime**.

Every runtime event MUST have these mandatory fields:

- `event_id`
- `event_type`
- `session_id`
- `timestamp`
- `payload`
- `trace`

These fields are mandatory contract data.

The event model must remain typed.

Avoid untyped or bare collections such as:

- `dict`
- `list`
- `set`

where a typed annotation is required.

A generic payload may be represented with an explicitly typed mapping/object model, but the implementation must not leave the type ambiguous to static analysis.

---

# 8. RUNTIME MODULE MANIFEST — FROZEN

Every runtime module participating in the module runtime must expose or provide a manifest containing:

- `module_id`
- `runtime_layer`
- `depends_on`
- `provides`
- `version`

The manifest is part of the runtime contract.

Do not silently add unrelated manifest fields as architectural requirements.

---

# 9. WAVE 1 MODULE ORDER

Wave 1 implementation order:

1. W1.01 — Foundation Core
2. W1.02 — Configuration Runtime
3. W1.03 — Logging Runtime
4. W1.04 — Kernel Contracts
5. W1.05 — Dependency Injection
6. W1.06 — Lifecycle
7. W1.07 — Event Bus
8. W1.08 — Pipeline Context
9. W1.09 — Pipeline Orchestrator
10. W1.10 — Runner / Bootstrap
11. W1.11 — Kernel Test Suite

Only one module stage is active at a time.

A later stage MUST NOT be implemented early.

---

# 10. REPOSITORY BOUNDARY — WAVE 1

The relevant canonical structure is:

```text
src/
├── core/
│   ├── __init__.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── types.py
│   ├── version.py
│   ├── settings.py
│   ├── config.py
│   ├── logging_config.py
│   └── logger.py
│
├── kernel/
│   └── contracts/
│       ├── __init__.py
│       ├── context.py
│       ├── events.py
│       ├── lifecycle.py
│       ├── module.py
│       ├── runtime.py
│       └── service.py
│
├── runtime/
├── events/
├── shared/
├── theme/
├── layout/
├── motion/
├── input/
├── selection/
├── focus/
├── scroll/
├── accessibility/
├── components/
├── renderer/
├── compiler/
├── devtools/
└── ai/
```

The presence of a directory in the overall repository structure does not authorize implementation during Wave 1.

Only the currently active stage may create or modify its approved files.

---

# 11. FORBIDDEN FILE CREATION

The following are explicitly forbidden unless separately approved:

- `src/utils/helpers.py`
- ad-hoc `src/utils/` packages
- generic `models.py` files that become unowned dumping grounds
- duplicate configuration modules
- duplicate logging modules
- compatibility shims created only to hide an architecture error
- temporary production modules
- ORION-domain modules

There must be an owner for every production file.

A file without a canonical owner is a design defect.

---

# 12. FILE OWNERSHIP MAP — WAVE 1

## W1.01 — Foundation Core

Allowed:

```text
src/core/__init__.py
src/core/constants.py
src/core/exceptions.py
src/core/types.py
src/core/version.py
```

Do not place configuration or logging implementation here.

## W1.02 — Configuration Runtime

Allowed:

```text
src/core/settings.py
src/core/config.py
```

Configuration loading belongs to W1.02.

Do not move configuration into `constants.py`.

## W1.03 — Logging Runtime

Allowed:

```text
src/core/logging_config.py
src/core/logger.py
```

Logging belongs to W1.03.

Do not create additional logging helpers without approval.

## W1.04 — Kernel Contracts

Allowed:

```text
src/kernel/contracts/__init__.py
src/kernel/contracts/context.py
src/kernel/contracts/events.py
src/kernel/contracts/lifecycle.py
src/kernel/contracts/module.py
src/kernel/contracts/runtime.py
src/kernel/contracts/service.py
```

W1.04 contains contracts only.

It must not contain concrete runtime implementations.

---

# 13. KR-004 — KERNEL CONTRACTS BOUNDARY

KR-004 is currently the critical architecture boundary.

The package must remain contract-only.

Expected contract responsibilities:

### context.py

Defines the kernel execution/context contracts used by downstream runtime infrastructure.

It must not implement orchestrator logic, event dispatch, I/O, or service registration.

### events.py

Defines the typed event contract.

Mandatory event fields:

- `event_id`
- `event_type`
- `session_id`
- `timestamp`
- `payload`
- `trace`

### lifecycle.py

Defines lifecycle contracts and lifecycle semantics.

Lifecycle semantics must remain explicit and statically representable.

Do not invent additional lifecycle phases merely to simplify implementation.

### module.py

Defines the runtime module contract / module manifest boundary.

The manifest MUST preserve:

- `module_id`
- `runtime_layer`
- `depends_on`
- `provides`
- `version`

### runtime.py

Defines the runtime contract boundary.

It must not perform concrete runtime bootstrapping.

### service.py

Defines the service contract.

The service contract MUST expose explicit initialization and shutdown behavior.

The contract must contain abstract behavior rather than being an empty ABC.

---

# 14. CONTRACT-ONLY RULE

Contracts MUST NOT:

- open network connections
- touch disk for runtime operation
- start threads
- start subprocesses
- initialize concrete providers
- perform event dispatch
- instantiate application services
- create a global singleton
- mutate process-global state
- contain workflow/business logic

Contracts describe ownership and behavior.

Implementations belong to later stages.

---

# 15. STATIC TYPING RULES

Python version:

**Python 3.13**

Use modern Python 3.13 typing.

Preferred:

```python
type UserId = str
```

rather than legacy `TypeAlias` for simple aliases when appropriate.

Collections must be parameterized.

Forbidden:

```python
dict
list
set
```

when the contents are known or should be modeled.

Prefer:

```python
dict[str, object]
list[str]
set[str]
```

or an intentionally narrower contract type.

Dataclass factories must be explicit.

Avoid mutable default values.

Fields with defaults must follow fields without defaults.

Use typing that passes strict Pyright analysis.

---

# 16. DATACLASS RULES

For dataclasses:

- annotate every field,
- use `field(default_factory=...)` for mutable defaults,
- keep required fields before defaulted fields,
- do not use implicit `Any`,
- do not use untyped mappings merely to silence implementation complexity.

Example pattern:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Example:
    identifier: str
    metadata: dict[str, object] = field(default_factory=dict)
```

This example is illustrative of typing discipline, not permission to introduce a new architecture type.

---

# 17. API STABILITY RULE

Before creating a public class or function, verify:

1. it has a canonical owning module,
2. it is required by the current stage,
3. it is required by the architecture,
4. its import dependencies are permitted,
5. its behavior is defined by contract,
6. it is not duplicating another existing abstraction.

Do not create public APIs merely because they are convenient.

---

# 18. IMPORT BOUNDARY RULE

For each module:

- standard library dependencies are allowed where appropriate,
- project imports must point only toward permitted layers/contracts,
- imports from future/unimplemented stages are forbidden,
- imports that create circularity are forbidden,
- imports from ORION components are forbidden.

When unsure whether an import is architecturally permitted:

**stop and report the dependency question.**

Do not "fix" the import by adding a new shared utility.

---

# 19. BUILD PROTOCOL

Every implementation stage follows this exact order.

## Step A — Preflight

Before writing code:

- inspect current repository state,
- read this handoff pack,
- identify the active stage,
- identify the exact allowed files,
- identify dependencies,
- identify acceptance criteria.

If a requested file is not in the active stage:

**STOP.**

## Step B — Contract check

For each file:

- identify its owner,
- identify its public surface,
- identify its dependencies,
- identify its invariants.

Do not code from memory.

## Step C — Implementation

Create or modify only approved files.

One response / one active implementation file.

Do not combine unrelated stages.

## Step D — Local validation

After the file is implemented:

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

All relevant checks must be green.

## Step E — Stop on failure

If a check fails:

- diagnose,
- correct only the current stage,
- rerun the checks.

Do not start the next stage while the current stage is red.

## Step F — Tech Lead gate

The stage is not complete until the implementation has passed:

- architectural check,
- file ownership check,
- dependency check,
- Ruff,
- Pyright,
- Pytest,
- scope isolation review.

---

# 20. TESTING POLICY — CORRECTED GATE

A command that exits successfully while collecting zero tests is not equivalent to meaningful test coverage.

For a stage that declares tests as part of its Definition of Done:

- relevant tests must exist,
- tests must be collected,
- tests must execute,
- tests must pass.

`collected 0 items` MUST NOT be used as evidence that the module is tested.

This rule exists because a green tool exit code can otherwise conceal an untested implementation.

---

# 21. RUFF POLICY

Ruff is mandatory.

The agent may use:

```powershell
uv run ruff check .
```

Automatic fixes are allowed only for mechanical issues such as:

- import ordering,
- formatting,
- safe style normalization.

Do not use automated lint fixes as a substitute for architecture review.

Never allow Ruff to silently restructure architecture.

---

# 22. PYRIGHT POLICY

Pyright is mandatory.

Target:

```text
0 errors
0 warnings
0 informations
```

Particular care is required for:

- `Unknown`,
- implicit `Any`,
- untyped dict/list fields,
- incompatible dataclass defaults,
- incorrect field ordering,
- abstract contract completeness,
- invalid imports.

Static typing problems are contract-quality problems, not cosmetic problems.

---

# 23. ERROR HANDLING PROTOCOL

When the agent discovers an error, classify it before editing:

### Class A — Mechanical

Examples:

- import order,
- formatting,
- trivial naming/style issue.

May be repaired directly.

### Class B — Local implementation

Examples:

- wrong annotation,
- incorrect default factory,
- missing abstract method,
- implementation typo.

Repair inside the current module.

### Class C — Contract conflict

Examples:

- required field missing,
- file belongs to another stage,
- dependency violates layer rules,
- existing API conflicts with frozen architecture,
- required behavior is not defined.

Do not patch around it.

Stop and report the contract conflict.

### Class D — Architecture conflict

Examples:

- new dependency direction,
- new runtime layer,
- new global ownership model,
- new scope,
- new event semantics.

This requires RFC/ADR.

Do not implement it inside the build stage.

---

# 24. NO SILENT REPAIR RULE

The implementation agent may repair implementation defects.

The implementation agent may not silently repair architecture defects.

Never write:

> "I changed the design slightly so the code works."

That is an architecture change.

Instead:

> "The current contract conflicts with implementation requirement X. Implementation is blocked pending contract resolution."

---

# 25. CURRENT REPOSITORY RECONCILIATION

The current project has already had implementation attempts for:

- KR-001 Foundation Core
- KR-002 Configuration Runtime
- KR-003 Logging Runtime
- KR-004 Kernel Contracts

The earlier build process exposed avoidable problems:

- stage mixing,
- accidental file creation,
- typing ambiguity,
- dataclass ordering problems,
- empty abstract contracts,
- insufficient separation between contracts and implementations,
- treating zero collected tests as adequate validation.

The purpose of this handoff pack is to prevent repetition.

Do not perform another sequence of ad-hoc one-line fixes before the contract boundary is clear.

---

# 26. PROVISIONAL STATUS OF EARLIER MODULES

Earlier modules may be present in the repository.

Their presence does not grant permission to redesign them during KR-004.

However, an earlier module is not automatically QA-certified merely because Ruff/Pyright exited successfully.

A module may be considered implementation-complete only when its actual acceptance evidence exists.

When the repository is audited, classify each earlier module as one of:

- Implemented + validated
- Implemented + validation incomplete
- Conflicting
- Out of scope
- Missing

Do not falsely promote "no tests collected" to "fully tested".

---

# 27. DEFINITION OF DONE — PER FILE

A file is complete only when:

- correct canonical path,
- correct owning module,
- correct stage,
- contract-aligned public surface,
- permitted dependencies,
- no architecture invention,
- strict typing,
- logging instead of `print` where runtime logging is required,
- no mutable global runtime state,
- Ruff passes,
- Pyright passes,
- relevant tests pass,
- no known unresolved contract conflict.

---

# 28. DEFINITION OF DONE — PER MODULE

A module is complete only when:

- every planned file exists,
- no unplanned files were created,
- imports form a valid DAG,
- public APIs are contract-aligned,
- tests exist where required,
- tests are actually collected,
- tests pass,
- static analysis passes,
- no later-stage implementation leaked into the module,
- Tech Lead accepts the result.

---

# 29. OUTPUT CONTRACT FOR BUILD CHAT

For every completed stage, return:

```text
Module ID:
Stage:
Status:
Purpose:
Dependencies:
Files Created:
Files Modified:
Public API:
Validation:
Ruff:
Pyright:
Pytest:
Architecture Checks:
Open Issues:
Definition of Done:
```

When the stage is blocked, return:

```text
Module ID:
Stage:
Status: BLOCKED

Blocking Contract:
Observed Conflict:
Why It Cannot Be Safely Inferred:
Affected Files:
Required Architecture Decision:
```

Do not hide unresolved issues.

---

# 30. NON-NEGOTIABLE FORBIDDEN BEHAVIOR

The implementation agent MUST NOT:

- invent architecture,
- mix stages,
- create convenience modules outside the manifest,
- introduce generic utility dumping grounds,
- use ORION components,
- add hidden global state,
- introduce extra DI scopes,
- weaken event typing,
- mutate state from render,
- create cyclic dependencies,
- silently alter frozen contracts,
- declare success when required tests were not collected,
- fix an architecture problem with a convenience abstraction.

---

# 31. FIRST ACTION AFTER READING THIS DOCUMENT

The Build agent must NOT immediately continue coding.

It must first perform an **Implementation Preflight**:

1. inspect repository tree,
2. inspect current KR-001/002/003/004 files,
3. compare files against this handoff pack,
4. identify files that are out of stage,
5. identify contract/type/test gaps,
6. report the reconciliation result.

Only after the preflight is clean should implementation continue.

---

# 32. KR-004 RESTART RULE

KR-004 MUST be treated as a clean contract-stage restart.

Do not continue patching a contract file indefinitely.

For KR-004:

- audit current files,
- compare against contract responsibilities,
- regenerate incorrect contract files cleanly where required,
- keep the package contract-only,
- run strict validation,
- add contract tests where required by the Wave 1 test strategy.

The goal is a coherent contract package, not an accumulation of fixes.

---

# 33. CANONICAL PRINCIPLE

One architecture fact must have one canonical source.

The implementation should never require the agent to choose between:

- an old code assumption,
- a remembered architecture detail,
- a convenience abstraction,
- and the frozen contract.

The handoff layer exists specifically to remove that ambiguity.

---

# 34. TECHNOLOGY BASELINE

Language:

**Python 3.13**

Environment:

**uv**

Testing:

**pytest**

Linting / formatting:

**Ruff**

Static analysis:

**Pyright**

Configuration:

`.env` / environment-based configuration as defined by the configuration stage.

Logging:

standard Python logging through the approved AURORA logging runtime.

Do not add dependencies unless the active contract requires them.

---

# 35. HANDOFF STATUS

**Wave 1 implementation is authorized only through this process.**

**KR-004 is not to be advanced by ad-hoc patching.**

The next correct action is:

**Preflight → Contract reconciliation → Clean KR-004 implementation → Validation → Tech Lead review**

---

# 36. FINAL DIRECTIVE TO CODEX / BUILD AGENT

You are an implementation agent, not an architecture author.

Use the frozen architecture.

Use this handoff pack.

Use the repository as implementation state, not as architectural truth.

Do not infer missing architecture.

Do not add convenience abstractions.

Do not create files outside the current stage.

Do not mix modules.

Do not proceed through a red validation gate.

When something is genuinely unspecified, stop and expose the ambiguity instead of inventing an answer.

The required behavior is:

**read → preflight → implement one file → validate → report → wait for the next stage**

