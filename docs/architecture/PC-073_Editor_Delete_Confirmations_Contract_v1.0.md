# AURORA — Editor Delete Confirmations Contract v1.0

- Document ID: PC-073
- Status: APPROVED — compiled from ADR-078 under ADR-001
- Date: 2026-11-01
- Module: UI-030 — Editor Delete Confirmations
- Authority: ADR-001/003/020/078; PC-009/014

## Exact ownership

UI-030 may create only:

```text
docs/architecture/ADR-078_Editor_Delete_Confirmation_Decision_v1.0.md
docs/architecture/PC-073_Editor_Delete_Confirmations_Contract_v1.0.md
```

It may modify only:

```text
frontend/src/components/Workspace.tsx
frontend/src/i18n.ts
frontend/src/styles.css
frontend/tests/App.test.tsx
frontend/e2e/manual-site-starter.spec.ts
README.md
```

All other production, test, architecture, generated-site, dependency,
lockfile, workflow, launcher, secret and user-data files remain outside
this module.

## Required behavior

Apply ADR-078 only to the existing page/section remove controls and the
page-row CSS overflow needed to reach them. Prompt before commit. Cancel
must preserve the exact editor and section selection, and issue no save.
Accept must use the existing commit path once, preserving all other
fields and the `index` homepage guard. Do not call asset DELETE or change
P1/P6/P7 ownership. Add deterministic RU/EN unit regressions and one
browser journey covering both controls and unchanged export. Preserve prior
tests.

Run frozen pnpm install, TypeScript, Vitest, Vite build, browser tests,
Ruff, Pyright and discovered Pytest. Inspect the exact diff and latest-head
CI before routine ADR-003 merge. Produce one UI-030 module report.
