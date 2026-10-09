# AURORA — Local Static ZIP Export API Proposal v1.0

Document ID: ADR-017
Status: APPROVED — Architecture Authority approved ZX-01–ZX-05
Date: 2026-10-09
Proposed module: P6-004 — Local Static ZIP Export API
Repository baseline: 9bd669979be0513fb8b541de647d3fc8ce39fb9f

## Decision boundary

This decision authorizes compilation of the exact PC-011 implementation contract. ADR-002
requires a downloadable static site, and P4 already produces a
deterministic ZIP from a typed build. P6-003 can preview a saved editor
site, but no approved P6 contract may expose a ZIP through HTTP.
This new public route, response body, staging and failure behavior
need a decision. Architecture Freeze v1.0, Master Pack v1.1 and all
approved owner boundaries remain unchanged. The full Freeze and
Master Pack are not in this checkout; this draft does not replace them.

The proposed decisions ZX-01–ZX-05 form one narrow P6 module task.
They do not imply that a saved draft is automatically publishable or
that the Windows MVP is already usable.

## ZX-01 — Ownership, files and imports

P6-004 would extend only the existing local application-composition
owner. Proposed implementation scope:

    src/local_api/app.py
    src/local_api/schemas.py
    tests/local_api/test_site_zip_export.py
    tests/integration/test_local_site_zip_export.py

The first two files may be modified; the two tests would be created.
No P1/P4/P7 production file, existing test, dependency, workflow,
Kernel/Runtime, frontend or launcher file may change. The exact
create_app signature and public src.local_api gateway remain unchanged.

P6 may additionally import only StaticSiteExporter and SiteExportError
from the already admitted public src.site_export gateway. It continues
using public P1, P7 and P4 gateways, never private implementation files.
The P6 and P4 import-guard tests already admit this public dependency;
they must pass unchanged. No lower owner imports P6. Within app.py,
a private P6 helper may share the approved load → asset read → P7
projection → P4 build path with P6-003, without changing preview
behavior or adding a public abstraction.

After approval, compile PC-011 and make only narrow PC-004/PC-006
documentation clarifications. A product HTTP route is not a P4
exporter API change.

## ZX-02 — Explicit same-origin ZIP download

Propose exactly one new route:

    POST /api/v1/projects/{project_id}/exports/zip
    JSON body: {"expected_updated_at": <string>}
    Success: 200 application/zip

The JSON body has exactly that one field, uses P6's strict schema,
and remains under the existing 2 MiB JSON body limit. The existing
Host, exact Origin and X-Aurora-Request: 1 mutation gates apply.
No caller-provided destination, filename, HTML, asset bytes or ZIP
may enter this route.

Under the existing app-instance lock, P6 validates the project ID,
loads the current P1 document, and compares expected_updated_at to
the saved metadata exactly as existing P6 save routes do. A mismatch
returns 409 before reading assets or building. P6 then uses the same
saved-editor and referenced-asset composition approved by PC-010:
P1 verified bytes, P7 typed projection, P4 StaticSiteBuilder build.
It passes only that P4 build to StaticSiteExporter.export_zip. This
does not accept arbitrary StaticSiteBuild objects from the browser.

Use an invocation-owned temporary directory outside the project.
Export to a new absolute path below it, read the completed ZIP bytes
before returning a response, and dispose of only that temporary
staging area before sending success. P4's exclusive output and exact
ZIP member/order/metadata rules remain the artifact authority. The
ZIP contains the compiled site members at its root, with no dist/
wrapper, project JSON, settings, prompts or credential. No project
site/ or exports/ write, persistent artifact, cache, background job
or network operation occurs. A single response holds the bounded
P4 artifact bytes in memory; this is an explicit MVP memory trade-off,
not an unbounded streaming or crash-transaction claim.

## ZX-03 — Response and failure policy

Success uses a fixed download name independent of project input:

    Content-Type: application/zip
    Content-Disposition: attachment; filename="aurora-site.zip"
    Cache-Control: no-store
    X-Content-Type-Options: nosniff
    Cross-Origin-Resource-Policy: same-origin

No CORS header is added. The response body is byte-for-byte the P4
ZIP output; P6 does not rewrite members or alter compression metadata.

Missing project returns 404; stale expected timestamp returns 409;
missing/unsupported/malformed editor, invalid P4 draft or referenced
asset returns 400. P1 native I/O, temporary staging/read/cleanup,
P4 export-stage failure and other native failures return 500.
An exporter validation failure at the staging boundary is 500 because
the destination is server-selected, not user-supplied; P4 builder
validation of the saved draft remains 400. All errors use P6's fixed
numeric-code JSON envelope and reveal no local path, ZIP bytes, project
state, prompt, token or raw exception text. A failed request cannot
overwrite a prior export or mutate saved project state.

## ZX-04 — Tests and validation

Use tmp_path projects, synthetic raster signatures, fake credentials,
P6 TestClient and deterministic P4 ZIP inspection. Test exact request
shape, Host/Origin/header and existing 2 MiB body controls; missing
project, stale timestamp before build, malformed editor, bad draft,
missing/corrupt asset, native staging and cleanup errors; fixed
errors and no data leakage. Verify byte-identical repeated ZIPs,
member list/bytes at root, no project/settings/credential files,
no project site/exports writes, no temp staging residue, and unchanged
preview and other P6 routes. Integration must create → upload → save
editor → ZIP → reopen → ZIP through public HTTP, and compare with the
public P4 exporter using temporary files only. No real user project,
paid AI request, deployment or browser launch.

Run Ruff, scoped formatter check, strict Windows/Linux Pyright, full
discovered Pytest, scope/import review and latest-head hosted CI.
Produce one P6-004 module report and stop for Tech Lead review.

## ZX-05 — Explicit deferrals

Folder export still needs a separate decision on user-selected
destination and consent. Netlify deployment HTTP, structured
one-prompt and image generation, global settings, React/Vite workspace
and Windows launcher remain separate approved-contract tasks. The
P4 exporter remains directly usable by approved application callers;
this proposal adds only a browser-facing ZIP download path. Passing
P6-004 alone does not meet ADR-002 usable-Windows acceptance.

## Approval record

On 2026-10-09 the Architecture Authority replied «полностью утверждаю,
дальше» to the request to approve ADR-017 ZX-01–ZX-05. All five decisions
are approved without amendment. PC-011 compiles their exact P6-004
implementation boundary. This approval does not replace the missing full
architecture volumes, waive latest-head validation, or approve a later
implementation PR before its required review and checks.
