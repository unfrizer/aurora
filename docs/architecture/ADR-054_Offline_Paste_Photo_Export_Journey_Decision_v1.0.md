# AURORA — Offline Paste, Photo and Export Journey Decision v1.0

- Document ID: ADR-054
- Status: APPROVED — delegated test-only decision under ADR-001
- Date: 2026-10-22
- Module: QA-016 — Offline Paste, Photo and Export Journey
- Baseline: Architecture Freeze v1.0; ADR-001/003/037/042/047/048/049/051/052;
  PC-004/011/032/037/042/043/044/046/047

## Decision

The existing tests separately cover direct prepared-JSON paste, manual photo
attachment and static ZIP integrity. They do not yet verify that a user can
take the combined no-AURORA-API-key path all the way to an exportable website
in the real browser. QA-016 adds one test-only Chrome journey against the
existing isolated composed local app; it changes no user-facing behavior.

A synthetic P7 v1 document is pasted into a new project. A synthetic PNG is
selected and manually attached to the existing section. The test confirms
selection alone uploads nothing, the attached bytes and editor reference are
saved, and the saved site can be exported as a folder and downloaded ZIP. It
checks rendered text, SEO and image reference in the folder, compares every
ZIP member digest to the folder artifact, and reopens the saved project after
browser reload. The path makes no AI/provider, credential or deployment call.

## Boundary

QA-016 may create only this ADR, its PC-049 contract and one Playwright spec.
Reuse the existing built UI, public loopback API, isolated fake-service test
server and read-only ZIP inventory helper without changing them. No production
source, other test, workflow, dependency, lockfile, launcher, project format,
credential or user data may change. Use a fresh ignored `build/browser-e2e-<UUID>`
root, refuse an occupied dedicated loopback port, and stop the child server.

This is evidence only for a synthetic, manually assembled offline path. It
does not claim live ChatGPT integration, automatic photo placement, image
quality, clean-Windows acceptance, production hosting or autonomous business
generation.

Run frozen frontend install, TypeScript, Vitest, Vite build, browser tests,
repository Ruff, Pyright and discovered Pytest. Review exact scope and
latest-head hosted CI before routine merge under ADR-003. Produce one QA-016
module report and stop.
