# AURORA — In-App Prepared JSON Guide Decision v1.0

- Document ID: ADR-056
- Status: APPROVED — delegated UI guidance decision under ADR-001
- Date: 2026-10-22
- Module: UI-010 — In-App Prepared JSON Guide
- Baseline: Architecture Freeze v1.0; ADR-001/003/047/051; PC-042/046

## Decision

The approved no-API-key import path accepts a text-only P7 v1 document
prepared outside AURORA. README already contains a copyable preparation
prompt, but the Projects screen offers no in-app format guidance. UI-010
places an optional, collapsed preparation guide alongside the existing file
and paste import controls. Its read-only selectable prompt describes the
already approved P7 v1 shape and rules. The example language follows the
current interface language; the user may edit the copied prompt elsewhere.

The guide contains no project name, business brief, credentials, or user
content. Opening it and selecting its text have no side effects: no browser
storage, project mutation, clipboard write, upload, external navigation,
provider request, generation, export or deployment. The user manually copies
the prompt, adds only material they are permitted to share in their chosen
external tool, reviews its output and pastes raw JSON into the existing field.
The existing one-MiB, strict JSON/P7, null-image and create/save rules remain
unchanged. Customer photos still require separate manual attachment.

## Boundary

This is one browser-client UI module. It may add this ADR, PC-051, a pure
prompt-template file and its unit test; it may modify only the Projects
component, RU/EN labels and their existing App test. Do not change the P7
schema/parser, import flow, Python source/tests, API, Runtime, README,
dependency, lockfile, workflow or user data. The in-app prompt is guidance,
not a ChatGPT integration or a guarantee of valid external output.

Run frozen frontend install, typecheck, Vitest, Vite build and browser
regressions, plus repository Ruff, Pyright and discovered Pytest. Review
exact scope and latest-head hosted CI; publish routinely under ADR-003 only
when required checks pass. Produce one UI-010 module report and stop.
