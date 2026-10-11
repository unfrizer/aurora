# AURORA — Local One-Prompt Project Draft API Contract v1.0

**Document ID:** PC-016
**Status:** APPROVED — compiled from explicitly approved ADR-022 DG-01–DG-05
**Module:** P6-006 — Local One-Prompt Project Draft API
**Date:** 2026-10-11

## Authority and boundary

[ADR-022](ADR-022_Local_Project_Draft_Generation_API_Proposal_v1.0.md)
DG-01–DG-05 are incorporated in full. The Architecture Authority explicitly
approved them on 2026-10-11. AGENTS.md, ADR-001/002/003, PC-001/002/003/006/007/015
and existing P6 extensions remain in force. This is one P6 application-composition
task, not a new L0–L8 Runtime or a revision to Architecture Freeze v1.0.

## Exact ownership and imports

The active P6-006 build may modify only `src/local_api/app.py`,
`src/local_api/schemas.py`, `tests/local_api/test_security.py` and
`tests/project_generation/test_models.py`, and create only
`tests/local_api/test_project_draft_generation.py` and
`tests/integration/test_local_project_draft_generation.py` among implementation
files. This approval record and PC-016 are the only architecture-document
changes for this task. No other production file, test, dependency, workflow,
frontend, launcher or lower owner may change.

P6 may import only `ProjectDraftRequest`, `ProjectDraftOutcome` and
`ProjectDraftGenerator` from the public `src.project_generation` gateway.
The P6 import guard may add only that gateway; the PG reverse-import guard
may admit only `src/local_api/app.py` as a public-gateway consumer, preserving
its prohibition on all other imports. `src.local_api.__all__`, the exact
`create_app(*, project_root, credential_store, allowed_origin)` signature,
existing routes, and all other dependency boundaries remain unchanged.

## HTTP and candidate semantics

Add exactly `POST /api/v1/projects/{project_id}/generation/draft` with the
strict, extra-forbidden JSON body and exact fields in DG-02. The request
requires the actual JSON boolean `confirm_generation: true`, and P6 mirrors
the local prompt/model/name validation limits before any paid call. All
existing exact-loopback Host, Origin, X-Aurora-Request, 2 MiB JSON-body,
no-CORS and numeric-error protections apply.

Under the app-instance lock, validate a canonical project UUID, load P1,
compare the expected timestamp, reject valid existing editor state or
malformed/unsupported existing editor state according to DG-02/04, validate
the P1-owned project name and retrieve only the P2 OpenAI key. Release the
lock before constructing P3 and calling PG-001 exactly once. No retry,
background work, provider request under the lock, or project write is allowed.

Both terminal PG outcomes return HTTP 200 with exactly the DG-03 five-field
candidate response and specified security headers. A completed document is
encoded only through P7's public `save_editor_state` codec; a failed result
contains only P3/PG's three safe failure fields. No prompt, credential,
provider output, path or native exception text appears in the response.
P6 does not re-read the project after the provider call. Acceptance is a
separate existing editor PUT with the captured `source_updated_at`, so a
stale candidate is rejected with 409 rather than silently saved.

Pre-PG error precedence and mappings are exactly DG-04. In particular,
missing project is 404; stale or existing valid editor or missing key is
409; malformed input/editor/name is 400; P2 native read or invalid stored
P3 key is 503; unexpected/P1 native failure is 500. Once PG executes, its
terminal failed outcome is HTTP 200, not a local provider-status translation.

## Acceptance and deferrals

Use fake P2 and fake P3 with temporary P1 projects and real PG/P7/P4.
Cover the complete DG-05 security, validation, precedence, one-call,
concurrency, no-mutation and stale-acceptance matrix without a real key,
network request, paid call or skipped/xfail acceptance. Run Ruff, scoped
formatter check, strict Pyright, full discovered Pytest, exact diff/import
review and latest-head hosted CI before routine merge. Produce one P6-006
module report and stop for Tech Lead review.

This contract does not approve React generation UI, automatic draft
acceptance/autosave, image generation, settings, folder export, Windows
distribution or live OpenAI acceptance. Passing P6-006 does not certify the
full ADR-002 usable-Windows path.
