# AURORA — Local Static Folder Export API Contract v1.0

- Document ID: PC-023
- Status: APPROVED — compiled from explicitly approved ADR-029 FE-01–FE-05
- Module: P6-008 — Local Static Folder Export API
- Date: 2026-10-16
- Authority: Architecture Authority approval of FE-01–FE-05

## Authority and exact ownership

ADR-029 FE-01–FE-05 are incorporated in full. P6 is application composition;
P1 retains project identity and path ownership, P7 retains saved-editor
projection and P4 retains build and artifact writing. Only these
implementation and acceptance files are authorized:

```text
src/local_api/app.py                               # modify
src/local_api/schemas.py                           # modify
tests/local_api/test_site_folder_export.py         # create
tests/integration/test_local_site_folder_export.py # create
```

The ADR-029 approval record, this contract and PC-006's narrow extension
note are the only architecture-document changes. No existing test, public
src.local_api gateway, create_app signature, P1/P4/P7 file, dependency,
lockfile, workflow, frontend, launcher or other production file may change.
P6 uses only existing public P1/P7/P4 gateways. A private P6 helper may share
the saved-site composition only if all existing routes retain their approved
behavior. No public service, global state, worker or new Runtime is approved.

## Exact HTTP operation

Add only `POST /api/v1/projects/{project_id}/exports/folder`. Its strict JSON
body contains exactly required `expected_updated_at: str` and
`confirm_export: Literal[True]`; the latter accepts literal JSON true only.
Existing 2 MiB JSON, exact loopback Host and Origin, and
`X-Aurora-Request: 1` mutation gates apply. No client-chosen destination,
filename, source HTML, site bytes, state or arbitrary path is accepted.
Malformed requests create no artifact. A future UI must ask for explicit
confirmation; merely opening Export/Deploy must not call this route.

Under the existing app-instance lock, validate project ID, load the P1
document, and compare the expected timestamp exactly with saved metadata.
Return 409 before asset reads, build or export-parent lookup on mismatch.
Decode only the saved P7 editor; an absent, unsupported or malformed editor
is invalid. Collect logo and section raster references in editor order with
first-occurrence deduplication, read verified bytes through P1, project
through P7 and compile through P4 exactly as the approved ZIP route does.

Only after successful build, call public
`ProjectRepository.export_directory(project_id)`. Select one new child
`aurora-site-<lowercase-uuid4>` beneath that validated parent and pass the
typed build and absolute child to `StaticSiteExporter.export_folder`.
P4 writes exclusively; there is no overwrite or automatic collision retry.
The response is built while the app lock is held. This does not promise
cross-process serialization or crash durability. No project site/ write,
saved-state change, provider/credential/network call, ZIP staging or deploy
occurs. Each confirmed call is a new export, so an uncertain lost response
must not be silently retried; the user can inspect exports/ or deliberately
request another export.

## Success and failure boundary

Return `201 application/json` with exactly one field,
`{"folder_path": <absolute native path string>}`. This is the sole approved
exception to PC-006's no-project-path response rule. Disclose the path only
in this same-origin confirmed success body, never in URL, redirect, cookie,
normal log, error response, project state or provider request. Add exactly
these safety headers (and no CORS or Location header):

```text
Cache-Control: no-store
X-Content-Type-Options: nosniff
Cross-Origin-Resource-Policy: same-origin
Referrer-Policy: no-referrer
```

All errors retain P6's fixed numeric `{"error":{"code": <status>}}`
envelope. Missing project is 404; stale timestamp is 409; missing,
unsupported or malformed saved editor, invalid site projection and
missing/malformed/corrupt referenced raster are 400. Invalid P1 export
directory, native I/O, P4 destination validation/collision/export and other
server-selected output failures are 500. No raw exception, path, content or
credential enters an error response. P4 owns invocation-created best-effort
cleanup. P6 must not recursively remove exports/, prior/unknown children or
an incomplete partial child. A failure may leave a recognizable partial
child but cannot overwrite a prior export or mutate saved project contents.

## Acceptance and deferrals

Use temporary P1 projects, synthetic raster bytes, fake credentials,
FastAPI TestClient and public P4 services. Exercise strict body and request
gates; 404/409 precedence; invalid editor/site/asset; unsafe/missing P1
export directory; native, P4, collision and incomplete-cleanup faults; exact
safe response and error headers; unique child names and deterministic bytes;
no project/settings/secret/unrelated asset leakage; unchanged project data,
old exports and site/; no provider calls. Integration creates/uploads/saves,
exports, reopens the app, exports again and compares with a direct P4 build.
Existing ZIP, preview, Netlify and other P6 routes remain unchanged.

Run Ruff, scoped formatter check, strict Pyright and full discovered Pytest;
inspect exact file/import scope and latest-head hosted CI before routine
merge. Produce one P6-008 module report and stop for Tech Lead review.
No real user project, paid provider call, deploy or browser launch.

UI-005 remains a separate approved-contract task. This module does not add
React/Explorer UI, arbitrary destinations, export enumeration/download/
deletion, background work, auto-retry, settings, installer, live-provider
acceptance or complete ADR-002's usable-Windows path.
