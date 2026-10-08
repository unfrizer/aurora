# AURORA — Local Application API Contract v1.0

**Document ID:** PC-006
**Status:** APPROVED — compiled from ADR-012 A-01–A-06
**Module:** P6-001 — Local FastAPI Application API Foundation
**Date:** 2026-10-08

## Authority and scope

[ADR-012](ADR-012_Local_Application_API_Proposal_v1.0.md) is incorporated
in full. The Architecture Authority explicitly approved A-01–A-06 on
2026-10-08. AGENTS, ADR-001/002/003 and PC-001/002/003 remain in force.
P6 is application composition, not an L0–L8 Runtime. It provides a testable
FastAPI app factory; it does not start a server or ship a Windows UI.

## Exact ownership and imports

P6-001 may change only `src/local_api/__init__.py`, `app.py`, `schemas.py`;
`tests/local_api/__init__.py`, `test_app.py`, `test_security.py`;
`tests/integration/test_local_api.py`; and P6 dependency declarations in
`pyproject.toml` with the matching `uv.lock` update. ADR-012 and this
contract are the only architecture-document changes in the module task.

`src.local_api` exports exactly `create_app` with the ADR-012 signature.
For P6-001, the app may use standard library, FastAPI/Pydantic, and the public package
gateways for P1, P2 and P3. Its schema types are private implementation
details. No concrete Kernel/Platform Runtime, private P1–P5 file, P4/P5
service, frontend, generic provider registry or upward lower-layer import.
No change to existing owners or their tests.

## HTTP and state boundary

The initial ten exact routes, methods, request fields, success statuses and semantic
owners in ADR-012 A-02 are normative. All paths have the `/api/v1` prefix.
P1 metadata arrays preserve the five metadata fields. A project document is
`{"metadata": {five metadata fields}, "state": object}`; no filesystem
path is exposed. The P3 terminal-job
projection has `job_id`, `status`, `result` or `failure`: a completed
result includes only `response_id`, `model`, `output_text`; a failed
result includes only `category`, `message`, `retryable`. It omits the
P3 request snapshot, prompt, instructions and credential.

P6 creates projects with empty state. On save it loads the current document
under its app-instance lock, validates `expected_updated_at`, retains
server-owned ID/format/creation time, and delegates to P1. A mismatched
timestamp is `409`. The API does not claim cross-process concurrency control
or recovery from P1's interrupted two-file commit. Known credential key names
are rejected at any depth of project state. P1 remains the persistence
validator and owner; P6-001 does not reinterpret state as an editor/site schema.

## Security and errors

ADR-012 A-03 is normative: validate exact loopback origin/Host; no CORS;
require same-origin `Origin` and `X-Aurora-Request: 1` on mutations;
require JSON media type on P6-001 body-bearing routes and cap raw bodies at 2 MiB
before effect. API construction has no I/O or provider/credential side effect.
All failures use a fixed JSON envelope `{"error":{"code": <HTTP status>}}`,
using the approved status mappings in A-04. Numeric HTTP status is the stable
code; no additional public error vocabulary is introduced. Validation and
framework-generated errors are sanitized, with no user input in response
or normal log. Secrets are accepted only on explicit PUT and never echoed.
The future launcher alone binds the socket, supplies the root/origin and
serves same-origin UI under a later contract. No actual user project or
credential mutation is part of P6 test execution.

## Dependency and acceptance gate

Add FastAPI as an application dependency and HTTPX as a dev/test dependency
using uv. Do not add Uvicorn, a UI toolchain, image-generation client, worker,
or another provider in P6. Tests use temporary projects, fake credentials
and fake P3 network; no real secret, paid request, Netlify deploy or browser.
Cover the ADR-012 A-06 matrix without skips/xfail. Run Ruff, strict Pyright
on Windows and Linux modes, full discovered Pytest, and inspect the exact
diff. Latest-head hosted CI is required before any routine merge. Produce
one P6 module report and stop for Tech Lead review. P6 success is not
ADR-002 usable-Windows acceptance.

## Approved P6-002 Extension

ADR-015 EA-01–EA-05 explicitly approves editor-aware save and project
raster transport as a separate task under the same P6 application owner.
PC-009 is its implementation contract. It adds only the four routes
specified there and permits P6 to import the public `src.editor`
gateway while retaining the existing P1/P2/P3 boundaries. The
approved raw-image POST alone has a 16 MiB body and one canonical
raster Content-Type; every existing JSON route retains this contract's
2 MiB media-type and body limit. Existing routes, `create_app`
signature, error envelope, same-origin/Host protection and app-local
locking remain unchanged. P6-002 does not approve P4/P5 imports,
site build/export/deploy routes, new dependencies or another Runtime.
The Architecture Authority subsequently approved one test-admission
corrections: `tests/local_api/test_security.py` may add only
`"src.editor"` and `"src.core.exceptions"` to its approved-import
set while preserving every other AST rule. The latter permits only
Foundation `ValidationError` for P1 validation-to-400 translation.
PC-009 lists the exact implementation file boundary.

## Approved P6-003 read-only preview extension

ADR-016 SP-01–SP-05 approves a separate P6-003 task for one GET
static-site preview route, compiled exactly in PC-010. P6 may
additionally import only the public src.site_export gateway for
StaticSiteAsset, StaticSiteBuilder and SiteValidationError. Its
existing create_app signature, routes, fixed error envelope,
loopback/Host controls, mutation Origin/header rules and body limits
remain unchanged. Preview is read-only and rebuilds from saved P1
state through P7 and P4 without an artifact cache or project write.
The only P6 test-guard correction is adding "src.site_export" to
tests/local_api/test_security.py's allowed-import set while retaining
all other assertions. PC-010 names the complete implementation scope.
This approval does not include export/deploy HTTP, a frontend or a
Windows launcher.
