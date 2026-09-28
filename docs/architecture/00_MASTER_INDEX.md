# AURORA — Implementation Master Index v1.0

**Status:** ACTIVE IMPLEMENTATION PACK  
**Purpose:** Single entry point for Codex implementation.

## Reading Order
1. `AGENTS.md`
2. `docs/architecture/00_MASTER_INDEX.md`
3. `docs/architecture/01_REPOSITORY_FILE_REGISTRY.md`
4. `docs/architecture/02_DEPENDENCY_GRAPH.md`
5. `docs/architecture/03_PUBLIC_API_REGISTRY.md`
6. `docs/architecture/04_TYPE_EVENT_DI_LIFECYCLE_REGISTRY.md`
7. active module contract under `docs/architecture/wave1/`
8. current repository implementation

## Authority
Frozen Engineering Architecture → Architecture Freeze / ADRs → Implementation Contract → Module/File Registry → Build Protocol → Source.

Source code is implementation state, not architecture authority.

## Runtime Layers
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

Lower layers must not depend on higher layers. Graphs are DAGs.

## Wave 1
```text
W1.01 Foundation Core
W1.02 Configuration Runtime
W1.03 Logging Runtime
W1.04 Kernel Contracts
W1.05 Dependency Injection
W1.06 Lifecycle
W1.07 Event Bus
W1.08 Pipeline Context
W1.09 Pipeline Orchestrator
W1.10 Runner / Bootstrap
W1.11 Kernel Test Suite
```

## Hard Rules
- No architecture invention.
- No files outside active ownership.
- No generic utility dumping grounds.
- No ORION code.
- No extra DI scopes.
- No event-schema changes.
- No dependency cycles.
- Render is read-only.
- Diagnostics are read-only.
- One authoritative runtime-state owner.
- Architecture conflicts require Tech Lead / RFC / ADR.

## Validation
```powershell
uv run pyright
uv run ruff check .
uv run pytest
```

`pytest` with zero collected tests is not a passing test gate when tests are required.

## Unknown Architecture Rule
If an exact file, symbol, signature, transition, event, or dependency is not defined by an authoritative contract, the implementation agent must stop rather than invent it.

## Current Known Documents
```text
AB-00A_Canonical_Implementation_Contract_v1.0.md
AB-00A_Reconciliation_Resolution_v1.0.md
AB-00A_Build_Protocol_Amendment_v1.0.md
AURORA_Wave1_Implementation_Handoff_v1.0.md
```

Wave 1 implementation-facing registry is being compiled from those contracts. Later-wave exact APIs must be compiled from the authoritative Engineering Bible before implementation.

## Expanded Implementation Registries

The following files are mandatory for the pre-build contract layer:

```text
05_FILE_API_DEPENDENCY_REGISTRY.md
06_MODULE_INTERACTION_MATRIX.md
07_BUILD_COMPLETION_MATRIX.md
08_CODEX_MASTER_BUILD_PROTOCOL.md
09_AUTHORITY_GAP_REGISTER.md
```

The expanded registry is authoritative for implementation planning only where its values are marked COMPLETE/CONFIRMED. It never overrides the Frozen Architecture.
