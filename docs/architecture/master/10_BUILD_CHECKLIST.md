# AURORA MASTER HANDOFF v1.0

## Approved core/test reconciliation — ADR-009

**Status:** APPROVED — explicit T-01–T-05 approval and root-admission clarification,
2026-10-07. Exact normative contracts:
[KR-002](../wave1/KR-002_CONFIGURATION.md),
[KR-003](../wave1/KR-003_LOGGING.md),
[KR-011](../wave1/KR-011_KERNEL_TEST_SUITE.md).

Only affected KR-002/KR-003/KR-011 declarations are superseded. Legacy duplicate
summaries/counts/examples for those modules elsewhere in this document are NOT
authority when they conflict with these exact contracts. Other module ownership,
L0–L8, DI/event/lifecycle vocabularies and approved ADR-004–008 acceptance remain.

KR-002: immutable BaseSettings, eight fields, Environment alias, three properties,
two validators; get_settings and validate_configuration, lru_cache(maxsize=1).
No reload_settings/clear_settings_cache/validate_settings, missing-.env error,
provider fields, absolute/existing-path or timezone-database validation requirement.

KR-003: get_logger(name, config=None), LOGGER; LoggingConfig (three fields, frozen/
slotted, positional-compatible), RuntimeContextFilter, ConsoleFormatter, JsonFormatter,
seven explicit correlation/session context functions and two default constants.
No configure_logging/reset_logging/ContextFilter alias, root configuration or
automatic trace/pipeline/runtime injection. Empty name and EXACT "root" plus invalid
levels reject before registry access/mutation with existing InvalidConfigurationError
and fixed safe messages. Keep cache and first-installed handlers. Foundation
constants keep KR-001 ownership; logger -> logging_config/ Foundation is allowed,
logging_config -> logger or concrete runtime is forbidden. No new import direction.

KR-011: eleven executable test modules plus tests/conftest.py (seven named fresh
function-scoped fixtures), exact paths and all public API/coverage gates in its
linked contract. No tests/runtime or split Registry/Scope/Resolver/Executor files.
Current narrow KR-003 changes only logger.py and test_logger.py; no other production,
test, dependency or workflow edit. KR-011 is a separate subsequent reviewed task.
Approved contract compilation is not a claim of implementation/test acceptance.


**Document ID:** M-10

**Document Name:** Build Checklist

**File:** `docs/architecture/master/10_BUILD_CHECKLIST.md`

**Status:** CANONICAL BUILD CHECKLIST

**Authority:** AB-00A + Wave1 Implementation Handoff

---

# Purpose

This document is the mandatory implementation checklist for Wave 1.

Every KR (Kernel Requirement) must satisfy **every applicable checkpoint** before the next KR begins.

If any checkpoint fails:

**STOP IMPLEMENTATION.**

No later KR may continue until the active KR is green.

---

# Global Repository Checklist

## Repository Structure

- [ ] Root folder is `aurora/`.
- [ ] `src/` exists.
- [ ] `tests/` exists.
- [ ] `docs/architecture/master/` exists.
- [ ] `pyproject.toml` exists.
- [ ] `.env.example` exists.
- [ ] `.gitignore` exists.
- [ ] `README.md` exists.

## Python Environment

- [ ] Python 3.13.
- [ ] uv project initialized.
- [ ] Ruff configured.
- [ ] Pyright configured.
- [ ] Pytest configured.
- [ ] Strict typing enabled.

---

# KR-001 — Foundation Core Checklist

## Files

- [ ] `types.py`
- [ ] `constants.py`
- [ ] `exceptions.py`
- [ ] `version.py`
- [ ] `__init__.py`

## Types

- [ ] RuntimeLayer contains only L0–L8.
- [ ] DIScope contains exactly four scopes.
- [ ] RuntimeStatus vocabulary matches M-05.
- [ ] EventPriority vocabulary unchanged.
- [ ] EventPhase vocabulary unchanged.
- [ ] Metadata is JSON-compatible.
- [ ] Payload is recursive JSON type.

## Constants

- [ ] Manifest fields include `provides`.
- [ ] Event fields match M-05.
- [ ] No duplicated version constants.
- [ ] Version imported from `version.py`.

## Exceptions

- [ ] AuroraError root exists.
- [ ] Exception tree matches M-08.
- [ ] No RuntimeError duplicates.

## Validation

- [ ] Ruff passes.
- [ ] Pyright passes.
- [ ] `test_types.py` passes.

---

# KR-002 — Configuration Runtime Checklist — ADR-009

- [ ] Exact eight-field frozen BaseSettings / Environment / five public members.
- [ ] get_settings and validate_configuration, immutable lru_cache(maxsize=1).
- [ ] Default/env/.env/alias/extra and actual frozen assignment checks.
- [ ] Relative Path conversion, descriptive timezone and exact error/cause policy.
- [ ] Complete tests/core/test_settings.py, all APIs, 100% executable lines per file.
- [ ] Required Ruff/format/Pyright/Pytest/smoke/latest-head CI green.

# KR-003 — Logging Runtime Checklist — ADR-009

- [ ] Exact LoggingConfig/15 symbols/filter/formatter/context API compatibility.
- [ ] Empty/"root"/invalid level rejected before registry access or mutation.
- [ ] No root interference, safe messages, first-installed handlers/cache preserved.
- [ ] Complete tests/core/test_logger.py, all APIs, 100% executable lines per file.
- [ ] Required Ruff/format/Pyright/Pytest/smoke/latest-head CI green.
- [ ] Separate module report/Tech Lead review before KR-011; no cross-owner repair.

---

# FOUNDATION FREEZE CHECKLIST

- [ ] KR-001 green.
- [ ] KR-002 green.
- [ ] KR-003 green.
- [ ] Core tests execute.
- [ ] No architecture conflicts.

Freeze status:

**FOUNDATION LOCKED**

---

# KR-004 — Contracts Checklist

## Files

- [ ] runtime.py
- [ ] module.py
- [ ] service.py
- [ ] lifecycle.py
- [ ] context.py
- [ ] events.py
- [ ] __init__.py

## RuntimeContract

- [ ] initialize()
- [ ] start()
- [ ] stop()
- [ ] shutdown()
- [ ] health()

## Manifest

- [ ] module_id
- [ ] runtime_layer
- [ ] depends_on
- [ ] provides
- [ ] version

## RuntimeContext

- [ ] Frozen.
- [ ] Metadata immutable.
- [ ] Trace immutable.

## RuntimeEvent

- [ ] Required fields first.
- [ ] Default fields last.
- [ ] Payload JSON only.

## Validation

- [ ] Ruff passes.
- [ ] Pyright passes.
- [ ] Contracts tests pass.

---

# KR-005 — DI Runtime Checklist

## Files

- [ ] container.py
- [ ] provider.py
- [ ] registry.py
- [ ] resolver.py
- [ ] scope.py

## Container

- [ ] register()
- [ ] resolve()
- [ ] remove()
- [ ] shutdown()

## Resolver

- [ ] Constructor injection.
- [ ] Circular detection.
- [ ] Dependency graph validation.

## Scope

- [ ] Application.
- [ ] Session.
- [ ] Pipeline.
- [ ] Transient.

## Registry

- [ ] Descriptor registration.
- [ ] Descriptor removal.
- [ ] Duplicate detection.

## Validation

- [ ] Container tests.
- [ ] Resolver tests.
- [ ] Scope tests.
- [ ] Registry tests.

---

# KR-006 — Lifecycle Checklist

## Files

- [ ] lifecycle.py
- [ ] state.py
- [ ] hooks.py

## Lifecycle Manager

- [ ] initialize()
- [ ] start()
- [ ] stop()
- [ ] shutdown()

## State Machine

- [ ] CREATED
- [ ] INITIALIZING
- [ ] READY
- [ ] RUNNING
- [ ] FAILED
- [ ] STOPPED

## Hooks

- [ ] BEFORE_INITIALIZE
- [ ] AFTER_INITIALIZE
- [ ] BEFORE_START
- [ ] AFTER_START
- [ ] BEFORE_STOP
- [ ] AFTER_STOP

## Validation

- [ ] Lifecycle tests pass.

---

# KR-007 — Event Bus Checklist

## Files

- [ ] bus.py
- [ ] dispatcher.py
- [ ] publisher.py
- [ ] subscriber.py
- [ ] event.py

## Event Bus

- [ ] publish()
- [ ] subscribe()
- [ ] unsubscribe()

## Dispatcher

- [ ] Sync dispatch.
- [ ] Async dispatch.
- [ ] Priority ordering.

## Subscriber Registry

- [ ] Registration.
- [ ] Removal.
- [ ] Lookup.

## Validation

- [ ] Event tests pass.

---

# KR-008 — Runtime Context Checklist

## Files

- [ ] context.py
- [ ] metadata.py
- [ ] session.py

## Context API

- [ ] get()
- [ ] set()
- [ ] remove()
- [ ] contains()

## Session

- [ ] Session scope lifetime.
- [ ] Metadata snapshot.

## Validation

- [ ] Context tests pass.

---

# KR-009 — Pipeline Checklist

## Files

- [ ] pipeline.py
- [ ] manifest.py
- [ ] executor.py
- [ ] orchestrator.py

## Pipeline Definition

- [ ] DAG validation.
- [ ] Duplicate stage detection.
- [ ] Dependency validation.

## Executor

- [ ] Stage execution.
- [ ] Failure propagation.
- [ ] Pipeline completion event.

## Orchestrator

- [ ] Register module.
- [ ] Register stage.
- [ ] Execute pipeline.
- [ ] Shutdown runtime.

## Validation

- [ ] Pipeline tests pass.
- [ ] Executor tests pass.

---

# KR-010 — Bootstrap Checklist

## Files

- [ ] runtime.py
- [ ] bootstrap.py
- [ ] main.py

## Build Checklist

- [ ] Load Settings.
- [ ] Configure Logger.
- [ ] Build Container.
- [ ] Register Services.
- [ ] Initialize Lifecycle.
- [ ] Create EventBus.
- [ ] Create RuntimeContext.
- [ ] Start Orchestrator.
- [ ] Execute Pipeline.

## Shutdown Sequence

- [ ] Reverse startup order.
- [ ] Dispose scopes.
- [ ] Stop EventBus.
- [ ] Stop Lifecycle.
- [ ] Shutdown Container.

## Validation

- [ ] Bootstrap tests pass.
- [ ] Runtime tests pass.

---

# KR-011 — Test Suite Checklist — APPROVED ADR-009

- [ ] tests/conftest.py
- [ ] tests/core/test_types.py
- [ ] tests/core/test_settings.py
- [ ] tests/core/test_logger.py
- [ ] tests/kernel/test_contracts.py
- [ ] tests/kernel/test_container.py
- [ ] tests/kernel/test_lifecycle.py
- [ ] tests/kernel/test_event_bus.py
- [ ] tests/kernel/test_context.py
- [ ] tests/kernel/test_pipeline.py
- [ ] tests/kernel/test_bootstrap.py
- [ ] tests/integration/test_runtime_startup.py

- [ ] Eleven executable modules plus seven fresh function-scoped shared fixtures.
- [ ] Preserve every approved ADR-004–008/module acceptance, no skips/xfail/exclusions.
- [ ] Exact T-02 configuration and T-03 logging assertions.
- [ ] Exact T-04 API/per-file executable-line gates; separate line/API/branch evidence.
- [ ] All local and latest-head hosted gates pass.
- [ ] STOP/report any other-owner defect; no source/dependency/workflow/later-test edit.
- [ ] Separate task after narrow KR-003 acceptance; completed module report and review.

---

# Repository Validation Gate

Run after every KR:

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

Expected:

- Ruff → 0 errors.
- Pyright → 0 errors / 0 warnings.
- Pytest → non-empty collected tests.

---

# Final Wave 1 Acceptance Checklist

## Architecture

- [ ] Matches M-01.
- [ ] Matches M-02.
- [ ] Matches M-03.
- [ ] Matches M-04.
- [ ] Matches M-05.
- [ ] Matches M-06.

## Runtime

- [ ] Boots successfully.
- [ ] Executes empty pipeline.
- [ ] Graceful shutdown works.

## Quality Gates

- [ ] Ruff clean.
- [ ] Pyright clean.
- [ ] Pytest clean.
- [ ] Coverage ≥97%.

---

# Wave 1 Definition of Done

Wave 1 is complete only if **every checkbox in this document is satisfied**.
