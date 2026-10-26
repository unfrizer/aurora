# AURORA — Local Project Search Clear Decision v1.0

- Document ID: ADR-067
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-26
- Module: UI-021 — Local Project Search Clear
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/066; PC-014/061

## Finding and decision

UI-020 provides transient local project-name search, but after entering a query
the user must remove it character by character or rely on browser-specific
search controls. UI-021 adds one explicit localized clear-search button next to
the existing search control.

The button is rendered only while the raw controlled query contains at least
one character, including whitespace. Activating it sets that same transient
query to the empty string. The existing UI-020 derivation then restores the
complete project list in its original server order. The button is absent when
the query is empty and when the repository list itself is empty.

Clearing search remains available while another project operation is busy
because it is a local display action and does not change that operation. It
performs no API/provider/asset call, browser-storage write, project mutation,
navigation, sorting, import, generation, build, export or deployment. It does
not change matching, the 128-character boundary, the empty-repository state,
or any project identity/callback.

No dependency, route, schema, Runtime or lower-layer owner changes.

## Boundary and acceptance

PC-062 grants exact file scope. Test EN/RU labels, conditional visibility,
restoration of the original list and order, the whitespace-query case, the
empty-repository state and absence of project/provider/storage side effects.
Preserve every existing regression. Run frozen frontend install, typecheck,
Vitest, Vite build, browser tests, Ruff, Pyright and all discovered Pytest.
Inspect exact scope and latest-head hosted CI before routine ADR-003 merge.
Produce one UI-021 module report and stop.
