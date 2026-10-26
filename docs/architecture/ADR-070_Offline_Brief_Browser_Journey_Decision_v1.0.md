# AURORA — Offline Brief Browser Journey Decision v1.0

- Document ID: ADR-070
- Status: APPROVED — delegated test-only decision under ADR-001
- Date: 2026-10-26
- Module: QA-018 — Offline Brief Browser Journey
- Baseline: Architecture Freeze v1.0; ADR-001/003/037/069; PC-006/007/032/064

## Decision

UI-023's offline brief starter has component tests, but the complete no-key
browser path is not yet covered. QA-018 adds one Chrome journey against the
existing isolated composed local app and actual built React UI. It verifies
that entering a brief and pressing Enter or declining the public-content
confirmation creates nothing; explicit acceptance creates exactly one project
and saves the unchanged brief in the first section exactly once. It checks the
saved editor, visible preview, project-local static folder export, browser
reload and project reopen.

The brief used in the test is synthetic and safe to publish. Its visible
appearance in the exported site is an intended consequence of ADR-069, not
evidence of a private project-note feature. No AI generation, credential,
asset upload, Netlify deploy or external network request is part of this path.

## Boundary

QA-018 may create only this ADR, its PC-065 contract and one Playwright spec.
Reuse the existing built UI, public loopback API and isolated browser-test
server without changing them. Use a fresh ignored `build/browser-e2e-<UUID>`
root, refuse an occupied dedicated loopback port and stop the child server.
No production source, existing test, workflow, dependency, lockfile, launcher,
project schema, credential or user data may change.

This test proves one synthetic offline path in a local browser. It does not
certify a clean Windows installation, live providers, AI-generated copy,
customer confidentiality or production hosting.

## Acceptance

PC-065 fixes exact ownership and assertions. Run frozen frontend install,
TypeScript, Vitest, Vite build, browser tests, Ruff, Pyright and all discovered
Pytest. Review exact scope and latest-head hosted CI before routine merge
under ADR-003. Produce one QA-018 module report and stop.
