# AURORA — Local Image Generation API Proposal v1.0

- Document ID: ADR-025
- Status: APPROVED — Architecture Authority approved LI-01–LI-05 in full on 2026-10-13
- Date: 2026-10-13
- Proposed module: P6-007 — Local Image Generation API
- Repository baseline: `3382f80c565ecbacccc46a790b3bf6f249cacdd2`

## Decision boundary

ADR-002 requires generated images in the usable Windows product. Approved
ADR-024 and PC-018 supply one P3 image attempt and an in-memory PNG; they
explicitly defer credential retrieval, project checks, P1 publication, and
same-origin HTTP behavior to a separate P6 contract. PC-008 owns raster asset
storage, PC-009 owns asset transport, and PC-016 owns the separate text-only
project-draft command. None authorizes a browser-triggered image request.

This proposal specifies one narrow P6 application-composition extension. It
does not add an L0–L8 Runtime, change P1/P2/P3/P7 ownership, modify existing
routes, or make the text-draft command generate images. The full Architecture
Freeze document is not present in this checkout; this proposal cannot replace
it. The separate APPROVED PC-019 implementation contract compiles the
explicitly approved LI-01–LI-05 decisions.

## LI-01 — Exact owner, files, and dependencies proposed

P6-007 would change only:

```text
src/local_api/app.py
src/local_api/schemas.py
tests/local_api/test_image_generation.py        # create
tests/integration/test_local_image_generation.py # create
```

The existing `src.local_api` public Python gateway and `create_app` signature
remain unchanged. P6 imports the already-public `ImageGenerationRequest`,
`ImageGenerationJob`, and `OpenAIImageClient` from `src.generation`; it uses
the already-approved public P1 and P2 gateways. The P6 import guard already
admits these gateways and must not be weakened. No P1, P2, P3, P7, P4, P5,
frontend, launcher, dependency, workflow, or existing test file may change.
No lower owner imports P6. No provider registry, second provider, background
worker, or process-global state is introduced.

## LI-02 — Explicit paid command proposed

Add exactly:

```text
POST /api/v1/projects/{project_id}/generation/image
Content-Type: application/json
Strict JSON body with exactly:
  prompt: str, required
  model: str, required
  expected_updated_at: str, required
  confirm_generation: literal true, required
```

The request contains no credential, output path, filename, editor state,
provider URL, image bytes, or hidden default model. `model` is caller-selected
configuration, not a business-logic constant. `prompt` is nonblank, valid
UTF-8, at most 8 KiB and passed unchanged to P3; `model` is nonblank and
valid UTF-8. No value is silently trimmed or rewritten. Confirmation must
be the actual JSON boolean `true`, not `1` or a truthy string. This is
per-attempt charge consent, not persistent consent, a price quotation, or
an account-access guarantee. A later UI contract must specify the visible
confirmation interaction.

The existing P6 exact Host/Origin/`X-Aurora-Request: 1` mutation gates,
2 MiB JSON limit, lack of CORS, and fixed numeric error envelope apply.
Invalid schema, missing or false confirmation, and unsafe origin fail before
credential retrieval, provider access, or project mutation.

## LI-03 — Project, credential, provider, and asset sequence proposed

Under the existing app-instance project lock, P6 validates a canonical
project UUID, loads P1, checks `expected_updated_at` exactly, captures that
timestamp, and retrieves only P2's `openai_api_key`. A missing key fails
before any provider call. The lock is released before constructing P3's
client and making exactly one synchronous image attempt. P6 does not retry,
create a background task, reserve a project version, or claim cancellation
after a transport interruption.

For a completed P3 job, reacquire the app-instance lock and load the same
P1 project ID again. If the project still exists, persist the returned PNG
using only `ProjectRepository.write_asset(project_id, data, "image/png")`.
Return a path only after P1 publication succeeds. P6 never writes editor
state, modifies an image reference, builds a site, or changes the project
metadata. P1's content-addressed path, validation, quota, safe publication,
and idempotence rules remain authoritative.

An intervening editor or project save does not invalidate this independent
asset publication: the generated asset may be safely stored but remains
unreferenced, and the response retains the **pre-call**
`source_updated_at`. A later editor save using that timestamp must receive
the existing 409 conflict if state changed; the UI must reload and ask the
user where to attach the already-saved asset. A project deleted during the
remote call yields 404 and no P1 write. A successful remote call can thus
be billable even when local publication later fails or the project was
deleted; P6 must not automatically call OpenAI again. App-instance locking
does not claim cross-process transaction safety.

## LI-04 — Sanitized result and failure behavior proposed

Both terminal P3 outcomes use HTTP 200 with exactly:

```json
{
  "job_id": "canonical UUID",
  "status": "completed | failed",
  "source_updated_at": "P1 timestamp captured before generation",
  "asset_path": "assets/<sha256>.png or null",
  "failure": "{category, message, retryable} or null"
}
```

On `completed`, `asset_path` is P1's returned reference and `failure` is
null. On `failed`, `asset_path` is null, `failure` contains only P3's three
sanitized fields, and no asset is written. Neither response contains the
prompt, API key, image/base64 bytes, provider response body, native exception
text, project filesystem path, or P3 request snapshot. Set
`Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, and
`Cross-Origin-Resource-Policy: same-origin` on both HTTP 200 outcomes.
Existing `GET /assets/{asset_name}` serves the saved image; this command
does not add a binary response route.

Before P3 runs, invalid request, noncanonical ID, or invalid prompt/model
is 400; unknown project is 404; stale timestamp or missing key is 409;
P2 native read failure or invalid stored API key is 503. After a successful
P3 call, a now-missing project is 404; P1 validation, signature, corruption,
or quota failure is 400; native P1 I/O and unexpected server errors are
500. All non-200 responses retain P6's fixed
`{"error":{"code": <HTTP status>}}` envelope. P3 authentication, rate
limit, remote, network, and invalid-response outcomes remain terminal job
failures within HTTP 200; they are not recast as local 401/429. No error
response or normal log contains provider, prompt, image, key, or path data.

## LI-05 — Acceptance and explicit deferrals proposed

Use FastAPI TestClient, temporary P1 projects, a fake P2 store, and a
substituted P3 image client returning synthetic PNG-signature bytes and
terminal jobs. Cover exact route and strict body; true-boolean consent;
UTF-8/8 KiB boundaries; Host/Origin/header/media/body limits; missing and
stale project before secret/provider access; missing/native-failed/invalid
credential; exactly one call and unchanged prompt/model; completed path and
P1 byte read; failed job without asset; P1 quota/signature/I/O failures
after a billable call without retry; project deletion or state mutation
during the fake provider call; stale editor attachment rejection; unchanged
project state/metadata and other routes; response redaction and headers.
No real credential, paid request, user project, browser, or skip/xfail
acceptance test is permitted.

Run Ruff, scoped formatter check, strict Pyright, all discovered Pytest,
exact ownership/import diff, and latest-head hosted CI before routine
merge. Produce one P6-007 module report and stop for Tech Lead review.

This proposal does **not** approve image-generation UI controls, automatic
generation from the one-prompt draft command, automatic P7 attachment,
image edits, multiple images per attempt, regeneration of existing assets,
settings persistence, a second provider, or a live paid acceptance test.
Those require their own approved owner contracts and, where applicable,
product decisions.

## Sources and approval needed

- AGENTS.md; ADR-001/002/024; PC-006/008/009/016/018.
- [OpenAI Images API create-image reference](https://developers.openai.com/api/reference/resources/images/methods/generate).
- [OpenAI GPT-Image-2 model](https://developers.openai.com/api/docs/models/gpt-image-2).

## Approval record

The Architecture Authority approved LI-01–LI-05 in full in the project
conversation on 2026-10-13. PC-019 compiles those decisions for P6-007.
Approval does not extend to the deferred UI, automatic image attachment,
additional paid calls, or a live provider acceptance test.
