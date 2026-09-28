# KR-003 — Logging Runtime Contract v1.0

## Files
```text
src/core/logging_config.py
src/core/logger.py
```

## Responsibilities
- logging configuration;
- project logging API;
- execution/logging context.

## Allowed Infrastructure
Not automatically an architecture conflict:
- ContextVar;
- standard-library logger registry;
- logger caching;
- module-level logger references.

They are allowed when they do not become authoritative mutable AURORA runtime-state ownership or bypass the DI/lifecycle model.

## Must Not
- implement DI;
- implement Event Bus;
- implement pipeline orchestration;
- create a second logging subsystem;
- create generic logging utilities.

## Tests
Required:
```text
tests/core/test_logger.py
```
