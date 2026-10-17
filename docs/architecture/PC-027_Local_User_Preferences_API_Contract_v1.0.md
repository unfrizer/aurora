# AURORA — Local User Preferences API Contract v1.0

- Document ID: PC-027
- Status: APPROVED — delegated compilation of ADR-032 under ADR-001
- Module: P6-009 — Local User Preferences API
- Date: 2026-10-17

## Exact ownership

This module may modify only `src/local_api/app.py`,
`src/local_api/schemas.py`, and the narrow gateway admission in
`tests/local_api/test_security.py`; it may create
`tests/local_api/test_preferences_api.py` and
`tests/integration/test_local_preferences_api.py`. ADR-032, PC-027, and a
narrow PC-006 extension note are the only architecture document changes.
No launcher, P8 implementation, P1/P2/P3, frontend, dependency, workflow,
or other production/test file may change.

P6 may import the public `src.preferences` gateway only, not P8 internals.
`src.local_api` still exports exactly `create_app`. The factory adds keyword
argument `preferences_store: PreferencesStore | None = None`, preserving
existing calls and doing no settings I/O during construction. With no store,
only the two new endpoints return sanitized 503. Later launcher composition
must inject the default-path store; this module does not do so.

## HTTP contract

`GET /api/v1/preferences` loads the current P8 snapshot under the existing
app-instance lock and returns HTTP 200 JSON:

```json
{
  "preferences": {
    "schema_version": 1,
    "language": null,
    "general_model": "gpt-5.6-terra",
    "image_model": "gpt-image-2",
    "onboarding_completed": false
  },
  "revision": "<lowercase SHA-256 hex>",
  "projects_directory": "<server-owned absolute project root>"
}
```

The revision is the SHA-256 of the compact, sorted-key, UTF-8 JSON encoding
of exactly the five validated P8 fields. It is an optimistic comparison
token, not an authentication credential. GET does not create a settings file
or project directory. The path is drawn only from the injected project root,
never a request parameter. It appears only in this successful GET response.

`PUT /api/v1/preferences` requires an exact strict JSON object with
`preferences` (exactly the five P8 fields and their types) and
`expected_revision` (exactly 64 lowercase hexadecimal characters). It
passes the existing Host/Origin/`X-Aurora-Request: 1`, JSON media type and
2 MiB raw-body gates before any effect. Under the app-instance lock P6 loads
the current snapshot, compares the supplied revision and saves the new P8
snapshot only on match. HTTP 200 returns only `preferences` and the new
`revision`; it does not return the project path. Missing settings file means
defaults and can be first-saved. A stale revision returns fixed 409.

Invalid bodies or invalid proposed P8 snapshots return fixed 400. Missing
injection, corrupt/unsafe existing settings and P8 storage failures return
fixed 503; no silent reset or overwrite. All failures retain PC-006's numeric
envelope without paths, content, model text or secrets. Successful GET/PUT
responses set no-store, nosniff, same-origin resource policy and no-referrer.
No CORS is introduced. The store's own strict schema and atomic writer remain
the sole persistence owner. App-local locking does not claim cross-process
transactions.

## Acceptance

Tests inject a P8 store under `tmp_path`, with fake credentials and no real
LOCALAPPDATA, browser, network, paid request or deployment. Cover inert
construction, defaults/no file, exact GET schema and path, confirmed PUT and
reopening, stale revision, invalid bodies, no path override, Host/Origin/body
gates, corrupt-file fail-closed byte preservation, absent store, safe headers,
unaffected project data, and P6 import boundary. Run Ruff, strict Pyright and
all discovered Pytest, inspect the exact diff and require latest-head hosted
CI before routine merge. Produce one P6-009 report and stop for Tech Lead
review; launcher and React remain separate modules.
