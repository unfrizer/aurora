# AURORA — Prepared JSON Guide Copy Decision v1.0

- Document ID: ADR-062
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-25
- Module: UI-016 — Prepared JSON Guide Copy
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/047/051/056;
  PC-014/042/046/051

## Finding and decision

The in-app prepared-site guide exposes a long read-only prompt and currently
requires manual selection and copying. UI-016 adds one explicit, localized
**Copy preparation prompt** action inside the existing collapsed guide. The
action copies exactly `preparedSitePrompt(language)` to the browser clipboard
and reports a localized success status. If clipboard access is unavailable or
denied, it reports a fixed localized failure and leaves the existing read-only,
focus-selectable textarea available for manual copying.

The copied value is the existing static prompt for the current interface
language. It must not include the project name, business prompt, pasted JSON,
selected filename, credentials, project state or any other user input. Copying
does not open an external site, call a provider, create or modify a project,
import JSON, write browser storage, or automatically paste into another app.
The user remains responsible for choosing an external tool, adding only a
brief they are permitted to share, reviewing the response, and explicitly
importing raw JSON.

This decision adds no new dependency, route, schema, Runtime, permission
request or automatic fallback. Browser clipboard policy remains authoritative.

## Boundary and acceptance

PC-057 grants exact file scope. Test successful RU/EN copies, exact copied
content without user data, denied/unavailable clipboard behavior, manual
textarea fallback and absence of project/provider side effects. Preserve all
existing import and generation behavior. Run frozen frontend install,
typecheck, Vitest, Vite build, browser tests, Ruff, Pyright and discovered
Pytest. Inspect the final diff and latest-head hosted CI before a routine
ADR-003 merge. Produce one UI-016 module report and stop.
