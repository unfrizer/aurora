# AURORA — Wave 1 EventPriority Resolution v1.0

**Document ID:** AB-00C  
**Document Name:** Wave 1 EventPriority Resolution  
**Canonical Path:** `docs/architecture/AB-00C_Wave1_EventPriority_Resolution_v1.0.md`  
**Version:** 1.0  
**Status:** APPROVED — CANONICAL RESOLUTION  
**Scope:** Wave 1 — Kernel Runtime  
**Authority:** Architecture Freeze v1.0 + AB-00B Wave 1 Architecture Resolution v1.0

---

# Purpose

This document resolves one implementation-blocking EventPriority contradiction that remains after AB-00B.

It does not redesign EventBus Runtime, change EventBus ownership, change Runtime layers, or introduce a new runtime mechanism.

---

# RESOLUTION-001 — Canonical EventPriority Vocabulary

**Canonical owner:** `src/core/types.py`

The canonical `EventPriority` vocabulary contains exactly five members:

```python
class EventPriority(IntEnum):
    BACKGROUND = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    CRITICAL = 100
```

The semantic dispatch order is always highest priority first:

```text
CRITICAL
   ↓
HIGH
   ↓
NORMAL
   ↓
LOW
   ↓
BACKGROUND
```

Equivalent ordering rule:

```python
CRITICAL > HIGH > NORMAL > LOW > BACKGROUND
```

No additional EventPriority value is permitted without a future architecture resolution.

---

# RESOLUTION-002 — Dispatch Ordering

`DispatcherRuntime` must order queued events by descending `EventPriority`.

Therefore the canonical dispatch order is:

1. `CRITICAL`
2. `HIGH`
3. `NORMAL`
4. `LOW`
5. `BACKGROUND`

Events with equal priority preserve FIFO / registration-stable ordering as defined by the EventBus specification.

No implementation may omit `CRITICAL` or `BACKGROUND` from the ordering model.

---

# RESOLUTION-003 — Conflicting Documents

For EventPriority vocabulary, numeric values, and ordering only, this document supersedes conflicting text in:

- M-06 `06_MODULE_SPECIFICATIONS.md`;
- M-09 `09_TEST_MATRIX.md`;
- AB-00A implementation/reconciliation documents;
- `KR-001_Reconciliation_Decision_v1.0.md`.

M-05 `05_STATE_EVENT_DI_LIFECYCLE_REGISTRY.md` is confirmed as the canonical source for the five-level priority model.

Any AB-00A or KR-001 reconciliation instruction that requires preserving the previous EventPriority enum, preserving the previous EventPriority member set, or forbids redefining EventPriority is superseded for this subject only.

AB-00C is therefore the final authority for:

- the complete EventPriority member set;
- EventPriority numeric values;
- EventPriority dispatch ordering.

All unrelated AB-00A and KR-001 reconciliation decisions remain unchanged.

## M-06 Required Reconciliation

The section that currently defines handler execution as:

```text
HIGH
NORMAL
LOW
```

is superseded.

It must be reconciled to:

```text
CRITICAL
HIGH
NORMAL
LOW
BACKGROUND
```

The M-06 `EventPriority` enum vocabulary must also include `BACKGROUND`.

## M-09 Required Reconciliation

The test order currently defined as:

```text
CRITICAL
HIGH
NORMAL
LOW
```

is incomplete.

It must be reconciled to:

```text
CRITICAL
HIGH
NORMAL
LOW
BACKGROUND
```

Tests must verify that `BACKGROUND` executes after `LOW`.

---

# Precedence

For EventPriority vocabulary and dispatch order only:

```text
Architecture Freeze v1.0
        ↓
AB-00B Wave 1 Architecture Resolution v1.0
        ↓
AB-00C Wave 1 EventPriority Resolution v1.0
        ↓
M-05 State / Event / DI / Lifecycle Registry
        ↓
M-06 Module Specifications
        ↓
M-09 Test Matrix
        ↓
AB-00A implementation/reconciliation documents
        ↓
KR-001_Reconciliation_Decision_v1.0.md
        ↓
Generated implementation
```

AB-00C changes no subject outside EventPriority vocabulary and ordering.

---

# Validation Requirements

The conflict is considered resolved only when:

- `EventPriority` contains exactly five members;
- values are `BACKGROUND=0`, `LOW=25`, `NORMAL=50`, `HIGH=75`, `CRITICAL=100`;
- dispatch is descending by priority;
- equal-priority ordering remains stable;
- M-06 contains the five-level ordering;
- M-09 tests all five levels;
- no Wave 1 specification contains a three-level or four-level EventPriority ordering as canonical behavior;
- Ruff passes;
- Pyright passes with 0 errors, 0 warnings, and 0 informations;
- Pytest collects, executes, and passes the EventBus priority tests.

---

# Definition of Done

- [x] EventPriority vocabulary resolved.
- [x] EventPriority numeric values resolved.
- [x] Dispatch order resolved.
- [x] M-06 conflict resolved.
- [x] M-09 conflict resolved.
- [x] M-05 five-level model confirmed.
- [x] Implementation no longer requires an architectural guess.

---

# Approval

**Architecture State:** FROZEN  
**Resolution State:** APPROVED  
**Effective Version:** v1.0  
**Applies From:** Wave 1 — Kernel Runtime  
**Change Policy:** Any change to EventPriority vocabulary or ordering requires a new explicit architecture resolution / ADR.

---

**END OF DOCUMENT — AB-00C WAVE 1 EVENTPRIORITY RESOLUTION v1.0**
