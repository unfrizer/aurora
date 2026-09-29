# AURORA — Wave 6 Interaction Runtime Contract & ADR v1.0

**Document ID:** AB-00I  
**Status:** APPROVED — CANONICAL WAVE 6 AUTHORIZATION  
**Scope:** Wave 6 — L5 Interaction Runtime  
**Implementation Module:** W6-001 Interaction Core Runtime  
**Authority:** Architecture Freeze v1.0, Master Pack v1.1, AB-00B through
AB-00H, and ADR-001.

## Purpose and Boundary

W6-001 adds the only L5 runtime, `InteractionRuntime`. It owns the latest
validated immutable interaction request and its monotonically increasing
revision for one runtime lifetime. It is the narrow domain boundary between a
future input surface and later consumers.

It does not map platform input, render UI, execute commands, publish Event Bus
events, access Layout/Theme/Motion runtimes, persist history, implement
undo/redo, start background work, or access files or network resources.
The Master Pack reserves L5 but gives no exact API; ADR-001 authorizes the
immutable, deterministic in-memory default recorded here.

## Exact Files and Public API

W6-001 owns exactly:

```text
src/interaction/__init__.py
src/interaction/contracts.py
src/interaction/runtime.py
src/interaction/module.py
tests/interaction/__init__.py
tests/interaction/test_contracts.py
tests/interaction/test_runtime.py
tests/interaction/test_module.py
tests/integration/test_interaction_runtime.py
```

The package exports only:

```text
InteractionRequest
InteractionSnapshot
InteractionContract
InteractionRuntime
INTERACTION_MANIFEST
```

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class InteractionRequest:
    interaction_id: str
    action: str
    target_id: str

@dataclass(slots=True, frozen=True, kw_only=True)
class InteractionSnapshot:
    revision: int
    latest: InteractionRequest | None
```

All `InteractionRequest` fields must be non-empty strings after trimming.
`action` is deliberately opaque; W6-001 introduces no input/action vocabulary.

`InteractionContract` extends `RuntimeContract` and adds only:

```python
def current(self) -> InteractionRequest | None: ...
def snapshot(self) -> InteractionSnapshot: ...
def submit(self, request: InteractionRequest) -> InteractionSnapshot: ...
def clear(self) -> InteractionSnapshot: ...
```

`submit()` validates, stores, and increments revision exactly once, even when
the same request is re-submitted. `clear()` increments only when a latest
request exists. Reads do not mutate state. Shutdown releases owned state, and a
subsequent initialize begins a fresh lifetime at revision zero.

## Identity, Manifest, and Dependencies

`InteractionRuntime` has `runtime_name == "interaction"` and
`runtime_layer is RuntimeLayer.L5_INTERACTION`. It has no lifecycle resources
and returns read-only `HealthStatus.OK`.

```python
INTERACTION_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("interaction.core"),
    runtime_layer=RuntimeLayer.L5_INTERACTION,
    depends_on=(),
    provides=(ServiceId("interaction.core"),),
    version="1.0.0",
)
```

W6-001 may import only `src.core.types`, `src.core.exceptions`, and L0
contracts. It may not import lower concrete runtimes, L6–L8, Event Bus,
platform libraries, or any network/persistence provider. Its manifest creates
no runtime or registration side effect.

## Quality Gate

The module is complete only when Ruff, Pyright, and a non-empty Pytest suite
pass. Future action semantics, event dispatch, UI bindings, input mapping,
history, and persistence require a separate approved contract.
