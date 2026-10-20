# AURORA — Portable Browser Journey Decision v1.0

- Document ID: ADR-044
- Status: APPROVED — delegated test decision under ADR-001
- Date: 2026-10-20
- Module: QA-009 — Portable Browser Journey
- Baseline: Architecture Freeze v1.0, ADR-002/003/036/037/043, PC-031/032/038

## Decision and boundary

QA-008 proves that the packaged `AURORA.exe` serves the UI and persists a
synthetic project across a process restart through its local API. QA-002 proves
the React browser journey against a source-composed test server. QA-009 closes
the remaining packaging/UI seam by running a small Chrome journey against the
actual extracted executable after QA-008's restart. The executable retains
its isolated temporary profile and existing synthetic project.

The browser journey chooses RU, completes onboarding, opens the project,
initializes a blank site, edits and saves text, previews the saved site,
downloads a static-site ZIP, reloads the page and reopens the edited project.
It never enters Settings, writes credentials, sends generation requests,
contacts a provider or deploys anything. The existing pinned Playwright test
dependency and installed Chrome are reused; no new dependency or packaged
browser is introduced.

Chrome on Windows rejects a redirected `USERPROFILE` even when Playwright
supplies a unique browser data directory. Only the browser test process uses
the hosted runner's original disposable `USERPROFILE`, with isolated
`LOCALAPPDATA` and temporary directory plus Playwright's fresh browser
context. The already-running AURORA process retains the isolated profile it
inherited at launch. The test never opens a user's AURORA project directory.

This is a test-only extension. It changes no production source, public API,
Runtime, project format, build artifact or distribution behavior. The journey
does not certify a clean Windows PC, live AI/image quality, Credential Manager,
Netlify or the complete ADR-002 acceptance path. PC-039 fixes exact scope.
