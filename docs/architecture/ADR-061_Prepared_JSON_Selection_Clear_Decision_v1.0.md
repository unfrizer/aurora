# AURORA — Prepared JSON Selection Clear Decision v1.0

- Document ID: ADR-061
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-25
- Module: UI-015 — Prepared JSON Selection Clear
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/047/051/059/060;
  PC-014/042/046/054/055

## Finding and decision

The Projects screen can stage one local JSON file for the explicit import
action, but has no way to remove a mistaken selection without choosing another
file or leaving the screen. UI-015 adds a visible, localized **Clear selected
file** control next to the selected filename. The control is available only
while a file is selected and no project action is busy. Activating it removes
the staged file, clears a prior file-drop error, and resets the native file
picker so that the same file can be selected again. It leaves the project name,
business prompt, pasted JSON and all other project-path state unchanged.

If a dropped file replaces a picker selection, the native picker is reset so
that it cannot continue to display the old filename. The staged filename
remains the explicit display of the current selection. Neither dropping nor
clearing a file reads its bytes, validates JSON, creates a project, calls a
provider, uploads an asset, or writes persistent browser state. Import still
requires its existing explicit button and the UI-007 validator; the 1-MiB,
strict UTF-8/P7 and null-asset rules remain unchanged. The separate pasted
JSON action remains independent.

This is a browser-client selection-state refinement only. It introduces no
route, schema, dependency, Runtime, clipboard access or new import behavior.

## Boundary and acceptance

PC-056 grants exact file scope. Test picker and drop selection clearing,
same-file reselection, disabled file import after clearing, no mutation from
clear, and preservation of pasted text. Preserve existing import/generation
regressions. Run frozen frontend install, typecheck, Vitest, Vite build, browser
tests, Ruff, Pyright and discovered Pytest. Inspect the final diff and
latest-head hosted CI before a routine ADR-003 merge. Produce one UI-015
module report and stop.
