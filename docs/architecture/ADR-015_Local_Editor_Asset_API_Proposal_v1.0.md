# AURORA — Local Editor and Asset API Proposal v1.0

**Document ID:** ADR-015
**Status:** APPROVED — EA-01–EA-05
**Date:** 2026-10-08
**Target module:** P6-002 — Local Editor and Raster Asset API
**Repository baseline:** `4254b4aea1d3a6e799c3063bc61342634a5b301b`

## Why a decision is needed

P7-001 validates and projects versioned editor state, and P1-002 now
persists project-owned raster bytes. P6-001 exposes only opaque project
JSON and a plain-text generation endpoint. Its approved PC-006 import
boundary excludes P7 and its mutation middleware accepts only JSON up
to 2 MiB. A browser therefore cannot upload a 16 MiB raster asset
through the local API or ask P6 to validate an editor save. These are
new public HTTP and security behaviors; existing implementation does
not authorize them.

This proposal extends the **existing P6 application-composition owner**.
It does not change a Runtime, P1/P7 schemas, an existing route, the
Windows credential boundary or a provider. The decisions below
authorize a PC-009 contract and a separate P6-002 module task. The
Architecture Freeze and full Master Pack are not present in this
checkout; this ADR does not claim to replace either authority.

## EA-01 — Ownership and dependency direction

P6-002 would modify only `src/local_api/app.py` and
`src/local_api/schemas.py`, and add
`tests/local_api/test_editor_assets.py` and
`tests/integration/test_local_editor_assets.py`. Existing-test
exceptions are limited to `tests/local_api/test_security.py`
(add only `"src.editor"` and `"src.core.exceptions"` to its
approved-import set) and `tests/editor/test_models.py` (admit only
`src/local_api/app.py` as a public `src.editor` consumer while
preserving the prohibition for every other production file and
private P7 imports). No other existing test, production file,
dependency declaration or public Python gateway changes.
`create_app` retains its exact P6-001 signature.

P6 may additionally import the public `src.editor` gateway and
Foundation `ValidationError` from `src.core.exceptions` solely to
map P1 validation failures to HTTP 400 without catching unrelated
failures. It
continues to import P1 through the public `src.projects` gateway and
does not import private P1/P7 files, P4/P5, Kernel/Platform Runtime
implementations or frontend code. Lower owners never import P6. The
existing app-instance project lock coordinates editor and asset
mutations within one app instance; it is not cross-process concurrency
control or a new DI scope.

## EA-02 — Explicit editor-save route

Add only this editor-aware JSON route:

```text
PUT /api/v1/projects/{project_id}/editor
Body: {"editor": <exact P7 version-one object>,
       "expected_updated_at": <string>}
Success: 200 <the existing P6 ProjectDocument JSON projection>
```

Under the existing project lock, P6 loads the P1 document, checks
`expected_updated_at` exactly as the existing opaque project PUT
does, decodes the supplied editor subtree with P7, saves through P7's
`save_editor_state` while preserving all unrelated top-level state,
reapplies the existing recursive credential-key check, and persists
through P1. P6 does not generate missing editor defaults, silently
repair invalid existing editor state, change the project name, or
interpret P7 as a P4-publishable site. Missing projects return 404,
stale timestamps 409, invalid P7 payload/state 400, and P1 I/O 500
using P6's existing sanitized error envelope.

The existing `GET /projects/{project_id}` supplies saved editor state;
no redundant editor GET is added. Existing P6-001 opaque project routes
remain byte-for-byte compatible, including their ability to carry
opaque JSON. The later UI must use the editor-aware PUT for validated
editor changes and may call it after confirmed changes for autosave;
P6 creates no background autosave task.

## EA-03 — Exact raster HTTP routes

Add exactly these routes:

| Method and path | Body / success |
| --- | --- |
| `POST /api/v1/projects/{project_id}/assets` | Raw bytes with exact `Content-Type` of `image/png`, `image/jpeg`, `image/gif` or `image/webp`; `201 {"path":"assets/<sha256>.<ext>"}` |
| `GET /api/v1/projects/{project_id}/assets/{asset_name}` | No body; `200` verified bytes from P1 with the canonical image Content-Type |
| `DELETE /api/v1/projects/{project_id}/assets/{asset_name}` | No body; `204` if removed |

`asset_name` is exactly the canonical P1 basename (lowercase SHA-256
and extension); P6 passes `assets/{asset_name}` to P1 after validating
the URL project ID. No caller-provided filesystem path, project root,
external URL, multipart filename, asset ID alias or alternative image
representation is accepted. POST delegates signature, content hash,
capacity, non-overwrite and safe publication to P1. GET delegates
regular-file and integrity checks to P1; it sets `Cache-Control:
no-store`, `X-Content-Type-Options: nosniff` and
`Cross-Origin-Resource-Policy: same-origin`. DELETE delegates
reference-aware refusal to P1 and never edits state. The UI must save
an unreferenced editor state before requesting delete.

Missing project or valid-but-absent asset is 404. Malformed asset
reference, unsupported type, signature/capacity failure, corrupt
managed file or referenced deletion is 400; P1 exposes the same
`ValidationError` for these cases, so P6 does not invent a more
specific public reason. Native filesystem failure is 500. All errors
retain only P6's fixed `{"error":{"code": <status>}}` response.

## EA-04 — Bounded same-origin upload exception

The existing Host, exact Origin and `X-Aurora-Request: 1` gates
continue for mutations, without CORS or public network bind. The
existing 2 MiB JSON rule remains unchanged for all other body-bearing
routes. Only the exact asset POST is exempt from JSON media type and
uses one approved raster media type and a maximum of 16 MiB raw body.
P6 reads the request stream incrementally and stops before retaining
more than 16 MiB plus one byte, including when `Content-Length` is
absent or false. Oversize, absent/unsupported media type, wrong Origin,
Host or custom header fail before P1 write, with status 400 and the
fixed envelope. No upload bytes, project state, local path or secret
appear in normal logs or error responses. GET responses are not
cross-origin readable; this does not claim protection from malicious
same-user local processes or a compromised same-origin UI.

## EA-05 — Acceptance and deferred work

Tests use `tmp_path`, synthetic raster signatures and FastAPI's
test client. Cover exact route set and unchanged P6-001 routes;
validated editor save, stale save, missing/unsupported editor and
opaque-key preservation; four raster media types, deterministic
path/reopen/read, bounded raw streaming, invalid media/signature/path,
Host/Origin/header rejection, absent/corrupt/linked assets, referenced
deletion and dereference-then-delete, fixed errors and no unexpected
P1/P7 mutation. Integration tests exercise create → upload → editor
save → reopen → asset GET → editor dereference → delete through the
public HTTP boundary. No real user projects, credentials, provider,
network request, build, deployment or browser launch.

Run Ruff, strict Windows/Linux Pyright, full discovered Pytest, final
ownership/import review and latest-head hosted CI. Produce one
P6-002 module report and stop for Tech Lead review. This module does
not add structured one-prompt generation, image generation, preview,
build/export/deploy HTTP, global settings, React/Vite, or a Windows
launcher. P6-002 alone is not the ADR-002 usable Windows version.

## Approval record

On 2026-10-08, the Architecture Authority explicitly approved
**EA-01–EA-05 in full** in the project conversation. PC-006 may be
narrowly amended, PC-009 may compile this decision, and P6-002 may
begin as a separate module task with its own validation and Tech Lead
review. A different upload format, route shape, security limit, error
mapping or owner requires a new decision.

After the P6-001 import-guard test exposed a conflict with EA-01's
original prohibition on existing-test edits, the Architecture
Authority explicitly approved this single test-admission correction
on 2026-10-08. It permits adding only `"src.editor"` to
`tests/local_api/test_security.py`'s allowed-import set; it does not
weaken any other test rule or expand production imports. PC-009
records the same narrow exception.

The Architecture Authority subsequently approved the second
test-admission correction on 2026-10-08: P6-002 may import
`ValidationError` from `src.core.exceptions` only for the
approved P1-to-HTTP error mapping, and the same test's allowed-import
set may additionally contain only `"src.core.exceptions"`. This
does not authorize any other Foundation import, generic exception
mapping, or test-rule weakening.

The Architecture Authority explicitly approved the third narrow
test-admission correction on 2026-10-08 after the full P6 suite
identified P7's blanket consumer ban. Only
`tests/editor/test_models.py` may be adjusted to admit
`src/local_api/app.py` importing the public `src.editor` gateway.
All other production consumers and private P7 imports remain
forbidden. No P7 production code or public surface changes.
