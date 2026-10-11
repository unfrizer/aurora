# AURORA — Local Project Draft Generation API Proposal v1.0

- Document ID: ADR-022
- Status: APPROVED — Architecture Authority approved DG-01–DG-05 in full on 2026-10-11
- Date: 2026-10-11
- Proposed module: P6-006 — Local One-Prompt Project Draft API
- Repository baseline: `f7f9ad2d914b5921af6043dd34ea2bcccd86e3cf`

## Decision boundary

ADR-002 approves the one-prompt Windows product goal. PC-003 owns one
stateless OpenAI Responses text call; PC-002 owns secret retrieval; PC-001
owns project persistence; PC-007 owns editor state; PC-006 owns the local,
same-origin HTTP boundary. ADR-021 and PC-015 now approve PG-001, which
returns an in-memory, P7-valid and P4-publishable text-only site candidate.
PG-001 deliberately has no HTTP route or persistence. The existing P6
`POST /api/v1/generation/text` returns raw text and cannot safely stand in
for a structured project-draft command.

This decision specifies one P6 extension only. It does not change L0–L8,
lower application owners, the PG-001 public API, or Architecture Freeze v1.0.
The full Architecture Freeze and Master Pack are not present in this checkout;
this decision does not replace them. Its implementation authority is the
separate APPROVED PC-016 contract, compiled after explicit DG-01–DG-05 approval.

OpenAI's official [text generation guide](https://developers.openai.com/api/docs/guides/text)
documents direct Responses requests with separate instructions and input.
P6-006 reuses P3/PG-001; it adds no new OpenAI call shape or model policy.

## DG-01 — Exact P6 ownership and dependency admission proposed

The P6-006 module would change only:

```text
src/local_api/app.py
src/local_api/schemas.py
tests/local_api/test_project_draft_generation.py       # create
tests/integration/test_local_project_draft_generation.py # create
tests/local_api/test_security.py                        # narrow import admission
tests/project_generation/test_models.py                 # narrow import admission
```

The P6 import guard would add only `src.project_generation` to its approved
public-gateway set. The PG-001 reverse-import guard would admit only
`src/local_api/app.py` as a public `src.project_generation` consumer, while
retaining its prohibition on all other production imports. P6 may import
`ProjectDraftRequest`, `ProjectDraftOutcome`, and `ProjectDraftGenerator`
only from the `src.project_generation` gateway. It continues to import only
the approved public P1/P2/P3/P7/P4/P5 gateways and Foundation validation
error. No PG-001, P1–P5, P7, frontend, launcher, Runtime, dependency,
workflow or unrelated test file may change. `src.local_api.__all__`, the
exact `create_app(*, project_root, credential_store, allowed_origin)`
signature, and existing routes remain unchanged. No lower owner imports P6.

## DG-02 — One explicit, paid draft command proposed

Add exactly:

```text
POST /api/v1/projects/{project_id}/generation/draft
Content-Type: application/json
Strict JSON body with exactly:
  business_prompt: str, required
  language: "ru" | "en", required
  model: str, required
  expected_updated_at: str, required
  confirm_generation: literal true, required
```

The browser does not supply a project name, API key, editor object, assets,
provider endpoint, instructions or arbitrary output schema. P6 takes the
project name from the loaded P1 metadata and the model from the explicit
request; it does not hard-code a model. `confirm_generation` must be the
actual JSON boolean `true`, not `1` or a truthy string, so an accidental
form submission cannot silently incur a paid request. It is a request-time
confirmation marker, not persistent consent, a price estimate or an OpenAI
account-access guarantee. Only a later UI contract can define the visible
confirmation interaction.

P6 mirrors PG-001's local bounds before any credential or provider call:
nonblank UTF-8 business prompt at most 8 KiB, nonblank model, and nonblank
P1 project name at most 256 UTF-8 bytes. It neither trims nor truncates
them. Request body fields are strict and reject extra keys. The existing
2 MiB JSON body cap, exact loopback Host, same-origin Origin,
`X-Aurora-Request: 1`, no-CORS policy and fixed error envelope apply.

Under the existing app-instance lock, P6 validates the project UUID, loads
P1, compares `expected_updated_at` exactly, checks that the existing editor
subtree is absent, validates the project name, and reads only P2's
`openai_api_key`. If the editor key exists with a valid P7 document,
generation is rejected with 409 before credential/provider access; an
invalid or unsupported existing editor subtree is 400. Missing credential
is 409. This route deliberately does not regenerate or overwrite an
existing editor document. P6 copies the project name and timestamp,
releases the lock, then constructs P3's client and invokes PG-001 once.
The synchronous provider call may occupy a request worker but never holds
the project lock. No automatic retry, background job or second paid call.

## DG-03 — Candidate response and acceptance conflict proposed

The route never writes P1 state, project metadata, assets, site or exports.
It returns an in-memory candidate, not an accepted editor save. Both
PG-001 terminal outcomes use HTTP 200 with exactly:

```json
{
  "job_id": "string",
  "status": "completed | failed",
  "source_updated_at": "P1 timestamp captured before generation",
  "editor": "P7 version-one object or null",
  "failure": "{category, message, retryable} or null"
}
```

On `completed`, `editor` is the exact P7 editor subtree produced via the
public `save_editor_state({}, outcome.document)` codec, and `failure` is
null. On `failed`, `editor` is null and `failure` contains only PG-001/P3's
sanitized three fields. The HTTP representation excludes prompt, raw
provider output, instructions, key, P3 request, project filesystem path
and exception text. Send `Cache-Control: no-store`,
`X-Content-Type-Options: nosniff` and
`Cross-Origin-Resource-Policy: same-origin` on either 200 response.
An HTTP 200 with `status="failed"` means a completed request with a
terminal generation failure, not a publishable document.

P6 does not hold a lock or reserve a project version during the network
call and does not re-read or silently overwrite the project afterward.
It returns the captured `source_updated_at` even if the project changed
while generating. A later explicit user acceptance must call the already
approved `PUT /api/v1/projects/{project_id}/editor` with that timestamp.
Its existing optimistic check returns 409 if the project changed. Thus a
paid candidate remains visible to the caller without falsely claiming it
is saved or current. This is only per-app-instance concurrency; PC-001's
cross-process and crash-transaction limitations remain unchanged.

## DG-04 — Fixed failure precedence and mapping proposed

Existing P6 numeric-code JSON errors remain exactly
`{"error":{"code": <HTTP status>}}`, without input or native error text.
Proposed precedence and mappings before PG-001 is invoked:

1. Invalid Host/Origin/header/media/body/strict JSON or missing/false
   confirmation: 400, before repository/credential/provider effects.
2. Noncanonical project UUID or invalid local prompt/model: 400.
3. Missing project: 404. Stale `expected_updated_at`: 409 before editor,
   credential or provider read.
4. Invalid existing P7 editor subtree or invalid/oversized project name:
   400. Existing valid editor: 409, before credential or provider read.
5. Missing OpenAI credential: 409. P2 native read failure or invalid
   stored key when constructing P3: 503, not a browser validation error.

P1 native filesystem and other unexpected server failures remain 500.
Once PG-001 runs, its `failed` outcome — including P3 authentication,
rate limit, transport, remote and `invalid_response` categories — is
returned as the HTTP 200 terminal snapshot from DG-03, consistent with
the existing P6 raw-text generation job convention. P6 does not expose
OpenAI HTTP status as local AURORA authentication or retry automatically.
Existing routes and their error mappings are unaffected.

## DG-05 — Acceptance matrix, quality gates and deferrals proposed

Tests use FastAPI TestClient, temporary P1 projects, a fake P2 store and
a patched P3 generation boundary with synthetic results. They use real
PG-001/P7/P4 code but no real Windows Credential Manager entry, API key,
paid OpenAI call, browser, user project or persistence outside `tmp_path`.
Cover exact schema and origin/body gates, confirmation type, UTF-8 size
boundaries, missing project, stale-before-secret precedence, absent versus
valid/malformed existing editor, missing/native-failed/invalid credential,
one provider call, lock released during provider work, completed bilingual
candidate shape, sanitized failed outcome, no project mutation, and
unchanged old routes. Simulate a project save while the fake provider is
running: the candidate retains its source timestamp and the existing
editor PUT rejects stale acceptance with 409. No skip/xfail acceptance.

Run Ruff, scoped formatter check, strict Pyright, full discovered Pytest,
exact diff/import review and latest-head hosted CI before any routine merge.
Produce one P6-006 module report and stop for Tech Lead review.

This proposal does not approve a React generation screen, automatic draft
acceptance or autosave, image generation/persistence, global settings,
folder export, Windows distribution or live OpenAI acceptance. PG-001 is
text-only, so P6-006 alone does not achieve ADR-002's usable-Windows path.

## Approval record

The Architecture Authority approved DG-01–DG-05 in full on 2026-10-11,
including literal paid-call confirmation, 409 for an existing editor,
HTTP 200 terminal snapshots, and timestamp-bound separate acceptance.
PC-016 compiles this decision for the P6-006 implementation task. The
approval does not extend to any deferred UI, image, packaging or live-call work.
