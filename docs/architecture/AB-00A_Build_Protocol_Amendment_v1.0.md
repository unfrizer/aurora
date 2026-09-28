# AURORA — Build Protocol Amendment v1.0

**Document ID:** AB-00A-BPA-001  
**Status:** ACTIVE  
**Purpose:** Replace file-by-file conversational orchestration with module-batch implementation while preserving architecture control.

---

# 1. NEW BUILD UNIT

The canonical Build unit is:

```text
1 module = 1 implementation task
```

The implementation agent may modify all files explicitly owned by the active module.

Example:

```text
KR-001 → all KR-001-owned files
KR-002 → all KR-002-owned files
KR-003 → all KR-003-owned files
KR-004 → all KR-004-owned files
```

The agent must not modify files owned by another module.

---

# 2. SELF-REPAIR AUTHORITY

Within the active module, the Build agent MAY automatically repair local implementation defects.

Allowed self-repair examples:

- Ruff import ordering;
- formatting;
- Pyright type errors;
- dataclass field ordering;
- incorrect default factories;
- incorrect local imports;
- missing local test adjustments required by the already-approved contract;
- other mechanical/local implementation errors.

The agent MUST rerun validation after repairs.

---

# 3. MANDATORY STOP CONDITIONS

The Build agent MUST STOP and return control to Tech Lead when it encounters:

- Architecture Conflict;
- Contract Conflict;
- missing authoritative architecture;
- ambiguity that changes public behavior;
- need for a new dependency direction;
- need for a new runtime layer;
- need for a new DI scope;
- need to alter a frozen event schema;
- need to alter ownership semantics;
- need to create a new architectural abstraction;
- conflict between authoritative documents.

The agent must not solve these by invention.

---

# 4. MODULE-BATCH WORKFLOW

For one active module:

```text
1. Read AGENTS.md
2. Read AB-00A
3. Read Reconciliation / module-specific decisions
4. Inspect current module
5. Reconcile existing implementation
6. Implement all authorized files of the module
7. Run Pyright
8. Run Ruff
9. Run Pytest
10. Self-repair local implementation defects
11. Repeat validation until green
12. Produce one module report
13. Stop
```

Do not return control after every individual file.

---

# 5. VALIDATION

The module is not complete until:

```powershell
uv run pyright
uv run ruff check .
uv run pytest
```

passes.

`pytest` must collect and execute relevant tests when the active module has required tests.

`collected 0 items` is not evidence of successful testing.

---

# 6. SCOPE OF SELF-REPAIR

Self-repair is restricted to the active module.

The agent MUST NOT repair another module merely because repository-wide validation exposes an error there.

For example:

```text
Active: KR-001
Error: KR-004 events.py
```

The agent must report the pre-existing KR-004 failure and continue/complete only KR-001.

It may use repository-wide validation commands, but must distinguish:

```text
new error introduced by active module
```

from:

```text
pre-existing error outside active module
```

---

# 7. ARCHITECTURE ESCALATION

A technical problem becomes an architecture escalation when solving it would require changing:

- public contract;
- layer ownership;
- dependency direction;
- scope model;
- event schema;
- lifecycle model;
- manifest schema;
- canonical identifier model;
- runtime ownership model.

The Build agent must stop rather than patch around such a requirement.

---

# 8. REPORTING

At the end of a module task, return one report:

```text
Module:
Status:

Files Modified:

Architecture Compliance:

Self-Repairs:
- ...

Validation:
Pyright:
Ruff:
Pytest:

Pre-existing Failures:
- ...

Architecture/Contract Blockers:
- ...

Definition of Done:
PASS / BLOCKED
```

No per-file conversational report is required.

---

# 9. TECH LEAD REVIEW

Tech Lead reviews the completed module as a unit.

The review checks:

```text
architecture
ownership
public contract
dependencies
typing
tests
stage isolation
runtime invariants
```

Only after module approval can the next module begin.

---

# 10. ONE-MODULE BOUNDARY

Batching is allowed only inside one module.

Forbidden:

```text
KR-001 + KR-002
KR-003 + KR-004
Foundation + DI
Contracts + EventBus
```

Allowed:

```text
KR-001:
  types.py
  constants.py
  version.py
  __init__.py
```

provided all files belong to the active module and the module contract authorizes them.

---

# 11. RESOURCE EFFICIENCY PRINCIPLE

The Build protocol optimizes for:

```text
minimum communication overhead
+
maximum contract compliance
```

The implementation agent should solve mechanical/local defects autonomously rather than returning control to the Tech Lead for every lint/type correction.

Architecture decisions remain centralized.

Implementation corrections remain local to the active module.

---

# 12. EFFECTIVE BUILD MODEL

The resulting development loop is:

```text
Frozen Architecture
        ↓
Canonical Implementation Contract
        ↓
Module Decision
        ↓
Build Agent
        ↓
Implement complete module
        ↓
Self-repair local defects
        ↓
Validate
        ↓
One module report
        ↓
Tech Lead review
        ↓
Next module
```

This amendment supersedes the previous requirement to stop after every individual production file.

The one-file rule remains applicable only where a module-specific contract explicitly requires a file-by-file boundary or where Tech Lead imposes a temporary narrow scope.
