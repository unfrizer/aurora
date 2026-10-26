# AURORA — Local Project List Search Decision v1.0

- Document ID: ADR-066
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-26
- Module: UI-020 — Local Project List Search
- Baseline: Architecture Freeze v1.0; ADR-001/003/020; PC-014

## Finding and decision

The Projects screen renders every project returned by the existing P6 list
route but offers no way to narrow a growing list. UI-020 adds a localized,
session-only search field above a nonempty project list. It filters only the
already loaded `ProjectMetadata.name` values and never sends the query to P6.

Matching trims leading and trailing query whitespace, converts both query and
project name with JavaScript `toLowerCase()`, and performs a substring match.
An empty or whitespace-only query shows every project. The original server
order and original project objects remain unchanged. The query is limited to
128 characters and is not persisted. It does not search project IDs, timestamps,
editor content, assets or filesystem paths.

When a nonblank query has no matches, show a distinct localized empty-result
message. The existing no-projects message remains authoritative when the
repository list itself is empty; in that state no search control is rendered.

Search performs no API/provider/asset call, browser-storage write, project
mutation, navigation, sorting, import, generation, build, export or deploy.
Opening and deleting a visible project continue to use that project's unchanged
identity and existing callbacks. No dependency, route, schema, Runtime or
lower-layer owner changes.

## Boundary and acceptance

PC-061 grants exact file scope. Test EN/RU labels, case-insensitive substring
matching, trimmed/empty queries, stable ordering, no-match and empty-repository
states, the 128-character input boundary and absence of side effects. Preserve
all existing project actions and regressions. Run frozen frontend install,
typecheck, Vitest, Vite build, browser tests, Ruff, Pyright and all discovered
Pytest. Inspect exact scope and latest-head hosted CI before routine ADR-003
merge. Produce one UI-020 module report and stop.
