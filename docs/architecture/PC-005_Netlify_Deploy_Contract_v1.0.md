# AURORA — Netlify Deploy Adapter Contract v1.0

Document ID: PC-005
Status: APPROVED — compiled from explicitly approved ADR-011 N-01–N-05
Module: P5-001 — Netlify Deploy Adapter
Date: 2026-10-08

## Authority and scope

[ADR-011](ADR-011_Netlify_Deploy_Proposal_v1.0.md) is incorporated in full.
The Architecture Authority approved all N-01–N-05 on 2026-10-08. AGENTS,
ADR-001/002/003, PC-002 and PC-004 retain their unaffected rules. This is a
personal, locally operated Windows MVP integration using a user-provided
Netlify token. Public distribution as a Netlify integration would require a
separate OAuth contract. This module is application code, not an L0–L8 Runtime.

No live Netlify request, production site creation, credential-store read,
application bootstrap or usable-Windows acceptance is authorized by this
contract's implementation/testing task.

## Exact ownership and imports

| File | Sole responsibility |
| --- | --- |
| `src/deployment/__init__.py` | Re-export exactly the three public symbols below |
| `src/deployment/models.py` | Immutable result and sanitized adapter error |
| `src/deployment/netlify.py` | Explicit synchronous Netlify ZIP deployment |
| `tests/deployment/__init__.py` | Package marker only |
| `tests/deployment/test_models.py` | Public model/error/ownership assertions |
| `tests/deployment/test_netlify.py` | Fake-HTTP success, rejection, failure and cleanup tests |
| `tests/integration/test_netlify_deploy.py` | Real P4 build/export to fake Netlify flow |

Only these seven implementation/acceptance files plus this contract and the
ADR approval record may change in P5, with one later explicitly approved
exception: `tests/site_export/test_models.py` and the corresponding PC-004
contract clarification may change only to recognize P5's public-gateway
import. No other P4 file may change. The package gateway exports exactly
`NetlifyDeployer`, `NetlifyDeployment`, `NetlifyDeployError`. Standard library
and PC-004 public build/export API are the only production dependencies.
`models.py` does not import the client; the client imports models and PC-004.
No import from Kernel implementation, PC-001/002 implementation, OpenAI,
FastAPI, UI, or another deployment provider. Lower modules never import P5.
No new dependency, configuration key, global mutable client, generic provider
abstraction, worker, scheduler, or default deployment is created.

## Exact public surface

```text
NetlifyDeployer(api_token: str)
NetlifyDeployer.deploy(build: StaticSiteBuild, *, site_id: str | None = None)
    -> NetlifyDeployment

NetlifyDeployment(site_id: str, deploy_id: str, public_url: str)
NetlifyDeployError(stage, category, site_id, deploy_id)
```

`NetlifyDeployment` is a frozen, slotted, keyword-only dataclass with exactly
the three required string fields listed above. It is returned only after
Netlify's new deploy is confirmed `ready` by GET. `public_url` is the ready
deploy's `ssl_url`, not a fabricated host or a deploy-preview URL. It must
parse as HTTPS with a nonempty hostname and no URL-embedded credentials.

`NetlifyDeployError` is a `RuntimeError` with read-only properties:
`stage: Literal["validation", "site_create", "upload", "poll"]`,
`category: Literal["invalid_input", "auth", "rate_limit", "remote",
"transport", "protocol", "failed", "timeout"]`, `site_id: str | None`,
and `deploy_id: str | None`. The exception's own string/repr is a fixed safe
stage/category message. Known IDs are carried when available; otherwise
they are `None`. Never include tokens, ZIP bytes, project data, arbitrary
provider response text, raw request headers or URLs in error text/normal
logs. Do not chain raw network exceptions containing request details.

No other public method, alias, constant, exception, result field or gateway
symbol is authorized. Internal stateless helpers may remain private in these
owned files.

## Input, credential and staging boundary

The caller deliberately constructs a client with a nonempty, ASCII,
header-safe token retrieved by future composition from PC-002. P5 stores it
only in instance process memory. Constructor validation performs no I/O or
network and rejects invalid tokens with a validation/invalid_input error.
The client is not responsible for Credential Manager lookup or token lifetime.

`deploy` accepts only a PC-004 `StaticSiteBuild`, not arbitrary browser ZIP,
HTML, project JSON, caller-selected file path or endpoint. Use PC-004's
`StaticSiteExporter.export_zip` to stage the build in an invocation-owned
temporary directory before any network call. The archive has root
`index.html` and PC-004's exact relative members, without `dist/` nesting.
Any P4 validation/export failure is wrapped as a safe validation error before
network. Remove only invocation-owned temporary content. The caller's build
is not mutated. P5 does not claim that P4 scanned arbitrary file content for
secrets; application composition must keep secrets out of build projections.

`site_id` is either `None` or a canonical lowercase UUID string with groups
`8-4-4-4-12` of ASCII hexadecimal digits. Reject invalid values before
network. Use the UUID only as an API path segment, never as a host or URL.

## HTTP state machine and safety

The API base is fixed to `https://api.netlify.com/api/v1/`. Every request has
a 30-second per-request timeout. Reject every HTTP redirect, including one
to the same host. Limit each JSON response body to 1 MiB before parsing.
Use Bearer authorization from the instance token; never send it to any other
host. An unexpected status, malformed JSON, missing/wrongly typed mandatory
field or over-limit response is a safe categorized error.

1. Validate token, build, and optional site ID; create the P4 ZIP before any
   remote side effect.
2. For `site_id=None`, `POST /sites` with `{}` JSON and capture the returned
   canonical site UUID. For an existing site, skip creation.
3. `POST /sites/{site_id}/deploys` once with `Content-Type: application/zip`
   and the complete staged ZIP as binary body. Capture a nonempty deploy ID.
4. Poll `GET /deploys/{deploy_id}` for only this deploy, no more frequently
   than every two seconds, using a monotonic 120-second deadline starting
   after the ZIP POST returns. Confirm only state `ready` as success. A
   reported `error`, `failed`, or `canceled` state is `failed`; other
   non-ready states can be polled until timeout. On ready, require a valid
   `ssl_url`.

No automatic retry of the site-creation or ZIP POST, no delete/rollback of a
created site and no project-to-site ID persistence. A failed/uncertain POST
may have succeeded remotely. A polling timeout means only "not confirmed
ready". When IDs were already received, include them in the safe error so
future application composition can reconcile deliberately. P5 never opens
the public URL or starts a browser, and never calls Netlify at import or
construction time.

HTTP 401/403 is `auth`; 429 is `rate_limit`; other non-2xx is `remote`, except
redirects, which are `protocol`. Invalid response shape/URL is `protocol`;
network failure is `transport`; timeout is `timeout`; Netlify terminal
failure is `failed`. The stage reflects the operation in progress. No
arbitrary API body is surfaced as the error message.

## Acceptance and stop boundary

Use synthetic PC-004 builds and a fully fake HTTP boundary. Required tests:
new/existing site, no network before staging, exact ZIP members/bytes,
endpoint/method/auth/content type, canonical ID validation, no POST retry,
bounded ready polling, all error categories, uncertain POST with recoverable
IDs, malformed/oversize response, redirect denial, token redaction, cleanup,
no implicit side effects, and complete builder → ZIP → fake-deploy flow.
Do not use a real token or contact Netlify in tests. The tests cannot certify
live deployment or public distribution compliance.

Run Ruff, strict Windows/Linux Pyright, full discovered Pytest and bounded
smoke. Review the exact diff and latest-head hosted CI when publishing. After
one P5 module report, STOP for Tech Lead review. PR/merge may follow ADR-003
only with its conditions; it never implies an actual production deploy.
