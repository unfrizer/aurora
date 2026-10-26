# AURORA — Local Project Search Clear Contract v1.0

- Document ID: PC-062
- Status: APPROVED — compiled from ADR-067 under ADR-001
- Date: 2026-10-26
- Module: UI-021 — Local Project Search Clear
- Authority: ADR-001/003/020/066/067; PC-014/061

## Exact scope

UI-021 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

It may create only ADR-067 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

Within the existing nonempty project-list search region, render one localized
clear-search button exactly when `projectSearch.length > 0`. Activating it must
set `projectSearch` to the empty string. Do not trim, transform or persist the
query as part of this action.

The existing UI-020 derivation must then render the original `projects` array
without mutation, cloning or sorting. The button is absent for an empty query
and absent with the rest of the search control when `projects.length === 0`.
It remains enabled during unrelated project operations.

The action must not call an API/provider/asset function, navigate, persist
state, modify a project, or trigger import, generation, build, export or
deployment. Do not change search matching, maximum length, empty messages,
project actions, callback identities or introduce a dependency/public API.

## Acceptance

UI tests cover EN/RU labels, conditional visibility, clearing a matching and a
whitespace query, original-order restoration, empty repository, busy-state
availability and absence of side effects. Preserve every existing test. Run
frozen install, TypeScript, Vitest, Vite build, browser regressions, Ruff,
Pyright and all discovered Pytest. Inspect exact scope and latest-head CI before
ADR-003 merge. Produce one UI-021 module report and stop.
