# AURORA — Offline Import and Photo Browser Journey Decision v1.0

- Document ID: ADR-049
- Status: APPROVED — delegated test-only decision under ADR-001
- Date: 2026-10-21
- Module: QA-012 — Offline Import and Customer Photo Browser Journey
- Baseline: Architecture Freeze v1.0; ADR-001/002/003/037/047/048;
  PC-032/042/043

## Decision

UI-007 and UI-008 have deterministic component and integration tests, but
their combined no-API-key path has not been exercised in a real browser
against the composed local backend. QA-012 adds that missing seam as one
test-only module. It does not add or change any user-facing behavior.

The gate runs the existing built React UI and public loopback API under the
existing isolated browser test server. A local in-memory JSON file imports a
text-only P7 editor into a new project. Two synthetic customer PNGs are
selected in the transient photo tray, manually assigned to the logo and an
existing section, and attached one at a time. The test observes that
selection alone performs no upload, then verifies saved paths, original
asset bytes, unchanged user-authored image alt text, preview and persistence
after browser reload. It asserts that no provider or deployment request
occurs. No real credentials or customer data are used.

## Boundary

QA-012 may create only its own ADR, approved contract and one Playwright spec.
The existing test server, browser configuration and workflow already discover
and run the spec. No source file, P1/P6/P7/P4 owner, application API, package,
dependency, lockfile, CI configuration or earlier test changes. A unique
ignored `build/browser-e2e-<UUID>` root and process-local fake services are
required. The test must refuse an occupied fixed loopback port and stop its
server after execution. It may leave the isolated test directory for
inspection, as PC-032 permits.

This test is evidence for only the offline prepared-JSON plus manual-photo
path. It is not live ChatGPT, OpenAI, provider, Netlify, image-quality,
automatic-placement, clean-target Windows or portable-EXE acceptance. It
does not redefine the deferred work in ADR-047 or ADR-048.

## Acceptance

Run frozen pnpm install, TypeScript, Vitest, Vite build and the new browser
spec, plus repository Ruff, Pyright and all discovered Pytest. Review exact
file scope and require latest-head hosted CI before routine merge under
ADR-003. Produce one QA-012 module report and stop.
