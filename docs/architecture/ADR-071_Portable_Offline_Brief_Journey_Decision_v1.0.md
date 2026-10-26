# AURORA — Portable Offline Brief Journey Decision v1.0

- Document ID: ADR-071
- Status: APPROVED — delegated test-only decision under ADR-001
- Date: 2026-10-26
- Module: QA-019 — Portable Offline Brief Journey
- Baseline: Architecture Freeze v1.0; ADR-001/003/044/045/055/069/070;
  PC-039/040/050/064/065

## Decision

QA-018 proves the no-key offline brief starter in a source-composed browser
app. QA-019 checks the same customer path in the extracted Windows portable
executable, without changing product behavior. Run a new Chrome spec against
the already-running isolated EXE after the existing portable journeys. A
synthetic, non-confidential brief is entered; Enter and a declined public-site
confirmation create nothing. Explicit acceptance creates one project and
saves the unchanged brief as the first visible section. Check its preview,
project-local folder export, matching static ZIP and browser reopen. After the
workflow restarts the EXE, verify the same project's identity and exact brief
through the public loopback API.

The brief remains visible website content under ADR-069, not a private note.
No credential, provider, generation, asset upload, Netlify deployment or
external network request belongs to this test.

## Boundary

QA-019 may create only this ADR, its PC-066 contract and one portable
Playwright spec. It may narrowly extend the existing Windows portable
workflow to invoke that spec and assert persistence after process restart.
The EXE retains its isolated profile; Chrome uses the disposable runner
profile already authorized in ADR-044. Filesystem reads of an exported site
are permitted only after resolving its path inside the isolated project root.
The spec skips unless both packaged origin and isolated root are supplied.

Keep all existing ZIP, API, browser and restart assertions. Do not change
production source, public API, project format, other test, dependency,
lockfile, launcher, build script, release or user data. This is not clean
Windows target acceptance, live-provider testing or AI site generation.

## Acceptance

PC-066 fixes exact ownership and assertions. Run frozen frontend install,
TypeScript, Vitest, Vite build, source browser tests, Ruff, Pyright and all
discovered Pytest. Run an isolated local packaged check when safely available
and require latest-head hosted CI. Review exact scope and merge under ADR-003
only after all gates pass. Produce one QA-019 module report and stop.
