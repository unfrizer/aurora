# AURORA — Portable Offline Paste, Photo and Export Journey Decision v1.0

- Document ID: ADR-055
- Status: APPROVED — delegated test-only decision under ADR-001
- Date: 2026-10-22
- Module: QA-017 — Portable Offline Paste, Photo and Export Journey
- Baseline: Architecture Freeze v1.0; ADR-001/003/044/045/050/053/054;
  PC-039/040/045/048/049

## Decision

QA-016 proves that a prepared site can be pasted, supplied with a manually
attached customer image, and exported as a self-contained static site in the
source-composed local app. QA-015 separately proves paste in the packaged
Windows app. QA-017 checks the combined offline path in the extracted portable
executable, without changing product behavior.

Run one additional Chrome spec against the already-running isolated portable
app after the existing packaged browser journeys. Paste synthetic P7 v1 JSON,
manually attach one synthetic PNG, export the site folder and ZIP, verify the
rendered text, SEO and original image bytes, compare exact ZIP members and
digests to the folder, and reopen the saved project after browser reload. The
existing smoke restarts the same EXE and checks that project's identity, text
and image reference through its public loopback API. No credential, provider,
generation, deployment or external network request is allowed.

## Boundary

QA-017 may create this ADR, its PC-050 contract and one portable Playwright
spec, and narrowly extend the existing Windows portable workflow to run the
spec and check its project after restart. The EXE retains its isolated profile;
Chrome alone uses the disposable runner-profile exception of ADR-044. The spec
may read exported files only under the isolated project root passed by the
workflow, and uses the existing read-only ZIP inventory helper. It skips
without the packaged origin and isolated project-root variables so the source
browser gate remains unchanged.

Keep every existing ZIP, API, browser and restart assertion intact. Do not
change production source, public API, project format, dependency, lockfile,
launcher, build script, other test, release, user data or credential. This
gate is not clean-target Windows, live ChatGPT, automatic photo placement,
image-quality, provider or deployment acceptance.

Run frozen frontend install, typecheck, Vitest, Vite build, source browser
tests, repository Ruff, Pyright and discovered Pytest. Run an isolated local
portable build/smoke if safely available and require latest-head hosted CI.
Review exact scope, publish under ADR-003 only when all gates pass, and stop
after one QA-017 module report.
