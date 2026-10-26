# AURORA — Prepared JSON Brief Clear Decision v1.0

- Document ID: ADR-065
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-26
- Module: UI-019 — Prepared JSON Brief Clear
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/047/056/062/063/064;
  PC-014/042/051/057/058/059

## Finding and decision

UI-017 keeps the external-preparation brief available for correction after a
clipboard failure, but removing a potentially 8-KiB brief currently requires
manual text selection. UI-019 adds one explicit, localized **Clear brief**
action beside **Copy prompt with brief**. It appears for every nonempty brief,
including whitespace or invalid Unicode, and clears only that transient field.

Clearing also removes a copy status that referred to the former brief. A
clipboard operation started before the brief changed or was cleared must not
restore a stale success or failure status after it settles. The clear action is
disabled while the Projects screen is busy.

Project name, one-prompt input, staged JSON file and error, pasted JSON,
persisted projects and all other state remain unchanged. Clearing performs no
clipboard operation, API/provider/asset call, navigation, browser-storage
write, project mutation, import, build, export or deploy.

The static preparation prompt, brief validation, 8-KiB boundary and explicit
copy semantics remain unchanged. No dependency, route, schema, Runtime or
lower-layer owner changes.

## Boundary and acceptance

PC-060 grants exact file scope. Test EN/RU visibility, whitespace and invalid
input recovery, adjacent-input preservation, copy-status reset, stale async
clipboard completion suppression, busy-state gating and absence of project or
provider side effects. Preserve all existing regressions and run the complete
frontend, browser, Ruff, Pyright and Pytest gates. Inspect exact scope and
latest-head hosted CI before routine ADR-003 merge. Produce one UI-019 module
report and stop.
