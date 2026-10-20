# AURORA — Portable Project Reopen Smoke Decision v1.0

- Document ID: ADR-043
- Status: APPROVED — delegated test decision under ADR-001
- Date: 2026-10-20
- Module: QA-008 — Portable Project Reopen Smoke
- Baseline: Architecture Freeze v1.0, ADR-002/003/036, PC-001/031

## Decision and boundary

The Windows portable workflow already extracts and starts the actual packaged
`AURORA.exe` with an isolated temporary profile, checks loopback health and the
bundled UI, and stops the process. QA-008 extends that same smoke to create and
save a synthetic project through the packaged local API, stop that test process,
restart the same executable against the same isolated profile, and verify the
saved project can be reopened without data loss.

This is a test-only extension to PKG-001's workflow. It changes no packaged
application, public API, Runtime, project format, credentials, dependency,
provider behavior or distribution artifact. The test must not access the user's
normal profile or any live provider, credential, deployment, or production data.
It does not certify a clean Windows PC, browser editing, image generation, or
the complete ADR-002 journey. PC-038 fixes exact scope and acceptance.
