# AURORA --- Wave 1 Architecture Resolution v1.0

**Document ID:** AB-00B\
**Document Name:** Wave 1 Architecture Resolution\
**Canonical Path:**
`docs/architecture/AB-00B_Wave1_Architecture_Resolution_v1.0.md`\
**Version:** 1.0\
**Status:** APPROVED --- CANONICAL RESOLUTION\
**Scope:** Wave 1 --- Kernel Runtime\
**Authority:** Architecture Freeze v1.0

## Purpose

Resolve only the implementation-blocking contradictions identified for
Wave 1. This document does not redesign the frozen architecture, create
a new Runtime, change Runtime ownership, change runtime layers, or
change dependency direction.

For the six subjects explicitly resolved below, AB-00B supersedes
conflicting lower-authority wording in M-03, M-05, M-06, AB-00A
implementation/reconciliation documents, and the KR-001 Reconciliation
Decision. All unrelated decisions remain unchanged.

------------------------------------------------------------------------

# RESOLUTION-001 --- RuntimeLayer

**Canonical owner:** `src/core/types.py`

The final canonical enum member names are:

``` python
class RuntimeLayer(StrEnum):
    L0_KERNEL = "L0_KERNEL"
    L1_STATE = "L1_STATE"
    L2_LAYOUT = "L2_LAYOUT"
    L3_THEME = "L3_THEME"
    L4_MOTION = "L4_MOTION"
    L5_INTERACTION = "L5_INTERACTION"
    L6_ACCESSIBILITY = "L6_ACCESSIBILITY"
    L7_PLATFORM = "L7_PLATFORM"
    L8_RENDER = "L8_RENDER"
```

The short alternatives `KERNEL`, `STATE`, `LAYOUT`, `THEME`, `MOTION`,
`INTERACTION`, `ACCESSIBILITY`, `PLATFORM`, and `RENDER` are superseded
as enum member names.

No additional RuntimeLayer member is permitted without a future
architecture resolution.

------------------------------------------------------------------------

# RESOLUTION-002 --- RuntimeStatus

**Canonical owner:** `src/core/types.py`

The single canonical vocabulary contains exactly ten members:

``` python
class RuntimeStatus(StrEnum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"
```

Therefore `INITIALIZING`, `STARTING`, `STOPPING`, `SHUTTING_DOWN`, and
`TERMINATED` are explicitly canonical. Six-state and seven-state
alternatives are superseded.

## Normal transitions

``` text
CREATED
  → INITIALIZING
  → READY
  → STARTING
  → RUNNING
  → STOPPING
  → STOPPED
  → SHUTTING_DOWN
  → TERMINATED
```

  From              To
  ----------------- -----------------
  `CREATED`         `INITIALIZING`
  `INITIALIZING`    `READY`
  `READY`           `STARTING`
  `STARTING`        `RUNNING`
  `RUNNING`         `STOPPING`
  `STOPPING`        `STOPPED`
  `STOPPED`         `SHUTTING_DOWN`
  `SHUTTING_DOWN`   `TERMINATED`

## Failure transitions

  From              To
  ----------------- ----------
  `INITIALIZING`    `FAILED`
  `READY`           `FAILED`
  `STARTING`        `FAILED`
  `RUNNING`         `FAILED`
  `STOPPING`        `FAILED`
  `SHUTTING_DOWN`   `FAILED`

`FAILED` and `TERMINATED` are terminal. No transition not listed above
is legal.

`StateRuntime` owns lifecycle state mutation. `LifecycleRuntime`
coordinates lifecycle operations and does not own a second mutable
RuntimeStatus source.

------------------------------------------------------------------------

# RESOLUTION-003 --- Identifier Types

**Canonical owner:** `src/core/types.py`

The final types are:

``` python
from typing import NewType
from uuid import UUID

SessionId = NewType("SessionId", UUID)
PipelineId = NewType("PipelineId", UUID)
```

`SessionId` and `PipelineId` are UUID-backed. String-backed alternatives
for these two identifiers are superseded.

All Wave 1 contracts and runtime APIs must consume `SessionId` and
`PipelineId`, not raw `str` or raw `UUID`. Serialization boundaries may
encode UUID values as strings; the in-process public Python API remains
typed with the canonical aliases.

This resolution does not alter unrelated identifier aliases.

------------------------------------------------------------------------

# RESOLUTION-004 --- LifecycleState

**Canonical owner:** `src/kernel/contracts/lifecycle.py`

The expanded structure is canonical:

``` python
@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleState:
    current: RuntimeStatus
    previous: RuntimeStatus | None
    entered_at: datetime
    transition_count: int
```

The minimal `current` + `previous` structure is superseded.

Canonical derived properties:

``` python
@property
def is_running(self) -> bool: ...

@property
def is_ready(self) -> bool: ...

@property
def is_failed(self) -> bool: ...

@property
def is_terminal(self) -> bool: ...
```

Semantics:

-   `current`: active RuntimeStatus.
-   `previous`: immediately preceding status, or `None` for the initial
    snapshot.
-   `entered_at`: timezone-aware UTC timestamp when `current` became
    active.
-   `transition_count`: successful transitions since runtime creation,
    starting at `0`.

LifecycleState is an immutable snapshot. It does not execute
transitions. `StateRuntime` owns replacement of the active snapshot.

------------------------------------------------------------------------

# RESOLUTION-005 --- Event Bus Import

**Canonical owner file:** `src/kernel/runtime/bus.py`

The only canonical direct import is:

``` python
from src.kernel.runtime.bus import EventBusRuntime
```

`src/kernel/runtime/event_bus.py` and:

``` python
from src.kernel.runtime.event_bus import EventBusRuntime
```

are obsolete specification errors.

No compatibility module, alias module, forwarding module, or duplicate
EventBusRuntime implementation shall be created at `event_bus.py`.

All Wave 1 specifications, implementation files, tests, and generated
code must use `src.kernel.runtime.bus`.

------------------------------------------------------------------------

# RESOLUTION-006 --- Document Priority and Reconciliation

For subjects explicitly resolved by AB-00B, precedence is:

``` text
Architecture Freeze v1.0
        ↓
AB-00B Wave 1 Architecture Resolution v1.0
        ↓
Current Master Documents (M-03 / M-05 / M-06)
        ↓
AB-00A implementation/reconciliation documents
        ↓
KR-001 Reconciliation Decision
        ↓
Generated implementation
```

AB-00B does not override Architecture Freeze v1.0. It overrides lower
documents only where they contradict an explicit resolution in this
document.

## M-03 --- `03_API_REGISTRY.md`

Reconcile to AB-00B:

-   RuntimeLayer → `L0_KERNEL` through `L8_RENDER`;
-   RuntimeStatus → canonical ten-state vocabulary;
-   SessionId → UUID-backed NewType;
-   PipelineId → UUID-backed NewType;
-   LifecycleState → expanded four-field contract;
-   EventBusRuntime → `src/kernel/runtime/bus.py`.

Conflicting M-03 entries are superseded until physically corrected.

## M-05 --- `05_STATE_EVENT_DI_LIFECYCLE_REGISTRY.md`

M-05's ten-state RuntimeStatus lifecycle and its explicit transition
matrix are confirmed by AB-00B.

No additional lifecycle transition may be inferred from descriptive
prose.

Where another M-05 statement conflicts with an explicit AB-00B
resolution, AB-00B wins.

## M-06 --- `06_MODULE_SPECIFICATIONS.md`

Reconcile to AB-00B:

-   retain `L0_KERNEL` through `L8_RENDER`;
-   replace six-state RuntimeStatus definitions with the canonical
    ten-state vocabulary;
-   retain UUID-backed SessionId and PipelineId;
-   use expanded LifecycleState;
-   replace every `src.kernel.runtime.event_bus` import with
    `src.kernel.runtime.bus`.

Conflicting M-06 entries are superseded until physically corrected.

## AB-00A

AB-00A remains authoritative for implementation protocol and
reconciliation rules except where it conflicts with an explicit AB-00B
resolution.

Any AB-00A ambiguity on these six subjects is closed by AB-00B. Any
contradictory wording is superseded for that subject only.

## KR-001 Reconciliation Decision

The KR-001 Reconciliation Decision remains historical implementation
authority except for:

-   RuntimeLayer member naming;
-   RuntimeStatus vocabulary and transitions;
-   SessionId type;
-   PipelineId type.

For these subjects AB-00B is final. No unrelated KR-001 decision is
changed.

------------------------------------------------------------------------

# Reconciliation Matrix

  ------------------------------------------------------------------------------------------
  Subject                             Canonical Resolution
  ----------------------------------- ------------------------------------------------------
  RuntimeLayer                        `L0_KERNEL` ... `L8_RENDER`

  RuntimeStatus                       10 states and only the transitions defined in
                                      RESOLUTION-002

  SessionId                           `NewType("SessionId", UUID)`

  PipelineId                          `NewType("PipelineId", UUID)`

  LifecycleState                      `current`, `previous`, `entered_at`,
                                      `transition_count` + four derived properties

  EventBusRuntime                     `from src.kernel.runtime.bus import EventBusRuntime`
  ------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Implementation Gate

After approval of AB-00B:

1.  Documentation and implementation are reconciled to this resolution
    before conflicting lower-authority text is used.
2.  KR-004 may be regenerated against the resolved contracts.
3.  KR-005 through KR-011 may then be implemented sequentially according
    to the approved Wave Plan.
4.  No implementation agent may choose between superseded alternatives.
5.  A newly discovered contradiction outside these six resolutions is an
    Architecture Conflict and must not be silently resolved in code.

------------------------------------------------------------------------

# Validation Requirements

Reconciliation is complete only when:

-   RuntimeLayer has exactly nine canonical members.
-   RuntimeStatus has exactly ten canonical members.
-   lifecycle tests cover every allowed transition and reject unlisted
    transitions.
-   SessionId and PipelineId are UUID-backed aliases.
-   LifecycleState has the canonical four fields and four derived
    properties.
-   no Wave 1 source/specification imports EventBusRuntime from
    `src.kernel.runtime.event_bus`.
-   `src/kernel/runtime/event_bus.py` does not exist as a compatibility
    duplicate.
-   M-03, M-05, and M-06 no longer contradict AB-00B on the resolved
    subjects.
-   Ruff passes.
-   Pyright passes with 0 errors, 0 warnings, and 0 informations.
-   Pytest collects, executes, and passes the relevant tests.

------------------------------------------------------------------------

# Definition of Done

-   [x] RuntimeLayer naming ambiguity resolved.
-   [x] RuntimeStatus vocabulary resolved.
-   [x] RuntimeStatus transitions resolved.
-   [x] SessionId type resolved.
-   [x] PipelineId type resolved.
-   [x] LifecycleState structure resolved.
-   [x] EventBusRuntime import path resolved.
-   [x] Document precedence defined.
-   [x] Superseded alternatives explicitly identified.
-   [x] Wave 1 implementation can proceed without choosing between
    conflicting variants.

------------------------------------------------------------------------

# Approval

**Architecture State:** FROZEN\
**Resolution State:** APPROVED\
**Effective Version:** v1.0\
**Applies From:** Wave 1 --- Kernel Runtime\
**Change Policy:** Any change to a resolution in AB-00B requires a new
explicit architecture resolution / ADR.

------------------------------------------------------------------------

**END OF DOCUMENT --- AB-00B WAVE 1 ARCHITECTURE RESOLUTION v1.0**
