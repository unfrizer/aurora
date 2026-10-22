# AURORA — Prepared JSON Drop Selection Contract v1.0

- Document ID: PC-054
- Status: APPROVED — compiled from ADR-059 under ADR-001
- Date: 2026-10-23
- Module: UI-013 — Prepared JSON Drop Selection
- Authority: ADR-001/003/047/051/058/059; PC-042/046/053

## Exact scope

UI-013 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/src/styles.css
frontend/tests/App.test.tsx
```

It may create only ADR-059 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

A named, visible drop surface in the existing import path accepts exactly
one browser-supplied local `File` as a selection, not an import action. The
existing file picker and file-import button remain available; both selection
methods feed the same `File` state. Empty or multi-file drops show a fixed,
localized message and preserve the previous file. The selected filename is
displayed as escaped text, with no browser storage or logging. A drag without
a drop has no selection or request effect.

Only the existing explicit file-import action invokes UI-007 validation and,
if valid, the P6/P7 create/save sequence. The 1-MiB UTF-8 JSON/P7 rules and
all failure handling remain unchanged. A drop does not affect pasted text or
the separate paste-import action. No filename/MIME trust, implicit import,
provider call, asset upload, project overwrite, JSON repair or new contract
is authorized.

## Acceptance

Test RU/EN guidance, valid single-file selection, multi-file atomic rejection,
no request before action, explicit import through the existing validator and
paste-input isolation. Preserve all earlier frontend/browser regressions.
Run frozen frontend install, TypeScript, Vitest, Vite build, browser tests,
Ruff, Pyright and discovered Pytest; review exact diff and latest-head hosted
CI before ADR-003 merge. Produce one UI-013 module report and stop.
