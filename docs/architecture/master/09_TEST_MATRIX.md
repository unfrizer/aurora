# AURORA MASTER HANDOFF v1.0

**Document ID:** M-09

**Document Name:** Test Matrix

**File:** `docs/architecture/master/09_TEST_MATRIX.md`

**Status:** CANONICAL TEST SPECIFICATION

**Authority:** AB-00A + Wave1 Implementation Handoff

---

# Purpose

This document defines the complete Wave 1 testing specification.

It specifies:

- every required test file;
- every test case;
- edge cases;
- validation order;
- coverage requirements;
- CI quality gates.

Tests are part of the architecture and **must exist** before Wave 1 is considered complete.

---

# Test Philosophy

Wave 1 tests validate the Kernel Runtime.

Tests are divided into three groups:

1. Foundation.
2. Kernel Runtime.
3. Runtime Execution.

Every public API defined in M-03 must have executable tests.

---

# Test Directory Structure

tests/
├── core/
│   ├── test_types.py
│   ├── test_settings.py
│   └── test_logger.py
│
├── kernel/
│   ├── test_contracts.py
│   ├── test_container.py
│   ├── test_registry.py
│   ├── test_scope.py
│   ├── test_resolver.py
│   ├── test_lifecycle.py
│   └── test_events.py
│
└── runtime/
    ├── test_context.py
    ├── test_pipeline.py
    ├── test_executor.py
    ├── test_bootstrap.py
    └── test_runtime.py

---

# KR-001 Tests

## tests/core/test_types.py

### Purpose

Validate canonical Foundation types.

### Required Cases

- RuntimeLayer contains L0–L8 only.
- DIScope contains exactly four scopes.
- RuntimeStatus vocabulary unchanged.
- EventPriority vocabulary unchanged.
- EventPhase vocabulary unchanged.
- Metadata is JSON-compatible.
- Payload accepts nested JSON objects.

### Edge Cases

- Invalid RuntimeLayer creation.
- Invalid enum lookup.
- Nested JSON payload.

### Coverage

100% public symbols.

---

# KR-002 Tests

## tests/core/test_settings.py

### Required Cases

- Load .env successfully.
- Missing environment variable raises MissingConfigurationError.
- Invalid APP_ENV raises InvalidConfigurationError.
- Invalid LOG_LEVEL rejected.
- Path validation succeeds.
- reload_settings returns new immutable object.

### Edge Cases

- Empty .env.
- Invalid timezone.
- Unknown environment profile.

Coverage target:

100%.

---

# KR-003 Tests

## tests/core/test_logger.py

### Required Cases

- Logger factory returns Logger.
- Logger name preserved.
- JSON formatter enabled.
- Console formatter enabled.
- Correlation ID injected.
- Trace ID injected.
- Session ID injected.

### Edge Cases

- Multiple calls return cached logger.
- Unknown logger name.
- Missing context values.

Coverage target:

100%.

---

# KR-004 Tests

## tests/kernel/test_contracts.py

### RuntimeContract

- ABC cannot instantiate.
- Required methods exist.

### RuntimeModuleManifest

- module_id required.
- runtime_layer required.
- depends_on immutable.
- provides immutable.
- version required.

### RuntimeContext

- frozen dataclass.
- metadata immutable snapshot.

### RuntimeEvent

- required field order valid.
- payload immutable.
- trace immutable.

### LifecycleState

- default state valid.

Coverage target:

100%.

---

# KR-005 Tests

## tests/kernel/test_registry.py

### Registry Cases

- Register descriptor.
- Lookup descriptor.
- Duplicate registration raises ServiceRegistrationError.
- Remove descriptor.

---

## tests/kernel/test_scope.py

### Scope Cases

- Application scope lifetime.
- Session scope lifetime.
- Pipeline scope lifetime.
- Transient scope lifetime.

### Edge Cases

- Access disposed scope.
- Nested pipeline scope.
- Session disposal clears pipeline scope.

---

## tests/kernel/test_resolver.py

### Resolver Cases

- Resolve singleton.
- Resolve transient.
- Resolve nested dependencies.
- Resolve pipeline dependency.

### Edge Cases

- Missing dependency.
- Circular dependency.
- Invalid scope dependency.

---

## tests/kernel/test_container.py

### Container Cases

- Register provider.
- Resolve provider.
- has(service_id)
- remove(service_id)
- shutdown()

### Edge Cases

- Duplicate service.
- Unknown service.
- Shutdown disposes services.
- Eager initialization.

Coverage target:

100%.

---

# KR-006 Tests

## tests/kernel/test_lifecycle.py

### State Machine

- CREATED → INITIALIZING
- INITIALIZING → READY
- READY → RUNNING
- RUNNING → STOPPED
- RUNNING → FAILED

### Invalid Transitions

- CREATED → RUNNING
- READY → CREATED
- STOPPED → RUNNING

### Hooks

- BEFORE_INITIALIZE
- AFTER_INITIALIZE
- BEFORE_START
- AFTER_START
- BEFORE_STOP
- AFTER_STOP

Coverage target:

100%.

---

# KR-007 Tests

## tests/kernel/test_events.py

### Event Bus

- publish()
- subscribe()
- unsubscribe()

### Dispatch

- Sync dispatch.
- Async dispatch.
- Multiple handlers.
- Registration order preserved.

### Priority

Dispatch order:

1. Critical
2. High
3. Normal
4. Low

### Event Validation

- Missing payload.
- Missing trace.
- Invalid event_type.
- Invalid session_id.

### Edge Cases

- Handler throws AuroraError.
- Handler publishes new event.
- Duplicate subscription ignored.

Coverage target:

100%.

---

# KR-008 Tests

## tests/runtime/test_context.py

### Context API

- set()
- get()
- remove()
- contains()

### Metadata

- Immutable snapshot.
- JSON serialization.

### Lifetime

- Pipeline scope disposal.
- Session scope persistence.

Coverage target:

100%.

---

# KR-009 Tests

## tests/runtime/test_pipeline.py

### DAG Validation

- Valid DAG.
- Duplicate stage.
- Missing dependency.
- Dependency cycle.

### Pipeline Execution

- Sequential execution.
- Dependency execution.
- Independent stage execution.

Coverage target:

100%.

---

## tests/runtime/test_executor.py

### Executor Cases

- Execute stage.
- Execute pipeline.
- Skip dependent stage after failure.
- Publish pipeline events.

Coverage target:

100%.

---

# KR-010 Tests

## tests/runtime/test_bootstrap.py

### Startup

- Settings loaded.
- Logger initialized.
- Container built.
- EventBus created.
- Lifecycle initialized.

### Shutdown

- Reverse shutdown order.
- Resource cleanup.
- EventBus disposed.

Coverage target:

100%.

---

## tests/runtime/test_runtime.py

### Runtime

- boot()
- shutdown()
- execute_pipeline()

### Health

- Healthy runtime.
- Failed runtime.
- Runtime restart forbidden.

Coverage target:

100%.

---

# Integration Matrix

| Runtime Component | Test File |
|-------------------|-----------|
| Foundation Types | test_types.py |
| Configuration | test_settings.py |
| Logger | test_logger.py |
| Contracts | test_contracts.py |
| Registry | test_registry.py |
| Resolver | test_resolver.py |
| Container | test_container.py |
| Lifecycle | test_lifecycle.py |
| Event Bus | test_events.py |
| Context | test_context.py |
| Pipeline | test_pipeline.py |
| Executor | test_executor.py |
| Bootstrap | test_bootstrap.py |
| Runtime | test_runtime.py |

---

# Validation Order

After each KR implementation:

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

If any command fails:

STOP implementation.

Do not continue to the next KR.

---

# CI Quality Gates

## Ruff

- Zero violations.
- Import graph valid.
- Formatting valid.

## Pyright

- Zero errors.
- Zero warnings.
- Strict typing.

## Pytest

- No skipped Wave 1 tests.
- No xfail.
- No collected 0 items.

---

# Coverage Targets

| Runtime | Minimum Coverage |
|----------|-----------------:|
| KR-001 | 100% |
| KR-002 | 100% |
| KR-003 | 100% |
| KR-004 | 100% |
| KR-005 | 95% |
| KR-006 | 95% |
| KR-007 | 95% |
| KR-008 | 95% |
| KR-009 | 95% |
| KR-010 | 95% |

Overall Wave 1 coverage target:

**≥97% public API coverage**

---

# Definition of Done

Wave 1 testing is complete only if:

- every required test file exists;
- every public API has executable tests;
- Ruff passes;
- Pyright passes;
- Pytest executes non-empty test suite;
- Kernel Runtime boots successfully through `main.py`.