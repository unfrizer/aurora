# AURORA — Build Completion Matrix v1.0

**Status:** ACTIVE  
**Purpose:** Single view of implementation readiness.

| Stage | Contract | File Registry | API Registry | Dependency Registry | Tests | Build Ready |
|---|---|---|---|---|---|---|
| W1.01 | COMPLETE | COMPLETE | PARTIAL | COMPLETE | PENDING | RECONCILED |
| W1.02 | COMPLETE | COMPLETE | PARTIAL | COMPLETE | MISSING | NOT FULLY CERTIFIED |
| W1.03 | COMPLETE | COMPLETE | PARTIAL | COMPLETE | MISSING | NOT FULLY CERTIFIED |
| W1.04 | COMPLETE | COMPLETE | PARTIAL | COMPLETE | MISSING | RESTART REQUIRED |
| W1.05 | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | BLOCKED |
| W1.06 | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | BLOCKED |
| W1.07 | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | BLOCKED |
| W1.08 | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | BLOCKED |
| W1.09 | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | BLOCKED |
| W1.10 | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | BLOCKED |
| W1.11 | PARTIAL | COMPLETE | PARTIAL | COMPLETE | MISSING | BLOCKED |

## Meaning

### COMPLETE
Explicit enough for implementation without architectural inference.

### PARTIAL
Known responsibility exists, but exact implementation-level facts remain missing.

### BLOCKED
The implementation agent must not proceed.

## Target

Before the first large Codex implementation run:

```text
W1.01–W1.11
    ↓
COMPLETE
```

No implementation-critical row should remain PARTIAL.

## Required Minimum for Every File

```text
path
owner
purpose
public API
exact signatures
imports
consumers
state ownership
errors
tests
```
