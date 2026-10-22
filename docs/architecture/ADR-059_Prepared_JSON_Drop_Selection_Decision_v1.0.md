# AURORA — Prepared JSON Drop Selection Decision v1.0

- Document ID: ADR-059
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-23
- Module: UI-013 — Prepared JSON Drop Selection
- Baseline: Architecture Freeze v1.0; ADR-001/003/047/051/058;
  PC-042/046/053

## Decision

The existing prepared-site file import gains a drag-and-drop file-selection
surface. Dropping exactly one local file selects it for the existing **Import
prepared site** action. It does not read the file, validate its contents,
create a project, call a provider, upload assets or trigger import. The user
must still enter a project name and explicitly press the file-import button.

The file picker remains available. Both picker and drop use the same selected
`File` state and existing UI-007 import validator. Filename and MIME are not
trusted as proof of valid P7 JSON; strict UTF-8, byte limit, JSON/P7 and null
asset checks remain in the existing import flow after the explicit action.
A drop with zero or multiple files is rejected without replacing the previous
selection. The selected filename is shown as browser-local text and is never
stored or sent except as part of the already approved explicit import input.

The separate pasted-JSON field and button remain independent. Dragging over
the surface only changes its visual state. No new endpoint, dependency,
Runtime, persisted state, schema, automatic repair, Markdown cleanup or
external integration is introduced.

## Boundary and acceptance

PC-054 grants exact browser-client file scope. Add RU/EN guidance and tests
for one-file staging, no side effects before action, rejected multi-file drop
with prior-selection preservation, picker equivalence and paste isolation.
Run the frontend and repository quality gates and latest-head hosted CI before
routine ADR-003 merge. This is not live ChatGPT integration or clean-target
Windows acceptance.
