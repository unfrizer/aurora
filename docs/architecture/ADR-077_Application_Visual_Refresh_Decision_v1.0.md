# AURORA — Application Visual Refresh Decision v1.0

- Document ID: ADR-077
- Status: APPROVED — delegated browser presentation decision under ADR-001
- Date: 2026-11-01
- Module: UI-029 — Application Visual Refresh
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/076; PC-014/071

## Decision

Refresh only the local React application's CSS presentation. Use an ink-blue
navigation bar, a pale blue-gray workspace canvas, white content surfaces and
a teal action accent. Give the Projects screen a clear introductory panel,
use its available desktop width for the creation paths, and visually separate
the editor's page rail, canvas and inspector. Improve hierarchy, spacing,
focus indicators, and narrow-window layout without adding a dependency or
requiring network assets.

This is a browser-client presentation decision. Project brand colors and font,
the generated site's CSS and preview, editor schema, accessibility names,
localized copy, DOM behavior, API calls, save/confirm/error flows, credentials,
and P1–P8 or L0–L8 ownership remain unchanged. No application theme setting,
new public behavior or new design abstraction is introduced.

Desktop and narrow layouts must remain usable at 1440 px and 390 px viewport
widths. Keyboard focus must remain visible. Do not hide controls, content or
warnings for visual effect; collapsed panels must continue to work. Motion
is limited to short hover transitions and respects reduced-motion settings.

## Acceptance

PC-072 fixes ownership. Inspect the built UI at desktop and narrow widths,
check for horizontal overflow, and run the existing browser journeys. Run
frozen frontend install, TypeScript, Vitest, Vite build, Ruff, Pyright and
discovered Pytest. Inspect exact diff and latest-head CI before ADR-003 merge.
