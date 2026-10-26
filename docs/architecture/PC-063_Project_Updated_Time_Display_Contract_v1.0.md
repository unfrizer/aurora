# AURORA — Project Updated Time Display Contract v1.0

- Document ID: PC-063
- Status: APPROVED — compiled from ADR-068 under ADR-001
- Date: 2026-10-26
- Module: UI-022 — Project Updated Time Display
- Authority: ADR-001/002/003/020/066/067/068; PC-014/061/062

## Exact scope

UI-022 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

It may create only ADR-068 and this contract under `docs/architecture/`.
Every other production, test, documentation, dependency, lockfile, workflow,
launcher and user-data file remains outside this module.

## Required behavior

For each project card, label the last update in the active UI language. If
`new Date(project.updated_at).getTime()` is finite, format that date with
`Intl.DateTimeFormat(language === 'ru' ? 'ru-RU' : 'en-US',
{ dateStyle: 'medium', timeStyle: 'short' })`, using the browser's time zone.
Render the result in `<time dateTime={project.updated_at}>`. If the date is not
finite, show the localized unknown-time label without a `<time>` element.

Do not change the timestamp value, list order, search matching, any object or
callback identity, project actions or API request. Do not introduce a new
dependency or public API. Rendering must not throw on invalid timestamp text.

## Acceptance

Tests cover RU/EN labels and local formatting, original semantic timestamp,
invalid timestamp fallback, stable ordering, and no project/provider/storage
side effects. Preserve all existing tests. Run frozen frontend install,
typecheck, Vitest, Vite build, browser regressions, Ruff, Pyright and all
discovered Pytest. Review exact diff and latest-head CI before ADR-003 merge.
Produce one UI-022 module report and stop.
