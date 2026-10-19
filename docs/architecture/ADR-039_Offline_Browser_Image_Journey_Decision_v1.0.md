# AURORA — Offline Browser Image Journey Decision v1.0

- Document ID: ADR-039
- Status: APPROVED — delegated test decision under ADR-001
- Date: 2026-10-19
- Module: QA-004 — Offline Browser Image Journey
- Baseline: Architecture Freeze v1.0, ADR-003/026/027/037/038, PC-020/021/032/033

## Decision and boundary

QA-002 exercises the real React client against an isolated composed backend,
but intentionally stops at the guided-image choice. UI-003 and UI-004 have
unit tests with synthetic fetch responses, while the browser-to-API-to-project
image seam is not covered by that browser gate. QA-004 extends the existing
Windows/Chrome journey to exercise the approved guided logo and section-image
path, using the already patched fake image client and test-only project root.

This is a test module only. It may improve the fake PNG bytes so a browser can
decode them, but it must not change application source, routes, request/response
contracts, project schema, Runtime ownership, provider behavior, dependencies,
or test infrastructure outside PC-034's exact files. No real credential,
OpenAI request, paid action, Netlify publish, user project or public release
is involved. Existing explicit consent and review steps remain visible in
the test; automation accepts only the synthetic test dialogs.

## Evidence boundary

The browser spec must prove that dismissing the fake paid-call confirmation
creates no image request; accepting it creates one request and a saved but
unattached asset; a separate attachment persists the image reference. For a
section image it must prove that user-entered alt text is required and saved.
The saved preview and folder export must reference the attached image, and
reopening must preserve it. This does not prove visual quality, model/account
availability, clean-PC operation or any live-provider result. QA-003's manual
acceptance remains outstanding.

PC-034 fixes ownership, assertions and validation. Successful QA-004 is not
certification of the first usable Windows journey.
