# AURORA — Publication Checklist Contract v1.0

- Document ID: PC-071
- Status: APPROVED — compiled from ADR-076 under ADR-001
- Date: 2026-11-01
- Module: UI-028 — Publication Checklist
- Authority: ADR-001/003/020/073/075/076; PC-007/010/011/012/014

## Exact ownership

UI-028 may create only:

```text
docs/architecture/ADR-076_Publication_Checklist_Decision_v1.0.md
docs/architecture/PC-071_Publication_Checklist_Contract_v1.0.md
frontend/src/publication_checklist.ts
```

It may modify only:

```text
frontend/src/App.tsx
frontend/src/components/ExportDeploy.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
frontend/e2e/manual-site-starter.spec.ts
README.md
```

All other production, test, architecture, dependency, lockfile, workflow,
launcher and user-data files remain outside this module.

## Required behavior

Implement ADR-076's exact advisory checks as a pure browser helper over the
existing P7 editor type. Report one-based page/section positions without
echoing text; count all gaps and show no more than 20. The Export/Deploy UI
receives the existing editor snapshot, renders localized guidance and performs
no new request. No checklist result may be represented as a successful P4
build or used to enable/disable export or deploy. An empty list still includes
a manual-review notice. Existing action, confirmation, timestamp and recovery
flows remain unchanged.

Add deterministic RU/EN frontend regressions and one browser journey
assertion. Preserve prior tests. Run frozen pnpm install, typecheck, Vitest,
Vite build, browser tests, Ruff, Pyright and discovered Pytest. Inspect exact
diff and latest-head CI before routine ADR-003 merge. Produce one UI-028
module report.
