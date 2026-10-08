# AURORA — Netlify Deploy Adapter Proposal v1.0

**Document ID:** ADR-011
**Status:** APPROVED — N-01–N-05 explicitly approved by Architecture Authority
**Date:** 2026-10-08
**Target module:** P5-001 — Netlify Deploy Adapter
**Repository baseline:** `45056a8cde98470f3514299748b3fc70e982ac49`

## Authority and current state

The Architecture Authority replied "утверждаю все" on 2026-10-08 to the
request to approve N-01–N-05, including the personal/local token boundary.
That response approves these five decisions without changing their values.
PC-005 compiles their implementation contract; P5 implementation and Tech
Lead acceptance remain separate. This record does not claim a live Netlify
deploy, independent human review, passing hosted CI, or a usable Windows MVP.

ADR-002 approves Netlify as the only integrated MVP deploy target and requires
build → ZIP → API deploy → poll until ready → public URL. It also requires a
separate approved adapter contract before implementation. PC-002 owns the
`netlify_token` credential; PC-004 owns `StaticSiteBuild` and deterministic
ZIP export. No PC-005, Netlify adapter, or Netlify acceptance tests exist.

The later approved ADR-010/PC-004 place site files at ZIP root, without an
enclosing `dist/`. P5 must use that artifact; it cannot add a directory to
reconcile ADR-002's earlier ZIP wording. The exported folder and ZIP contents
are the same site tree.

Netlify's [official API guide](https://docs.netlify.com/api-and-cli-guides/api-guides/get-started-with-api/)
documents ZIP deployment, site creation, polling and authentication. Its
[API reference](https://open-api.netlify.com/) describes deploy URL fields.
These external API facts inform this decision; they do not change AURORA's
frozen Runtime ownership. Approval authorizes compiling PC-005 and a separate
P5 module build, not a live site creation or production deployment.

## Frozen invariants

- No new Runtime, RuntimeLayer, DI scope, event/lifecycle vocabulary, or
  ownership transfer between L0–L8.
- No changes to Kernel, persistence, credentials, generation, P4 build/export,
  or their tests. No generic provider framework or second deployment target.
- No new package dependency, mutable global token, background worker,
  implicit deploy, or automatic publish.
- A deploy is an explicit future user action, never an import, construction,
  validation, build, export, save, or test side effect.
- Netlify tokens remain in PC-002's Windows Credential Manager. P5 receives a
  token from future application composition and never writes, returns, logs,
  serializes, or embeds it in a site.

## N-01 — Application ownership and file scope

**Approved decision — N-01.** P5 is an application outbound adapter,
not PlatformRuntime. It owns only Netlify-specific validation, HTTP, bounded
polling, and sanitized deploy results/failures. Proposed module files:

```text
src/deployment/__init__.py
src/deployment/models.py
src/deployment/netlify.py
tests/deployment/__init__.py
tests/deployment/test_models.py
tests/deployment/test_netlify.py
tests/integration/test_netlify_deploy.py
```

The test package marker avoids default-pytest module-name collisions. The
approved package gateway exports exactly `NetlifyDeployer`,
`NetlifyDeployment`, and `NetlifyDeployError`; PC-005 must register these
symbols and the files before implementation. P5 may
import the standard library and PC-004's public build/export API, but not a
concrete Kernel Runtime, PC-001 repository, PC-002 credential implementation,
FastAPI, or frontend. Lower layers never import P5.

## N-02 — Credential and distribution boundary

**Approved decision — N-02.** For the first personally operated local
Windows MVP, the user supplies their own Netlify personal access token in
future Settings. PC-002 stores it under `netlify_token`; future application
composition retrieves and passes it only on an explicit Deploy command. P5
does not fetch or persist it. An environment variable is not a production
Netlify credential path.

This scope is a personal/local tool, **not** a generally distributed public
Netlify integration. Netlify's official guide says public integrations for
others must use OAuth2. If AURORA is distributed as such, OAuth consent,
callback, token lifecycle, and credential ownership need another approved
contract first. This approval selects the local-token boundary, not OAuth now.

## N-03 — Build handoff and network boundary

**Approved decision — N-03.** Public entry point:

```text
NetlifyDeployer(api_token: str)
NetlifyDeployer.deploy(build: StaticSiteBuild, *, site_id: str | None = None)
    -> NetlifyDeployment
```

N-03 freezes these names and signatures. `build` comes from
the approved P4 builder. P5 reuses `StaticSiteExporter` in an invocation-owned
temporary directory to stage the exact PC-004 ZIP **before** contacting
Netlify. It accepts no arbitrary browser-supplied ZIP, user-selected upload
path, project JSON, HTML, or untyped deploy payload. Cleanup is limited to
its own temporary directory.

Reject an empty, non-ASCII or header-unsafe token before staging. Accept an
existing site ID only in canonical UUID form (`8-4-4-4-12` lowercase hex),
then send one ZIP deploy to that site.
Without a site ID, create one site, capture its returned ID, then send one ZIP
deploy. The API base is fixed to `https://api.netlify.com/api/v1/`; no caller-
supplied host, domain, team, name or endpoint. The ZIP contains the complete
site with root `index.html`, sent with `Content-Type: application/zip` and
Bearer authorization. Site creation is `POST /sites` with an empty JSON object;
ZIP deployment is `POST /sites/{site_id}/deploys`. Reject all HTTP redirects,
including a same-host redirect. Use a 30-second timeout per HTTP request and
cap each JSON response at 1 MiB; do not parse unbounded response bodies.

There is no automatic retry of site creation or ZIP POST: an uncertain result
could create another site or deploy. Creation and deployment are non-atomic
external effects. A failure after site creation must expose the known site ID
for deliberate recovery; P5 does not delete the site, persist the ID in a
project, or decide the future UI's project-to-site binding.

## N-04 — Polling, result and failure model

**Approved decision — N-04.** Poll only the newly created deploy via
`GET /api/v1/deploys/{deploy_id}`, under a monotonic 120-second deadline that
starts after the ZIP POST returns and
no more than one poll per two seconds. Succeed only at Netlify state `ready`.
No unbounded polling or background task.

`NetlifyDeployment` is a frozen, slotted, keyword-only dataclass
with exactly `site_id: str`, `deploy_id: str`, and `public_url: str`. Read
`public_url` from the ready deploy's `ssl_url` field only; require an HTTPS
URL with a nonempty host and no embedded credentials. A missing/invalid field
is a protocol error, not a fabricated URL. P5 does not open the URL.

`NetlifyDeployError(RuntimeError)` has read-only `stage`,
`category`, `site_id`, and `deploy_id` attributes. Stages are `validation`,
`site_create`, `upload`, and `poll`; categories are `invalid_input`, `auth`,
`rate_limit`, `remote`, `transport`, `protocol`, `failed`, and `timeout`.
Known IDs are carried as strings, unknown IDs as `None`. Its own message is
a fixed safe description of the stage/category, never a provider response.
Authentication, rate-limit, server, transport, malformed response, terminal
failure and timeout are never success. No token, ZIP bytes, arbitrary API
body, authorization header or project data in errors, repr, or normal logs.
Do not chain raw network exceptions into a public error with secret-bearing
request details. PC-004 validation/export failures are wrapped as safe
`validation` errors before any network request.

The created site can persist remotely after a later failure. A timeout means
"ready not confirmed," not "Netlify definitely did not publish." Recovery is
a future deliberate workflow, never an automatic second POST from P5.

## N-05 — Acceptance and publication gate

**Approved decision — N-05.** Compile PC-005,
then implement P5 in its own module task/branch, changing only registered
source/test files. Tests use synthetic PC-004 builds and fake HTTP, never a
real token or Netlify endpoint. Cover new/existing site, exact ZIP/target/
headers, bounded polling, all failure stages, uncertain POST, recoverable
IDs, malformed JSON/URLs, redirects, response bounds, token redaction,
cleanup and no import/construction side effects. Fake transport tests do not
prove a live public deployment.

Run Ruff, strict Windows/Linux Pyright, full discovered Pytest and relevant
bounded smoke. Inspect final diff and latest-head hosted CI; report one P5
module and stop for Tech Lead review. ADR-003 can govern normal PR/merge only
after the task is authorized and checks pass. It does not authorize an actual
production deployment.

## Approved decision record

The Authority approved N-01–N-05 in full, specifically:

1. Personal/local BYO Netlify token for this MVP, with public OAuth integration
   deferred to a separate contract.
2. Typed P4 build as the only deploy input and P5-owned temporary ZIP staging.
3. New-site creation and existing-site redeploy, with no automatic POST retry
   or site deletion after partial failure.
4. Bounded synchronous ready-result and recoverable-ID failure model.
5. Exact P5 ownership and fake-network acceptance boundary.

PC-005 may be compiled and P5 built only in its separate task. Future FastAPI/UI
composition, persistent project/site-ID binding, live-user verification and
public OAuth distribution remain separately owned contract work.
