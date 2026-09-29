# AURORA — Wave 9 Render Runtime Contract v1.0

**Document ID:** AB-00L  
**Status:** APPROVED — CANONICAL WAVE 9 AUTHORIZATION  
**Module:** W9-001 Render Core Runtime  
**Authority:** Architecture Freeze v1.0, Master Pack v1.1, AB-00B–AB-00K, ADR-001.

W9-001 is the L8 read-only `RenderRuntime` in the Master Pack’s canonical
`src/render/` directory. It validates immutable `RenderNode` trees and returns
an immutable `RenderTree`; it does not open a window, create HTML, call a UI
framework, access platform APIs, write files, dispatch events, retain state, or
invoke lower concrete runtimes.

Public API: `RenderNode`, `RenderTree`, `RenderContract`, `RenderRuntime`, and
`RENDER_MANIFEST`. A node has non-empty unique `node_id`, non-empty opaque
`kind`, optional text, and tuple children. Trees are acyclic. Render preserves
the input root exactly after validation. The contract adds `validate(root)` and
`render(root)` to `RuntimeContract`; identity is `"render"` / `L8_RENDER`.

```text
src/render/__init__.py
src/render/contracts.py
src/render/runtime.py
src/render/module.py
tests/render/test_render_contracts.py
tests/render/test_render_behavior.py
tests/render/test_render_module.py
tests/integration/test_render_runtime.py
```

The immutable manifest is `render.core`, `L8_RENDER`, no dependencies, provides
`render.core`, version `1.0.0`. Only core types/exceptions and L0 contracts are
allowed imports. Ruff, Pyright, and non-empty Pytest are mandatory.
