# AURORA — Local Static-Site Preview Proposal v1.0

Document ID: ADR-016
Status: APPROVED — SP-01–SP-05 explicitly approved by Architecture Authority
Date: 2026-10-08
Proposed module: P6-003 — Local Static-Site Preview API
Repository baseline: 38c9442c4a5f951f810564454d144c4c15502733

## Decision boundary

The Architecture Authority explicitly approved SP-01–SP-05 in full in the
project conversation on 2026-10-08. This decision authorizes compiling
PC-010 and a separate P6-003 implementation task under that contract; it
does not waive the module acceptance gate or Tech Lead review.
Architecture Freeze v1.0, Master Pack v1.1, ADR-002 and all approved
PC-series contracts remain in force. The frozen L0–L8 ownership and
dependency direction are unchanged.
The full Freeze and Master Pack are not present in this checkout; this
ADR does not claim to replace them or certify an unverified conflict away.

P1 owns project and verified asset bytes. P7 owns the editor payload and
its pure projection to a typed P4 document. P4 owns compilation to a
self-contained static build. P6 already serves the local application API,
but its approved contracts do not let it import P4 or serve a built site.
A new public HTTP behavior and narrow import-test admission are needed.

## SP-01 — Owner, files and dependency direction

Propose a separate P6-003 application-composition task. It would modify
only src/local_api/app.py; add tests/local_api/test_site_preview.py and
tests/integration/test_local_site_preview.py; and make the two exact
test-admission corrections below. No P1, P4, P7, Kernel, Runtime,
frontend, dependency or launcher production file changes. The public
create_app signature and src.local_api gateway remain unchanged.

P6 would additionally import only the public src.site_export gateway
for the P4 immutable asset model, builder and sanitized validation error.
It would continue using public src.projects and src.editor gateways.
P1, P4, P7 and lower Runtime owners never import P6. There is no new
Runtime, persistence owner, DI scope, global cache, worker or provider.

The test corrections are limited to:

1. Add only "src.site_export" to the P6 approved-import set in
   tests/local_api/test_security.py, retaining every other assertion.
2. Admit only src/local_api/app.py as another public src.site_export
   consumer in tests/site_export/test_models.py, retaining the existing
   P5 and P7 consumers and all private-P4/lower-layer prohibitions.

PC-010 records this file/import boundary. PC-004 and PC-006 receive
only the corresponding narrow clarifications.

## SP-02 — Read-only same-origin preview

Propose one new route:

    GET /api/v1/projects/{project_id}/preview/{file_path:path}
    Success: 200 bytes of exactly one compiled P4 file

The client opens preview/index.html in a same-origin sandboxed workspace
frame. P4-generated relative page, stylesheet and raster references
resolve under the same preview prefix. There is no arbitrary project-file
endpoint, directory listing, preview of raw editor JSON or caller-supplied
HTML/CSS.

For each request, P6 validates the project ID, loads the current P1
document, requires a supported P7 editor payload, collects the editor's
referenced logo and section raster paths once in deterministic order,
and reads each byte sequence through P1. P6 constructs immutable P4
StaticSiteAsset values, uses P7's to_static_site_document, then calls
StaticSiteBuilder.build. It returns bytes only when file_path exactly
matches a member of that compiled build. P4 remains the authority for
publishability, safe site paths, HTML escaping and build limits; P1
remains the project-path and asset-integrity authority. P6 does not
repair an invalid draft or follow a browser-provided filesystem path.

The existing app-instance project lock covers load, asset reads and build
so same-instance editor/asset mutations cannot interleave. This does not
assert cross-process snapshot consistency. Preview is rebuilt from the
latest saved state per request, with no persistent or global cache. It
does not write site/, exports/ or project state and does not run a
background build. Repeated compilation is an explicit MVP performance
trade-off, not a promise of cached asset delivery.

## SP-03 — HTTP, security and error policy

Preserve P6's loopback Host validation, no CORS and fixed numeric-code
error envelope. GET requires neither Origin nor a mutation header,
consistent with existing P6 GET routes. Serve only P4 build members,
never P1 raw files by a supplied preview path. Use canonical Content-Type
for HTML, CSS and the four P1 raster formats, plus Cache-Control: no-store,
X-Content-Type-Options: nosniff and Cross-Origin-Resource-Policy:
same-origin. HTML also receives a restrictive Content-Security-Policy
allowing only same-origin CSS/images and no script, connections, forms
or base URL override. No generated page is granted API mutation
capability by this route.

Missing project or nonmember compiled path returns 404. Absent,
unsupported or malformed editor state, invalid P4 draft, malformed
referenced asset and missing/corrupt referenced asset return 400.
Native P1 I/O failure returns 500. Only fixed numeric codes reach the
client; no project content, local path, asset bytes, secrets or raw
exception text appear in error responses or normal logs. No live
provider or deployment call occurs.

## SP-04 — Acceptance evidence

Use temporary P1 projects and synthetic raster bytes. Test saved RU
and EN editor states, homepage and secondary-page navigation, CSS
and raster responses, deterministic bytes across reopen, exact MIME
and security headers, empty/malformed editor, unbuildable drafts,
missing/corrupt raster, unknown/unsafe preview member, missing project,
native I/O sanitation and no mutation of project state or assets.
Assert that P4's builder is the actual compiler and P6 never serves
arbitrary files or uncompiled content. Existing P6 routes and their
Host/Origin/body controls remain unchanged. Integration uses public
HTTP, P1, P7 and P4 gateways only; no real project, credential,
network, provider, browser or Netlify operation.

Require Ruff, strict Windows/Linux Pyright, full discovered Pytest,
scoped format check, diff/import review and latest-head hosted CI.
The P6-003 module report then stops for Tech Lead review.

## SP-05 — Explicit deferrals

This module does not create a build manifest endpoint, cache, artifact
repository, folder/ZIP download, deployment endpoint, global settings,
image generation, one-prompt structured generation, React/Vite client
or Windows launcher. Those need separate approved contracts. The
ADR-002 usable-Windows acceptance path remains incomplete.

## Approval record and next gate

The Architecture Authority replied "утвеждаю полностью, продолжай" to
the explicit request to approve SP-01–SP-05 together. PC-010 may compile
this decision without changing its proposed route, error mapping or file
ownership. P6-003 code may begin only in its separate module task after
PC-010 is approved and available on the implementation baseline. A
different route, security policy, owner or response mapping needs a new
decision; source code cannot supply that authority.
