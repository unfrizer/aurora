# AURORA — Editor Section Duplication Decision v1.0

- Document ID: ADR-079
- Status: APPROVED — delegated browser interaction decision under ADR-001
- Date: 2026-11-01
- Module: UI-031 — Editor Section Duplication
- Baseline: Architecture Freeze v1.0; ADR-001/003/013/020/078; PC-007/014/073

## Decision

The Workspace offers an explicit localized **Duplicate section** action on
each existing section. One click creates a detached section object with a new
canonical browser UUID and the same heading, body, image path and image
description as the source. The copy is inserted immediately after the source
in that page. The editor selects the copy and submits exactly one ordinary
optimistic editor save through the existing commit path.

The action does not upload or copy asset bytes. If the section uses an image,
both sections refer to the same existing P1-managed asset path. Removing or
replacing one reference must not delete a file still referenced by the other.
The button is disabled when the page already has 100 sections, matching P4's
publication limit. It does not alter page fields, other sections, project
metadata, generated-site styling or the P7 schema.

This is a P7 client edit only. Existing save failure and 409 draft retention
remain in force. No provider request, confirmation, new API, dependency,
Runtime, persistence owner or generated-site behavior is introduced.

## Acceptance

PC-074 fixes ownership. Test ID uniqueness, immediate ordering, copied
content/image reference, one save, selected copy, 100-section guard and
reference-aware image removal. Exercise duplicate/save/remove/reopen in the
built browser journey. Run frozen frontend install, TypeScript, Vitest, build,
browser tests, Ruff, Pyright and discovered Pytest. Inspect exact diff and
latest-head CI before ADR-003 merge.
