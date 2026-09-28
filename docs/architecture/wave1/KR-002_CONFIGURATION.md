# KR-002 — Configuration Runtime Contract v1.0

## Files
```text
src/core/settings.py
src/core/config.py
```

## Responsibilities
- immutable configuration model;
- environment/configuration loading;
- configuration access.

Must not implement DI, Event Bus, or pipeline orchestration.

## Caching
Application-wide caching of immutable configuration is NOT an automatic architecture violation.

Do not remove or redesign `lru_cache` solely because it is process-level caching.

The architecture concern is uncontrolled mutable runtime ownership, not the caching technique itself.

## Tests
Required:
```text
tests/core/test_settings.py
```

## Acceptance
- immutable configuration semantics preserved;
- configuration loading works;
- cache behavior remains compatible with ownership model;
- no later-stage implementation;
- tests collected/executed/passed.
