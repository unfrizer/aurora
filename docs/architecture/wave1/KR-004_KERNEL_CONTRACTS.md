# KR-004 — Kernel Contracts Contract v1.0

**Status:** APPROVED — ADR-004 reconciliation, 2026-10-05.

**Authority:** AB-00A, AB-00B/C/D and explicitly approved ADR-004 P-01/P-04/P-05.

## Active Reconciliation Scope

This module task may change only:

- `src/kernel/contracts/service.py`: the descriptor extension and lifecycle documentation;
- `src/kernel/contracts/context.py`: snapshot-boundary documentation only;
- `src/kernel/contracts/events.py`: snapshot-boundary documentation only;
- `tests/kernel/test_contracts.py`: canonical contract-required test adjustments.

The other KR-004 files and exports remain unchanged. The test file remains owned
by KR-011; ADR-004 explicitly authorizes its adjustments for the active module.
Architecture registry corrections are governance changes under ADR-001.
No other production module, test file, dependency or runtime vocabulary changes.

AB-00D remains authoritative for the existing context, event and RuntimeContract
surface; AB-00B/C retain lifecycle and priority vocabulary. ADR-004 adds only the
descriptor field below. Its exact schema supersedes obsolete M-01/M-03 descriptor
factory/hook/metadata/property declarations, without introducing a ServiceFactory.

## Files
```text
src/kernel/contracts/__init__.py
src/kernel/contracts/context.py
src/kernel/contracts/events.py
src/kernel/contracts/lifecycle.py
src/kernel/contracts/module.py
src/kernel/contracts/runtime.py
src/kernel/contracts/service.py
```

## Boundary
Contract-only.

Forbidden:
- I/O;
- network;
- threads;
- subprocesses;
- event dispatch;
- service registration;
- bootstrap;
- provider execution;
- business logic;
- global runtime mutation.

## context.py
Defines kernel execution/context contracts.
Public metadata uses canonical `Metadata` typing.
Mutable defaults require factories.
The seven AB-00D fields remain unchanged. Frozen dataclasses prevent field
reassignment, not nested JSON mutation. Detached recursive JSON copies at public
context boundaries belong to KR-008; context object identity is not guaranteed.
Direct contract construction does not copy, deep-freeze or validate metadata.

## events.py
Defines Typed Event Runtime contract.
Mandatory:
```text
event_id
event_type
session_id
timestamp
payload
trace
```
No concrete dispatch.
AB-00C/AB-00D retain the existing `priority` field and NORMAL default. Frozen event
shells do not deep-freeze payloads. Publisher/Dispatch in KR-007 own detached JSON
copies at publication and per-handler delivery; copying preserves logical event
identity and does not create a new event. These runtime changes are not implemented
or claimed complete by this contract module.

## module.py
Defines `RuntimeModuleManifest`:
```text
module_id
runtime_layer
depends_on
provides
version
```

## lifecycle.py
Defines lifecycle contract boundary.
Do not invent lifecycle states/transitions.

## runtime.py
Defines runtime contract only.
No concrete bootstrap.

## service.py
Defines service contract with:
```text
initialize()
shutdown()
```
Implementation descriptors must be compatible with ServiceContract.

`ServiceDescriptor` remains a frozen, keyword-only, slotted dataclass with exactly:

| Field | Type | Default |
| --- | --- | --- |
| service_id | ServiceId | required |
| scope | DIScope | required |
| implementation | type[ServiceContract] | required |
| eager | bool | False |
| dependencies | tuple[tuple[str, ServiceId], ...] | () |

Each dependency pair binds a constructor keyword parameter to a registered
ServiceId. Different parameters may bind the same ID. Empty bindings preserve
existing no-dependency descriptors. No new factory, hook-name, metadata or derived
property API is introduced. Construction of a descriptor must not instantiate,
initialize or resolve a service. Validation of duplicate/unknown parameter names,
missing IDs, constructor compatibility and dependency scope/graph belongs to
KR-005, not this dataclass. No descriptor `__post_init__` is added.

ServiceContract keeps exactly async `initialize() -> None` and
`shutdown() -> None`. Under ADR-004, DI awaits initialization once before publishing
a ready instance; shutdown must tolerate partial initialization. KR-004 documents
these obligations but does not implement DI acquisition or cleanup.

## DI
Only:
```text
Application
Session
Pipeline
Transient
```
No DI container implementation in KR-004.

## Tests
Required:
```text
tests/kernel/test_contracts.py
```

Acceptance: exact five-field descriptor schema, typed implementation, immutable
binding/default tuples, old constructor compatibility, keyword-only/slotted/frozen
shells, no concrete service behavior, unchanged exports/abstract methods, manifest
fields, mandatory event fields, priority and UTC/default factory independence.
Nested JSON detachment acceptance belongs to KR-007/KR-008, not direct dataclass
construction. Run repository Pyright, Ruff and Pytest; no empty/skipped/xfail suite
is success. Passing existing runtime tests does not establish ADR-004 compliance
of modules that have not yet been reconciled.
