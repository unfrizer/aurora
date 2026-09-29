# AURORA — Wave 8 Platform Runtime Contract & ADR v1.0

**Document ID:** AB-00K  
**Status:** APPROVED — CANONICAL WAVE 8 AUTHORIZATION  
**Scope:** Wave 8 — L7 Platform Runtime  
**Implementation Module:** W8-001 Platform Core Runtime  
**Authority:** Architecture Freeze v1.0, Master Pack v1.1, AB-00B through AB-00J, and ADR-001.

## Boundary

W8-001 introduces `PlatformRuntime`, the L7 owner of a caller-supplied immutable
target-platform descriptor. It is deliberately a bridge contract, not a Windows
adapter: it performs no OS detection or calls, filesystem access, process launch,
window management, browser control, persistence, network operation, Event Bus
publication, or rendering. Those integration concerns need later approved contracts.

The Master Pack reserves L7 without exact APIs; ADR-001 permits this deterministic,
in-memory minimal boundary.

## Files and API

Only these files are owned:

```text
src/platform/__init__.py
src/platform/contracts.py
src/platform/runtime.py
src/platform/module.py
tests/platform_runtime/test_platform_contracts.py
tests/platform_runtime/test_platform_behavior.py
tests/platform_runtime/test_platform_module.py
tests/integration/test_platform_runtime.py
```

Public exports are `PlatformDescriptor`, `PlatformSnapshot`, `PlatformContract`,
`PlatformRuntime`, and `PLATFORM_MANIFEST`.

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class PlatformDescriptor:
    platform_id: str
    display_name: str

@dataclass(slots=True, frozen=True, kw_only=True)
class PlatformSnapshot:
    revision: int
    platform: PlatformDescriptor | None
```

Both descriptor fields must be non-empty after trimming. `PlatformContract`
extends `RuntimeContract` with `current()`, `snapshot()`, `configure()`, and
`clear()`. Configure increments revision once; clear increments only when a
descriptor exists. Reads never mutate. Shutdown releases state, and initialize
after shutdown resets it to revision zero.

`PlatformRuntime` identity is `"platform"` and `RuntimeLayer.L7_PLATFORM`.
Lifecycle owns no resource and health is `HealthStatus.OK`.

```python
PLATFORM_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("platform.core"), runtime_layer=RuntimeLayer.L7_PLATFORM,
    depends_on=(), provides=(ServiceId("platform.core"),), version="1.0.0",
)
```

Only core types/exceptions and L0 contracts may be imported. No lower concrete
runtime or L8 import is allowed. Ruff, Pyright, and a non-empty Pytest suite are
the completion gate.

`tests/platform_runtime/` uses unique test module names. A `tests/platform/`
package would shadow Python's standard-library `platform` module during test
discovery, while flat generic test module names collide with other test files.
