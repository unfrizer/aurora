# AURORA — Local Static Folder Export API Proposal v1.0

- Document ID: ADR-029
- Status: APPROVED — Architecture Authority approved FE-01–FE-05 in full
- Date: 2026-10-16
- Proposed module: P6-008 — Local Static Folder Export API
- Repository baseline: `31b335e5219eea71e16cb8c71710ef86e84f7c91`

## Decision boundary

ADR-002 requires Export Folder. ADR-028 FX-01–FX-05 approves a new static-site
folder inside the selected project's existing `exports/` directory, rather
than a browser-supplied destination. P1-003 now provides the public validated
`ProjectRepository.export_directory(project_id)` path boundary; P4 already
builds a detached site and exclusively writes a new folder. P6-004's ZIP
route proves the saved P1 → P7 → P4 composition, but it deliberately has no
project artifact write. No approved contract yet authorizes a local HTTP
operation that performs this side effect or reveals its successful path.

The approved decisions below authorize one P6 application-composition task
as compiled in PC-023. No P1, P4, P7, React, launcher,
L0–L8 Runtime or provider ownership moves. The full Architecture Freeze and
Master Pack are not in this checkout; an incompatible frozen rule requires
reconciliation, not an implicit override by this proposal.

## FE-01 — Exact owner and file boundary

P6-008 would modify only:

```text
src/local_api/app.py
src/local_api/schemas.py
tests/local_api/test_site_folder_export.py             # create
tests/integration/test_local_site_folder_export.py    # create
```

The approval record in this ADR, PC-023, and a narrow PC-006 extension note
would be the only architecture-document changes. No P1/P4/P7 source or test,
existing P6 test, public `src.local_api` gateway, dependency, lockfile,
workflow, frontend, launcher or other production file may change. The exact
`create_app` signature stays unchanged. P6 uses only already-admitted public
P1, P7 and P4 gateways; it gains no private import or new dependency.

The route may use a private P6 helper to share the existing saved-editor →
verified-assets → typed-projection → P4-build sequence, provided the ZIP,
preview and Netlify routes retain their approved observable behavior. No
new public service, repository method, global state or background worker.

## FE-02 — Explicit same-origin request and snapshot

Propose exactly one route:

```text
POST /api/v1/projects/{project_id}/exports/folder
JSON body: {"expected_updated_at": <string>, "confirm_export": true}
Success: 201 application/json, {"folder_path": <absolute native path string>}
```

Both fields are required and no extras are accepted. `confirm_export` must
be literal JSON `true`, not a truthy number or string. The existing 2 MiB
JSON limit, exact loopback Host and Origin checks, and
`X-Aurora-Request: 1` mutation gate apply. The request has no destination,
filename, source HTML, bytes, project state or arbitrary path. A later UI
must ask the user before sending it; loading the Export/Deploy screen makes
no request. A malformed request creates nothing.

Under the existing app-instance lock, P6 validates the project ID, loads
its current P1 document, and compares `expected_updated_at` exactly with
saved metadata. Mismatch returns 409 before reading assets, building or
looking up the export directory. It then decodes only the saved P7 editor,
collects the logo and section raster references in editor order with first
occurrence deduplication, reads their verified bytes through P1, projects
through P7 and compiles through P4 as in P6-004. An absent, unsupported or
invalid editor is not silently replaced by a blank site.

Only after a successful build does P6 call P1's public
`export_directory(project_id)`. It selects one new child named exactly
`aurora-site-<lowercase-uuid4>` beneath that parent, without using the
project name or user input. P4 `StaticSiteExporter.export_folder` validates
the build and destination and writes exclusively. The P4 artifact files
are the exported folder contents at its root, without a `dist/` wrapper,
project JSON, settings, prompt, credential or unrelated asset. No site/
write, saved-state update, paid call, deployment, ZIP staging or network
operation occurs. The lock is held through the export and response
construction. This serializes one app instance, not independent processes.

Each confirmed request is a new export, not an idempotent retry. The route
does not overwrite an existing child or retry name collisions automatically.
A lost response can leave a completed folder whose path the browser did not
receive; the client must not silently retry. The user may inspect the
project's `exports/` directory or explicitly request another export.

## FE-03 — Response, errors and cleanup

On success return only the native absolute `folder_path` string in JSON.
Its disclosure is an explicit exception to P6-001's no-project-path response
rule, limited to this same-origin, user-confirmed local export result. Do
not include the path in a URL, redirect, cookie, log, error response or
project state. Set `Cache-Control: no-store`,
`X-Content-Type-Options: nosniff`,
`Cross-Origin-Resource-Policy: same-origin` and
`Referrer-Policy: no-referrer`; add no CORS header or `Location` header.
The future UI may display/copy this path but must not send it to a provider.

Missing project is 404. A stale timestamp is 409. Missing/unsupported/
malformed saved editor, invalid site projection, or missing/malformed/
corrupt referenced raster is 400. Invalid P1 export-directory structure,
native I/O, P4 destination validation, collision, export failure and other
server-selected output failures are 500. All failures use P6's existing
fixed `{"error":{"code": <status>}}` envelope, with no raw exception,
local path, content or credential in the response. In particular, a
server-selected destination fault is not reported as bad user input.

P4 retains its exclusive-write and invocation-owned best-effort cleanup
policy. P6 must not recursively delete project `exports/`, an existing
export, unknown entries, or a partially written folder after P4 reports
incomplete cleanup. A failed call cannot change saved JSON/assets or
overwrite an earlier export. A crash or incomplete cleanup may leave a
recognizable partial child; no cross-process transaction or durability
guarantee is claimed. The UI must not call a failed request successful.

## FE-04 — Acceptance and regression matrix

Deterministic tests use only `tmp_path` projects, synthetic raster bytes,
fake credentials, FastAPI TestClient and the public P4 builder/exporter.
Cover the exact strict body; false/number/string confirmation; Host,
Origin, mutation header, media type and 2 MiB limit; invalid/missing
project; 409 precedence over assets/build/export-parent lookup; invalid
editor/site/asset; unsafe or missing P1 export directory; native write,
P4 validation, collision and incomplete-cleanup failures. Assert fixed
numeric errors and no leaked path, secret or content.

For successful calls, assert HTTP 201, exact one-field response and safety
headers; canonical unique child names under P1's validated parent;
deterministic file bytes across two distinct exports; no project JSON,
settings, credential or unrelated asset in output; preservation of old
exports and original site/, state, metadata and assets; no credential,
provider or deployment call. Integration creates/uploads/saves an editor,
exports a folder, reopens the app, exports another folder, and compares
both with a direct public P4 build. Existing ZIP, preview, Netlify and
other P6 routes must remain unchanged. No real user project, paid call,
deployment or browser launch.

Run Ruff, scoped formatter check, strict Pyright and all discovered Pytest;
review exact scope/imports; require latest-head hosted CI before routine
merge. Produce one P6-008 module report and stop for Tech Lead review.

## FE-05 — Explicit deferrals

P6-008 does not add a React button, open Windows Explorer, choose an
arbitrary directory, provide an API to enumerate/download/delete exports,
auto-retry, background jobs, a second export format, global settings,
installer or live-provider acceptance. UI-005 requires its own approved
contract to display/copy the returned folder path and retain ZIP export.
P6-008 alone does not complete ADR-002's usable-Windows acceptance path.

## Approval record

On 2026-10-16, the Architecture Authority replied «полностью утверждаю,
дальше» to the explicit request to approve FE-01–FE-05 in full. This includes
the local-path response exception, new-export retry semantics and 500 handling
of server-selected output faults. PC-023 compiles the exact P6-008
implementation boundary. This approval does not authorize UI-005, another
destination policy or a claim of complete usable-Windows acceptance.
