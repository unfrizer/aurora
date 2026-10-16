# AURORA — React Image Generation UI Proposal v1.0

- Document ID: ADR-026
- Status: APPROVED — Architecture Authority approved IU-01–IU-05 in full on 2026-10-16
- Date: 2026-10-13
- Proposed module: UI-003 — Reviewed Image Generation in the Workspace
- Repository baseline: `1545d635946a304dbdd12886de85e5abfbd83004`

## Decision boundary

ADR-002 requires generated images in the usable Windows product. ADR-024 and
PC-018 approve one P3 image attempt. ADR-025 and PC-019 approve a separate P6
image command that stores a PNG asset but deliberately does not attach it to
the editor. UI-001 has manual image upload; UI-002 has a text-only one-prompt
draft. Neither UI contract authorizes a paid image call, image review, or
editor attachment of its result.

This proposal defines one client-only bridge to those existing contracts. It
does not change an L0–L8 Runtime, backend owner, route, P7 schema, project
storage, or the frozen dependency direction. The complete Architecture Freeze
and Master Pack are not present in this checkout, so this proposal cannot
supersede an incompatible frozen fact. Implementation requires a separate
APPROVED UI-003 contract after the decisions below are approved.

## IU-01 — Owner and exact implementation files proposed

UI-003 may modify only:

```text
frontend/src/App.tsx
frontend/src/api.ts
frontend/src/types.ts
frontend/src/config.ts
frontend/src/i18n.ts
frontend/src/styles.css
frontend/src/components/Settings.tsx
frontend/src/components/Workspace.tsx
frontend/src/components/ImageGeneration.tsx  # create
frontend/tests/App.test.tsx
frontend/tests/api.test.ts
frontend/tests/image_generation.test.tsx    # create
README.md                                  # current capability/limit wording only
```

The new component is private to the browser application. The client uses
only relative same-origin P6 routes through `api.ts`. No Python source or
test, other frontend component, dependency, lockfile, workflow, launcher,
user data, or lower-owner file may change. The existing UI-001 and UI-002
flows remain available. UI-003 adds no browser persistence, provider client,
registry, background worker, or reusable frontend library API.

## IU-02 — Target, model, prompt, and per-attempt consent proposed

Only a project with a valid **saved** P7 v1 editor may start image generation.
The user chooses either the brand logo or one existing section's image slot
from the workspace. A selected section is identified by its current page ID
and section ID, not by array position. The user enters a nonblank image prompt
of at most 8 KiB UTF-8, without silent trimming, rewriting, or synthesis
from project text. A section image also requires a nonblank user-entered
`image_alt` before attachment; the client does not invent accessibility text.

Settings exposes a separate **session-only image model** initialized to
ADR-002's `gpt-image-2`, independent of the existing text model. The browser
does not persist either model, claim model availability, show a price quote,
or silently substitute a model. A nonblank model is required; P6 remains
authoritative for validation. No OpenAI key is passed through the image form.

Immediately before **each** paid attempt, a visible RU/EN confirmation says
that OpenAI may charge, one image will be generated, the returned PNG will
be stored as a project asset even if the user later declines to attach it,
and network loss may leave the charged outcome uncertain. Cancel sends no
request. Confirming flushes prior confirmed editor saves, requires a clean
saved timestamp, then sends exactly one PC-019 request with the unchanged
prompt and selected model, that timestamp, and actual JSON boolean
`confirm_generation: true`. A new attempt requires new confirmation. There
is no automatic retry, automatic one-prompt image request, or image edit.

## IU-03 — Strict result, review, and attachment proposed

`api.ts` parses the JSON as `unknown` and accepts exactly PC-019's five
response fields. It verifies a canonical job UUID, terminal status, source
timestamp identical to the submitted timestamp, and matching completed or
failed nullability. A completed result requires a canonical
`assets/<lowercase-sha256>.png` path and null failure. A failed result
requires null path and exactly the approved sanitized failure category,
message, and retryable flag. Malformed or mismatched responses are errors,
not candidates.

A completed asset is previewed through the existing same-origin P6 asset
GET and labelled **stored but not attached**. Generation never writes an
editor reference automatically. The review shows the frozen target, prompt
context without logging/persistence, and, for a section, the proposed alt
text. The user explicitly chooses **Attach and save** or **Discard**.
Attachment changes only `brand.logo_path` or the selected section's
`image_path` plus its user-entered `image_alt`, preserving all other editor
fields and opaque outer project state. It uses the existing editor PUT with
the pre-call `source_updated_at`, once per click. Only a successful parsed
P6 save marks the image attached. No static build or deployment is triggered.

Discard clears the browser candidate but does **not** delete the saved asset.
PC-019 may return a content-addressed path already present in the project;
the response cannot prove exclusive ownership of that file. An automatic
DELETE could remove a separately intended, unreferenced asset. The UI
discloses that discarded images remain stored and count toward P1's asset
quota. No asset cleanup or orphan manager is introduced in UI-003. Replacing
an old image likewise does not implicitly delete the old asset; the existing
manual remove/upload behavior is otherwise unchanged.

## IU-04 — Conflict, navigation, and uncertainty proposed

While a paid image request is pending or a completed candidate is awaiting
review, UI-003 blocks editor mutations, project switching, settings/export
navigation, and a second generation click. The pending state describes one
synchronous request, not fictional pipeline stages or cancellability.
`beforeunload` warns about a pending attempt or unreviewed candidate. An
explicit discard is required to leave review; closing the browser can lose
the in-memory candidate but not the P1 asset.

Before first attachment, the UI verifies that its saved editor snapshot and
selected target still match the generation start. The editor PUT uses the
original source timestamp. On HTTP 409, it retains the candidate and asset
path, reports a version conflict, and does not replace the timestamp or
overwrite silently. A separate explicit **Reload and choose target** action
loads the latest project while retaining the candidate in memory. If the
editor is unsupported, attachment remains blocked. Otherwise the user
selects a current logo or section target and explicitly confirms attachment
against the newly loaded timestamp; this is a new user action, never an
automatic rebase or another paid call. Other save failures retain the
candidate for an explicit retry or discard. If the project has been deleted,
the UI cannot attach and must not recreate it automatically.

A terminal P6 `failed` result has no preview or attachment action and shows
only the safe failure vocabulary. Transport loss or an HTTP error after the
request may mean a paid generation or saved asset exists despite no usable
client result; the UI does not promise cancellation, infer a charge, or retry
automatically. Prompt, candidate, asset path, and consent are held only in
memory. They are not put in localStorage/sessionStorage, URLs, logs,
telemetry, generated site content, or credential settings. No raw provider
error or secret is displayed.

## IU-05 — Acceptance and explicit deferrals proposed

Deterministic Vitest/jsdom tests with fake fetch cover RU/EN labels; separate
image-model default and session edits; logo/section target identity; prompt
UTF-8 bounds and unchanged body; clean-save flush; visible per-attempt consent
and cancel; exact same-origin route, headers, body, and one-call count;
strict success/failure parsing; saved-but-unattached preview; required
section alt text; explicit one-click editor attachment and unchanged other
state; discard without DELETE; blocked editing/navigation and unload warning;
409 retention and explicit reload/reselection without another paid call;
deleted/unsupported project, malformed response, safe failures, and uncertain
network outcome. Preserve UI-001/UI-002 regression tests. Use only synthetic
responses and project data: no real credential, paid API call, browser
automation, user project, or skipped/xfail acceptance test.

Run frozen pnpm install, strict TypeScript, Vitest, Vite build and
PC-013-compatible bundle check; repository Ruff, Pyright and all discovered
Pytest; inspect exact diff/import ownership; require latest-head hosted CI
before routine merge. Produce one UI-003 module report and stop for Tech
Lead review.

This proposal does **not** approve automatic image generation from the
one-prompt text draft, a multi-image job, edits/reference images,
transparent-logo guarantees, persistent settings, image-asset garbage
collection, folder export, Windows installer, live provider acceptance,
or a second AI provider. UI-003 alone does not complete ADR-002's full
usable-Windows acceptance path.

## Approval record

The Architecture Authority explicitly approved IU-01–IU-05 in full on
2026-10-16, including retained discarded assets, user-authored section alt
text, and explicit reload/reselection after a 409. PC-020 compiles those
decisions for UI-003. Approval does not extend to the deferred automatic
one-prompt image flow, asset cleanup, settings persistence, or live calls.
