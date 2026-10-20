# AURORA — Offline Browser ZIP Integrity Decision v1.0

- Document ID: ADR-042
- Status: APPROVED — delegated test decision under ADR-001
- Date: 2026-10-20
- Module: QA-007 — Offline Browser ZIP Integrity Journey
- Baseline: Architecture Freeze v1.0, ADR-003/010/017/037/040, PC-004/011/032/035

## Decision and boundary

The isolated Chrome journey downloads a ZIP and checks its name and nonzero
size. P4/P6 lower tests inspect archive members, but the browser gate does not
yet verify that the actual UI download contains the saved static site. QA-007
adds a read-only ZIP inventory to that browser journey. It changes no
production source, build/export behavior, API, Runtime, dependency, workflow,
provider, credential or user project.

A small Python test helper reads the downloaded archive with standard-library
`zipfile`, validates its CRC and reports only member names and SHA-256 digests.
It does not extract or execute members. The browser test compares the exact
member set and every digest with the already verified project-local folder
export from the same saved editor snapshot. This proves byte equality for the
offline synthetic journey, including the referenced raster and stylesheet,
and rejects extra project/settings/credential files in the ZIP.

PC-037 fixes exact scope and validation. This is not a clean-PC, live-provider,
image-quality or deployment acceptance result; QA-003 remains outstanding.
