# AURORA — Authority Gap Register v1.0

**Status:** OPEN  
**Purpose:** Prevent Codex from inventing architecture where the available implementation pack does not contain exact facts.

## Missing authoritative inputs

The current available pack contains explicit Wave 1 constraints, but exact implementation-level details are still missing for:

```text
W1.05 DI
W1.06 Lifecycle
W1.07 Event Bus
W1.08 Pipeline Context
W1.09 Pipeline Orchestrator
W1.10 Runner / Bootstrap
W1.11 detailed test matrix
```

For these modules the following must be compiled before a large implementation run:

- exact production file list;
- exact class/function names;
- exact signatures;
- exact field names/types/defaults;
- exact imports;
- exact consumers;
- exact lifecycle transitions;
- exact event handling semantics;
- exact error semantics;
- exact DI resolution semantics;
- exact test assertions.

## Rule

No placeholder in this register may be silently converted into implementation behavior.

## Source Requirement

The missing facts must come from:

1. Frozen Engineering Bible;
2. Architecture Freeze;
3. approved ADRs;
4. approved module-specific architecture documents.

Source code is not sufficient to establish a new architectural fact.

## Close Condition

Set this register to:

```text
CLOSED
```

only after every implementation-critical item above is populated.
