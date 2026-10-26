# AURORA — Workspace Brand Presets Contract v1.0

- Document ID: PC-070
- Status: APPROVED — compiled from ADR-075 under ADR-001
- Date: 2026-10-26
- Module: UI-027 — Workspace Brand Presets
- Authority: ADR-001/003/020/073/075; PC-007/014/068

## Exact ownership

UI-027 may create only:

```text
docs/architecture/ADR-075_Workspace_Brand_Presets_Decision_v1.0.md
docs/architecture/PC-070_Workspace_Brand_Presets_Contract_v1.0.md
frontend/src/brand_presets.ts
```

It may modify only:

```text
frontend/src/components/Workspace.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
frontend/e2e/manual-site-starter.spec.ts
README.md
```

No other production, test, architecture, dependency, lockfile, workflow,
launcher or user-data file belongs to this module.

## Required behavior

Implement only ADR-075's four fixed combinations over the existing P7 editor
brand fields. Keep their definitions immutable and reject unknown preset IDs.
Workspace presents an accessible RU/EN selection with no automatic mutation,
an explicit apply action, and a short explanation that current colors and
font are replaced. No apply is possible without a selection or when the
selected combination already matches the current brand. Applying uses the
current editor snapshot and the existing commit pipeline once; it must not
alter unrelated editor fields or bypass optimistic save/conflict handling.

Keep the manual site starter's default brand, all existing brand editing,
preview/export/deploy gates and P1/P4/P6/P7 ownership unchanged. Do not call
L3 Theme Runtime, AI providers, credentials or new routes. Add focused unit
and browser regressions. Run frozen pnpm install, typecheck, Vitest, build,
browser tests, Ruff, Pyright and discovered Pytest. Inspect exact diff and
latest-head CI before routine merge under ADR-003. Produce one UI-027 report.
