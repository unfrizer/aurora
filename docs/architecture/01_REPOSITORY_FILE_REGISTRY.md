# AURORA — Repository File Registry v1.0

**Rule:** Every production file has exactly one owner and one active implementation stage.

## Canonical Structure
```text
src/
├── core/
│   ├── __init__.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── types.py
│   ├── version.py
│   ├── settings.py
│   ├── config.py
│   ├── logging_config.py
│   └── logger.py
├── kernel/
│   └── contracts/
│       ├── __init__.py
│       ├── context.py
│       ├── events.py
│       ├── lifecycle.py
│       ├── module.py
│       ├── runtime.py
│       └── service.py
├── runtime/
├── events/
├── shared/
├── theme/
├── layout/
├── motion/
├── input/
├── selection/
├── focus/
├── scroll/
├── accessibility/
├── components/
├── renderer/
├── compiler/
├── devtools/
└── ai/
```

## Wave 1 Ownership
| Stage | Files |
|---|---|
| W1.01 | `src/core/__init__.py`, `constants.py`, `exceptions.py`, `types.py`, `version.py` |
| W1.02 | `src/core/settings.py`, `src/core/config.py` |
| W1.03 | `src/core/logging_config.py`, `src/core/logger.py` |
| W1.04 | `src/kernel/contracts/__init__.py`, `context.py`, `events.py`, `lifecycle.py`, `module.py`, `runtime.py`, `service.py` |
| W1.05–W1.10 | Exact file sets require their authoritative module contracts |
| W1.11 | Wave 1 executable tests |

## Forbidden Unless Explicitly Approved
```text
src/utils/
src/utils/helpers.py
core/models.py
misc.py
common.py
shared_runtime.py
```

No unowned production file is permitted.
