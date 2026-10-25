# AURORA — Prepared JSON Brief Copy Decision v1.0

- Document ID: ADR-063
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-26
- Module: UI-017 — Prepared JSON Brief Copy
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/047/051/056/062;
  PC-014/042/046/051/057

## Finding and decision

UI-016 can copy the static preparation template, but the user must still edit
it in an external tool to insert the business brief. UI-017 adds a separate,
localized textarea and an explicit **Copy prompt with brief** action inside
the existing prepared-site guide. The user deliberately enters only the brief
they are permitted to share. The action replaces the template's single brief
placeholder with the trimmed text and writes the resulting prompt to the
browser clipboard.

The brief is transient component state. It is not inserted into the static
**Copy preparation prompt** action, project name, OpenAI generation input,
pasted JSON or project state. It is never written to browser storage, project
files, logs or an API. The new action is disabled for blank, invalid-Unicode or
greater-than-8-KiB UTF-8 input. Clipboard success and failure use fixed
localized statuses; failure leaves both the brief and existing selectable
template available for manual recovery.

This is a second, visibly distinct user-data copy action. It supersedes
ADR-062/PC-057's no-user-input rule only for this new action; UI-016's static
copy remains exact and user-data-free. Copying does not navigate externally,
contact a provider, create or modify a project, import JSON, read the clipboard
or grant permission. External sharing remains a later user-controlled action.

No dependency, route, persisted schema, Runtime or lower-layer owner changes.

## Boundary and acceptance

PC-058 grants exact file scope. Test RU/EN labels, byte and Unicode gating,
exact single insertion of the trimmed brief, isolation from all other inputs,
unchanged static copy, clipboard denial and absence of project/provider side
effects. Run frozen frontend install, typecheck, Vitest, Vite build, browser
tests, Ruff, Pyright and discovered Pytest. Inspect the final diff and
latest-head hosted CI before a routine ADR-003 merge. Produce one UI-017
module report and stop.
