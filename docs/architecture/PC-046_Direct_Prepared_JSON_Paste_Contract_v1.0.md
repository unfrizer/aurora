# AURORA — Direct Prepared JSON Paste Contract v1.0

- Document ID: PC-046
- Status: APPROVED — compiled from explicitly approved ADR-051
- Date: 2026-10-21
- Module: UI-009 — Direct Prepared JSON Paste
- Authority: ADR-051, ADR-047, PC-042, ADR-001/003

## Boundary

ADR-051 is normative in full. UI-009 adds one input method to the existing
local text-only import. It introduces no Runtime, schema, API route, provider,
persisted client state, or dependency.

Authorized modifications are exactly:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
README.md
docs/architecture/ADR-051_Direct_Prepared_JSON_Paste_Decision_v1.0.md
docs/architecture/PC-046_Direct_Prepared_JSON_Paste_Contract_v1.0.md
```

All other files are read-only for this module. In particular, consume
`frontend/src/App.tsx`, `project_import.ts`, `types.ts`, and `api.ts` unchanged.

## Required behavior

The Projects screen provides a labeled multiline text field and a distinct
paste-import button. The button is unavailable without a non-blank project
name and non-blank pasted text or while an operation is busy. It submits only
the pasted text as a UTF-8 JSON file-like input to the existing import action.
The file-import button continues to submit only the selected file. Neither
input implicitly triggers the other.

The existing validator enforces at most 1 MiB of UTF-8 bytes, strict JSON and
P7 v1 structure, valid identifiers, and null image references before any
project mutation. The existing import flow creates one new project and makes
one versioned editor save, verifies the saved state, and reports uncertain
create/save outcomes honestly. Validation errors remain safe and localized.
No key, provider call, image upload, generation, build, export, or deployment
is involved. Customer photographs remain separate.

README guidance must show both file selection and direct JSON paste, require
raw JSON without Markdown fences, and explain review and text-only scope.

## Validation and handoff

Test valid and invalid paste paths, oversized UTF-8 input, independent file
and paste actions, disabled controls, and bilingual labels without live AI.
Run frozen frontend install, TypeScript typecheck, Vitest, Vite build, browser
regressions, repository Ruff, Pyright, and discovered Pytest. Inspect exact
file scope and latest-commit hosted CI. Produce one UI-009 module report.
