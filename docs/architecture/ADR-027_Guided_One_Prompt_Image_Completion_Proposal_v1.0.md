# AURORA — Guided One-Prompt Image Completion Proposal v1.0

- Document ID: ADR-027
- Status: APPROVED — Architecture Authority approved GI-01–GI-05 in full on 2026-10-16
- Date: 2026-10-16
- Proposed module: UI-004 — Guided Image Completion After Draft Acceptance
- Repository baseline: `c7a369f1d26b5c74b7b89d41fbe7940f3edd721a`

## Decision boundary

ADR-002 requires a usable one-prompt project with generated images. UI-002
currently creates and explicitly accepts a text-only brand/site/content/SEO
draft. UI-003 can generate and review one image for a saved editor, but its
user-entered prompt and target make that a separate editor action. Neither
contract approves an automatic image batch or a generated image prompt.

This proposal would add a **guided**, optional completion step after the user
accepts and saves the text draft. It would use the existing PC-019 P6 image
command and UI-003's reviewed attachment path. It does not change the text
draft command, P1/P2/P3/P4/P6/P7, L0–L8 ownership, provider policy, or site
schema. The separately APPROVED PC-021 implementation contract compiles the
decisions below for code.

The full Architecture Freeze and Master Pack are not present in this checkout.
If an incompatible frozen rule is found, implementation stops for
reconciliation rather than treating this proposal as higher authority.

## GI-01 — Owner and proposed exact file boundary

UI-004 would own only the React client integration:

```text
frontend/src/App.tsx
frontend/src/components/ImageGeneration.tsx
frontend/src/components/GuidedImageCompletion.tsx  # create
frontend/src/components/Workspace.tsx
frontend/src/i18n.ts
frontend/src/styles.css
frontend/tests/App.test.tsx
frontend/tests/generation.test.tsx
frontend/tests/image_generation.test.tsx
frontend/tests/guided_image_completion.test.tsx   # create
README.md                                         # capability/limit wording only
```

The existing `frontend/src/api.ts` and P6 request/response contracts remain
unchanged. The proposed component is private to the browser app. No backend,
lower Runtime, dependency, lockfile, workflow, launcher, project file, or
unlisted frontend file is in scope. Existing manual image generation remains
available.

## GI-02 — Entry, plan, and bounded cost

After a successful UI-002 **Accept and save**, offer a visible choice to
complete images or go directly to the normal workspace. The choice is not
preselected. An existing saved P7 v1 editor may reopen the guided step from
the workspace; an unsaved, unsupported, or malformed editor may not.

The proposed deterministic plan contains at most five targets: the brand
logo if empty, then the first section without an image in each page in
saved order, stopping after four section targets. Targets are frozen by
page/section IDs when the plan is shown. Existing image references are not
replaced by this flow. The screen discloses the number of initial paid
attempts before any call and warns that explicit retries may add charges.
It does not claim a total price or model availability. The user may skip
the entire plan or any individual target; skipping creates no request.

For each target, the browser proposes an editable image prompt from only
the saved editor language, brand name/tagline, and the target's page and
section headings. The proposed template is exactly:

```text
Logo: Create a brand logo for "{brand.name}". Tagline: "{brand.tagline}". Language: {editor.language}.
Section: Create an image for page "{page.heading}", section "{section.heading}", brand "{brand.name}". Language: {editor.language}.
```

Placeholders are inserted as saved, without escaping, trimming, or an extra
hidden instruction. This visible suggestion is not an OpenAI schema or a
guarantee of image content. The client does not retain or silently transmit
the original business prompt, which UI-002 deliberately keeps only in
memory. It does not use hidden instructions, section body text, user files,
or project paths.
The exact proposed text is visible before consent. It is never silently
truncated: a prompt exceeding PC-019's 8 KiB bound must be edited or skipped.
An empty/invalid prompt cannot trigger a call.

For a section, the user must **enter** nonblank `image_alt` before the paid
attempt and may edit it before attachment. No AI-generated or implicit alt
text is accepted. This preserves UI-003's accessibility rule, although the
guided flow is not a fully hands-off one-click image batch.

## GI-03 — One explicit attempt and review per target

Each image uses UI-003's separate session image model and requires its own
visible charge confirmation immediately before one PC-019 request. The
confirmation states that the proposed prompt context is sent to OpenAI,
one image may incur a charge, a completed PNG is stored even if discarded,
and connection loss can leave the charged outcome uncertain. Cancel makes
no request. There is no background batch, auto-retry, hidden consent,
automatic editor write, or simultaneous paid call.

The saved timestamp is flushed before each request. A completed result is
reviewed as stored but unattached. The user explicitly attaches it through
the existing versioned editor PUT or discards it. Only after a successful
save does the guided flow advance. A discarded asset remains in P1 and
counts toward its quota, as in UI-003. Failure or uncertain transport does
not advance automatically or erase previously attached images. The user
may retry only through a fresh confirmation or skip the target.

The existing UI-003 409 policy applies unchanged: retain the candidate,
reload the latest project, explicitly reselect a current **empty** target
and confirm the attachment against the new timestamp. If no empty target
remains, the user may discard the candidate; it remains stored in P1. After
any successful attachment or reload, the guide reconciles its frozen target
IDs against the latest saved editor rather than advancing a stale index or
adding new targets. The wizard must not silently rebase or overwrite. A
deleted project ends the flow without recreation.

## GI-04 — Session, navigation, and acceptance meaning

The plan and proposed prompts are browser-memory state, not project schema,
global settings, localStorage, sessionStorage, URL, logs, or telemetry. After
close/reopen, the user may start a new plan from the currently saved editor;
already-attached targets are skipped. A partial image set is a valid saved
project and can still be previewed or exported. The UI describes which
targets completed, were skipped, or still need attention; it does not label
the project as fully image-complete when some planned targets remain empty.

While a paid request or unreviewed candidate exists, UI-003's navigation,
mutation, and unload protections remain in force. Leaving the guide at an
idle boundary is allowed without deleting the saved text draft, attached
images, or stored-but-discarded assets. This step does not launch a static
build or deployment.

This decision defines “one prompt” as **one initial business prompt feeding
the accepted text draft, from which image prompts are proposed**. It is not
an unattended generation pipeline: users review each paid image and supply
section alt text. If the Architecture Authority instead requires fully
automatic multi-image generation, that is a different product and backend
contract, not an interpretation silently inserted into UI-004.

## GI-05 — Acceptance and explicit deferrals

Deterministic Vitest/jsdom tests with fake fetch would cover RU/EN labels,
opt-in/skip, bounded ordered ID targets, existing-image exclusion, exact
visible prompt derivation and 8 KiB refusal, user-entered alt, per-attempt
consent and one-call count, strict PC-019 parsing, saved-but-unattached
review, explicit attach/discard, partial completion, reopening from saved
state, 409 reload/reselection, deleted project, safe failed/uncertain
outcomes, navigation/unload protection, and UI-001/002/003 regressions.
No real key, paid request, user project, browser automation, skipped/xfail
acceptance, or claim of live-provider certification is allowed.

Run frozen pnpm install, strict TypeScript, Vitest, Vite build and
PC-013-compatible bundle check; repository Ruff, Pyright and all discovered
Pytest; exact diff/import review and latest-head hosted CI. Produce one
UI-004 module report and stop for Tech Lead review.

This proposal does **not** approve automatic multi-image background jobs,
new P6 routes, silent image attachment, image editing/reference images,
replacing populated slots, persistent settings, folder export, Windows
packaging, live OpenAI acceptance, or another AI provider. UI-004 would
advance but not alone complete ADR-002's full usable-Windows path.

## Approval record

The Architecture Authority approved GI-01–GI-05 in full in the project
conversation on 2026-10-16. This includes the five-target cap,
editor-derived prompt, user-entered section alt, and guided rather than
unattended consent/review flow. PC-021 is the exact UI-004 implementation
contract. The frozen-ID reconciliation above makes GI-02 and GI-03's
combined constraint explicit; it does not replenish the plan after a save
or 409 reload. Approval does not extend to the deferred batch, persistence,
folder export, packaging or live paid calls.
