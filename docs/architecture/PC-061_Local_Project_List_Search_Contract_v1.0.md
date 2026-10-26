# AURORA — Local Project List Search Contract v1.0

- Document ID: PC-061
- Status: APPROVED — compiled from ADR-066 under ADR-001
- Date: 2026-10-26
- Module: UI-020 — Local Project List Search
- Authority: ADR-001/003/020/066; PC-014

## Exact scope

UI-020 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

It may create only ADR-066 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

When `projects.length > 0`, render one localized search input at the beginning
of the existing project-list region. The input is controlled by transient
component state, uses `type="search"`, and has `maxLength={128}`. Do not render
the input for an empty repository list.

Derive a query key with `query.trim().toLowerCase()`. The empty key returns the
original projects array. Otherwise render only projects whose
`project.name.toLowerCase()` includes the key. Do not mutate or sort the input
array, clone metadata, search other fields, or alter open/delete callback IDs.

When the repository list is empty, show only the existing localized no-projects
message. When it is nonempty but filtering produces zero results, keep the
search input visible and show a distinct localized no-matches message. The
search operation must not call any API/provider/asset function, navigate,
persist state, modify a project, or trigger import, generation, build, export
or deployment. No new dependency or public API is authorized.

## Acceptance

UI tests cover EN/RU labels, substring and case matching, surrounding and
whitespace-only queries, stable result order, zero matches, empty repository,
the 128-character DOM boundary and absence of project/provider/storage side
effects. Preserve every existing test. Run frozen install, TypeScript, Vitest,
Vite build, browser regressions, Ruff, Pyright and all discovered Pytest.
Inspect exact scope and latest-head CI before ADR-003 merge. Produce one UI-020
module report and stop.
