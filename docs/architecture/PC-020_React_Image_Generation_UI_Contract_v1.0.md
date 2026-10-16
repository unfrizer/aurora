# AURORA — React Image Generation UI Contract v1.0

- Document ID: PC-020
- Status: APPROVED — compiled from explicitly approved ADR-026 IU-01–IU-05
- Module: UI-003 — Reviewed Image Generation in the Workspace
- Date: 2026-10-16

## Authority and exact scope

[ADR-026](ADR-026_React_Image_Generation_UI_Proposal_v1.0.md) IU-01–IU-05
are incorporated in full. The Architecture Authority explicitly approved
them on 2026-10-16. AGENTS.md, ADR-001/002/003/024/025, PC-014/017/018/019,
and all other unaffected approved contracts remain in force. UI-003 is a
browser client module, not an L0–L8 Runtime or a second P1/P3/P6/P7 owner.

Only the implementation files enumerated in ADR-026 IU-01 may be modified
or created, plus ADR-026's approval record and this contract. The client
uses only the already-approved relative same-origin P6 route via `api.ts`.
No Python source/test, other frontend component, dependency, lockfile,
workflow, launcher, user data, or lower-owner file may change.

## Required behavior

Implement IU-02's explicit logo or section target, user-authored prompt,
separate session image model, saved-editor prerequisite, clean-save flush,
and visible per-attempt paid-call confirmation. Send exactly one PC-019
request per confirmed attempt. Do not add an image call to the one-prompt
text-draft route, retry automatically, or expose a key in the browser form.

Interpret the five-field P6 result strictly as IU-03. A completed PNG is a
saved but unattached asset until the user separately accepts it. Attach only
through the existing editor PUT with the original source timestamp, and
mark success only after a parsed matching save. Discard or replacement does
not automatically delete any project asset. Require user-authored nonblank
alt text for a section attachment.

Follow IU-04's pending/review navigation lock, unload warning, 409 candidate
retention, and explicit reload/reselection on a fresh timestamp. Never
silently rebase, overwrite, infer cancellation, display raw provider detail,
persist the candidate or prompt in browser storage, or claim that a failed
terminal job yielded an image.

## Acceptance and deferrals

Cover the full IU-05 deterministic fake-fetch/jsdom matrix without a real
credential, paid call, user project, browser automation, or skipped/xfail
acceptance test. Preserve UI-001/UI-002 regressions. Run frozen pnpm install,
strict TypeScript, Vitest, Vite build and PC-013-compatible bundle check;
repository Ruff, Pyright and discovered Pytest; exact diff/import review;
and required latest-head hosted CI before routine merge. Produce one UI-003
module report and stop for Tech Lead review.

This contract does not authorize automatic image generation from one prompt,
image edits, multiple images, persistent settings, image-asset garbage
collection, folder export, Windows packaging, live provider acceptance, or
a second AI provider. It does not by itself fulfill ADR-002's complete
usable-Windows acceptance path.
