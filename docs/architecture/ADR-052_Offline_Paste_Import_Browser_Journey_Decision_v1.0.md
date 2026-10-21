# AURORA — Offline Paste Import Browser Journey Decision v1.0

- Document ID: ADR-052
- Status: APPROVED — delegated test-only decision under ADR-001
- Date: 2026-10-21
- Module: QA-014 — Offline Paste Import Browser Journey
- Baseline: Architecture Freeze v1.0; ADR-001/003/037/047/049/051;
  PC-032/042/044/046

## Decision

UI-009 has deterministic component tests but no real-browser check of direct
JSON paste against the composed local backend. QA-014 adds this missing seam
as one test-only module. It does not add or change user-facing behavior.

The existing browser-test server serves the built React UI and public loopback
API with a fresh isolated project root, fake process-local credentials, and
disabled external deployment. The browser first attempts malformed pasted
JSON and verifies that no project is created. It then leaves an invalid file
selected, pastes valid P7 v1 JSON, explicitly chooses the paste action and
verifies that the pasted document—not the file—is saved in one new project.
It checks preview and persistence after reload/reopen, and observes no
provider, asset-upload, deployment or external-network request.

No live ChatGPT account, OpenAI credential, paid call, customer asset or
production deployment is used. This test does not certify clean-Windows
installation, portable-EXE packaging, live-provider generation or image
quality.

## Boundary

QA-014 may create only this ADR, its approved PC-047 contract and
`frontend/e2e/offline-paste-import.spec.ts`. Existing browser configuration,
test server and CI must discover the spec unchanged. No production source,
other test, dependency, lockfile, workflow or lower-layer owner may change.
Use a unique ignored `build/browser-e2e-<UUID>` root and a fixed loopback port
that is refused when occupied; stop the server after the test.

Run frozen frontend install, TypeScript typecheck, Vitest, Vite build, browser
tests, repository Ruff, Pyright and all discovered Pytest. Review exact scope
and latest-head hosted CI before routine merge under ADR-003. Produce one
QA-014 module report and stop.
