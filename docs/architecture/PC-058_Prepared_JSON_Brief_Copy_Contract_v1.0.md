# AURORA — Prepared JSON Brief Copy Contract v1.0

- Document ID: PC-058
- Status: APPROVED — compiled from ADR-063 under ADR-001
- Date: 2026-10-26
- Module: UI-017 — Prepared JSON Brief Copy
- Authority: ADR-001/003/020/047/051/056/062/063;
  PC-014/042/046/051/057

## Exact scope

UI-017 may modify only:

```text
frontend/src/prepared_site_prompt.ts
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/prepared_site_prompt.test.ts
frontend/tests/App.test.tsx
```

It may create only ADR-063 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

Add a transient, localized business-brief textarea inside the existing import
guide and a distinct **Copy prompt with brief** button. The button is enabled
only for a nonblank string that can be URI-encoded and whose original UTF-8
encoding is no greater than 8 KiB. On activation, trim only leading/trailing
whitespace, replace the existing preparation template's one brief placeholder
with that value exactly once, and write the complete current-language prompt
through `navigator.clipboard.writeText`.

Show a localized success status for the brief copy. Missing or denied
clipboard access shows the existing safe manual-copy failure status and keeps
the textarea content unchanged. The existing static copy action must continue
to copy exactly `preparedSitePrompt(language)` with no user data. The brief
must not contain or derive from project name, OpenAI prompt state, pasted JSON,
selected files, credentials or project state unless the user manually types
that text into this dedicated field.

No clipboard read, permission persistence, browser storage, API/provider call,
project mutation, import, navigation or automatic external sharing. Do not
change P7, import validation, P6 routes, credentials, paid-call consent,
project persistence or any L0–L8 owner. No new dependency or public backend
API is authorized.

## Acceptance

Pure prompt tests cover placeholder replacement, trimming and preservation of
embedded line breaks. UI tests cover RU/EN, empty/8-KiB/oversized/malformed
Unicode gating, exact copied content, input isolation, unchanged static copy,
clipboard failure and no project/provider side effects. Preserve all existing
tests. Run frozen frontend install, TypeScript, Vitest, Vite build, browser
regressions, Ruff, Pyright and all discovered Pytest. Inspect exact scope and
latest-head hosted CI before ADR-003 merge. Produce one UI-017 module report
and stop.
