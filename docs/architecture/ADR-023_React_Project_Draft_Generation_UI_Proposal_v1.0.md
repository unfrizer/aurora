# AURORA — React Project Draft Generation UI Proposal v1.0

- Document ID: ADR-023
- Status: APPROVED — Architecture Authority approved UD-01–UD-05 in full on 2026-10-12
- Date: 2026-10-12
- Proposed module: UI-002 — One-Prompt Draft Generation and Acceptance
- Repository baseline: `b8dcb6231a67a2aebd3ea5a48724fa9c3c74e201`

## Decision boundary

ADR-002 requires a one-prompt New Project and Generation experience. ADR-020
and PC-014 approved UI-001 as a manual workspace and explicitly deferred
structured project generation. ADR-021/PC-015 own in-memory text-only draft
composition. ADR-022/PC-016 now approve the same-origin P6 command
`POST /api/v1/projects/{project_id}/generation/draft`, which returns a
candidate without saving it. Existing `PUT /api/v1/projects/{project_id}/editor`
is the only approved acceptance write.

This proposal defines one client-only bridge from UI-001 to those approved
routes. It does not change L0–L8, backend owners, P7 schema, P6 request or
response, model policy, or Architecture Freeze v1.0. The complete Freeze and
Master Pack are not present in this checkout; this proposal cannot replace
them. Its implementation authority is the separate APPROVED PC-017 contract,
compiled after explicit UD-01–UD-05 approval.

## UD-01 — Exact UI ownership and dependencies proposed

UI-002 may change only:

```text
frontend/src/App.tsx
frontend/src/api.ts
frontend/src/types.ts
frontend/src/i18n.ts
frontend/src/styles.css
frontend/src/components/Projects.tsx
frontend/src/components/ProjectGeneration.tsx  # create
frontend/tests/App.test.tsx
frontend/tests/api.test.ts
frontend/tests/generation.test.tsx             # create
README.md                                      # current capability/limit wording only
```

No Python source/test, P1–P7 or PG production file, existing lower Runtime,
dependency, lockfile, CI workflow, launcher, user data or unrelated frontend
component may change. The new component is private to the UI application;
there is no reusable frontend library API or new browser runtime package.
The client uses only relative same-origin P6 HTTP routes through `api.ts`.
Existing blank-project, text-assist, editor, asset, preview, ZIP and Netlify
behaviors remain available and unchanged except for navigation needed to
reach the new generation view.

## UD-02 — One prompt and explicit paid-call consent proposed

The Projects form offers two distinct actions: **Create blank project** and
**Generate from prompt**. The latter collects the project name and one
business prompt; session language and session model come from existing App
state. No browser-supplied key, project ID, editor, instructions or output
schema enters the draft request. The existing name is not silently truncated;
the prompt is not trimmed or rewritten. Before enabling generation, the UI
checks a nonblank name of at most 256 UTF-8 bytes, a nonblank prompt of at
most 8 KiB UTF-8, and a nonblank model. P6 remains authoritative if these
checks differ. Empty prompt keeps the blank-project path available.

An explicit visible confirmation immediately before **each** draft request
states that OpenAI may charge for generation, that this version generates a
text-only brand/site/content/SEO draft, that images are not generated, and
that the result will not be saved until separately accepted. Declining
confirmation performs neither project creation nor provider request for a
new project. Confirming creates an empty project through existing P6 POST,
then sends exactly one draft request with that project's ID and first
`updated_at`, the unchanged prompt, language, model and actual boolean
`confirm_generation: true`. No preflight provider request, automatic retry,
background attempt, stored consent or price estimate is implied.

An existing project with no `editor` key may start the same flow from its
empty workspace. It uses the currently loaded timestamp and requires fresh
confirmation for every attempt. A valid editor hides the action; malformed
or unsupported editor state shows the existing error and cannot be
overwritten. If project creation succeeds but the later draft request fails,
the empty project remains visible for deliberate retry or blank editing;
the UI neither auto-deletes it nor claims that generation succeeded.

## UD-03 — Exact candidate interpretation and explicit acceptance proposed

`api.ts` parses P6 JSON as `unknown`, accepts exactly the five PC-016 keys,
and validates canonical UUID `job_id`, terminal status, source timestamp,
and matching completed/failed shape. A completed candidate must have a
P7 version-one `editor` accepted by the existing `parseEditor`, `failure`
null, and language equal to the requested language. A failed candidate must
have `editor` null and exactly the three safe failure fields, with a category
from P3's approved set (`authentication`, `rate_limited`, `remote`, `network`,
`invalid_response`), string message and boolean retryable. The returned
`source_updated_at` must equal the timestamp sent with the request; a
mismatch or malformed response is an error, never a save attempt.

A completed candidate is shown in a structured review view: brand and
tagline, colors/font, ordered pages with headings, sections and per-page SEO.
React renders all generated text as text, without HTML injection or a local
site preview. P6's saved-project preview route is unavailable until the
candidate is accepted. The view labels the candidate **not saved** and
offers separate **Accept and save** and **Discard** actions. Generation
never calls editor PUT automatically, including after a successful P6 200.

Accept calls the existing `saveEditor(project_id, candidate.editor,
candidate.source_updated_at)` exactly once per user click. Only a successful
P6 response, parsed as the matching project with a valid saved P7 editor,
opens the normal workspace and clears the candidate. A 409 keeps the
candidate in memory, reports a version conflict, blocks blind rebase/force
overwrite and requires an explicit discard/reload decision. Other save
failures also retain the candidate for an explicit retry; no automatic
save retry is allowed. Discard destroys only the in-memory candidate and
does not delete or change the P1 project. Terminal `failed` outcomes show
a localized safe error and an explicit new-attempt option, not an editor.

## UD-04 — Navigation, uncertainty and security proposed

While a paid generation request is pending, the interface shows an honest
single-stage progress state and disables project switching and another
generation click. It must not display fictional business/brand/image/SEO
stage completion from the one synchronous P3 call. Browser close or network
loss may leave the paid request's remote outcome unknown; the UI does not
promise cancellation or automatic recovery. `beforeunload` warns while a
request is pending or a candidate is unaccepted. Leaving a candidate review
requires explicit confirmation and discards only browser memory.

The candidate, prompt and confirmation live only in component memory:
no localStorage/sessionStorage, project state, URL query, browser log,
telemetry or generated site receives them. The OpenAI key remains accessible
to generation only through the existing P2/P6 credential path; the existing
Settings input temporarily handles a user-entered key and clears it after
submission, while generation never reads or retains that key in the browser.
All requests retain UI-001's same-origin relative URL, browser Origin,
`X-Aurora-Request: 1`, no CORS and numeric-error translation. The UI must
not leak raw provider text or exception details in generic errors. A P6
HTTP 200 with `status="failed"` is a terminal failure, never a successful
candidate. A save-time 409 cannot be repaired by replacing the candidate's
source timestamp with the latest project timestamp.

## UD-05 — Tests, gates and explicit deferrals proposed

Deterministic Vitest/jsdom tests with fake fetch cover exact request URL,
body, headers and one-call count; RU/EN; prompt/name UTF-8 bounds; explicit
confirmation and no call on cancel; create-then-generate ordering; existing
empty/valid/malformed editor states; honest pending state; strict malformed
candidate rejection; completed structured review; failed safe outcome;
separate accept/discard; stale timestamp and 409 candidate retention; no
automatic retry, no secret/browser-storage leakage, and unchanged blank
project/editor flows. Test a new-project partial failure leaving the empty
P1 project, and warn on pending/candidate unload. Use only synthetic API
responses: no live OpenAI key or paid call, browser automation, user project,
or skipped/xfail acceptance.

Run frozen pnpm install, strict TypeScript, Vitest, Vite build and
PC-013-compatible bundle check; run repository Ruff, Pyright and all
discovered Pytest; inspect exact diff; require latest-head hosted CI before
routine merge. Produce one UI-002 report and stop for Tech Lead review.

This does **not** approve AI images, persistent global settings, folder
export, installed Windows distribution, model pricing/availability claims,
live OpenAI acceptance, automatic draft saving, whole-project regeneration,
or a multistage generation pipeline. UI-002 still does not meet the full
ADR-002 usable-Windows path.

## Approval record

The Architecture Authority approved UD-01–UD-05 in full on 2026-10-12,
including per-attempt paid-call confirmation, create-then-generate partial
failure, unsaved review with separate acceptance, and stale-candidate
retention without timestamp rebasing. PC-017 compiles these decisions for
UI-002. Approval does not extend to any deferred image, settings, export,
packaging or live-call work.
