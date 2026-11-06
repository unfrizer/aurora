# AURORA — Editor Page Duplication and Capacity Decision v1.0

- Document ID: ADR-080
- Status: APPROVED — delegated browser interaction decision under ADR-001
- Date: 2026-11-06
- Module: UI-032 — Editor Page Duplication and Capacity Guards
- Baseline: Architecture Freeze v1.0; ADR-001/003/013/020/079; PC-004/007/014/074

## Decision

The Workspace offers an explicit localized **Duplicate page** action for each
existing page, including the `index` homepage. One click copies the page title,
heading, meta description and ordered sections to a new page immediately after
the source. The new page and every copied section receive fresh canonical
browser UUIDs. The new page receives the next unused `page-N` slug from the
existing client helper, never a second `index` slug. The copy becomes the
selected page, and the ordinary editor commit path saves it once. Its sections
retain their image paths as references to the same P1 assets; no bytes are
copied or uploaded.

P4 limits publication to 100 pages and 100 sections per page. At a page count
of 100, the client disables page duplication and page addition. At a section
count of 100 on the selected page, it disables section addition. Submission
handlers enforce the same limits. These guards prevent these known invalid
draft expansions but do not make the editor a P4 validator; existing drafts
that already exceed limits are not rewritten. P4 remains the build authority.

The existing homepage protection, page and section ordering, image reference
rules, serialized saves, failure and 409 draft retention remain in force. No
new schema, route, dependency, provider call, Runtime or persistence owner is
introduced.

## Acceptance

PC-075 fixes ownership. Test copied page fields and sections, fresh IDs,
next-unused slug, insertion order, selection, one save, image reference reuse,
homepage uniqueness and both capacity guards. Exercise page duplicate, save,
remove and reopen in the built browser journey. Run frontend and repository
quality gates and required latest-head CI before routine ADR-003 merge.
