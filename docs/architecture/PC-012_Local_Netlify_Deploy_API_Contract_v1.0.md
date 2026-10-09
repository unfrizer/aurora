# AURORA — Local Netlify Deploy API Contract v1.0

Document ID: PC-012
Status: APPROVED — compiled from explicitly approved ADR-018 ND-01–ND-05
Module: P6-005 — Local Netlify Deploy API
Date: 2026-10-09
Authority: Architecture Authority approval of all ADR-018 decisions

## Authority and exact ownership

[ADR-018](ADR-018_Local_Netlify_Deploy_API_Proposal_v1.0.md) ND-01–ND-05
are incorporated in full. P6-005 is a separate P6 application-composition
task, not a Runtime, P5 change or license to make live test deployments.
Only these implementation files are authorized:

- Modify src/local_api/app.py and src/local_api/schemas.py.
- Create tests/local_api/test_netlify_deploy.py and
  tests/integration/test_local_netlify_deploy.py.
- Modify tests/local_api/test_security.py only to add "src.deployment"
  to its public-gateway allowed-import set.

No other production file, existing test, dependency, workflow, frontend,
launcher or lower owner may change. P6 may additionally import only
NetlifyDeployer and NetlifyDeployError from the public src.deployment
gateway, never a private P5 file. Approved P1/P2/P7/P4 public-gateway
dependencies remain. The public src.local_api gateway and exact
create_app signature remain unchanged. Existing import guards and lower
dependency prohibitions remain in force except for the named P6 admission.

## Exact HTTP and snapshot boundary

Add only POST /api/v1/projects/{project_id}/deployments/netlify. Its
strict JSON body has required expected_updated_at: str and
confirm_deploy: Literal[True], plus optional site_id: str | None = None.
No extra fields are accepted. Absent/null site_id creates one new site;
a provided site_id must be PC-005's canonical lowercase UUID and
redeploys exactly that site. Malformed site IDs and missing/false
confirmation are 400 before any network operation. No token, endpoint,
ZIP, path, HTML, asset bytes, project state or build is accepted from
the browser. Apply the existing 2 MiB JSON body limit, exact loopback
Host and Origin checks, X-Aurora-Request: 1 mutation gate and no CORS.

Under the existing app-instance lock, validate the project ID, load P1,
compare expected_updated_at exactly, then read only the P2 netlify_token.
Stale input is 409 before credential/asset/build/network; an absent token
is 409 before build/network. Decode the saved P7 editor and compose
verified, first-occurrence-deduplicated referenced P1 assets into a
detached P4 build as PC-010/011 specify. Missing/invalid editor, draft
or referenced asset is 400. Release the app lock before constructing
and invoking P5 for its bounded synchronous network operation.

Call NetlifyDeployer(token).deploy(build, site_id=site_id) exactly once.
P5 owns ZIP staging, fixed Netlify API, remote effects, polling and
safe results. A request may block its worker, but not the app lock.
Success is HTTP 200 JSON with exactly site_id, deploy_id and public_url
from P5's ready deployment. No project mutation, cache, persisted site
binding, automatic retry, background job or import/construction side
effect is permitted. The deployed build is the accepted snapshot; no
cross-process isolation or remote rollback is claimed.

## Failure and recovery boundary

Retain P6's fixed numeric-code JSON error envelope for all pre-existing
routes and for P6-005 failures without a P5-known ID. ND-03 approves
one new-route-only exception: for a NetlifyDeployError carrying at least
one P5-validated site_id or deploy_id, return the numeric-code error
with exactly a recovery object containing site_id and deploy_id,
using null for either unknown ID. No stage, category, token, URL,
provider body or raw exception text is exposed. The error middleware
may preserve only this route-specific, internally constructed recovery
response; every other error continues to be sanitized as before.

Map invalid request/site_id/editor/P4 draft/referenced asset to 400;
missing project to 404; stale timestamp or missing token to 409;
P2 native credential failure to 503; P5 auth/remote/protocol/failed
to 502; P5 rate_limit/transport to 503; P5 timeout to 504; and
server-composed P5 validation/export, native P1 I/O or unexpected
server failure to 500. A provider 401/403 is not local AURORA 401.
Known recovery IDs do not prove deployment success. If an uncertain
remote effect has no returned ID, a user must inspect Netlify before
deliberately retrying; P6 never retries or invents an ID.

## Acceptance and deferrals

Use temporary P1 projects, synthetic rasters, fake P2 credentials,
fake P5 deployment/network and P6 TestClient only. Test strict request
shape and same-origin/body gates, stale/missing-token precedence,
typed P4 build handoff, new/existing-site success, no app lock held
during P5, all fixed status mappings, known-ID recovery and unknown-ID
envelope, no secret/raw-response leakage, no retry, no project mutation
and unchanged old routes. Integration uses public P1/P7/P4/P6
interfaces with a fake P5 boundary. No real credential read, live
Netlify call, production project, browser or user acceptance claim.

Run Ruff, scoped formatter check, strict Windows/Linux Pyright, full
discovered Pytest, exact diff/import review and latest-head hosted CI.
Produce one P6-005 module report and stop for Tech Lead review.

Project/site binding persistence, automatic recovery, live deploy,
Netlify OAuth/public distribution, folder export, React/Vite workspace,
Windows launcher, structured one-prompt/image generation and global
settings remain separate decisions. P6-005 is not the complete
ADR-002 usable-Windows product.
