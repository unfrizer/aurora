# AURORA — Portable Offline Import and Photo Journey Decision v1.0

- Document ID: ADR-050
- Status: APPROVED — delegated test-only decision under ADR-001
- Date: 2026-10-21
- Module: QA-013 — Portable Offline Import and Photo Journey
- Baseline: Architecture Freeze v1.0; ADR-001/002/003/044/045/047/048/049;
  PC-039/040/042/043/044

## Decision

QA-012 verifies the no-key JSON-import and manual-photo path against the
source-composed app in Chrome. The packaged Windows executable is separately
tested for blank-site editing and restart persistence, but that exact offline
customer path is not yet covered in the packaged UI. QA-013 adds a second
Chrome spec against the already-running isolated portable executable in the
existing Windows portable workflow, after its original browser journey.

The new test uses only synthetic in-memory JSON and PNG data. It imports a
new text-only project without a credential, stages and manually attaches
one logo and one section image, checks byte-preserving raster responses,
saved editor references, preview and browser-reload reopening. The existing
smoke then restarts the same executable with its isolated profile and checks
that this imported project and image references still exist. No provider or
deployment request is permitted.

## Boundary

QA-013 is test-only. It may add its ADR, contract and portable Playwright
spec, and narrowly extend the existing Windows portable smoke to run that
spec and assert its saved project after process restart. QA-009's original
browser journey and QA-010's original persistence assertions remain intact.
No production source, API, Runtime, persistence format, package dependency,
build step, ZIP artifact, release, credential or user data changes.

The portable spec is skipped when `AURORA_PORTABLE_ORIGIN` is absent, so the
source browser CI retains its existing behavior. The packaged executable
keeps the workflow's isolated profile; only Chrome uses the disposable
runner profile exception already approved in ADR-044. No real AI key, paid
call, external HTTP request, publication or project deletion is performed.

This test does not certify a clean Windows target, live providers, image
quality, automatic photo placement or the full ADR-002 usable-version
acceptance. PC-045 fixes the exact file scope and assertions.
