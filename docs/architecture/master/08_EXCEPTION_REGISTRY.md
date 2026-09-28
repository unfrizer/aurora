# AURORA MASTER HANDOFF v1.0

**Document ID:** M-08

**Document Name:** Exception Registry

**File:** `docs/architecture/master/08_EXCEPTION_REGISTRY.md`

**Status:** CANONICAL EXCEPTION REGISTRY

**Authority:** AB-00A + Wave1 Implementation Handoff

---

# Purpose

This document defines the complete exception hierarchy for AURORA Wave 1.

It specifies:

- every exception class;
- owning module;
- when it is raised;
- who catches it;
- propagation rules;
- logging policy.

No new exception may be introduced without updating this registry.

---

# Exception Hierarchy

AuroraError
├── ConfigurationError
│   ├── MissingConfigurationError
│   └── InvalidConfigurationError
│
├── ValidationError
│   ├── ContractValidationError
│   └── StateValidationError
│
├── ManifestError
│   ├── InvalidManifestError
│   └── RuntimeDependencyError
│
├── ContainerError
│   ├── ServiceRegistrationError
│   ├── ServiceResolutionError
│   └── CircularDependencyError
│
├── ScopeViolationError
│
├── EventBusError
│   ├── InvalidEventError
│   ├── EventPublishError
│   └── EventHandlerError
│
└── RuntimeError
    ├── RuntimeInitializationError
    ├── RuntimeShutdownError
    └── RuntimeStateError

---

# Root Exception

## AuroraError

### Owner

`src/core/exceptions.py`

### Purpose

Root exception for the entire repository.

### Rules

- Every custom exception inherits from AuroraError.
- Never raise AuroraError directly.
- Never catch `Exception` when AuroraError is sufficient.

---

# Configuration Exceptions

## ConfigurationError

Raised when configuration subsystem fails.

Caught by:

- bootstrap.py
- runtime.py

Logs:

ERROR

Terminates Runtime startup.

---

## MissingConfigurationError

Raised when required ENV variable is absent.

Examples

- OPENROUTER_API_KEY missing.
- APP_ENV missing.

Caught by:

Configuration loader.

Propagated to Bootstrap.

---

## InvalidConfigurationError

Raised when ENV value is invalid.

Examples

- Invalid log level.
- Invalid timezone.
- Invalid directory path.

---

# Validation Exceptions

## ValidationError

Base validation failure.

Used by:

- Manifest validation.
- Runtime validation.
- Pipeline validation.

---

## ContractValidationError

Raised when a contract implementation violates KR-004.

Examples

- RuntimeModule missing manifest field.
- Invalid ServiceDescriptor.

---

## StateValidationError

Raised when lifecycle transition is illegal.

Examples

- CREATED → RUNNING.
- STOPPED → RUNNING.

---

# Manifest Exceptions

## ManifestError

Base manifest failure.

Used during module registration.

---

## InvalidManifestError

Raised when manifest schema is invalid.

Examples

- Missing `provides`.
- Missing `module_id`.
- Invalid runtime layer.

---

## RuntimeDependencyError

Raised when dependency graph is invalid.

Examples

- Unknown dependency.
- Dependency cycle.
- Duplicate module.

---

# Container Exceptions

## ContainerError

Base DI failure.

---

## ServiceRegistrationError

Raised during service registration.

Examples

- Duplicate ServiceId.
- Invalid scope.

---

## ServiceResolutionError

Raised when service cannot be resolved.

Examples

- Missing provider.
- Missing dependency.

---

## CircularDependencyError

Raised when resolver detects a cycle.

Examples

A → B → C → A

Implementation must stop immediately.

---

## ScopeViolationError

Raised when scope visibility is violated.

Examples

Application depends on Pipeline.

Session resolves Transient after disposal.

---

# Event Bus Exceptions

## EventBusError

Base Event Bus failure.

---

## InvalidEventError

Raised before publishing.

Examples

Missing required event field.

Invalid payload.

---

## EventPublishError

Raised during publish pipeline.

Examples

Dispatcher unavailable.

Event Bus stopped.

---

## EventHandlerError

Raised when handler throws AuroraError.

Rules

Original exception preserved as cause.

Handler name included.

---

# Runtime Exceptions

## RuntimeError

Base runtime execution failure.

---

## RuntimeInitializationError

Raised during startup.

Examples

Container failed.

Logger failed.

Configuration failed.

Lifecycle initialization failed.

Startup stops immediately.

---

## RuntimeShutdownError

Raised during graceful shutdown.

Examples

Module stop failure.

Resource cleanup failure.

Shutdown continues collecting failures.

---

## RuntimeStateError

Raised when runtime state machine is violated.

Examples

Execute pipeline before RUNNING.

Shutdown before INITIALIZED.

---

# Exception Ownership Matrix

| Exception Group | Owner Runtime |
|-----------------|---------------|
| Configuration | KR-002 |
| Validation | KR-001 |
| Manifest | KR-004 |
| Container | KR-005 |
| Scope | KR-005 |
| Event Bus | KR-007 |
| Runtime | KR-006 / KR-010 |

No exception is owned by multiple runtimes.

---

# Logging Policy

| Exception | Log Level |
|-----------|-----------|
| MissingConfigurationError | ERROR |
| InvalidConfigurationError | ERROR |
| ContractValidationError | ERROR |
| RuntimeDependencyError | ERROR |
| CircularDependencyError | ERROR |
| EventPublishError | ERROR |
| EventHandlerError | ERROR |
| RuntimeInitializationError | CRITICAL |
| RuntimeShutdownError | WARNING |
| RuntimeStateError | ERROR |

Exceptions are logged exactly once.

---

# Catching Rules

## Allowed

```python
except AuroraError:
```

```python
except ConfigurationError:
```

```python
except ContainerError:
```

## Forbidden

```python
except Exception:
```

unless re-raising AuroraError.

Never swallow exceptions silently.

---

# Propagation Rules

Configuration

Settings

↓

Bootstrap

↓

RuntimeInitializationError

Container

Resolver

↓

ServiceResolutionError

↓

RuntimeInitializationError

Event Bus

Handler

↓

EventHandlerError

↓

EventPublishError (optional propagation)

Pipeline

Stage

↓

AuroraError

↓

pipeline.failed event

↓

Runtime continues according to DAG policy.

---

# Exception Serialization Rules

Every AuroraError must expose:

- error_code
- message
- module_id (optional)
- details (JSON serializable)

Forbidden fields:

- traceback object
- logger
- file handle
- runtime object

---

# Validation Requirements

Pyright

- No bare Exception subclasses.
- No unknown exception types.

Ruff

- No empty except blocks.
- No broad exception catches.

Pytest

Required tests:

- configuration errors
- container errors
- circular dependency
- invalid manifest
- invalid event
- runtime initialization failure
- lifecycle state validation

---

# Definition of Done

Exception Registry is complete only if:

- every exception exists exactly once;
- every runtime owns only its exceptions;
- propagation follows this document;
- logging follows this document;
- serialization is JSON-compatible.