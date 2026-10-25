# AURORA — Prepared JSON Guide Copy Contract v1.0

- Document ID: PC-057
- Status: APPROVED — compiled from ADR-062 under ADR-001
- Date: 2026-10-25
- Module: UI-016 — Prepared JSON Guide Copy
- Authority: ADR-001/003/020/047/051/056/062; PC-014/042/046/051

## Exact scope

UI-016 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

It may create only ADR-062 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

Inside the existing prepared JSON guide, show one button that explicitly
writes the current `preparedSitePrompt(language)` value with
`navigator.clipboard.writeText`. On success show a localized non-alert status.
On a missing clipboard API, rejected promise or synchronous failure, show a
fixed localized failure status and keep the read-only textarea selectable for
manual copying. A later successful copy clears the previous failure.

The copied string must equal the existing template exactly and contain no
project name, business prompt, pasted JSON, selected file content/name,
credential, project state or hidden interpolation. Do not request or persist
clipboard permission, read from the clipboard, navigate externally, contact a
provider, mutate a project, trigger import, or write browser storage.

Do not modify the prompt generator, P7 parser, import validator, P6 routes,
credentials, paid-call consent, project persistence or any L0–L8 owner. No
new dependency or public API is authorized.

## Acceptance

Add deterministic RU/EN tests for exact successful copies and localized
status. Cover denied and unavailable clipboard access, retained manual
selection fallback, no copied user input and no project/provider side effect.
Preserve all existing tests. Run frozen frontend install, TypeScript, Vitest,
Vite build, browser regressions, Ruff, Pyright and all discovered Pytest.
Inspect exact scope and latest-head hosted CI before ADR-003 merge. Produce
one UI-016 module report and stop.
