# AURORA — Wave 7 Accessibility Runtime Contract & ADR v1.0

**Document ID:** AB-00J  
**Status:** APPROVED — CANONICAL WAVE 7 AUTHORIZATION  
**Scope:** Wave 7 — L6 Accessibility Runtime  
**Implementation Module:** W7-001 Accessibility Core Runtime  
**Authority:** Architecture Freeze v1.0, Master Pack v1.1, AB-00B through
AB-00I, and ADR-001.

## Purpose and Boundary

W7-001 adds the only L6 runtime, `AccessibilityRuntime`. It deterministically
audits an immutable semantic tree. The only semantic rule introduced here is
that an explicitly interactive node requires a non-empty accessible label.
This produces a portable, platform-neutral accessibility boundary for later UI
layers.

The runtime does not render, query operating-system accessibility APIs, map
input, change layout/theme/motion/interaction state, publish events, persist
reports, use a screen reader, or access files, network, threads, or tasks.
The Master Pack reserves L6 without an implementation API; ADR-001 authorizes
this immutable deterministic default only.

## Exact Files and Public API

W7-001 owns exactly:

```text
src/accessibility/__init__.py
src/accessibility/contracts.py
src/accessibility/runtime.py
src/accessibility/module.py
tests/accessibility/__init__.py
tests/accessibility/test_contracts.py
tests/accessibility/test_runtime.py
tests/accessibility/test_module.py
tests/integration/test_accessibility_runtime.py
```

The package exports exactly:

```text
AccessibilityNode
AccessibilityIssue
AccessibilityReport
AccessibilityContract
AccessibilityRuntime
ACCESSIBILITY_MANIFEST
```

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class AccessibilityNode:
    node_id: str
    role: str
    label: str | None = None
    is_interactive: bool = False
    children: tuple["AccessibilityNode", ...] = ()

@dataclass(slots=True, frozen=True, kw_only=True)
class AccessibilityIssue:
    node_id: str
    message: str

@dataclass(slots=True, frozen=True, kw_only=True)
class AccessibilityReport:
    issues: tuple[AccessibilityIssue, ...]
    is_accessible: bool
```

Node IDs and roles are non-empty after trimming, IDs are unique per tree,
children are immutable tuples, and a tree is acyclic. `role` remains opaque:
W7-001 creates no platform or ARIA role vocabulary. A non-interactive node may
have no label. The audit preserves pre-order traversal and emits one issue with
message `"Interactive node requires an accessible label"` for each interactive
node whose label is missing or whitespace-only.

`AccessibilityContract` extends `RuntimeContract` and adds only:

```python
def validate(self, root: AccessibilityNode) -> None: ...
def audit(self, root: AccessibilityNode) -> AccessibilityReport: ...
```

## Identity, Manifest, and Dependencies

`AccessibilityRuntime` has `runtime_name == "accessibility"` and
`runtime_layer is RuntimeLayer.L6_ACCESSIBILITY`. Its asynchronous lifecycle
methods allocate no resource. `health()` is read-only and returns
`HealthStatus.OK`.

```python
ACCESSIBILITY_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("accessibility.core"),
    runtime_layer=RuntimeLayer.L6_ACCESSIBILITY,
    depends_on=(),
    provides=(ServiceId("accessibility.core"),),
    version="1.0.0",
)
```

Only `src.core.exceptions`, `src.core.types`, and L0 contract imports are
allowed. No concrete lower runtime or L7–L8 import is permitted. The manifest
is immutable and has no registration or construction side effect.

## Quality Gate

Tests must cover immutable models, abstract inheritance, tree validation,
recursive deterministic auditing, report semantics, lifecycle, and manifest
contents. Ruff, Pyright, and a non-empty Pytest suite must pass. Expanded
accessibility rules, role standards, contrast analysis, focus order, screen
reader adapters, and platform integration require another approved contract.
