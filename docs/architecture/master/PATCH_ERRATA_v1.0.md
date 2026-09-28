# PATCH ERRATA v1.0

Status: CANONICAL

Applies To:
- PATCH-04 Module Filename Disambiguation
- PATCH-06 Events Filename Disambiguation

---

## ERRATA-001 — Module Filename Disambiguation

Replace the sentence:

"There is src/kernel/runtime/module.py."

With:

"There is no src/kernel/runtime/module.py.
RuntimeModuleManifest exists only in src/kernel/contracts/module.py."

---

## ERRATA-002 — Events Filename Disambiguation

Replace the implication that runtime/events.py exists.

Canonical rule:

There is no src/kernel/runtime/events.py.

RuntimeEvent exists only in:

src/kernel/contracts/events.py

Event Runtime implementation files are:

- bus.py
- publisher.py
- dispatcher.py
- subscriber.py

All RuntimeEvent imports must use:

from src.kernel.contracts.events import RuntimeEvent