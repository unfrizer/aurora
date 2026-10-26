# AURORA — Offline Brief Draft Guard Decision v1.0

- Document ID: ADR-072
- Status: APPROVED — delegated browser UI correction under ADR-001
- Date: 2026-10-26
- Module: UI-024 — Offline Brief Draft Guard
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/060/069;
  PC-014/055/064

## Finding and decision

The blank **Create project** action and UI-023's brief field share the manual
start area. A user can enter a brief and then activate the adjacent blank
action, creating a project that does not contain the brief. Because the
Projects screen closes on success, the transient text then disappears. UI-024
adds a localized confirmation before blank creation whenever the offline brief
field contains at least one character, including whitespace or invalid text.
It states that the empty project will not carry the brief. Declining makes no
request and preserves all fields. Accepting continues the existing blank
creation exactly once with the trimmed shared project name; it does not save
the brief or initialize an editor.

UI-024 also adds an explicit localized **Clear offline brief** action for any
nonempty value. It clears only that transient field and is disabled while a
Projects operation is busy. The project name, AI prompt, import selection,
pasted JSON, external-preparation brief, clipboard status and persisted
projects remain unchanged. Clearing makes no API, provider, clipboard,
browser-storage, build, export or deploy request.

The UI-023 **Create project with brief** action retains its own public-site
confirmation and exact versioned save. Enter in the shared name field remains
inert under ADR-060. No route, project/editor schema, dependency, Runtime or
lower-layer owner changes.

## Boundary and acceptance

PC-067 fixes exact file scope. Test EN/RU confirmation, cancellation and
field preservation, acceptance and unchanged blank-project semantics,
empty-brief bypass, clear action visibility and busy gating, and absence of
provider or persistence side effects when cancelled or cleared. Preserve all
existing regressions. Run frozen frontend install, TypeScript, Vitest, Vite
build, browser tests, Ruff, Pyright and all discovered Pytest. Inspect exact
scope and latest-head hosted CI before routine ADR-003 merge. Produce one
UI-024 module report and stop.
