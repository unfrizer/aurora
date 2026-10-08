# AURORA — Local Editor and Asset API Contract v1.0

**Document ID:** PC-009
**Status:** APPROVED — compiled from ADR-015 EA-01–EA-05
**Module:** P6-002 — Local Editor and Raster Asset API
**Date:** 2026-10-08
**Authority:** ADR-015 (explicit EA-01–EA-05 approval), PC-006

## Scope and ownership

This is a separate implementation task extending the existing P6
FastAPI application-composition owner. It may modify only
`src/local_api/app.py` and `src/local_api/schemas.py`, and create
`tests/local_api/test_editor_assets.py` and
`tests/integration/test_local_editor_assets.py`. No P1/P7/P4/P5
production file, existing test, dependency, public `src.local_api`
gateway, Runtime or frontend file may change. The public Python
`create_app(*, project_root, credential_store, allowed_origin)`
signature and inert construction behavior are unchanged.

P6-002 may import standard library, FastAPI/Pydantic, and public
`src.projects`, `src.editor`, `src.credentials` and
`src.generation` gateways. It may not import private P1/P7
implementations, P4/P5, concrete Kernel/Platform Runtimes or a
frontend module. No lower owner imports P6. Use the existing
per-app-instance project lock for editor and asset mutations.

## Editor save

Add `PUT /api/v1/projects/{project_id}/editor` with a strict JSON
object containing exactly `editor` (the P7 version-one object) and
`expected_updated_at` (string). Return status 200 and the existing
P6 ProjectDocument JSON projection. Inside the app lock, load the P1
document, check the expected timestamp exactly as the existing opaque
project PUT does, decode the supplied P7 editor subtree, call
`save_editor_state` on the current state, reapply the existing
recursive credential-key rejection, and persist through P1 without
changing the project name or unrelated top-level state. Existing
malformed/unsupported editor state cannot be silently overwritten.
P6 does not make a draft publishable, generate IDs/defaults, or start
a background autosave job. Existing project routes retain their
approved behavior; GET project already returns the editor state.

Return 404 for missing project, 409 for stale timestamp, 400 for
invalid P7 payload/state, and 500 for P1 I/O. All failures use only
P6's existing fixed `{"error":{"code": <status>}}` envelope.

## Raster transport

Add exactly:

| Route | Success |
| --- | --- |
| `POST /api/v1/projects/{project_id}/assets` | Raw bytes with exact `image/png`, `image/jpeg`, `image/gif` or `image/webp` Content-Type; `201 {"path":"assets/<sha256>.<ext>"}` |
| `GET /api/v1/projects/{project_id}/assets/{asset_name}` | `200` P1-verified bytes with canonical raster Content-Type |
| `DELETE /api/v1/projects/{project_id}/assets/{asset_name}` | `204` if P1 removes an unreferenced asset |

Validate the URL project ID and form only the relative P1 reference
`assets/{asset_name}`. P1 remains sole project-path, asset-signature,
digest, capacity, publication, read-integrity and reference-aware
delete authority. P6 does not expose or accept project filesystem
paths, user-supplied upload filenames, multipart forms, remote URLs,
alternate image representations or P1 internals. GET sets
`Cache-Control: no-store`, `X-Content-Type-Options: nosniff` and
`Cross-Origin-Resource-Policy: same-origin`.

Missing project or valid-but-absent asset returns 404. Malformed
reference, unsupported media, bad signature, capacity failure,
corruption and referenced deletion return 400. Native filesystem
errors return 500. The error response is the fixed P6 envelope and
never contains input, filename, local path, project state or secret.

## Request security and bounded body

Preserve P6-001's exact Host, Origin and `X-Aurora-Request: 1`
mutation gates, lack of CORS and loopback-only launcher contract.
All existing JSON body routes remain capped at 2 MiB and retain
their media-type behavior. Only the exact raster POST accepts raw
image bytes and its four approved Content-Types. Reject a declared
body over 16 MiB before service effects; read an undeclared or
misdeclared request incrementally, stopping before retaining more
than 16 MiB plus one byte. Invalid media/size/Host/Origin/header
returns 400 before P1 writes. No normal log or error response may
contain upload bytes, user state, filenames or secrets. No claim is
made against malicious same-user processes or compromised same-origin
UI.

## Acceptance and publication

Use `tmp_path`, synthetic raster signatures and the in-memory
FastAPI test client. Cover the four new routes and unchanged P6-001
routes; P7 save, stale/missing/unsupported editor, opaque-key
preservation; four media types, deterministic reopen/read, 16 MiB
boundary and streaming over-limit rejection; invalid media, path,
signature, Host/Origin/header; absent, linked and corrupt assets;
referenced deletion, dereference-then-delete; fixed errors and no
unexpected P1/P7 mutation. The integration path is create → upload
→ editor save → reopen → asset GET → editor dereference → delete,
through public HTTP only. No real user project, credential, provider,
network, build, deploy or browser launch.

Run Ruff, strict Windows/Linux Pyright, full discovered Pytest,
scope/import review and latest-head hosted CI. Produce one P6-002
module report and stop for Tech Lead review. Structured one-prompt
generation, image generation, preview, build/export/deploy HTTP,
global settings, React/Vite and a Windows launcher remain separate
contracted work; P6-002 is not usable-Windows acceptance.
