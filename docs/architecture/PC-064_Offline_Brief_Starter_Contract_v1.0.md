# AURORA — Offline Brief Starter Contract v1.0

- Document ID: PC-064
- Status: APPROVED — compiled from ADR-069 under ADR-001
- Date: 2026-10-26
- Module: UI-023 — Offline Brief Starter
- Authority: ADR-001/002/003/020/047/069; PC-006/007/014/042

## Exact scope

UI-023 may create:

```text
frontend/src/offline_starter.ts
docs/architecture/ADR-069_Offline_Brief_Starter_Decision_v1.0.md
docs/architecture/PC-064_Offline_Brief_Starter_Contract_v1.0.md
```

It may modify only:

```text
frontend/src/App.tsx
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
README.md
```

Every other production, test, architecture, dependency, lockfile, workflow,
launcher and user-data file remains outside this module.

## Required implementation

The new browser helper validates name and brief with ADR-069's bounds and
constructs a detached editor from the existing `blankEditor`. It may not add
new editor fields or derive site copy, brand, SEO, images or model policy from
the brief. The only difference from a fresh blank editor is that the first
section body equals the user's brief exactly.

The Projects screen renders a distinct labeled textarea and button inside the
manual path. Disable the button when busy or local validation fails. Use
`type="button"` so Enter in the shared name field does not create anything.
Display fixed RU/EN copy stating the text is placed unchanged, visible in
preview and site exports, and must be edited before publishing if it contains
internal details. Do not imply that it is a private note, AI generation or a
completed site. Before any create request, require an explicit confirmation
that repeats the public-content consequence. Declining it makes no request.

The App revalidates on activation and guards concurrent starts. Call existing
`createProject(trimmedName)` then `saveEditor(projectId, editor, updatedAt)`.
Parse the saved editor, compare every field with the sent editor and verify
the project ID before opening it. The successful flow refreshes the project
list and opens the saved workspace. A failure after attempting create shows
an uncertain-create message; a failure after receiving create shows an
uncertain-save message. Neither failure auto-deletes or automatically retries.
Keep the Projects screen visible for recovery. The messages never include
brief text, paths or provider diagnostics.

No credential, model, AI text/image, asset, build, export, deploy, browser
storage or new API route is permitted. Apart from the named create, save and
list routes, no API call is permitted. Existing blank, import and OpenAI
actions keep their current behavior.

## Acceptance

Test input boundaries and explicit action, EN/RU labels, confirmation and
cancellation, exact brief content, one create/save with optimistic timestamp,
saved-state verification, duplicate guard, create/save failure recovery and
absence of provider effects. Preserve all regressions. Run frozen install,
TypeScript, Vitest, Vite build, browser tests, Ruff, Pyright and all discovered
Pytest. Review diff and latest-head hosted CI before ADR-003 merge. Produce
one UI-023 module report and stop.
