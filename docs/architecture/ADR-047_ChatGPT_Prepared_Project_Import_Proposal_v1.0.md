# AURORA — ChatGPT-Prepared Project Import Proposal v1.0

- Document ID: ADR-047
- Status: APPROVED — IM-01–IM-05 explicitly approved by Architecture Authority on 2026-10-20
- Date: 2026-10-20
- Proposed module: UI-007 — Local Text-Only Project Import
- Baseline: Architecture Freeze v1.0, ADR-001/002/003/013/020, PC-007/009/014

## Decision boundary

The owner selected local import of a project prepared in ChatGPT as the next
no-additional-service workflow and explicitly approved IM-01–IM-05. Its
implementation requires the separate approved PC-042 module contract. This
decision does not amend ADR-002's AI-provider policy or claim that a
ChatGPT subscription can be used as an OpenAI API key. A user manually obtains
an import file and selects it in the existing local AURORA UI; AURORA makes no
ChatGPT, OpenAI, or other provider request on this path.

The full Architecture Freeze v1.0 is not present in this checkout. No L0–L8
Runtime, dependency direction, or existing P1/P6/P7/P4 ownership changes are
proposed.

## IM-01 — Ownership and scope

The proposed implementation is one browser-client module. It may modify only:

```text
frontend/src/App.tsx
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
README.md
```

It may create only:

```text
frontend/src/project_import.ts
frontend/tests/project_import.test.ts
```

Its approval record and resulting module contract may also change under
`docs/architecture/`. Existing `frontend/src/types.ts` and `api.ts` are
consumed unchanged. No Python source/test, lower-layer owner, new HTTP route,
dependency, lockfile, launcher, generated artifact, user project, or CI workflow
may change in this module. This import is not a second project repository or
editor-schema owner.

## IM-02 — Import format and validation

The selected local file is a UTF-8 JSON document containing exactly the
existing P7 version-one `EditorDocument` object: `schema_version`, `language`,
`brand`, and `pages`. The user supplies the new project's name in the Projects
screen; the file contains no P1 metadata, outer project state, credentials,
HTML, or deployment data. No new persisted schema or public backend API is
introduced.

Accept at most 1 MiB of file bytes. Reject invalid UTF-8, invalid JSON,
unsupported version, unknown or missing P7 fields, invalid/duplicate IDs,
or a document that fails the existing frontend `parseEditor` check. Reject
non-null `brand.logo_path` or `section.image_path`: a text-only file cannot
claim ownership of project assets that were never uploaded. Treat all imported
text as untrusted data, never as executable HTML or instructions to AURORA.
The existing P6/P7 editor-save route remains the final structural authority;
P4 remains the only static-site publication authority.

An import file is not a complete portable AURORA project archive. Customer
photos are uploaded and attached separately through the existing approved
asset/editor controls. No image analysis, transformation, matching, upload,
generation, or implicit paid call is part of UI-007.

## IM-03 — User action, persistence, and failure

The Projects screen exposes a distinct **Import prepared site** action. After
the user selects a file and confirms the new project name, client-side
validation must succeed before any mutation. The app then calls only existing
same-origin P6 `POST /api/v1/projects` and `PUT /api/v1/projects/{id}/editor`,
in that order, with the returned `updated_at` as the save precondition.

The import always creates a new project. It never replaces or silently merges
an existing project's editor, never writes directly to project files, and
never changes another project's assets. Open the imported workspace only
after the editor save returns and the saved P7 document is parsed. No build,
export, deployment, image generation, or text generation runs automatically.

Invalid files leave the repository untouched. If project creation succeeds but
the editor save fails, do not report import success or automatically delete the
new project. Explain in the UI that a new empty project may remain and can be
opened or removed by the user. An accepted editor remains a draft until the
existing P4 preview/build validates publishability; import must not claim a
successful site build merely from a successful editor save.

## IM-04 — User guidance

The README must provide a copyable ChatGPT prompt that asks for only the P7
v1 JSON shape, lowercase UUIDs for pages/sections, null image paths, and
ordinary text for brand, pages, sections, and SEO. It must state that ChatGPT
output requires review, that import is local and text-only, and that the user
must attach supplied customer photos separately. The instructions must not
ask users to paste API keys, secrets, or private customer data into Git.

## IM-05 — Acceptance and deferrals

Frontend tests must cover valid import; invalid size/encoding/JSON/schema;
non-null asset references; duplicate IDs; no mutation before validation;
create and save failures; exact use of existing P6 routes; no overwrite of an
existing project; saved-state verification; no provider or deployment calls;
and bilingual UI copy. Preserve all existing browser-client regressions.

After approval, compile these decisions into one UI-007 contract, then run
frozen pnpm install, TypeScript typecheck, Vitest, Vite build, repository Ruff,
Pyright, discovered Pytest, exact scope/import review, and required latest-head
hosted CI. Produce one module report and stop under AGENTS.md. A green synthetic
test is not a claim of live ChatGPT integration or clean-target acceptance.

This proposal does not authorize ChatGPT OAuth/plan usage, a ChatGPT plugin,
AI generation from the import file, automatic placement/processing of customer
photos, arbitrary JSON state migration, import into an existing project,
provider switching, or a cloud/multi-user service. Each requires a separate
explicit decision and owned contract.
