# AURORA — Offline Browser Journey Decision v1.0

- Document ID: ADR-037
- Status: APPROVED — delegated test decision under ADR-001
- Date: 2026-10-19
- Module: QA-002 — Offline Browser Journey

## Decision and boundary

QA-001 verifies the composed local API with a synthetic UI; PKG-001 verifies
that the portable executable serves the built UI. Neither runs the actual
React client through a browser against the composed backend. QA-002 adds one
Windows-hosted Chromium end-to-end gate for that missing seam. It is a test
module only: no production Python, browser source, API, project schema,
Runtime, provider, launcher, or packaging behavior changes.

The test server uses `src.launcher.create_desktop_app` with the real built UI,
an isolated ignored project/settings directory, a process-local fake Windows
credential store, and deterministic fake OpenAI text/image methods. It binds
only `127.0.0.1`; it never contacts a provider or accesses a real user
profile. Browser actions exercise explicit confirmation and acceptance as
the existing UI requires. No paid action, real credential, Netlify publish,
or project deletion is performed.

`@playwright/test` is approved as a pinned **test-only** frontend dependency.
The test targets locally installed Chrome on Windows; GitHub-hosted Windows
runners include Chrome. No browser is added to the AURORA distribution and no
new runtime dependency is introduced. A missing browser fails the gate rather
than silently falling back to jsdom. PC-032 fixes exact files and assertions.

## Acceptance meaning

The automated journey verifies onboarding, a fake one-prompt text draft,
explicit draft acceptance, browser editor save, saved preview, site export,
and reopening after page reload. It also verifies that the fake key and
temporary project/settings roots remain separate. This is stronger than a
synthetic-UI API test but **not** clean-PC, live-provider, real-credential,
image-quality, or deployment acceptance. PKG-001's actual executable smoke
and QA-001's lower-boundary assertions remain required.
