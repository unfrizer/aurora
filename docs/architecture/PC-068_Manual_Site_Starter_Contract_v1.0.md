# AURORA — Manual Site Starter Contract v1.0

- Document ID: PC-068
- Status: APPROVED — compiled from ADR-073 under ADR-001
- Date: 2026-10-26
- Module: UI-025 — Manual Site Starter
- Authority: ADR-001/002/003/020/047/069/072/073; PC-006/007/014/064/067

## Exact ownership

UI-025 may create only:

```text
docs/architecture/ADR-073_Manual_Site_Starter_Decision_v1.0.md
docs/architecture/PC-068_Manual_Site_Starter_Contract_v1.0.md
frontend/src/manual_site.ts
frontend/e2e/manual-site-starter.spec.ts
```

It may modify only:

```text
frontend/src/App.tsx
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
README.md
```

No backend, other source/test, dependency, lockfile, workflow, launcher or user
data may change.

## Required behavior

Expose the distinct manual-site form within the no-key Projects path. Keep
the blank and offline-brief paths intact. Validate and construct the exact P7
v1 editor from `blankEditor` according to ADR-073. The new fields contain
user-supplied public copy, not a transformed business brief. A confirmed
activation uses only P6 create, versioned editor save and project list routes.
It must verify the returned project ID and complete editor state before opening.
Cancel makes no request. Duplicate activation is blocked. Failures preserve
the form and show localized uncertain-result recovery without deletion/retry.
No provider, credential, generated asset, build, export or deploy request is
allowed in this path.

Add deterministic frontend and browser acceptance cases for mapping, bounds,
confirmation, recovery and a real save/reopen/preview/export journey. Preserve
all regressions. Run frozen pnpm install, typecheck, Vitest, Vite build,
browser tests, Ruff, Pyright and discovered Pytest. Inspect exact diff and
latest-head CI before routine merge under ADR-003. Produce one UI-025 report.
