# AURORA — Wave 3 Layout Runtime Contract & ADR v1.0

**Document ID:** AB-00F  
**Document Name:** Wave 3 Layout Runtime Contract & ADR  
**Canonical Path:** `docs/architecture/AB-00F_Wave3_Layout_Runtime_Contract_v1.0.md`  
**Version:** 1.0  
**Status:** APPROVED — CANONICAL WAVE 3 AUTHORIZATION  
**Scope:** Wave 3 — L2 Layout Runtime  
**Implementation Module:** W3-001 Layout Core Runtime  
**Authority:** Architecture Freeze v1.0 + AB-00B + AB-00C + AB-00D + AB-00E

---

# 1. Purpose

AB-00F authorizes the first implementation scope of Wave 3.

The frozen topology already assigns:

```text
L0 Kernel Runtime        — Wave 1
L1 Shared State Runtime  — Wave 2
L2 Layout Runtime        — Wave 3
L3 Theme Runtime         — Wave 4
L4 Motion Runtime        — Wave 5
L5 Interaction Runtime   — Wave 6
L6 Accessibility Runtime — Wave 7
L7 Platform Runtime      — Wave 8
L8 Render Runtime        — Wave 9
```

AB-00F authorizes only **W3-001 Layout Core Runtime** in `src/layout/`.

L3–L8 remain forbidden until their own approved contracts/ADRs exist.

---

# 2. Authority and Layer Rule

The architecture baseline remains **Architecture Freeze v1.0**.  
The Master Pack v1.1 is the current documentation revision under the version-resolution established by AB-00E.

Canonical dependency direction remains:

```text
higher layer → same/lower layer
lower layer ↛ higher layer
```

Therefore L2 may depend on L0 and L1, but L0 and L1 must never import `src.layout`.

AB-00F does not modify any Wave 1 or Wave 2 ownership.

---

# 3. Authorized Scope

Wave 3 W3-001 contains exactly one new runtime:

```text
LayoutRuntime
```

Canonical layer:

```python
RuntimeLayer.L2_LAYOUT
```

Canonical directory:

```text
src/layout/
```

LayoutRuntime owns only deterministic geometric arrangement of immutable layout input.

It does not own:

- shared application state;
- lifecycle state;
- Event Bus dispatch;
- Theme;
- Motion;
- Interaction;
- Accessibility;
- Platform;
- Render;
- persistence;
- networking;
- filesystem IO.

---

# 4. Exact Production Files

W3-001 may create exactly:

```text
src/layout/__init__.py
src/layout/contracts.py
src/layout/solver.py
src/layout/runtime.py
src/layout/module.py
```

No additional production file under `src/layout/` is authorized.

The following are explicitly out of scope:

```text
flex.py
grid.py
constraints.py
measure.py
intrinsic.py
cache.py
events.py
state.py
utils.py
helpers.py
models.py
```

W3-001 must not modify:

```text
src/kernel/runtime/bootstrap.py
src/kernel/runtime/runtime.py
src/main.py
src/state/*
```

for the purpose of wiring LayoutRuntime into a lower layer.

---

# 5. Public API Surface

W3-001 exposes exactly eight public symbols:

```text
LayoutDirection
LayoutSize
LayoutRect
LayoutNode
LayoutBox
LayoutContract
LayoutRuntime
LAYOUT_MANIFEST
```

Canonical package export:

```python
from src.layout import (
    LAYOUT_MANIFEST,
    LayoutBox,
    LayoutContract,
    LayoutDirection,
    LayoutNode,
    LayoutRect,
    LayoutRuntime,
    LayoutSize,
)
```

No other W3-001 symbol is public.

---

# 6. Layout Contracts

Canonical owner:

```text
src/layout/contracts.py
```

## LayoutDirection

```python
class LayoutDirection(StrEnum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"
```

No additional direction is authorized in W3-001.

## LayoutSize

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class LayoutSize:
    width: float
    height: float
```

Valid dimensions are finite and `>= 0.0`.

## LayoutRect

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class LayoutRect:
    x: float
    y: float
    width: float
    height: float
```

No pixel rounding occurs in W3-001.

## LayoutNode

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class LayoutNode:
    node_id: str
    size: LayoutSize
    direction: LayoutDirection = LayoutDirection.VERTICAL
    gap: float = 0.0
    children: tuple["LayoutNode", ...] = ()
```

Rules:

- `node_id` must be non-empty after `strip()`;
- every node ID is unique inside one tree;
- `gap` is finite and `>= 0.0`;
- children are an immutable tuple;
- input tree is acyclic;
- node size is explicit;
- no in-place mutation.

## LayoutBox

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class LayoutBox:
    node_id: str
    rect: LayoutRect
    children: tuple["LayoutBox", ...] = ()
```

LayoutBox is an immutable recursive geometry result.

---

# 7. LayoutContract

Canonical owner:

```text
src/layout/contracts.py
```

```python
class LayoutContract(RuntimeContract, ABC):

    @abstractmethod
    def validate(self, root: LayoutNode) -> None:
        ...

    @abstractmethod
    def layout(self, root: LayoutNode) -> LayoutBox:
        ...
```

It inherits the AB-00D RuntimeContract unchanged:

```text
runtime_name
runtime_layer
async initialize()
async start()
async stop()
async shutdown()
health()
```

No additional lifecycle API is introduced.

---

# 8. Canonical Layout Algorithm

W3-001 implements one deterministic stack algorithm.

The root is placed at:

```text
x = 0.0
y = 0.0
width  = root.size.width
height = root.size.height
```

For `VERTICAL`, direct children preserve input order:

```text
child[0].x = parent.x
child[0].y = parent.y

child[n].x = parent.x
child[n].y = child[n-1].y + child[n-1].height + parent.gap
```

For `HORIZONTAL`:

```text
child[0].x = parent.x
child[0].y = parent.y

child[n].x = child[n-1].x + child[n-1].width + parent.gap
child[n].y = parent.y
```

Every child is recursively arranged using its own direction and gap.

Returned coordinates are absolute in the root coordinate space.

W3-001 does not stretch, shrink, wrap, clip, scroll, or reject geometric overflow. A child may extend outside its parent.

Equal immutable input must always produce equal output.

---

# 9. Validation

`LayoutRuntime.validate()` validates the complete tree before layout.

Required validation:

```text
non-empty node_id
unique node_id
finite non-negative width
finite non-negative height
finite non-negative gap
known LayoutDirection
acyclic tree
tuple children
```

Failure raises the existing canonical `ValidationError`.

W3-001 introduces no new exception class.

`layout()` must validate before solver execution and must never return a partial result for invalid input.

---

# 10. Private Solver

Canonical owner:

```text
src/layout/solver.py
```

Private implementation:

```python
class _LayoutSolver:
    ...
```

It owns only:

- recursive arrangement;
- cursor calculation;
- LayoutRect construction;
- LayoutBox construction.

It is not public, not a Runtime, not a DI service, and owns no cache or mutable application state.

---

# 11. LayoutRuntime

Canonical owner:

```text
src/layout/runtime.py
```

```python
class LayoutRuntime(LayoutContract)
```

Identity:

```python
runtime_name == "layout"
runtime_layer == RuntimeLayer.L2_LAYOUT
```

Lifecycle:

```python
async def initialize(self) -> None: ...
async def start(self) -> None: ...
async def stop(self) -> None: ...
async def shutdown(self) -> None: ...
```

These methods create no threads, tasks, subprocesses, filesystem resources, or network resources.

Health:

```python
def health(self) -> HealthStatus:
    ...
```

Health is read-only and uses the already-canonical L0 HealthStatus vocabulary.

Domain API:

```python
def validate(self, root: LayoutNode) -> None: ...
def layout(self, root: LayoutNode) -> LayoutBox: ...
```

Both domain methods are synchronous.

---

# 12. Runtime Manifest

Canonical owner:

```text
src/layout/module.py
```

Exports exactly:

```text
LAYOUT_MANIFEST
```

Canonical manifest:

```python
LAYOUT_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("layout.core"),
    runtime_layer=RuntimeLayer.L2_LAYOUT,
    depends_on=(),
    provides=(ServiceId("layout.core"),),
    version="1.0.0",
)
```

The manifest has no registration side effect and does not instantiate LayoutRuntime.

W3-001 intentionally has no required L1 runtime-module dependency. L2 is permitted to depend on L1, but this module does not require SharedStateRuntime.

---

# 13. Dependency Contract

Allowed direction:

```text
LayoutRuntime
    ↓
LayoutContract / layout contracts
    ↓
L0 core types + exceptions
    ↓
L0 RuntimeContract / RuntimeModuleManifest
```

Allowed production imports:

`contracts.py`:

```text
abc
dataclasses
enum
src.core.types
src.kernel.contracts.runtime
```

`solver.py`:

```text
src.layout.contracts
```

`runtime.py`:

```text
math
src.core.exceptions
src.core.types
src.layout.contracts
src.layout.solver
```

`module.py`:

```text
src.core.types
src.kernel.contracts.module
```

`__init__.py` imports only public sibling symbols.

Forbidden direct dependencies:

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
SharedStateRuntime
```

Forbidden higher-layer imports:

```text
src.theme
src.motion
src.interaction
src.accessibility
src.platform
src.render
src.renderer
```

---

# 14. State, Events and Concurrency

W3-001 stores no authoritative application state and no retained layout tree.

There is no layout cache.

W3-001 publishes no events and registers no Event Bus handlers.

W3-001 creates:

```text
0 threads
0 subprocesses
0 background tasks
0 worker pools
```

Reactive invalidation, retained layout state, Event Bus integration, or Shared State integration require a later ADR.

---

# 15. Explicit Out-of-Scope Features

AB-00F does not authorize:

- Flexbox;
- Grid;
- percentages;
- min/max constraints;
- intrinsic/content measurement;
- text measurement;
- alignment modes;
- wrapping;
- margins/padding/borders;
- absolute/fixed positioning modes;
- clipping;
- scrolling;
- responsive breakpoints;
- Theme resolution;
- Motion;
- dirty-tree propagation;
- incremental layout;
- layout caching;
- renderer/platform integration.

Any such feature requires an approved extension to Wave 3.

---

# 16. Exact Test Files

W3-001 may create exactly:

```text
tests/layout/test_contracts.py
tests/layout/test_runtime.py
tests/layout/test_module.py
tests/integration/test_layout_runtime.py
```

No empty, placeholder, skipped, or xfail-based required tests.

---

# 17. Test Matrix

## `tests/layout/test_contracts.py`

Must verify:

- LayoutDirection contains exactly HORIZONTAL and VERTICAL;
- LayoutSize, LayoutRect, LayoutNode and LayoutBox are frozen dataclasses;
- children use tuples;
- LayoutContract is abstract;
- LayoutContract extends RuntimeContract;
- domain contract exposes `validate()` and `layout()`.

## `tests/layout/test_runtime.py`

Must verify:

- runtime identity and L2 layer;
- lifecycle methods are awaitable;
- no background work is created;
- invalid IDs, sizes and gaps are rejected;
- duplicate node IDs are rejected;
- cyclic input is rejected;
- vertical layout coordinates;
- horizontal layout coordinates;
- nested recursive coordinates;
- child order is preserved;
- parent gap affects only direct children;
- overflow is permitted;
- input is not mutated;
- repeated equal input produces equal output;
- health is read-only.

## `tests/layout/test_module.py`

Must verify:

- module ID `layout.core`;
- layer `L2_LAYOUT`;
- `depends_on == ()`;
- `provides == (ServiceId("layout.core"),)`;
- version `1.0.0`;
- manifest immutability;
- importing the manifest creates no Runtime instance.

## `tests/integration/test_layout_runtime.py`

Required flow:

```text
construct
→ initialize
→ start
→ create immutable LayoutNode tree
→ validate
→ layout
→ verify recursive LayoutBox geometry
→ stop
→ shutdown
```

Also verify:

- API works through LayoutContract;
- Event Bus is not required;
- SharedStateRuntime is not required;
- no filesystem/network resources are created;
- no L0/L1 ownership changes occur.

---

# 18. Quality Gates

W3-001 is GREEN only if:

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

all pass with:

```text
Ruff: 0 violations
Pyright: 0 errors, 0 warnings, 0 informations
Pytest: non-empty suite, 0 failures
```

Public API coverage target: **100%**.

---

# 19. Implementation Order

```text
1. src/layout/contracts.py
2. src/layout/solver.py
3. src/layout/runtime.py
4. src/layout/module.py
5. src/layout/__init__.py
6. tests/layout/test_contracts.py
7. tests/layout/test_runtime.py
8. tests/layout/test_module.py
9. tests/integration/test_layout_runtime.py
10. Ruff
11. Pyright
12. Pytest
```

W3-001 is one implementation task.

All W3-001-owned files may be generated in one batch.

A required change outside this scope is an Architecture Blocker and must stop implementation.

---

# 20. PR Boundary

The Wave 3 W3-001 PR may contain only:

```text
docs/architecture/AB-00F_Wave3_Layout_Runtime_Contract_v1.0.md
src/layout/*
tests/layout/*
tests/integration/test_layout_runtime.py
```

plus already-permitted tool metadata changes when genuinely required.

No unrelated Wave 1/Wave 2 refactor is permitted.

---

# 21. Future-Wave Gate

AB-00F grants no implementation authority for L3–L8.

The following remain blocked:

```text
Wave 4 — L3 Theme Runtime
Wave 5 — L4 Motion Runtime
Wave 6 — L5 Interaction Runtime
Wave 7 — L6 Accessibility Runtime
Wave 8 — L7 Platform Runtime
Wave 9 — L8 Render Runtime
```

Each requires its own approved contract/ADR.

Additional Wave 3 modules beyond W3-001 also require an approved extension.

Reserved or empty directories are not implementation authorization.

---

# 22. Definition of Done

- [x] L2 ownership fixed.
- [x] W3-001 scope fixed.
- [x] exact production file set fixed.
- [x] exact public API fixed.
- [x] immutable layout contracts fixed.
- [x] deterministic layout algorithm fixed.
- [x] validation ownership fixed.
- [x] dependency direction fixed.
- [x] state/event/concurrency policy fixed.
- [x] exact test files fixed.
- [x] test matrix fixed.
- [x] quality gates fixed.
- [x] PR boundary fixed.
- [x] L3–L8 remain blocked.
- [x] W3-001 no longer requires implementation-time architecture invention.

---

# 23. Approval

**Architecture Baseline:** Architecture Freeze v1.0  
**Master Documentation Revision:** v1.1  
**Wave:** 3  
**Layer:** L2 Layout Runtime  
**Module:** W3-001 Layout Core Runtime  
**Resolution State:** APPROVED  
**Implementation Authorization:** GRANTED FOR W3-001 ONLY  
**L3–L8 Authorization:** NOT GRANTED  
**Change Policy:** Any expansion requires a new approved ADR / architecture resolution.

---

**END OF DOCUMENT — AB-00F WAVE 3 LAYOUT RUNTIME CONTRACT & ADR v1.0**
