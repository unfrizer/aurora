# AURORA — Local Static-Site Preview Contract v1.0

Document ID: PC-010
Status: APPROVED — compiled from ADR-016 SP-01–SP-05
Module: P6-003 — Local Static-Site Preview API
Date: 2026-10-08
Authority: explicit Architecture Authority approval of ADR-016

## Boundary and exact ownership

This is a separate implementation task under the existing P6 application
owner, not an L0–L8 Runtime, site compiler, project repository or frontend.
ADR-016 SP-01–SP-05 are normative. P6-003 may:

- modify src/local_api/app.py only among production files;
- create tests/local_api/test_site_preview.py and
  tests/integration/test_local_site_preview.py;
- add only "src.site_export" to the existing P6 allowed-import set in
  tests/local_api/test_security.py;
- add only src/local_api/app.py as another public src.site_export
  consumer in tests/site_export/test_models.py, preserving P5 and P7
  admissions and all private/lower-owner prohibitions.

No other existing test, source file, dependency, workflow, Runtime or
frontend file may change in the P6-003 implementation task. The public
src.local_api gateway and exact create_app signature remain unchanged.
This contract and the narrow PC-004/PC-006 clarifications are governance
records, not a license for additional implementation files.

The only new production import is the public src.site_export gateway:
StaticSiteAsset, StaticSiteBuilder and SiteValidationError. P6 continues
to use public src.projects and src.editor gateways and the previously
approved Foundation ValidationError mapping. It imports no P4 private
module, P5 deployer, concrete Kernel/Platform Runtime, frontend or
provider. No lower owner imports P6.

## Exact HTTP surface

Add only:

    GET /api/v1/projects/{project_id}/preview/{file_path:path}

The route returns status 200 and the bytes of exactly one P4
StaticSiteBuild member whose relative path equals the decoded
file_path in full. The intended entry is preview/index.html.
Relative P4 page, CSS and raster references resolve below this prefix.
There is no route for arbitrary P1 files, listing, raw editor state,
caller-supplied HTML/CSS, build manifest or artifact download.
Unknown, empty and unsafe/nonmember file paths return the fixed 404.

Inside the existing per-app project lock, P6 validates the project ID
with its existing validator and loads the current P1 ProjectDocument.
It decodes the saved P7 editor via load_editor_state; absence is an
invalid uninitialized preview, not an empty publishable site. It
collects non-null brand logo and section image references in editor
order, deduplicated by first appearance, and obtains each byte sequence
solely through ProjectRepository.read_asset. It creates immutable
StaticSiteAsset values, calls to_static_site_document(editor, assets),
and passes that detached typed document to StaticSiteBuilder.build.
It selects the requested file only from the completed build. P6 never
opens an asset path, compiles HTML itself, silently repairs draft
fields, loads unused assets or writes project/site/export state.

Each GET rebuilds from the latest saved P1 state. There is no cache,
background task, global mutable state or persistent preview artifact.
The app lock protects same-instance mutation interleaving only; no
cross-process snapshot or performance guarantee is claimed. P1
retains project-path and asset-integrity authority, P7 retains editor
schema/projection authority, and P4 retains build validation, safe
paths, escaping and capacity authority.

## Representation, security and errors

Preserve the existing loopback Host validation, no CORS and mutation
Origin/header rules. This GET does not require Origin or
X-Aurora-Request, matching existing P6 GET semantics. A successful
response has exact bytes from P4, no-store caching, nosniff and
same-origin cross-origin-resource policy. Use text/html with UTF-8
charset for .html, text/css with UTF-8 charset for assets/site.css,
and image/png, image/jpeg, image/gif or image/webp for the corresponding
managed raster asset. P4 is the file membership authority; MIME is
derived only from a member's canonical extension, never request input
in isolation.

HTML additionally receives this restrictive CSP:

    default-src 'none'; style-src 'self'; img-src 'self'; script-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; frame-ancestors 'self'

No script, network connection or form submission is permitted from a
generated page. The later workspace client may embed it in a sandboxed
same-origin frame, but frontend implementation is not part of P6-003.

Use only P6's existing fixed JSON error envelope with numeric status.
Missing project and nonmember build path are 404. Missing, unsupported
or malformed P7 editor, invalid P4 build, malformed or missing/corrupt
referenced P1 asset are 400. Native P1 I/O failures are 500. A valid
project is loaded before referenced assets so an absent project is
unambiguously 404; P1 FileNotFoundError during a referenced asset read
is an invalid preview and maps to 400. No local path, project content,
asset bytes, secret or raw exception string is returned or normally
logged. Existing P6 routes, statuses and body limits are unchanged.

## Acceptance gate

Use temporary P1 projects, synthetic raster bytes, fake credentials
and FastAPI TestClient. Required behavioral tests cover:

- RU and EN saved editors, homepage and secondary-page HTML/navigation,
  exact P4 CSS and raster bytes, deterministic reopen/rebuild;
- exact Content-Type, cache, nosniff, same-origin and HTML CSP headers;
- absent, malformed and unsupported editor state and P4-invalid draft;
- missing/corrupt/malformed referenced assets and missing project;
- unknown, unsafe and nonmember preview paths with no file escape;
- fixed 400/404/500 envelopes without private data or unexpected
  project/asset mutation;
- existing P6 Host/Origin/header/body controls and route compatibility;
- P4 builder invocation through the public gateway and integration
  entirely through public HTTP/P1/P7/P4 contracts.

No real user project, credential mutation, paid API call, provider
network, browser launch or deployment. Run Ruff, scoped formatter
check, strict Windows/Linux Pyright, full discovered Pytest, scope/import
review and latest-head hosted CI. Produce one P6-003 module report and
stop for Tech Lead review.

## Deferred modules

Build manifest, folder/ZIP export HTTP, deployment HTTP, one-prompt
structured and image generation, global settings, React/Vite workspace
and Windows launcher need separate approved contracts. Passing P6-003
does not establish ADR-002 usable-Windows acceptance.
