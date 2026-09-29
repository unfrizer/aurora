# AURORA — Wave 5 Motion Runtime Contract & ADR v1.0

**Document ID:** AB-00H  
**Status:** APPROVED — CANONICAL WAVE 5 AUTHORIZATION  
**Scope:** Wave 5 — L4 Motion Runtime  
**Implementation Module:** W5-001 Motion Core Runtime  
**Authority:** Architecture Freeze v1.0, Master Pack v1.1, AB-00B through
AB-00G, and ADR-001.

## Purpose and Boundary

W5-001 introduces the only L4 runtime, `MotionRuntime`. It deterministically
samples normalized progress for an immutable `MotionDefinition` from a
caller-supplied elapsed time. The runtime does not own clocks, animation loops,
rendering, layout, UI state, event publication, persistence, provider calls,
or background work.

The Master Pack reserves L4 but has no implementation-level API. ADR-001
permits this narrow default: immutable contracts and pure, deterministic
in-memory behavior. Future easing curves, timelines, keyframes, animation
scheduling, interpolation, platform integration, and rendering require a new
approved contract.

## Exact Production Files

```text
src/motion/__init__.py
src/motion/contracts.py
src/motion/runtime.py
src/motion/module.py
```

No other Wave 5 production file is authorized.

## Public API

The package exports exactly:

```text
MotionDefinition
MotionSample
MotionContract
MotionRuntime
MOTION_MANIFEST
```

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class MotionDefinition:
    motion_id: str
    duration_ms: float

@dataclass(slots=True, frozen=True, kw_only=True)
class MotionSample:
    motion_id: str
    progress: float
    is_complete: bool
```

`motion_id` is non-empty after trimming. `duration_ms` and public
`elapsed_ms` inputs are finite non-negative numbers. For a non-zero duration,
progress equals `min(elapsed_ms / duration_ms, 1.0)`. A zero-duration motion is
immediately complete with progress `1.0`.

`MotionContract` extends the L0 `RuntimeContract` and adds exactly:

```python
def validate(self, definition: MotionDefinition) -> None: ...
def sample(self, definition: MotionDefinition, elapsed_ms: float) -> MotionSample: ...
```

`MotionRuntime` has `runtime_name == "motion"` and
`runtime_layer is RuntimeLayer.L4_MOTION`. Lifecycle methods have no side
effects; `health()` is read-only and returns `HealthStatus.OK`.

## Dependencies and Manifest

W5-001 may import only `math`, `src.core.exceptions`, `src.core.types`, and L0
contract modules. It must not import `src.state`, `src.layout`, `src.theme`, L0
concrete runtimes, or L5–L8. Lower layers must not import `src.motion`.

```python
MOTION_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("motion.core"),
    runtime_layer=RuntimeLayer.L4_MOTION,
    depends_on=(),
    provides=(ServiceId("motion.core"),),
    version="1.0.0",
)
```

The immutable manifest has no registration side effect and does not construct
the runtime.

## Tests and Definition of Done

W5-001 owns exactly:

```text
tests/motion/__init__.py
tests/motion/test_contracts.py
tests/motion/test_runtime.py
tests/motion/test_module.py
tests/integration/test_motion_runtime.py
```

Tests cover immutability, abstract inheritance, input validation, zero and
finite duration sampling, clamping, lifecycle, manifest contents, and an
end-to-end in-memory flow. Ruff, Pyright, and Pytest must pass with a non-empty
suite before the module is complete.
