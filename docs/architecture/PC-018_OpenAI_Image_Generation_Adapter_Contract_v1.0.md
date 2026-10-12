# AURORA — OpenAI Image Generation Adapter Contract v1.0

- Document ID: PC-018
- Status: APPROVED — compiled from explicitly approved ADR-024 IG-01–IG-05
- Module: P3-002 — OpenAI Image Generation Adapter
- Date: 2026-10-12

## Authority and exact ownership

[ADR-024](ADR-024_OpenAI_Image_Generation_Adapter_Proposal_v1.0.md)
IG-01–IG-05 are incorporated in full. The Architecture Authority explicitly
approved them on 2026-10-12. AGENTS.md, ADR-001/002/003, PC-003, PC-008,
PC-009, and earlier application contracts remain in force. P3-002 is an
application adapter, not a new L0–L8 Runtime.

The implementation task may only create `src/generation/image_models.py`,
`src/generation/openai_image_client.py`,
`tests/generation/test_image_models.py`, and
`tests/generation/test_openai_image_client.py`, and extend
`src/generation/__init__.py`. This contract and the ADR-024 approval record
are the only documentation changes in scope. Do not change PC-003 text
implementation, lower owners, P6/UI, dependencies, lockfiles, or CI.

## Public contract and request

Export `ImageGenerationRequest`, `ImageGenerationResult`,
`ImageGenerationJob`, and `OpenAIImageClient`. Use frozen, slotted,
strictly typed request/result/job dataclasses. A request carries model and
prompt, with prompt redacted from representation. The client is initialized
with an in-memory API key and finite positive timeout; invalid local
configuration or request raises existing `GenerationConfigurationError`
before any network call. The model is supplied by the caller and remains
configurable. Prompt must be nonblank, valid UTF-8, at most 8 KiB, and sent
unchanged. No credential lookup, project path, or state mutation occurs here.

## Provider and result boundary

One valid attempt sends one direct JSON POST to
`https://api.openai.com/v1/images/generations` with exactly the IG-03 body
fields. The client refuses redirects, uses a finite timeout, closes HTTP
error bodies, and reads no more than 24 MiB plus one byte. A success must
contain exactly one data item with valid base64 PNG bytes, nonempty and at
most 16 MiB. The returned result contains detached bytes and literal
`image/png`, not a project asset reference. A terminal job has a canonical
local UUID and exactly one result or sanitized existing P3 failure.

Do not leak prompt, key, provider body, base64, or image bytes through
representations, logs, error messages, or public failure snapshots. Do not
retry automatically or imply that a network interruption cancels a paid
remote attempt. Account model access, pricing, and live generation are not
asserted by this contract.

## Acceptance and deferrals

Tests use a substituted opener and synthetic bytes, covering the full
IG-05 matrix: dataclass invariants/redaction, exact outbound request,
valid and malformed results, size bounds, safe failure categories,
network uncertainty, redirect denial, timeout validation, and no retries.
Run Ruff, strict Pyright, all discovered Pytest, ownership/import review,
and latest-head hosted CI before routine merge under ADR-003. Produce one
P3-002 module report and stop for Tech Lead review.

P6 credential use, same-origin HTTP route, P1 persistence, P7 editor
reference updates, UI controls, image edits and automatic image generation
during the existing one-prompt draft call require separate approved contracts.
