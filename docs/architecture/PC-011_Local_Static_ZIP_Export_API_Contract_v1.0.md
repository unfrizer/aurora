# AURORA — Local Static ZIP Export API Contract v1.0

Document ID: PC-011
Status: APPROVED — compiled from explicitly approved ADR-017 ZX-01–ZX-05
Module: P6-004 — Local Static ZIP Export API
Date: 2026-10-09
Authority: Architecture Authority approval of all ADR-017 decisions

## Authority and ownership

[ADR-017](ADR-017_Local_Static_ZIP_Export_API_Proposal_v1.0.md) ZX-01–ZX-05
are incorporated in full, without changing Architecture Freeze v1.0,
Master Pack v1.1 or any lower owner. P6-004 is one separate application
composition module task. Only these implementation files are authorized:

- Modify src/local_api/app.py and src/local_api/schemas.py.
- Create tests/local_api/test_site_zip_export.py and
  tests/integration/test_local_site_zip_export.py.

No other production file, existing test, dependency, workflow, frontend,
launcher or Runtime may change. The public src.local_api gateway and
create_app signature do not change. P6 may additionally import only
StaticSiteExporter and SiteExportError from the already admitted public
src.site_export gateway; the approved P1/P7/P4 gateway dependencies remain.
The existing P6/P4 import guards must pass unchanged. A private app.py
helper may share preview composition without changing preview behavior or
creating a public abstraction.

## Exact HTTP contract

Add only POST /api/v1/projects/{project_id}/exports/zip. Its strict JSON
body has exactly one required string field, expected_updated_at. Apply the
existing 2 MiB JSON body limit, exact loopback Host and Origin checks and
X-Aurora-Request: 1 mutation gate. The browser cannot supply a destination,
filename, compiled document, HTML, asset bytes or ZIP.

Under the app-instance lock, validate the project ID, load the current P1
document and compare expected_updated_at exactly with its saved metadata.
Return 409 on a mismatch before reading assets or building. Decode its
saved P7 editor; absence is invalid. Collect the brand logo and section
image references in editor order, deduplicating their first occurrence.
Read only those bytes through P1's verified asset reader, create typed
StaticSiteAsset values, project with to_static_site_document and compile
with StaticSiteBuilder. Pass only this typed P4 build to
StaticSiteExporter.export_zip.

P6 creates an invocation-owned temporary directory outside the project,
exports to a new absolute ZIP path in it, reads the complete ZIP bytes
before the response, and disposes of its own staging before success. P4
retains exact ZIP member, byte, ordering and metadata authority. Members
are at ZIP root, without a dist/ wrapper or project files. No project
site/ or exports/ write, cache, persistence, background job, network
operation or overwrite is authorized. Holding one bounded P4 artifact
in memory is the approved MVP trade-off.

Success is HTTP 200, Content-Type application/zip, a body byte-for-byte
equal to P4's ZIP, and these fixed headers:

    Content-Disposition: attachment; filename="aurora-site.zip"
    Cache-Control: no-store
    X-Content-Type-Options: nosniff
    Cross-Origin-Resource-Policy: same-origin

No CORS header is added. All failures use the existing fixed numeric-code
P6 JSON envelope. Missing project is 404; stale timestamp is 409;
missing/unsupported/malformed editor, invalid P4 draft and missing,
malformed or corrupt referenced asset are 400. Native P1 I/O, temporary
staging/read/cleanup, P4 export-stage validation or export failure and
other native failures are 500. The builder's saved-draft validation is
400, whereas exporter validation of the server-selected destination is
500. Do not expose raw exception text, local paths, project content,
prompt, secrets or ZIP bytes on failure. A failed request must not
mutate saved state or overwrite an existing artifact.

## Acceptance gate

Create the two authorized test files only. Use temporary P1 projects,
synthetic raster signatures, fake credentials, P6 TestClient and P4 ZIP
inspection. Cover strict request shape, Host/Origin/header and body limits;
404/409 precedence; invalid editor/draft/referenced asset and native
staging/cleanup/export failures; fixed error envelopes and no leakage.
Assert repeated ZIP byte identity, root member names and contents, absence
of project/settings/credential files, no project site/exports writes, no
temporary residue and unchanged existing routes.

Integration must create, upload an asset, save an editor, ZIP, reopen and
ZIP through public HTTP, then compare with the public P4 exporter using
temporary files only. No real user project, paid AI, deploy or browser
launch. Run Ruff, scoped formatter check, strict Windows/Linux Pyright,
full discovered Pytest, exact scope/import review and latest-head hosted
CI. Produce one P6-004 module report and stop for Tech Lead review.

## Deferrals

Folder export, deployment HTTP, structured one-prompt/image generation,
global settings, React/Vite workspace and Windows launcher require
separate decisions and module tasks. P6-004 alone does not satisfy
ADR-002 usable-Windows acceptance.
