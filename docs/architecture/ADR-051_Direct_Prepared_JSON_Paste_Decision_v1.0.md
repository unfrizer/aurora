# AURORA — Direct Prepared JSON Paste Decision v1.0

- Document ID: ADR-051
- Status: APPROVED — Architecture Authority explicitly approved the UI-009 scope on 2026-10-21
- Date: 2026-10-21
- Module: UI-009 — Direct Prepared JSON Paste
- Baseline: Architecture Freeze v1.0, ADR-001/003/047, PC-042

## Decision

The Projects screen may accept a ChatGPT-prepared text-only P7 v1 JSON object
through a direct paste field as an additional input method. The user supplies
a new project name and explicitly chooses **Import pasted site**. This is a
local import, not a ChatGPT connection or an AI request.

The pasted text is encoded as UTF-8 and passed through the existing UI-007
import validation and create/save flow. The 1 MiB limit applies to encoded
bytes. All P7 shape, ID, asset-reference, save-precondition, saved-state, and
failure rules of ADR-047 and PC-042 remain normative. No automatic repair of
JSON, Markdown fence removal, image import, or existing-project replacement is
authorized. The file chooser and its separate action remain available; if
both inputs contain data, each button uses only its own input.

Pasted text remains transient in the browser component and is not written to
browser storage. A validation failure leaves it editable. A successful import
opens the newly saved project, discarding the transient text with the Projects
screen. No provider, upload, build, export, or deployment call is added.

## Ownership and acceptance

One UI-009 browser-client module may modify only
`frontend/src/components/Projects.tsx`, `frontend/src/i18n.ts`,
`frontend/tests/App.test.tsx`, and `README.md`, and may create this decision
and `PC-046_Direct_Prepared_JSON_Paste_Contract_v1.0.md`. Existing P7 parsing,
UI-007 import flow, Python production/tests, dependencies, and CI are unchanged.

Frontend tests must cover a valid paste, a rejected paste before mutation,
the encoded size limit, independent file/paste actions, and RU/EN controls.
Run frozen frontend install, typecheck, tests, build, browser regressions,
repository Ruff, Pyright, and Pytest. Review exact scope and latest-head CI
before merge under ADR-003. A green test is not proof of a live ChatGPT link.
