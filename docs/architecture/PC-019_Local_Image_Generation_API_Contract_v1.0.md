# AURORA — Local Image Generation API Contract v1.0

- Document ID: PC-019
- Status: APPROVED — compiled from explicitly approved ADR-025 LI-01–LI-05
- Module: P6-007 — Local Image Generation API
- Date: 2026-10-13

## Authority and exact scope

[ADR-025](ADR-025_Local_Image_Generation_API_Proposal_v1.0.md) LI-01–LI-05
are incorporated in full. The Architecture Authority explicitly approved
them on 2026-10-13. AGENTS.md, ADR-001/002/003/024, PC-006/008/009/016/018
and all other unaffected approved contracts remain in force. P6-007 extends
the existing application-composition owner; it is not an L0–L8 Runtime.

The implementation task may modify only `src/local_api/app.py` and
`src/local_api/schemas.py`, and create only
`tests/local_api/test_image_generation.py` and
`tests/integration/test_local_image_generation.py` among implementation
files. ADR-025's approval record and this contract are the only documentation
changes in scope. No other source, existing test, dependency, lockfile,
workflow, frontend, launcher, or lower-owner file may change.

The existing `src.local_api.__all__`, `create_app` signature, P6 import
guard, and existing route behavior remain unchanged. P6 may consume only the
public `src.generation`, `src.projects`, and `src.credentials` gateways for
this extension. No new import admission or reverse dependency is needed.

## HTTP and image lifecycle

Add exactly `POST /api/v1/projects/{project_id}/generation/image` with
the strict four-field JSON body, literal true confirmation, prompt/model
validation, and existing same-origin/security gates of LI-02. No request
contains an API key, asset path, editor state, or image bytes. The route
does not select a model or trigger from the text-draft endpoint.

Under the existing app-instance lock, validate the canonical project ID,
load P1, compare the expected timestamp, capture it, and read only the P2
OpenAI credential. Release the lock before one synchronous P3 image attempt.
For a completed job, reacquire the lock, re-load the same project ID, and
write the PNG through P1. Do not recheck the timestamp after the provider
call: an asset write is independent of editor state, and the captured
`source_updated_at` tells the caller whether a later editor attachment
would be stale. Never update editor state or project metadata in this route.
If the project was deleted while generating, return 404 without publication.
Do not retry a paid call after provider or local persistence failure.

Both terminal P3 outcomes return HTTP 200 with exactly the five LI-04
fields, matching success/failure nullability, safe failure projection,
and no-store/nosniff/same-origin headers. Non-200 statuses, precedence and
fixed numeric-code envelopes follow LI-04. Neither response nor normal
logs expose prompt, key, image bytes, provider body, native error text,
or project filesystem path.

## Acceptance and deferrals

Cover the full LI-05 unit and integration matrix with fake P2/P3 and
temporary P1 projects. No live OpenAI call, actual credential, user project,
skipped/xfail acceptance test, or backend change outside P6 is allowed.
Run Ruff, scoped formatter check, strict Pyright, full discovered Pytest,
exact diff/import review, and latest-head hosted CI before routine merge.
Produce one P6-007 report and stop for Tech Lead review.

This contract does not authorize image UI controls, automatic generation
from a one-prompt text draft, automatic P7 reference insertion, image edits,
multiple images per request, settings persistence, new providers, or live
paid acceptance testing. A later separately approved UI module must own
visible per-attempt consent and editor attachment behavior.
