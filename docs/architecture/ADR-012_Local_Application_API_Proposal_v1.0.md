# AURORA — Local Application API Proposal v1.0

**Document ID:** ADR-012
**Status:** APPROVED — A-01–A-06 explicitly approved by Architecture Authority
**Date:** 2026-10-08
**Target module:** P6-001 — Local FastAPI Application API Foundation
**Repository baseline:** `43765401b933a7dfcd34d0cdcb693ce8fcb23e4f`

## Authority and current boundary

ADR-002 selects Python 3.13 + FastAPI bound to `127.0.0.1` for the Windows
desktop-web MVP and requires a separate approved API contract. PC-001 through
PC-005 own project persistence, Windows secrets, text generation, static-site
build/export, and Netlify deployment. AB-00K makes L7 PlatformRuntime an
in-memory descriptor owner, not an HTTP server. P6 would be application
composition above those owners, never a new L0–L8 Runtime.

The Authority first approved preparation of this proposal after P5, then
explicitly replied “утверждаю, дальше” to the request to approve A-01–A-06
on 2026-10-08. This approves the specified HTTP routes, security policy,
dependency additions and deferred boundaries without claiming implementation
or product acceptance. PC-006 compiles the exact P6 implementation contract.

## A-01 — Ownership and import boundary (approved)

Approved owned files:

```text
src/local_api/__init__.py
src/local_api/app.py
src/local_api/schemas.py
tests/local_api/__init__.py
tests/local_api/test_app.py
tests/local_api/test_security.py
tests/integration/test_local_api.py
pyproject.toml                 # P6 dependency declarations only
uv.lock                        # matching lock update
```

The sole public Python gateway is `create_app(*, project_root: Path,
credential_store: WindowsCredentialStore, allowed_origin: str) -> FastAPI`.
Construction registers routes and app-local coordination only; it does not
touch files, read secrets, contact providers, launch a browser, or start a
server. A later launcher supplies the canonical project root, credential
adapter, and actual loopback origin.

P6 may import standard library, FastAPI/Pydantic, and the public gateways
`src.projects`, `src.credentials`, and `src.generation`. It may not import
concrete Kernel/Platform Runtimes, private P1–P5 modules, frontend code, or
another provider. Lower layers never import P6. P6-001 does not import P4/P5:
there is no approved typed projection from opaque `ProjectDocument.state` to
`StaticSiteDocument`; a build/deploy route would invent that editor schema.

## A-02 — Versioned HTTP surface (approved)

All P6 routes use `/api/v1`; JSON except empty `204` responses.

| Method and route | Request | Success |
| --- | --- | --- |
| `GET /health` | None | `200 {"status":"ok"}`; API liveness only, not Kernel health |
| `GET /projects` | None | `200` P1 metadata array |
| `POST /projects` | `{"name": string}` | `201` P1 document with empty state |
| `GET /projects/{project_id}` | None | `200` P1 document |
| `PUT /projects/{project_id}` | `{"name": string, "state": object, "expected_updated_at": string}` | `200` saved P1 document |
| `DELETE /projects/{project_id}` | None | `204` after explicit P1 deletion |
| `GET /credentials/{name}/status` | None | `200 {"configured": boolean}` |
| `PUT /credentials/{name}` | `{"secret": string}` | `204`; never echo secret |
| `DELETE /credentials/{name}` | None | `204`, including absent secret |
| `POST /generation/text` | `{"model": string, "prompt": string, "instructions"?: string}` | `200` P3 terminal job projection without request/prompt/key |

Credential `{name}` accepts only `openai_api_key` or `netlify_token`.
Generation obtains the OpenAI key from P2 only on explicit POST, creates a
request-scoped P3 client, and returns status, job/result/failure fields but
never the request snapshot or key. A failed P3 job remains a failed terminal
job response. The caller supplies the model until a settings policy is
approved; P6 does not hard-code ADR-002 defaults in business logic.

Project save loads the P1 document under one app-local lock, checks URL ID and
`expected_updated_at`, retains server-owned ID, creation time and format,
then calls P1 `save` with requested name/state. Stale saves return `409`.
The lock coordinates one app instance, not separate processes; no
cross-process transaction or multi-user editing is claimed. It is not a
Runtime DI scope or process-global registry. Known P2 credential field names
are rejected recursively in opaque project state. Arbitrary secrets cannot
be inferred, so callers must also keep them out of state.

These route shapes are the approved P6-001 public HTTP behavior.

## A-03 — Loopback browser security (approved)

The later launcher must bind only `127.0.0.1`. P6 validates
`allowed_origin` as exactly `http://127.0.0.1:<port>`, accepts only that
Host, distrusts forwarded host headers, and enables no production CORS.
The future production UI is served from the same origin. Cross-origin Vite
development requires a separate development-only proxy/allowlist decision;
wildcard CORS is forbidden.

Every mutating route requires exact same-origin `Origin`, custom
`X-Aurora-Request: 1`, and `application/json` for a body. Reject missing,
`null`, or foreign origins, wrong content type, and JSON bodies over 2 MiB
before service effects. Safe GET routes never mutate. No cookies, browser
localStorage credential, query-string token, or public bind. This blocks
ordinary cross-site browser writes; it does **not** authenticate or defend
against malicious processes running as the same user or a compromised
same-origin UI. Those need a separate security contract.

FastAPI's [strict Content-Type](https://fastapi.tiangolo.com/advanced/strict-content-type/)
and [CORS](https://fastapi.tiangolo.com/tutorial/cors/) guidance,
Starlette's [TrustedHostMiddleware](https://www.starlette.io/middleware/),
and [OWASP CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
inform the security decision; the approval comes from the Architecture Authority.

## A-04 — Errors and data exposure (approved)

Failures use a fixed sanitized JSON error envelope with stable code. Never
include Python traceback, native error text, local path, credential, prompt,
provider response body, or project state in errors or normal request logs.
Approved mappings: invalid input `400`, missing project `404`, stale save
or missing OpenAI credential `409`, native credential failure `503`,
project I/O or unexpected internal failure `500`. P3's sanitized terminal
failure stays a `200` job with `status="failed"`. Framework validation
responses must also be sanitized because request data can contain secrets.
Project state is not interpreted as site, Runtime context, or Render node.
Deletion is an explicit user operation; tests only delete temporary projects.

## A-05 — Dependencies and launch boundary (approved)

ADR-002 expressly selects FastAPI. P6 adds FastAPI at runtime and HTTPX only
to the dev/test group for FastAPI `TestClient`; `uv.lock` is updated using
uv, Python remains 3.13. FastAPI's [testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
documents HTTPX. P6 does not add Uvicorn, a worker, scheduler, React bundle,
or browser launcher. Server startup, ephemeral port, same-origin static UI
serving, and browser opening require a later launcher/UI contract. P6 is a
testable API foundation, **not** yet a launchable Windows application.

## A-06 — Acceptance and publication (approved)

Tests use `tmp_path`, fake credential/native behavior, and fake P3 network;
no real user project, secret, paid OpenAI call, Netlify deploy, or browser.
Cover route/schema/status behavior, app-factory no-side-effects, P1 CRUD and
stale save, credential non-disclosure, P3 terminal failure, sanitized errors,
Host/Origin/header/content-type/body-limit rejection, and forbidden imports.
No skipped/xfail acceptance tests. Run Ruff, Windows/Linux strict Pyright,
full discovered Pytest and latest-head hosted CI before routine publication.
Produce one P6 module report and stop for Tech Lead review.

## Deferred contracts and approval record

P6-001 does **not** deliver typed editor state, one-prompt business workflow,
structured/image generation, autosave, preview, build/export/deploy HTTP,
settings persistence, UI hosting, server lifecycle, onboarding, or RU/EN UI.
Each needs a separate owned approved contract. Passing P6 tests cannot be
reported as ADR-002 usable-Windows acceptance.

The Authority approved **A-01–A-06** in full, specifically the limited route
set, same-origin local security posture, FastAPI/HTTPX dependencies and
deferral of launcher/editor/site behavior. PC-006 may be compiled and P6-001
built as a separate module task. This approval does not certify a live server,
an actual OpenAI call or a usable Windows application.
