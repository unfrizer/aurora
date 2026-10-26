# AURORA — Manual Site Draft Guard Contract v1.0

- Document ID: PC-069
- Status: APPROVED — compiled from ADR-074 under ADR-001
- Date: 2026-10-26
- Module: UI-026 — Manual Site Draft Guard
- Authority: ADR-001/003/020/060/069/072/073/074; PC-014/055/064/067/068

## Exact ownership

UI-026 may create only:

```text
docs/architecture/ADR-074_Manual_Site_Draft_Guard_Decision_v1.0.md
docs/architecture/PC-069_Manual_Site_Draft_Guard_Contract_v1.0.md
```

It may modify only:

```text
frontend/src/App.tsx
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

Every other production, test, architecture, dependency, lockfile, workflow,
launcher and user-data file remains outside this module.

## Required behavior

Detect any typed manual-site field without treating the shared project name
as a draft. Guard blank creation, offline-brief start, OpenAI generation,
prepared JSON import, opening another project, navigation away from Projects
and browser unload. Before each effect, ask the localized warning described
in ADR-074. For offline brief and OpenAI generation, use one combined
confirmation retaining the original public-content or paid-action warning.
For blank creation with both transient drafts, show one combined warning.
Declining preserves inputs and has no effect; accepting invokes the original
action exactly once. Keep the brief-only confirmation unchanged.

Show an explicit clear action for the five manual fields. It performs no
request and does not affect any other state. On failed or uncertain action,
retain the form and its dirty indicator. Clear the indicator only after a
successful transition or explicit clear. No browser storage, new API route,
new model field or provider behavior is permitted.

Add deterministic RU/EN frontend regressions and preserve existing browser
journeys. Run frozen pnpm install, TypeScript, Vitest, Vite build, browser
tests, Ruff, Pyright and discovered Pytest. Inspect exact diff and latest-head
CI before routine merge under ADR-003. Produce one UI-026 module report.
