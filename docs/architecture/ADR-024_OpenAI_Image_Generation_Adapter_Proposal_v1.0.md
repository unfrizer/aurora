# AURORA — OpenAI Image Generation Adapter Proposal v1.0

- Document ID: ADR-024
- Status: APPROVED — Architecture Authority approved IG-01–IG-05 in full on 2026-10-12
- Date: 2026-10-12
- Proposed module: P3-002 — OpenAI Image Generation Adapter
- Repository baseline: `33e97a9af6e5661b2e6b3427273f7a744eb4b4b8`

## Decision boundary

ADR-002 requires image generation for the first usable Windows product and
selects OpenAI as the sole provider with configurable default model
`gpt-image-2`. PC-003 currently authorizes **text only** through the Responses
API. PC-008 already owns validated raster storage in P1; PC-009 owns local
HTTP asset upload. UI-002 can review and accept a structured **text-only**
draft. None of these contracts authorizes an image-provider call or automatic
image insertion.

This proposal adds a narrow P3 application adapter for one synchronous image
generation attempt. It does not add or change an L0–L8 Runtime, move P1/P2/P6/P7
ownership, amend PC-003 text behavior, or authorize a browser/provider call.
The complete Architecture Freeze and Master Pack are not present in this
checkout; this proposal cannot replace them. Its implementation authority is
the separate APPROVED PC-018 contract, compiled after explicit IG-01–IG-05
approval.

## IG-01 — Owner, exact files, and dependency direction proposed

P3-002 may create or modify only:

```text
src/generation/image_models.py             # create
src/generation/openai_image_client.py       # create
src/generation/__init__.py                  # extend P3 gateway
tests/generation/test_image_models.py       # create
tests/generation/test_openai_image_client.py # create
```

P3-002 depends only on Python standard-library networking/decoding facilities,
Foundation validation where already applicable, and the existing P3 safe
failure vocabulary. It neither imports nor constructs the P1 project repository,
P2 credential store, P6 HTTP app, P7 editor, platform bridge, or browser UI.
The caller supplies a raw API key only in memory; production retrieval remains
P2's responsibility. No new dependency, registry, background worker, global
mutable state, retry engine, or provider abstraction is proposed.

## IG-02 — Public request, result, and job proposed

Expose `ImageGenerationRequest`, `ImageGenerationResult`,
`ImageGenerationJob`, and `OpenAIImageClient` from the P3 gateway. Requests,
results, and terminal jobs are frozen, slotted dataclasses with strict typing.
The request contains a caller-supplied nonblank `model` and nonblank `prompt`.
The prompt is bounded to 8 KiB UTF-8, is not silently truncated or rewritten,
and is excluded from representations. The caller chooses the configured model;
the adapter does not hard-code `gpt-image-2` or select a different model.

A successful result contains exactly one detached PNG byte string and the
literal media type `image/png`; raw bytes are excluded from representations.
The result is not a project asset path and is not automatically saved. A job
contains a canonical locally generated UUID, its request, status `completed`
or `failed`, and exactly one matching result or sanitized failure. Reuse the
existing P3 `GenerationFailure` categories (`authentication`, `rate_limited`,
`remote`, `network`, `invalid_response`) without extending the vocabulary.
No provider response body, revised prompt, URL, token, or opaque metadata is
retained. Local invalid configuration raises the existing
`GenerationConfigurationError` before any network call.

## IG-03 — One direct OpenAI Images API call proposed

For each valid attempt, send exactly one `POST` to
`https://api.openai.com/v1/images/generations` with the caller-supplied
`model`, unchanged `prompt`, `n: 1`, `size: "1024x1024"`, and
`output_format: "png"`. Use a bearer credential and JSON request body.
This endpoint and `gpt-image-2` support are documented by OpenAI; the Images
API is distinct from PC-003's Responses text path. Do not send a deprecated
`response_format` parameter, request streaming/partials, pass reference
images, ask for edits, or silently fall back to another model.

The client uses a finite positive timeout, refuses HTTP redirects so the key
cannot follow a redirect, bounds the complete response to 24 MiB before JSON
parsing, and closes HTTP error responses. It accepts only a successful JSON
object with exactly one `data` entry containing a nonblank base64 `b64_json`.
Decode strictly, require a PNG signature and a nonempty payload no larger than
16 MiB, and reject malformed/oversized/ambiguous results as
`invalid_response`. P1 independently validates the bytes if a later caller
chooses to persist them; P3 does not claim full image decoding or malware
scanning. The 24 MiB envelope accommodates base64 for P1's 16 MiB asset limit
plus bounded JSON overhead; a response outside it fails safely.

HTTP 401/403, 429, 5xx, other HTTP rejection, transport failure, and invalid
response map to the existing safe P3 categories and retryability pattern.
Do not log or expose prompts, keys, raw provider errors, base64, image bytes,
or arbitrary provider messages. A network interruption can make the remote
billable outcome uncertain; do not retry automatically or claim cancellation.
Availability and pricing for the user's account are not assumed.

## IG-04 — Explicit downstream boundary proposed

This adapter alone does not fulfill ADR-002's image experience. A later
separately approved P6 integration must own credential retrieval, explicit
per-attempt charge consent, project identity/version checks, calling P3,
writing through P1, and a sanitized same-origin result. A later UI contract
must own image-generation controls, unsaved/saved state, accessibility,
progress/uncertainty wording, and editor reference updates through existing
P7/P6 paths. Whether one-prompt generation automatically triggers image
requests is a separate product/architecture decision: the existing text-draft
call must not silently gain additional paid calls. No image is embedded in
project JSON or sent directly to a browser from this adapter.

## IG-05 — Deterministic acceptance and deferrals proposed

Tests replace the network opener and use synthetic small PNG-signature bytes.
Cover public dataclass invariants and representation redaction; exact URL,
method, headers, and JSON body; configured model and unchanged prompt; one
call/no automatic retry; success and strict base64; response and decoded-byte
limits; missing/multiple `data` entries; malformed JSON/PNG; finite timeout;
redirect rejection and credential non-forwarding; HTTP category mapping,
closed error responses, transport failures, and non-sensitive errors.

Run Ruff, strict Pyright, all discovered Pytest, exact ownership/import diff,
and latest-head hosted CI. No live key, paid image call, existing user project,
browser automation, or skipped/xfail acceptance test is part of this module.
Produce one P3-002 module report and stop for Tech Lead review.

This proposal does **not** approve P6/UI integration, image edits, multiple
images per attempt, transparent logos, automatic insertion into P7, generated
site rebuilding, model migration, image pricing claims, settings persistence,
or Windows packaging.

## Sources and approval needed

- ADR-001, ADR-002, PC-003, PC-008, PC-009 and the approved UI-002 boundary.
- [OpenAI GPT-Image-2 model](https://developers.openai.com/api/docs/models/gpt-image-2).
- [OpenAI Images API create-image reference](https://developers.openai.com/api/reference/resources/images/methods/generate).

## Approval record

The Architecture Authority approved IG-01–IG-05 in full on 2026-10-12.
PC-018 compiles those decisions for P3-002. Approval does not extend to
the deferred P6/UI integration, additional paid calls, image edits, automatic
asset insertion, or a live provider acceptance test.
