# AURORA — Local Netlify Deploy API Proposal v1.0

Document ID: ADR-018
Status: DRAFT — Architecture Authority decision required
Date: 2026-10-09
Proposed module: P6-005 — Local Netlify Deploy API
Repository baseline: 8877bc9cd219e950c2b8c8f5ce6b44e85af3a35b

## Decision boundary

ADR-002 approves Netlify as the sole integrated MVP deployment target.
PC-005 already approves the outbound P5 NetlifyDeployer with a typed P4
build, explicit site creation/redeploy, bounded polling and safe partial-
failure identifiers. PC-006 owns the same-origin P6 HTTP boundary.
PC-010/011 already compose a saved P7 editor and verified P1 assets into
a P4 build for preview and ZIP. None of these contracts approves a browser-
facing deployment route, a public response or the handling of a partially
completed external side effect. This proposal supplies those decisions
without changing L0–L8, P1/P2/P4/P5/P7 ownership or the public P5 API.

The full Architecture Freeze v1.0 and Master Pack v1.1 are not present
in this checkout. This DRAFT cannot substitute for them or authorize code.
The proposed decisions ND-01–ND-05 form one separate P6 module task.
No real Netlify request, token read, site creation or deploy occurs while
preparing or testing the proposal.

## ND-01 — P6 ownership and exact file scope

Propose these implementation files only:

    src/local_api/app.py
    src/local_api/schemas.py
    tests/local_api/test_netlify_deploy.py
    tests/integration/test_local_netlify_deploy.py
    tests/local_api/test_security.py

The first two existing source files may change; the next two tests are
created. The existing test_security.py may add only "src.deployment"
to its approved public-gateway import set, preserving every other import
rule. P6 may import NetlifyDeployer and NetlifyDeployError only from the
public src.deployment gateway. P6 continues to use the approved public
P1/P2/P7/P4 gateways and no P5 private file. No P1/P2/P4/P5/P7 source or
test, existing P6 test other than the one guard, dependency, workflow,
frontend, launcher or Runtime changes. The public src.local_api gateway
and create_app signature remain unchanged. Private P6 composition may
be shared with preview/ZIP without changing those routes' behavior.

After approval, compile PC-012 and narrowly clarify PC-005/PC-006.
An HTTP route is not a new P5 API or an L0–L8 Runtime.

## ND-02 — Explicit same-origin deploy command

Propose exactly:

    POST /api/v1/projects/{project_id}/deployments/netlify
    Strict JSON body:
      expected_updated_at: string, required
      confirm_deploy: literal true, required
      site_id: canonical lowercase UUID string or null, optional
    Success: 200 JSON
      {"site_id": string, "deploy_id": string, "public_url": HTTPS string}

Absent/null site_id deliberately creates a new Netlify site; a canonical
site_id deliberately redeploys that site. P6 validates a supplied site_id
against PC-005's canonical UUID format before any network effect.
The caller cannot supply a token, API host, ZIP, path, HTML, asset bytes,
project state or arbitrary build. A false/missing confirm_deploy is 400.
The existing exact loopback Host, same-origin Origin, X-Aurora-Request: 1
and 2 MiB JSON body gates apply. No CORS is added. The command is never
called on import, app construction, project save, preview or ZIP export.

Under the existing app-instance lock, P6 validates the project ID, loads
P1, checks expected_updated_at exactly and obtains the configured P2
netlify_token. A stale timestamp returns 409 before credential read,
asset read, build or network. Missing token returns 409 before build or
network. P6 then decodes the saved P7 editor, reads only deduplicated
referenced assets through P1 and builds a detached typed P4 artifact as
PC-010/011 do. Invalid editor/draft/asset is 400. P6 releases the app
lock after this snapshot and before the synchronous P5 network call.
The deployed artifact is this accepted snapshot; a later editor change
does not mutate it. No cross-process snapshot guarantee is claimed.

P6 constructs NetlifyDeployer with the retrieved token and calls
deploy(build, site_id=...). P5 alone owns temporary ZIP staging,
Netlify HTTP, polling, result validation and sanitized adapter errors.
No project site/exports write, cached artifact, background job,
automatic retry, project-to-site binding or persistence is added.
The route may block its request worker for P5's bounded synchronous
operation; it must not hold the app lock while waiting on Netlify.

## ND-03 — Partial failure recovery and PC-006 exception

PC-006 currently mandates the exact error body
{"error":{"code": <HTTP status>}} for every route. P5 may know a site_id
and/or deploy_id after remote creation/upload even if ready is not
confirmed. Discarding those IDs would make a safe retry ambiguous:
another request with site_id=null could create another remote site.

Propose one narrow exception for this new route only. When P5 raises
NetlifyDeployError with at least one known, P5-validated ID, return:

    {"error":{"code": <HTTP status>,
              "recovery":{"site_id": string|null,
                          "deploy_id": string|null}}}

When neither ID is known, preserve the existing exact numeric envelope.
The recovery object contains only these two validated identifiers: no
token, URL, provider body, local path, project data or exception text.
The P6 error middleware must preserve this narrowly constructed response
only for this route, while keeping every existing route's sanitization
unchanged. Approval of ND-03 is an explicit, route-limited amendment of
PC-006; without it P6-005 must STOP, not silently change the envelope.

No failed or uncertain POST is retried automatically. A returned ID is
information for a later deliberate UI recovery action, not proof of
success or a durable project/site binding. If an uncertain remote effect
occurred before an ID was received, the API cannot reconstruct it; the
user must inspect Netlify directly before attempting another new-site
deploy. This limitation must be visible in later UI instructions.

## ND-04 — Fixed failure mapping and safety

Preserve numeric-code JSON and no raw errors. Proposed status mapping:

- Invalid request, noncanonical site_id or invalid P7/P4 saved draft or
  referenced asset: 400.
- Missing project: 404. Stale timestamp or missing Netlify token: 409.
- P2 native credential failure: 503.
- P5 auth, remote, protocol or terminal failed: 502.
- P5 rate_limit or transport: 503; P5 timeout: 504.
- P5 validation/export-stage failure from the server-composed build,
  native P1 I/O and other unexpected server failures: 500.

P6 validates browser site_id itself before P5 so a P5 validation failure
cannot be mistaken for malformed browser input. A Netlify 401/403 is not
local AURORA authentication and therefore is not translated to HTTP 401.
No fixed error may include raw provider response, token, prompt, project
state, ZIP bytes or private path. Existing preview, ZIP, credentials,
generation and project route behavior remains unchanged.

## ND-05 — Tests, gate and deferrals

Use temporary P1 projects, synthetic rasters, fake P2 credentials, fake P5
deployer/network and FastAPI TestClient. No live Netlify request, real
credential read, production project or browser launch. Cover exact
request/confirmation/site-ID shape, Host/Origin/header/body gates,
stale-before-credential/build/network precedence, missing token,
invalid editor/draft/asset, P5 invocation with the typed build,
new-site and existing-site success, result fields, all fixed failure
statuses, known-ID recovery envelope, unknown-ID original envelope,
no token/response leakage, no retry or project mutation, and continued
behavior of existing routes. Integration uses public P1/P7/P4/P6
interfaces with a fake P5 boundary only.

Run Ruff, scoped formatter check, strict Windows/Linux Pyright, full
discovered Pytest, exact scope/import review and latest-head hosted CI.
Produce one P6-005 module report and stop for Tech Lead review.

No project-to-site persistence, automatic retry/reconciliation, live
deployment, Netlify OAuth/public distribution, folder export, React/Vite
workspace, Windows launcher, structured one-prompt/image generation or
global settings is authorized here. P6-005 alone does not meet the
ADR-002 usable-Windows acceptance path.

## Decision requested

The Architecture Authority must approve, revise or reject ND-01–ND-05,
especially the route-limited PC-006 recovery-envelope exception and
the no-automatic-retry/unknown-ID limitation. Until then this document
is DRAFT. No PC-012 compilation or P6-005 implementation is authorized.
