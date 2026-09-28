# AURORA — Wave 2 Shared State Runtime Contract & ADR v1.0

**Document ID:** AB-00E  
**Document Name:** Wave 2 Shared State Runtime Contract & ADR  
**Canonical Path:** `docs/architecture/AB-00E_Wave2_Shared_State_Runtime_Contract_v1.0.md`  
**Version:** 1.0  
**Status:** APPROVED — CANONICAL WAVE 2 AUTHORIZATION  
**Scope:** Wave 2 — L1 Shared State Runtime  
**Implementation Module:** W2-001 Shared State Runtime  
**Authority:** Architecture Freeze v1.0 + AB-00B + AB-00C + AB-00D

---

# 1. Purpose

This document authorizes the first and only implementation scope of Wave 2.

The frozen runtime topology already reserves:

```text
L0 — Kernel Runtime
L1 — Shared State Runtime
L2 — Layout Runtime
L3 — Theme Runtime
L4 — Motion Runtime
L5 — Interaction Runtime
L6 — Accessibility Runtime
L7 — Platform Runtime
L8 — Render Runtime
```

Wave 2 implements **only L1 Shared State Runtime**.

AB-00E defines the missing implementation contract required before code generation:

- authority/version reconciliation;
- exact Wave 2 scope;
- exact production file set;
- exact public API;
- ownership boundaries;
- dependency graph;
- runtime manifest;
- test matrix;
- quality gates;
- Definition of Done.

AB-00E does not redesign the architecture and does not authorize any L2–L8 implementation.

---

# 2. Architecture Authority Resolution

## 2.1 Architecture Version vs Documentation Revision

The canonical architecture baseline remains:

```text
Architecture Freeze v1.0
```

The current Master package may identify itself as:

```text
AURORA Engineering Bible v1.1
```

These version labels refer to different things.

- **Architecture Freeze v1.0** = frozen architecture baseline.
- **Engineering Bible / Master Pack v1.1** = reconciled documentation revision describing that frozen architecture plus approved resolutions.

Master Pack v1.1 does **not** create `Architecture Freeze v1.1`.

## 2.2 AGENTS.md Reconciliation

Any `AGENTS.md` wording that refers to `Engineering Bible v1.0` is interpreted as the frozen architecture baseline and is superseded **only as a documentation-version label**.

For implementation authority, the canonical meaning is:

```text
Architecture Freeze v1.0
+ current canonical Master Pack v1.1
+ approved architecture resolutions AB-00B, AB-00C, AB-00D, AB-00E
```

No other `AGENTS.md` engineering rule is superseded by AB-00E.

## 2.3 Wave 2 Authority Order

For Wave 2 implementation:

```text
Architecture Freeze v1.0
        ↓
AGENTS.md operational engineering rules
        ↓
AB-00B / AB-00C / AB-00D
        ↓
AB-00E Wave 2 Shared State Runtime Contract
        ↓
current canonical Master Pack v1.1
        ↓
older v1.0 master/handoff wording
        ↓
implementation
```

Where AB-00E explicitly defines Wave 2 behavior, AB-00E is authoritative.

---

# 3. Wave 2 Scope Freeze

## 3.1 Authorized Runtime

Wave 2 contains exactly one new runtime:

```text
SharedStateRuntime
```

Runtime layer:

```python
RuntimeLayer.L1_STATE
```

Canonical directory:

```text
src/state/
```

Implementation Module ID:

```text
W2-001
```

Module name:

```text
Shared State Runtime
```

## 3.2 Ownership Boundary

`SharedStateRuntime` owns:

- shared in-process runtime state;
- state-key lookup;
- state replacement through copy-on-write operations;
- state revision numbering;
- detached state snapshots;
- lifecycle of its own in-memory store.

`SharedStateRuntime` does **not** own:

- L0 lifecycle state;
- `RuntimeStatus`;
- dependency injection internals;
- Event Bus dispatch;
- RuntimeContext;
- Pipeline execution;
- filesystem persistence;
- database persistence;
- network synchronization;
- UI layout state;
- theme state;
- motion state;
- interaction state;
- accessibility state;
- platform state;
- render state.

## 3.3 StateRuntime Name Collision Rule

The existing L0:

```text
src/kernel/runtime/state.py
StateRuntime
```

remains the owner of **runtime lifecycle state**.

The new L1:

```text
src/state/runtime.py
SharedStateRuntime
```

owns **shared application/runtime data state**.

They are different concepts and must never be merged, renamed into each other, or given overlapping ownership.

---

# 4. Exact Production File Registry

Wave 2 W2-001 may create exactly these production files:

```text
src/state/__init__.py
src/state/contracts.py
src/state/store.py
src/state/runtime.py
src/state/module.py
```

No additional production file under `src/state/` is authorized by AB-00E.

The following are explicitly forbidden without a future ADR:

```text
src/state/events.py
src/state/reducer.py
src/state/selectors.py
src/state/history.py
src/state/persistence.py
src/state/serialization.py
src/state/cache.py
src/state/utils.py
src/state/helpers.py
src/state/models.py
```

No Wave 2 implementation may modify L0 production files merely to wire L1 into the kernel.

In particular, W2-001 must not modify:

```text
src/kernel/runtime/bootstrap.py
src/kernel/runtime/runtime.py
src/main.py
```

because L0 must not acquire an upward dependency on L1.

---

# 5. Public Symbol Registry

Wave 2 exposes exactly four public symbols:

```text
StateSnapshot
SharedStateContract
SharedStateRuntime
SHARED_STATE_MANIFEST
```

Canonical export surface:

```python
from src.state import (
    SHARED_STATE_MANIFEST,
    SharedStateContract,
    SharedStateRuntime,
    StateSnapshot,
)
```

No other Wave 2 symbol is public in W2-001.

`store.py` contains implementation-private storage only.

---

# 6. Shared State Contract

## 6.1 StateSnapshot

Canonical owner:

```text
src/state/contracts.py
```

Canonical structure:

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class StateSnapshot:
    revision: int
    values: Metadata
```

Rules:

- `revision >= 0`;
- `values` contains JSON-compatible values only;
- snapshots never alias the runtime's internal mutable dictionary;
- nested dictionaries/lists are deep-detached before crossing the public boundary;
- mutation of a caller-owned returned object must never mutate runtime truth.

The frozen dataclass shell plus detached data forms the Wave 2 snapshot boundary.

## 6.2 SharedStateContract

Canonical owner:

```text
src/state/contracts.py
```

`SharedStateContract` extends the canonical L0 `RuntimeContract`.

Canonical domain API:

```python
class SharedStateContract(RuntimeContract, ABC):

    @abstractmethod
    def get(
        self,
        key: str,
    ) -> JSONValue | None:
        ...

    @abstractmethod
    def contains(
        self,
        key: str,
    ) -> bool:
        ...

    @abstractmethod
    def snapshot(
        self,
    ) -> StateSnapshot:
        ...

    @abstractmethod
    def set(
        self,
        key: str,
        value: JSONValue,
    ) -> StateSnapshot:
        ...

    @abstractmethod
    def remove(
        self,
        key: str,
    ) -> StateSnapshot:
        ...

    @abstractmethod
    def clear(
        self,
    ) -> StateSnapshot:
        ...
```

The inherited RuntimeContract surface remains exactly the AB-00D contract:

```text
runtime_name
runtime_layer
async initialize()
async start()
async stop()
async shutdown()
health()
```

No new lifecycle vocabulary is introduced.

---

# 7. SharedStateRuntime API

Canonical owner:

```text
src/state/runtime.py
```

Canonical class:

```python
class SharedStateRuntime(SharedStateContract)
```

## 7.1 Identity

```python
@property
def runtime_name(self) -> str:
    ...
```

Canonical value:

```text
shared_state
```

```python
@property
def runtime_layer(self) -> RuntimeLayer:
    ...
```

Canonical value:

```python
RuntimeLayer.L1_STATE
```

## 7.2 Lifecycle

```python
async def initialize(self) -> None:
    ...
```

Initializes the private in-memory store.

```python
async def start(self) -> None:
    ...
```

Starts no background tasks.

```python
async def stop(self) -> None:
    ...
```

Stops no background tasks and preserves current state until shutdown.

```python
async def shutdown(self) -> None:
    ...
```

Releases the owned in-memory state.

No filesystem, thread, subprocess, network request, timer, or background worker is created by any lifecycle method.

## 7.3 Health

```python
def health(self) -> HealthStatus:
    ...
```

AB-00E does not redefine `HealthStatus`.

The method uses the canonical L0 `HealthStatus` vocabulary in force after Wave 1 reconciliation.

It is read-only and must never mutate shared state.

## 7.4 Read API

```python
def get(
    self,
    key: str,
) -> JSONValue | None:
    ...
```

Rules:

- key must be a non-empty non-whitespace string;
- returned nested JSON data is detached from internal storage;
- missing key returns `None`;
- use `contains()` when `None` must be distinguished from an absent key.

```python
def contains(
    self,
    key: str,
) -> bool:
    ...
```

Read-only.

```python
def snapshot(
    self,
) -> StateSnapshot:
    ...
```

Returns the complete detached state snapshot.

Read operations never increment revision.

## 7.5 Mutation API

```python
def set(
    self,
    key: str,
    value: JSONValue,
) -> StateSnapshot:
    ...
```

Behavior:

1. validate key;
2. validate JSON-compatible value;
3. deep-detach input;
4. replace the key using copy-on-write semantics;
5. increment revision exactly once;
6. return the new detached snapshot.

`set()` increments revision even when the new JSON value compares equal to the previous value because a successful write operation occurred.

```python
def remove(
    self,
    key: str,
) -> StateSnapshot:
    ...
```

Behavior:

- existing key: remove it and increment revision exactly once;
- missing key: no-op and do not increment revision;
- return current detached snapshot.

```python
def clear(
    self,
) -> StateSnapshot:
    ...
```

Behavior:

- non-empty state: clear and increment revision exactly once;
- already-empty state: no-op and do not increment revision;
- return current detached snapshot.

## 7.6 Revision Semantics

Initial revision:

```text
0
```

Revision is:

- monotonically increasing during one runtime lifetime;
- owned only by SharedStateRuntime/private store;
- changed only by successful public mutation operations;
- reset only when a new SharedStateRuntime lifetime begins.

Revision is not a RuntimeStatus and must never be routed through L0 `StateRuntime`.

---

# 8. Private State Store

Canonical owner:

```text
src/state/store.py
```

The implementation class is private:

```python
class _StateStore:
    ...
```

It is not exported.

It owns exactly:

```text
_state: dict[str, JSONValue]
_revision: int
```

Rules:

- no module-level mutable state;
- no singleton;
- no hidden global cache;
- no public imports of `_StateStore`;
- no direct consumer outside `SharedStateRuntime`;
- all ingress/egress data is detached;
- deterministic copy-on-write mutation;
- no persistence.

`_StateStore` is an internal component, not a separate Runtime and not a DI service.

---

# 9. Runtime Module Manifest

Canonical owner:

```text
src/state/module.py
```

The module exports exactly:

```python
SHARED_STATE_MANIFEST
```

Canonical manifest:

```python
SHARED_STATE_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("state.shared"),
    runtime_layer=RuntimeLayer.L1_STATE,
    depends_on=(),
    provides=(ServiceId("state.shared"),),
    version="1.0.0",
)
```

Rules:

- immutable manifest;
- exactly one L1 module identity;
- no dependency on L2+;
- `depends_on=()` means W2-001 has no declared runtime-module service dependency;
- `provides` declares the Shared State service identity;
- manifest declaration has no registration side effect.

AB-00E authorizes the manifest declaration but does not authorize L0 Bootstrap to import or construct SharedStateRuntime.

---

# 10. Dependency Graph

Canonical dependency direction:

```text
L2+ future consumers
        │
        ▼
SharedStateContract
        │
        ▼
SharedStateRuntime
        │
        ├── _StateStore
        │
        ├── src.core.types
        ├── src.core.exceptions
        └── src.kernel.contracts.*
                │
                ▼
              L0
```

Allowed production dependencies:

## `src/state/contracts.py`

May import:

```text
abc
dataclasses
src.core.types
src.kernel.contracts.runtime
```

## `src/state/store.py`

May import:

```text
copy
src.core.types
src.core.exceptions
src.state.contracts
```

## `src/state/runtime.py`

May import:

```text
src.core.types
src.state.contracts
src.state.store
```

It may use the canonical logger only if required by implementation, but logging must not become state ownership.

## `src/state/module.py`

May import:

```text
src.core.types
src.kernel.contracts.module
```

## `src/state/__init__.py`

May import only public sibling symbols.

---

# 11. Forbidden Dependencies

Wave 2 W2-001 must not import:

```text
src.layout
src.theme
src.motion
src.input
src.selection
src.focus
src.scroll
src.accessibility
src.renderer
src.compiler
src.devtools
src.ai
```

W2-001 also must not depend directly on these L0 runtime implementations:

```text
ContainerRuntime
LifecycleRuntime
StateRuntime
EventBusRuntime
ContextRuntime
ExecutorRuntime
OrchestratorRuntime
BootstrapRuntime
RuntimeKernel
```

Use L0 contracts/types only.

L0 production code must not import `src.state`.

This preserves:

```text
L1 → L0
```

and forbids:

```text
L0 → L1
```

---

# 12. Event Policy

W2-001 publishes no events.

W2-001 registers no Event Bus handlers.

W2-001 introduces no new EventPhase or EventPriority values.

State-change events, subscriptions, reducers, selectors, and reactive propagation are outside AB-00E scope and require a future explicit ADR.

This prevents Wave 2 from silently extending the frozen Event Bus vocabulary.

---

# 13. Persistence Policy

W2-001 is in-memory only.

Forbidden:

```text
filesystem persistence
SQLite
PostgreSQL
Redis
browser storage
remote state
network synchronization
background persistence
state recovery
state history
undo/redo
```

Persistence requires a future architecture decision.

---

# 14. Concurrency Policy

W2-001 creates:

```text
0 threads
0 subprocesses
0 background tasks
0 worker pools
```

Domain state operations are synchronous.

Only inherited lifecycle methods are asynchronous because AB-00D defines the canonical RuntimeContract lifecycle as async.

W2-001 does not introduce locks or cross-thread synchronization.

---

# 15. Exact Test File Registry

Wave 2 W2-001 may create exactly these test files:

```text
tests/state/test_contracts.py
tests/state/test_runtime.py
tests/state/test_module.py
tests/integration/test_shared_state_runtime.py
```

No placeholder, skipped, or empty tests are allowed.

---

# 16. Test Matrix

## 16.1 `tests/state/test_contracts.py`

Required:

- `StateSnapshot` is a frozen dataclass.
- `revision` exists and is non-negative in runtime-produced snapshots.
- snapshot values do not alias runtime storage.
- nested JSON dictionaries/lists do not alias runtime storage.
- `SharedStateContract` is abstract.
- `SharedStateContract` extends canonical RuntimeContract.
- exact domain method set exists.
- no Event Bus API exists on the contract.

## 16.2 `tests/state/test_runtime.py`

Identity:

- `runtime_name == "shared_state"`.
- `runtime_layer is RuntimeLayer.L1_STATE`.

Lifecycle:

- `initialize()` is awaitable.
- `start()` is awaitable.
- `stop()` is awaitable.
- `shutdown()` is awaitable.
- no background task is created.
- stop preserves current state.
- shutdown releases owned state.

Read behavior:

- new runtime snapshot revision is `0`.
- new runtime state is empty.
- missing `get()` returns `None`.
- `contains()` differentiates missing key.

Mutation behavior:

- `set()` stores JSON scalar.
- `set()` stores nested JSON.
- `set()` increments revision exactly once.
- setting equal value still increments revision.
- `remove()` existing key increments revision.
- `remove()` missing key does not increment revision.
- `clear()` non-empty state increments revision.
- `clear()` empty state does not increment revision.

Isolation:

- mutating original input after `set()` does not mutate runtime truth.
- mutating value returned by `get()` does not mutate runtime truth.
- mutating snapshot values does not mutate runtime truth.

Validation:

- empty key rejected.
- whitespace-only key rejected.
- non-JSON-compatible runtime input rejected at the public boundary.

Health:

- `health()` returns canonical `HealthStatus`.
- `health()` does not mutate revision or values.

## 16.3 `tests/state/test_module.py`

Required:

- manifest module ID is `state.shared`;
- runtime layer is `L1_STATE`;
- dependency tuple is empty;
- provides contains exactly `state.shared`;
- version is `1.0.0`;
- manifest is immutable;
- manifest construction has no runtime side effect.

## 16.4 `tests/integration/test_shared_state_runtime.py`

Required flow:

```text
construct
→ initialize
→ start
→ set state
→ read state
→ snapshot
→ stop
→ verify state preserved
→ shutdown
```

Integration assertions:

- public API is usable through `SharedStateContract`;
- revision remains deterministic;
- no L0 runtime ownership changes;
- no Event Bus is required;
- no filesystem/network resource is created.

---

# 17. Quality Gates

W2-001 is GREEN only if all commands pass:

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

Required result:

```text
Ruff: 0 violations
Pyright: 0 errors, 0 warnings, 0 informations
Pytest: non-empty, 0 failures
```

Public API test coverage target:

```text
100%
```

No skipped Wave 2 tests.

No `xfail` used to hide a required behavior.

---

# 18. Implementation Order

Wave 2 implementation order is frozen for W2-001:

```text
1. src/state/contracts.py
2. src/state/store.py
3. src/state/runtime.py
4. src/state/module.py
5. src/state/__init__.py
6. tests/state/test_contracts.py
7. tests/state/test_runtime.py
8. tests/state/test_module.py
9. tests/integration/test_shared_state_runtime.py
10. Ruff
11. Pyright
12. Pytest
```

W2-001 is one implementation task.

All W2-001-owned files may be generated in one batch.

Local W2-001 defects may be repaired within the active module.

Any required change to L0 or to another runtime layer is a Cross-Wave Architecture Blocker and must stop implementation.

---

# 19. Explicit Out-of-Scope Registry

AB-00E does not authorize:

- Layout Runtime implementation;
- Theme Runtime implementation;
- Motion Runtime implementation;
- Interaction Runtime implementation;
- Accessibility Runtime implementation;
- Platform Runtime implementation;
- Render Runtime implementation;
- reactive selectors;
- reducers;
- middleware;
- undo/redo;
- persistence;
- event-based state propagation;
- distributed/shared-process state;
- modification of RuntimeLayer vocabulary;
- modification of DI scopes;
- modification of EventPriority/EventPhase;
- modification of Wave 1 Runtime ownership;
- upward L0 → L1 imports.

Any such requirement needs another architecture resolution.

---

# 20. Wave 2 PR Boundary

The first Wave 2 PR is authorized to contain only:

```text
AB-00E documentation if committed with the branch
src/state/*
tests/state/*
tests/integration/test_shared_state_runtime.py
```

plus tool-generated lock/metadata changes only when genuinely required by `uv` and already permitted by repository policy.

The PR must not contain unrelated cleanup or Wave 1 refactoring.

---

# 21. Definition of Done

AB-00E authorization is satisfied when:

- [x] Wave 2 owner layer is fixed to `L1_STATE`.
- [x] Wave 2 directory is fixed to `src/state/`.
- [x] L0 `StateRuntime` and L1 `SharedStateRuntime` ownership are disambiguated.
- [x] exact production file list is frozen.
- [x] exact public symbol list is frozen.
- [x] exact public API is frozen.
- [x] state mutation and revision semantics are frozen.
- [x] dependency direction is frozen.
- [x] event behavior is explicitly out of scope.
- [x] persistence is explicitly out of scope.
- [x] exact test file list is frozen.
- [x] exact test matrix is defined.
- [x] quality gates are defined.
- [x] AGENTS/master version-label conflict is resolved.
- [x] Wave 2 W2-001 can be implemented without inventing architecture.

---

# 22. Approval

**Architecture Baseline:** Architecture Freeze v1.0  
**Master Documentation Revision:** v1.1  
**Wave:** 2  
**Layer:** L1 Shared State Runtime  
**Module:** W2-001 Shared State Runtime  
**Resolution State:** APPROVED  
**Implementation Authorization:** GRANTED FOR W2-001 ONLY  
**Change Policy:** Any expansion of this scope requires a new explicit ADR / architecture resolution.

---

**END OF DOCUMENT — AB-00E WAVE 2 SHARED STATE RUNTIME CONTRACT & ADR v1.0**
