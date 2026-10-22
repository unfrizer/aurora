# AURORA — Local Photo Drop Staging Contract v1.0

- Document ID: PC-052
- Status: APPROVED — compiled from ADR-057 under ADR-001
- Date: 2026-10-22
- Module: UI-011 — Local Photo Drop Staging
- Authority: ADR-001/003/048/057; PC-043

## Exact scope

UI-011 may modify only:

```text
frontend/src/components/PhotoTray.tsx
frontend/src/i18n.ts
frontend/src/styles.css
frontend/tests/photo_tray.test.tsx
```

It may create only ADR-057 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

The drop surface accepts only files passed by a browser drop event and sends
them through the same validation/staging path as the existing picker. The
existing tray capacity and per-file MIME/size rules are unchanged. Invalid
additions leave prior staged files untouched. Dragging without dropping has
no staging effect. Dropping does not upload, save, attach, build, deploy, or
call AI. While one attachment is pending, both drop and picker additions are
disabled. The picker remains keyboard-accessible.

The UI distinguishes drop-to-select from attach-to-upload in both RU and EN,
and provides a visible drag state. No automatic placement, file conversion,
signature-validation substitute, persistent tray, or new endpoint is allowed.

## Acceptance

Add deterministic frontend tests for valid drops, invalid/drop-count atomicity,
no call on drag-only and pending-drop lock. Preserve picker and attach tests.
Run frozen frontend install, typecheck, Vitest, Vite build, browser regressions,
repository Ruff, Pyright and discovered Pytest. Review the exact diff and
latest-head hosted CI before a routine ADR-003 merge. Produce one UI-011
module report and stop.
