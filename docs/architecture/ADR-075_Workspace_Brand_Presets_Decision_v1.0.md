# AURORA — Workspace Brand Presets Decision v1.0

- Document ID: ADR-075
- Status: APPROVED — delegated browser editor decision under ADR-001
- Date: 2026-10-26
- Module: UI-027 — Workspace Brand Presets
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/073; PC-007/014/068

## Decision

The existing P7 editor brand exposes primary color, secondary color and font
family for user editing. UI-027 adds an explicit convenience action in the
Workspace brand inspector to set these three existing values together. The
user chooses one of four fixed starting combinations and activates **Apply
style**. Choosing an option alone has no persistence or provider effect.

| Option | Primary | Secondary | Font |
| --- | --- | --- | --- |
| Indigo | `#4F46E5` | `#0F172A` | `system` |
| Ocean | `#075985` | `#0C4A6E` | `system` |
| Forest | `#166534` | `#14532D` | `serif` |
| Warm | `#9A3412` | `#7C2D12` | `serif` |

Applying a style produces one ordinary immutable editor change through the
existing UI-001 commit and versioned save flow. The selected option itself is
not stored; only the P7 color/font fields are saved. Brand name, tagline, logo,
pages, text, SEO, images, language and IDs remain unchanged. Applying an option
already identical to the current values does nothing. Existing manual color
and font editing remains available. The UI explicitly states that applying
replaces the three current values and can be changed again.

This is a browser editor shortcut over P7 fields. It does not import, modify
or duplicate the L3 Theme Runtime or its active ThemeDefinition. P7/P1/P6/P4
retain schema, persistence, API and site-build ownership. UI-025 manual-site
creation keeps the blank editor's original palette and typography as ADR-073
requires; styles are applied only after opening Workspace.

No AI generation, provider call, network integration, new API route, project
schema, dependency, browser storage, global mutable state or automated
publication is introduced. Preview/export still use saved state and the
existing P4 builder.

## Acceptance

PC-070 fixes file ownership. Test exact values, immutable field isolation,
selection without effect, explicit application, no-op, ordinary versioned
save, RU/EN labels and preview/export persistence. Preserve all regressions.
Run frozen frontend install, TypeScript, Vitest, Vite build, browser tests,
Ruff, Pyright and discovered Pytest. Review exact diff and latest-head CI
before ADR-003 merge.
