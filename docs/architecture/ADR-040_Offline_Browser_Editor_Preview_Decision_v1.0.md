# AURORA — Offline Browser Editor and Preview Decision v1.0

- Document ID: ADR-040
- Status: APPROVED — delegated test decision under ADR-001
- Date: 2026-10-19
- Module: QA-005 — Offline Browser Editor and Preview Journey
- Baseline: Architecture Freeze v1.0, ADR-001/003/037/039, PC-032/034

## Decision and boundary

The existing isolated Chrome journey verifies the one-prompt draft, guided
images, one text edit, preview, export and reload. It does not yet verify the
manual brand and SEO edits, independent panel collapse, mobile-width preview or
the preview's separate browser tab. QA-005 adds those assertions to the same
test-only journey, using the already isolated fake-service server. It changes
no production source, provider adapter, route, project schema, Runtime,
dependency, workflow, package or user data.

The test must save and reopen manual brand and SEO edits, observe both panels
collapse and reopen independently, verify the edited SEO metadata in the
saved preview and exported site, switch desktop/mobile preview widths, and
open the saved preview in a separate local browser tab. It must not contact
OpenAI or Netlify, use real credentials or imply that these offline checks
constitute clean-PC or live-provider acceptance.

PC-035 fixes exact file ownership and validation. QA-003 manual acceptance
remains outstanding, including real service results and a separate clean PC.
