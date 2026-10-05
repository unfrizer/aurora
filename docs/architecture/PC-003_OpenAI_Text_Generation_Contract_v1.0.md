# AURORA — OpenAI Text Generation Contract v1.0

**Status:** APPROVED  
**Module:** P3-001 OpenAI Responses Text Generation  
**Authority:** ADR-001 and ADR-002

P3-001 is an application adapter, not an L0–L8 Runtime. It owns one synchronous,
direct OpenAI Responses API request for text or structured-text generation and its
terminal job/error snapshot. It may create:

```text
src/generation/__init__.py
src/generation/models.py
src/generation/openai_client.py
tests/generation/test_generation_models.py
tests/generation/test_openai_client.py
```

Public API is `GenerationRequest`, `GenerationResult`, `GenerationFailure`,
`GenerationJob`, `GenerationErrorCategory`, `OpenAIResponsesClient`, and
`GenerationConfigurationError`. All snapshots are frozen, slotted dataclasses.
The caller supplies the model, so `gpt-5.6-terra` and `gpt-5.6-sol` remain
configuration values owned by a future bootstrap/settings module rather than
business-logic constants. The adapter receives a raw API key only in memory;
P2 owns its production retrieval from Windows Credential Manager.

For each valid request, `OpenAIResponsesClient.generate` returns a terminal,
in-memory `GenerationJob`: either `completed` with a `GenerationResult`, or
`failed` with a sanitized `GenerationFailure`. It does not start a background
task, persist a job, retry automatically, call another provider, or log a
prompt, API key, or response body. It sends `POST https://api.openai.com/v1/responses`
with `model`, `input`, optional `instructions`, and `store: false`. `store: false`
matches this stateless local-MVP boundary; no response retrieval is required.

Success requires a completed, error-free response and completed assistant messages.
Refusals, incomplete output, malformed fields and whitespace-only text fail safely.
Text extraction examines every output message/content item marked `output_text`
and concatenates the text exactly, without adding separators that could corrupt
JSON. It must not assume `output[0].content[0]` exists. HTTP 401/403,
429, 5xx, network, and malformed-response failures are mapped to safe failure
categories without carrying a raw remote error body. Empty API keys and invalid
requests are local configuration errors. Tests replace the network function and
cover success, payload shape, multi-item output, status mapping, transport
failure, malformed output, and snapshot invariants. Ruff, Pyright, and Pytest
are required.

Audit clarification: HTTP redirects are rejected; credentials never follow a
redirect. The timeout must be finite and positive, response bodies are bounded
to 8 MiB, and HTTP error responses are closed. Snapshot representations omit
prompts, instructions, and generated text. No new error vocabulary is introduced.
P3-001 currently provides plain text only: schema-constrained generation, images,
and the multi-stage business generator remain future product work.

API references: [Responses create](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
and [text generation](https://developers.openai.com/api/docs/guides/text).
