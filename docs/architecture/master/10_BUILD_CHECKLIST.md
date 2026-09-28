# AURORA MASTER HANDOFF v1.0

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

# KR-002 — Configuration Runtime Checklist

## Files

- [ ] `settings.py`
- [ ] `config.py`

## Settings

- [ ] Frozen model.
- [ ] Environment validation.
- [ ] Path validation.
- [ ] Immutable values.

## Config Loader

- [ ] `get_settings()`
- [ ] `reload_settings()`
- [ ] Application cache only.

## Validation

- [ ] Missing env raises MissingConfigurationError.
- [ ] Invalid env raises InvalidConfigurationError.
- [ ] Ruff passes.
- [ ] Pyright passes.
- [ ] `test_settings.py` passes.

---

# KR-003 — Logging Runtime Checklist

## Files

- [ ] `logging_config.py`
- [ ] `logger.py`

## LoggingConfig

- [ ] JSON formatter.
- [ ] Console formatter.
- [ ] Context filter.

## Logger API

- [ ] `configure_logging()`
- [ ] `get_logger()`

## Logging Rules

- [ ] No `print()`.
- [ ] No `basicConfig()`.
- [ ] Structured logging.
- [ ] Correlation IDs.
- [ ] Session IDs.
- [ ] Trace IDs.

## Validation

- [ ] Ruff passes.
- [ ] Pyright passes.
- [ ] `test_logger.py` passes.

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

# KR-011 — Test Suite Checklist

## Core

- [ ] test_types.py
- [ ] test_settings.py
- [ ] test_logger.py

## Kernel

- [ ] test_contracts.py
- [ ] test_container.py
- [ ] test_registry.py
- [ ] test_scope.py
- [ ] test_resolver.py
- [ ] test_lifecycle.py
- [ ] test_events.py

## Runtime

- [ ] test_context.py
- [ ] test_pipeline.py
- [ ] test_executor.py
- [ ] test_bootstrap.py
- [ ] test_runtime.py

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