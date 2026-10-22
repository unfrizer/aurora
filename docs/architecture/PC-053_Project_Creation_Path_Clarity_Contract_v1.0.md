# AURORA — Project Creation Path Clarity Contract v1.0

- Document ID: PC-053
- Status: APPROVED — compiled from ADR-058 under ADR-001
- Date: 2026-10-22
- Module: UI-012 — Project Creation Path Clarity
- Authority: ADR-001/002/003/047/051/056/058; PC-042/046/051

## Exact scope

UI-012 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/src/styles.css
frontend/tests/App.test.tsx
```

It may create only ADR-058 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

The Projects screen groups the existing OpenAI prompt, blank-project, and
prepared-JSON import controls into three explicitly named, accessible paths.
The two keyless paths state only that they do not require an OpenAI API key
inside AURORA; importing still requires a JSON document prepared elsewhere.
The OpenAI path discloses key and possible provider cost. The shared project
name and all existing button disabled states, callbacks, file/paste isolation,
strict import validation and failure handling remain unchanged.

No tab switch, automatic generation, paid request, clipboard read/write,
external navigation, local persistence, project migration, new provider,
schema change, image handling or new dependency is authorized.

## Acceptance

Use deterministic RU/EN frontend tests for path labels, notes, accessibility,
existing action gating and no side effects from display. Preserve the existing
generation, blank-project, import file/paste and guide regressions. Run frozen
frontend install, TypeScript, Vitest, Vite build, browser tests, Ruff, Pyright
and discovered Pytest; inspect exact diff and latest-head hosted CI before
routine ADR-003 merge. Produce one UI-012 module report and stop.
