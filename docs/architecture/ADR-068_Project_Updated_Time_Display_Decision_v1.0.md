# AURORA — Project Updated Time Display Decision v1.0

- Document ID: ADR-068
- Status: APPROVED — delegated browser UI decision under ADR-001
- Date: 2026-10-26
- Module: UI-022 — Project Updated Time Display
- Baseline: Architecture Freeze v1.0; ADR-001/002/003/020/066/067; PC-014/061/062

## Decision

The Projects screen currently displays the raw P1 `updated_at` timestamp.
UI-022 labels it as the last update and formats valid timestamps in the
browser's local time zone, using `ru-RU` or `en-US` according to the active UI
language. The formatting uses the platform's medium date and short time styles.
The original timestamp remains unchanged in a semantic `<time dateTime>`
attribute. The UI does not calculate relative age, alter the server sort order,
or store a formatted value.

If the API yields a timestamp that cannot be parsed into a finite date, the
Projects screen displays a localized unknown-time label and does not create a
misleading `<time>` element. This is defensive display behavior; P1 retains
timestamp validation and ownership. The list retains its original objects,
order, project actions and search behavior.

Formatting performs no network, provider, asset, storage, mutation, import,
generation, build, export or deploy action. No dependency, API route, schema,
Runtime, lower-layer owner or persisted value changes.

## Boundary and acceptance

PC-063 grants exact file scope. Check valid timestamps in both languages,
semantic original timestamp, invalid-timestamp fallback, stable project order
and absence of side effects. Preserve existing regressions. Run frozen frontend
install, TypeScript, Vitest, Vite build, browser tests, Ruff, Pyright and all
discovered Pytest. Inspect exact scope and latest-head hosted CI before an
ADR-003 merge. Produce one UI-022 module report and stop.
