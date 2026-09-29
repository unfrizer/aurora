# AURORA — Wave 4 Theme Runtime Contract & ADR v1.0

**Document ID:** AB-00G  
**Status:** APPROVED — CANONICAL WAVE 4 AUTHORIZATION  
**Scope:** Wave 4 — L3 Theme Runtime  
**Implementation Module:** W4-001 Theme Core Runtime  
**Authority:** Architecture Freeze v1.0, Master Pack v1.1, AB-00B through
AB-00F, and ADR-001.

## 1. Purpose

W4-001 adds the single L3 runtime, `ThemeRuntime`. It provides deterministic,
in-memory ownership of the active visual-theme definition used by future
higher-layer consumers. It does not render a user interface, calculate layout,
generate a brand, store projects, use providers, or communicate over a network.

The Master Pack reserves L3 but defines no implementation-level Theme API.
ADR-001 therefore permits the narrow defaults recorded here: immutable public
contracts, deterministic in-memory state, no new dependencies, and no change
to lower-layer ownership.

## 2. Ownership and Dependencies

`ThemeRuntime` owns only its active `ThemeDefinition` and monotonically
increasing revision during one runtime lifetime. It is `RuntimeLayer.L3_THEME`.

It may import `src.core.types` and `src.core.exceptions`, and the L0
`RuntimeContract` and `RuntimeModuleManifest` contracts. It must not import or
modify `src.state`, `src.layout`, any L0 concrete runtime, or L4–L8 modules.
L0–L2 must not import `src.theme`.

No Event Bus handlers, DI registration, threads, tasks, subprocesses, file
resources, network resources, caches, persistence, or module-level mutable
state are authorized.

## 3. Exact Production Files

```text
src/theme/__init__.py
src/theme/contracts.py
src/theme/runtime.py
src/theme/module.py
```

No other production file in `src/theme/` belongs to W4-001.

## 4. Public API

The package exports exactly:

```text
ThemeDefinition
ThemeSnapshot
ThemeContract
ThemeRuntime
THEME_MANIFEST
```

### ThemeDefinition

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class ThemeDefinition:
    theme_id: str
    display_name: str
    tokens: tuple[tuple[str, str], ...] = ()
```

`theme_id` and `display_name` must be non-empty after trimming. `tokens` is an
immutable ordered sequence of unique, non-empty token-name/value pairs. Token
values remain opaque strings: W4-001 does not interpret CSS, typography,
platform colors, accessibility contrast, or rendering behavior.

### ThemeSnapshot

```python
@dataclass(slots=True, frozen=True, kw_only=True)
class ThemeSnapshot:
    revision: int
    theme: ThemeDefinition | None
```

`revision` starts at `0`, is never negative, and changes only on a successful
public mutation. The snapshot is immutable and contains no mutable state.

### ThemeContract and ThemeRuntime

`ThemeContract` extends the canonical L0 `RuntimeContract` and adds exactly:

```python
def get(self) -> ThemeDefinition | None: ...
def snapshot(self) -> ThemeSnapshot: ...
def set(self, theme: ThemeDefinition) -> ThemeSnapshot: ...
def clear(self) -> ThemeSnapshot: ...
```

`ThemeRuntime` implements the contract with:

```text
runtime_name == "theme"
runtime_layer is RuntimeLayer.L3_THEME
```

`set()` validates and installs a definition, incrementing the revision exactly
once even if it equals the active definition. `clear()` removes an active theme
and increments once; clearing an already empty runtime is a no-op. Read methods
never increment the revision. `shutdown()` releases the owned theme; a later
`initialize()` starts a fresh lifetime at revision `0`.

Lifecycle methods are asynchronous only because `RuntimeContract` requires
them. They create no resource or background work. `health()` is read-only and
returns the canonical `HealthStatus.OK`.

## 5. Module Manifest

```python
THEME_MANIFEST = RuntimeModuleManifest(
    module_id=ModuleId("theme.core"),
    runtime_layer=RuntimeLayer.L3_THEME,
    depends_on=(),
    provides=(ServiceId("theme.core"),),
    version="1.0.0",
)
```

The manifest is immutable, has no registration side effect, and does not
instantiate `ThemeRuntime`.

## 6. Exact Test Files

```text
tests/theme/__init__.py
tests/theme/test_contracts.py
tests/theme/test_runtime.py
tests/theme/test_module.py
tests/integration/test_theme_runtime.py
```

Tests must cover immutable contract shells, abstract contract inheritance,
validation, revision semantics, lifecycle, identity, manifest contents, and a
complete construct → initialize → start → set → read → stop → shutdown flow.
They must demonstrate that no Event Bus, Shared State, Layout Runtime, file, or
network resource is required.

## 7. Quality Gate and Definition of Done

W4-001 is complete only when `uv run ruff check .`, `uv run pyright`, and
`uv run pytest` all pass with a non-empty test suite. The change boundary is
this contract, the four production files, and the five test files above.

Future Theme features—token resolution, generated brand assets, persistence,
theme inheritance, contrast validation, platform adaptation, and render
integration—require a later approved contract.
