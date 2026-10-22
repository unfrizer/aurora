# AURORA — Portable Paste Import Journey Decision v1.0

- Document ID: ADR-053
- Status: APPROVED — delegated test-only decision under ADR-001
- Date: 2026-10-21
- Module: QA-015 — Portable Paste Import Journey
- Baseline: Architecture Freeze v1.0; ADR-001/003/044/045/050/051/052;
  PC-039/040/045/046/047

## Decision

QA-014 verifies direct JSON paste against the source-composed local app. The
packaged Windows executable has an import-and-photo journey for selected files,
but the UI-009 paste path has not been checked against the extracted EXE.
QA-015 adds one Playwright spec against the already-running isolated portable
app in the existing Windows workflow, after the existing browser journeys.

The test uses synthetic P7 v1 JSON without credentials or images. It proves
malformed paste creates nothing; when an invalid file is selected, choosing
the paste action still imports the valid pasted document into exactly one new
project. It checks saved P7 content, preview and browser reload. The existing
smoke then restarts the same EXE and reads the pasted project through its public
loopback API to verify identity and content. No provider, asset upload,
deployment or external HTTP request is permitted.

## Boundary

QA-015 is test-only. It may create this ADR, its PC-048 contract and one
portable Playwright spec, and narrowly extend the existing portable workflow
to invoke that spec and check its project after restart. Keep the ZIP build,
artifact upload, original API smoke, earlier browser journeys and their
persistence assertions intact. No production source, public API, dependency,
lockfile, launcher, project format, credential or user data changes.

The spec skips without `AURORA_PORTABLE_ORIGIN`; the source-browser gate is
unchanged. The EXE retains its isolated profile. Only Chrome uses the hosted
runner's disposable profile exception already approved in ADR-044. This is
not clean-target Windows, live ChatGPT/provider, image-quality or full MVP
acceptance evidence.

Run frozen frontend install, TypeScript, Vitest, Vite build, source browser
tests, repository Ruff, Pyright and discovered Pytest; run an isolated portable
build/smoke locally when safely available; require latest-head hosted Windows
portable CI before merge. Review exact scope and produce one QA-015 report.
