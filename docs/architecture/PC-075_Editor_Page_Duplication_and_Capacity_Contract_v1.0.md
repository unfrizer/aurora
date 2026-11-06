# AURORA — Editor Page Duplication and Capacity Contract v1.0

- Document ID: PC-075
- Status: APPROVED — compiled from ADR-080 under ADR-001
- Date: 2026-11-06
- Module: UI-032 — Editor Page Duplication and Capacity Guards
- Authority: ADR-001/003/013/020/080; PC-004/007/014/074

## Exact ownership

UI-032 may create only:

```text
docs/architecture/ADR-080_Editor_Page_Duplication_and_Capacity_Decision_v1.0.md
docs/architecture/PC-075_Editor_Page_Duplication_and_Capacity_Contract_v1.0.md
```

It may modify only:

```text
frontend/src/components/Workspace.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
frontend/e2e/manual-site-starter.spec.ts
README.md
```

All other production, test, architecture, dependency, lockfile, workflow,
launcher, secret, generated-site and user-data files are outside this module.

## Required behavior

Implement ADR-080 in the existing P7 client editor using browser UUIDs,
immutable array copies, `nextPageSlug` and the ordinary commit path. A copied
page receives a new ID and slug, and each copied section receives a new ID.
Preserve all other copied content, order and image references. Insert the copy
immediately after the source and select it. Keep the `index` page first and
unique. At or above 100 pages, offer no active page-add or page-duplicate
action. At or above 100 sections on the selected page, offer no active
section-add action. Guard both UI controls and form handlers. Do not mutate
oversized pre-existing drafts or replace P4 validation.

Add focused RU/EN unit regressions and one built-browser journey covering
duplicate/save/remove/reopen. Preserve previous tests. Run frozen pnpm
install, TypeScript, Vitest, Vite build, browser tests, Ruff, Pyright and
discovered Pytest. Inspect the exact diff and latest-head CI before routine
ADR-003 merge. Produce one UI-032 module report and stop.
