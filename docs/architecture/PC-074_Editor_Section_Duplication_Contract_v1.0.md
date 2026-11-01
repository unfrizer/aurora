# AURORA — Editor Section Duplication Contract v1.0

- Document ID: PC-074
- Status: APPROVED — compiled from ADR-079 under ADR-001
- Date: 2026-11-01
- Module: UI-031 — Editor Section Duplication
- Authority: ADR-001/003/013/020/079; PC-007/014/073

## Exact ownership

UI-031 may create only:

```text
docs/architecture/ADR-079_Editor_Section_Duplication_Decision_v1.0.md
docs/architecture/PC-074_Editor_Section_Duplication_Contract_v1.0.md
```

It may modify only:

```text
frontend/src/components/Workspace.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
frontend/e2e/manual-site-starter.spec.ts
README.md
```

All other production, test, architecture, generated-site, dependency,
lockfile, workflow, launcher, secret and user-data files remain outside this
module.

## Required behavior

Implement ADR-079 as one visible section action. Use the current page and
editor snapshot, `crypto.randomUUID()`, immutable array insertion and the
existing commit path. The copy receives all existing section fields except
the original ID. Select the copy. At 100 or more sections, do not offer an
active duplicate action. Shared image references stay under the existing
P1/P7/P6 rules, including reference-aware deletion. Do not modify unrelated
fields or bypass save errors/conflicts.

Add deterministic RU/EN unit regressions and one browser journey covering
save/reopen and deletion of a temporary duplicate. Preserve prior tests.
Run frozen pnpm install, TypeScript, Vitest, Vite build, browser tests, Ruff,
Pyright and discovered Pytest. Inspect exact diff and latest-head CI before
routine ADR-003 merge. Produce one UI-031 module report.
