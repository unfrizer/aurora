# AURORA — Codex Master Build Protocol v1.0

**Status:** PRE-BUILD PROTOCOL  
**Purpose:** Final compact protocol for the first large Codex implementation run.

## Input

Codex receives:

```text
AGENTS.md

docs/architecture/
├── 00_MASTER_INDEX.md
├── 01_REPOSITORY_FILE_REGISTRY.md
├── 02_DEPENDENCY_GRAPH.md
├── 03_PUBLIC_API_REGISTRY.md
├── 04_TYPE_EVENT_DI_LIFECYCLE_REGISTRY.md
├── 05_FILE_API_DEPENDENCY_REGISTRY.md
├── 06_MODULE_INTERACTION_MATRIX.md
├── 07_BUILD_COMPLETION_MATRIX.md
├── AB-00A_Canonical_Implementation_Contract_v1.0.md
├── AB-00A_Reconciliation_Resolution_v1.0.md
├── AB-00A_Build_Protocol_Amendment_v1.0.md
├── AURORA_Wave1_Implementation_Handoff_v1.0.md
├── KR-001_Reconciliation_Decision_v1.0.md
└── wave1/
    ├── KR-001_FOUNDATION_CORE.md
    ├── KR-002_CONFIGURATION.md
    ├── KR-003_LOGGING.md
    ├── KR-004_KERNEL_CONTRACTS.md
    ├── KR-005_DI.md
    ├── KR-006_LIFECYCLE.md
    ├── KR-007_EVENT_BUS.md
    ├── KR-008_PIPELINE_CONTEXT.md
    ├── KR-009_PIPELINE_ORCHESTRATOR.md
    ├── KR-010_RUNNER_BOOTSTRAP.md
    └── KR-011_KERNEL_TEST_SUITE.md
```

## Execution Rule

The build unit is one module.

Codex may modify all files owned by the active module.

Codex may self-repair local implementation defects.

Codex must stop on:

- architecture conflict;
- contract conflict;
- missing authoritative information;
- requirement that changes public architecture;
- cross-module ownership violation.

## Build Strategy

```text
READ
 ↓
PREFLIGHT
 ↓
RECONCILE
 ↓
IMPLEMENT MODULE
 ↓
SELF-REPAIR LOCAL DEFECTS
 ↓
VALIDATE
 ↓
TEST
 ↓
MODULE REPORT
 ↓
STOP
```

## Validation

```powershell
uv run pyright
uv run ruff check .
uv run pytest
```

Do not report success if required tests are absent or zero are collected.

## Repository Protection

The agent must not:

- create unowned files;
- create generic helper packages;
- import higher runtime layers;
- add new DI scopes;
- redefine frozen events;
- redefine lifecycle without authority;
- introduce ORION components;
- create compatibility shims hiding architecture conflicts.

## Quality Rule

Passing Ruff and Pyright is necessary but insufficient.

The module must also satisfy:

```text
architecture
ownership
API
dependencies
tests
```

## First Run Goal

The first large build should target the next fully specified implementation frontier.

If any required module remains `PARTIAL` in `07_BUILD_COMPLETION_MATRIX.md`, Codex must not guess missing architecture.

## Final Report

Return:

```text
Wave:
Status:
Files Created:
Files Modified:
Architecture Compliance:
Public API Compliance:
Dependency Compliance:
Pyright:
Ruff:
Pytest:
Pre-existing Failures:
Architecture Blockers:
Definition of Done:
```
