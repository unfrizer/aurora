# AURORA — Prepared JSON Selection Clear Contract v1.0

- Document ID: PC-056
- Status: APPROVED — compiled from ADR-061 under ADR-001
- Date: 2026-10-25
- Module: UI-015 — Prepared JSON Selection Clear
- Authority: ADR-001/003/020/047/051/059/060/061;
  PC-014/042/046/054/055

## Exact scope

UI-015 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

It may create only ADR-061 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

When a local file is selected through the existing picker or drop surface,
show one localized button to clear that selection. The button must be absent
without a selected file and disabled while a project action is busy. Clicking
it clears the staged `File`, any prior drop-selection error, and the native
picker value, allowing the same file to be chosen again. A valid replacement
drop also clears a stale native picker value. The project name, business
prompt, pasted text, other-path buttons and import flow are untouched.

Clearing never reads a file, calls `onImport`/`onCreate`/`onGenerate`, triggers
network or provider activity, or changes browser storage. With no selected
file, the existing file-import button is disabled. Pasted JSON, if present,
remains available through its own separate explicit action. Invalid
zero/multi-file drops still preserve the previous selection and error behavior.

Do not change P7 parsing, the 1-MiB import validator, P6 create/save routes,
credentials, paid-call consent, project persistence or any L0–L8 owner. No
new dependency or public API is authorized.

## Acceptance

Add deterministic RU/EN frontend tests for the visible clear control,
picker/drop clearing, same-file reselection, independence of pasted JSON, and
no project mutation until explicit import. Preserve all existing tests. Run
frozen frontend install, TypeScript, Vitest, Vite build, browser regressions,
Ruff, Pyright and all discovered Pytest. Inspect exact scope and latest-head
hosted CI before ADR-003 merge. Produce one UI-015 module report and stop.
