# AURORA — Application Visual Refresh Contract v1.0

- Document ID: PC-072
- Status: APPROVED — compiled from ADR-077 under ADR-001
- Date: 2026-11-01
- Module: UI-029 — Application Visual Refresh
- Authority: ADR-001/003/020/077; PC-014/071

## Exact ownership

UI-029 may create only:

```text
docs/architecture/ADR-077_Application_Visual_Refresh_Decision_v1.0.md
docs/architecture/PC-072_Application_Visual_Refresh_Contract_v1.0.md
```

It may modify only:

```text
frontend/src/styles.css
README.md
```

All component markup, TypeScript logic and tests, Python source, generated
site CSS, architecture owners, dependencies, lockfiles, workflows, launcher,
secrets and user data remain outside this module.

## Required behavior

Implement ADR-077 as CSS-only application presentation. The Projects screen
must use desktop width better while preserving every creation/import path.
The Workspace must maintain independent panel collapse, editor/preview,
inspector and toolbar reachability. Inputs, dialogs and alerts remain legible
with visible keyboard focus and no clipped content on narrow viewports.
Desktop and 390 px layouts receive manual visual QA; existing browser
journeys and repository checks remain the functional regression gate.

Run frozen pnpm install, TypeScript, Vitest, Vite build, browser tests, Ruff,
Pyright and discovered Pytest. Inspect the exact diff and latest-head CI
before routine ADR-003 merge. Produce one UI-029 module report.
