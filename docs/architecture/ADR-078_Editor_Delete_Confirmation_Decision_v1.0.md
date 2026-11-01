# AURORA — Editor Delete Confirmation Decision v1.0

- Document ID: ADR-078
- Status: APPROVED — delegated browser interaction decision under ADR-001
- Date: 2026-11-01
- Module: UI-030 — Editor Delete Confirmations
- Baseline: Architecture Freeze v1.0; ADR-001/003/020; PC-014/009

## Decision

The existing Workspace page and section remove buttons ask for a native,
localized confirmation before changing the P7 editor document. The prompt
states that the selected content will be removed and that the editor has no
undo. A cancelled prompt has no editor mutation, selection change or save
request. An accepted prompt uses the current editor snapshot and the existing immutable client
commit and serialized optimistic-save path exactly once.

The fixed `index` homepage remains undeletable and the editor never has zero
pages. A removed page takes its sections out of the editor document; a removed
section takes its text and image reference out of that document. Neither
action calls the raster DELETE route. Stored asset files remain under P1
ownership and are not modified by this UI task. Existing image remove,
project delete, save failure, 409 conflict and navigation behavior remain
unchanged.

The confirmation is triggered only by the explicit remove click. It is not
shown for add, reorder, image dereference, or project deletion. No new API,
schema field, provider call, dependency, Runtime or persistence owner is
introduced.

Page-row actions must remain inside the page rail when the title is long.
This module may correct that local CSS overflow defect so the confirmation
button is reachable by pointer and keyboard.

## Acceptance

PC-073 fixes ownership. Cover cancel/accept for page and section, localized
copy, homepage guard, one save on acceptance, no asset deletion, and page-row
reachability with a long title. Exercise the confirmation in the built browser
journey. Run frozen frontend install,
TypeScript, Vitest, build, browser tests, Ruff, Pyright and discovered Pytest.
Review exact diff and latest-head CI before routine ADR-003 merge.
