# AURORA — Offline Brief Starter Decision v1.0

- Document ID: ADR-069
- Status: APPROVED — delegated browser UI decision under ADR-001
- Date: 2026-10-26
- Module: UI-023 — Offline Brief Starter
- Baseline: Architecture Freeze v1.0; ADR-001/002/003/020/047; PC-006/007/014/042

## Product boundary

A user without an OpenAI key may start with a blank site or import a fully
prepared P7 JSON file. UI-023 adds an explicit third manual starting action:
create a project with the user's ordinary business brief already in the first
section body. This is a deterministic placement of the user's text, not AI
generation, text transformation, SEO generation, image analysis or a claim that
the brief has become finished website copy. The UI and README must state that
the user reviews and edits the starter before building or publishing.

The inserted brief is site content: it appears in preview and in any site
export or deployment until the user removes or edits it. It is not a private
project note. The UI labels this consequence next to the input and requires a
separate confirmation immediately before creation. Declining confirmation
makes no request. Users must not paste confidential customer material into
this public-content field.

The new action is separate from the unchanged **Create project** blank action,
the OpenAI generation path and prepared-JSON import. It uses the same project
name field and its own labeled multiline brief. Entering or editing a brief
has no persistence effect. Only activating **Create project with brief**
creates a project. The brief is inserted verbatim, including surrounding
whitespace and line breaks. No prompt is sent to a provider.

## Owned behavior

Validate the name and brief before confirmation or any request: each must be
nonblank after trimming; UTF-8 limits are 256 bytes for the name and 8 KiB
for the brief; reject unpaired Unicode surrogates. Send only the trimmed name
to the existing P6 create route. After create succeeds, construct the existing
UI-001 blank P7 v1 editor shape in the active RU/EN language and replace only
the first section's empty body with the unchanged brief. Save through the
existing versioned P6 editor route using the new project's `updated_at`.
Verify saved project identity and returned editor content before opening the
workspace. P1/P6/P7 retain ownership of persistence and validation.

One activation makes at most one create and one save request. Prevent duplicate
in-flight activations. Never delete a project automatically if saving or
response verification fails: a new project or its brief may remain on disk.
Keep the user on Projects, refresh the list when possible and show an honest
localized recovery message. An uncertain create result likewise requires the
user to inspect the list before retrying. A list refresh failure after a
verified save does not invalidate that save; open the verified editor and show
the ordinary safe refresh error.

This action does not change the exact UI-001 blank-site initialization command
or any existing import/generation flow. It adds no route, schema, provider,
dependency, Runtime, lower-layer import, browser storage or global state.

## Acceptance

PC-064 names exact files. Verify RU/EN copy, public-content confirmation and
its cancellation, input bounds, verbatim body, one versioned save, verified
result, no paid/provider action, duplicate guard, and honest failure recovery.
Preserve current regressions.
Run frozen frontend install, TypeScript, Vitest, Vite build, browser tests,
Ruff, Pyright and all discovered Pytest. Review exact scope and latest-head
hosted CI before ADR-003 merge. Produce one UI-023 module report and stop.
