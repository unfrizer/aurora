# AURORA — Direct Prepared JSON Clear Decision v1.0

- Document ID: ADR-064
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-26
- Module: UI-018 — Direct Prepared JSON Clear
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/047/051/061;
  PC-014/042/046/056

## Finding and decision

The prepared-site paste path keeps its text available after validation failure,
but the user currently must select and delete a potentially large JSON document
manually. UI-018 adds one explicit, localized **Clear pasted JSON** action next
to the existing paste import action. The control appears only while the paste
field contains at least one character and clears only that transient field.

Clearing must preserve the shared project name, one-prompt input, staged JSON
file, external preparation brief, guide-copy status and every persisted project.
It performs no import validation, project mutation, provider call, upload,
generation, clipboard operation, browser-storage write, build, export or deploy.
The action is disabled while the Projects screen is busy so an in-flight import
or creation cannot have its visible source cleared.

This decision does not relax the one-MiB UTF-8, strict JSON/P7, null-image or
new-project-only import rules. It does not strip Markdown fences, repair JSON,
merge into an existing project or change any Runtime, route, dependency or
lower-layer owner.

## Boundary and acceptance

PC-059 grants exact file scope. Test empty/nonempty visibility, clearing
ordinary and whitespace-only values, preservation of every adjacent input,
busy-state gating, RU/EN labels and absence of project/provider side effects.
Preserve all existing import and generation regressions. Run frozen frontend
install, typecheck, Vitest, Vite build, browser tests, Ruff, Pyright and all
discovered Pytest. Inspect exact scope and latest-head hosted CI before routine
ADR-003 merge. Produce one UI-018 module report and stop.
