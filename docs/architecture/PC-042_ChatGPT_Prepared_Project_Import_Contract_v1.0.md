# AURORA — ChatGPT-Prepared Project Import Contract v1.0

- Document ID: PC-042
- Status: APPROVED — compiled from explicitly approved ADR-047 IM-01–IM-05
- Date: 2026-10-20
- Module: UI-007 — Local Text-Only Project Import
- Authority: ADR-047, ADR-001/002/003, PC-007/009/014

## Boundary and ownership

ADR-047 IM-01–IM-05 are normative in full. UI-007 is one browser-client
implementation task, not a new Runtime, provider integration, P1 repository,
P6 route, P7 editor schema, or P4 builder. The active module may modify only:

```text
frontend/src/App.tsx
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
README.md
docs/architecture/ADR-047_ChatGPT_Prepared_Project_Import_Proposal_v1.0.md
docs/architecture/PC-042_ChatGPT_Prepared_Project_Import_Contract_v1.0.md
```

It may create only:

```text
frontend/src/project_import.ts
frontend/tests/project_import.test.ts
```

No other source, test, documentation, dependency, lockfile, CI, or generated
file may change. `frontend/src/types.ts` and `api.ts` remain unchanged. The
client uses their existing P7 parsing and P6 create/save functions.

## Required behavior

Implement the exact ADR-047 IM-02 local-file boundary: at most 1 MiB of
strict UTF-8 JSON containing only an existing P7 v1 `EditorDocument`. The
browser prevalidates its shape and IDs with the existing `parseEditor` function
and rejects all non-null image paths. No filename or MIME claim substitutes
for content validation. Invalid files cause no P6 mutation. Error messages
are localized, fixed and non-sensitive; they never echo imported text.

The user enters a new project name and explicitly selects **Import prepared
site**. With one pending import at a time, call existing `createProject` and
`saveEditor` only after local validation, in that order. The returned
`updated_at` is the optimistic save precondition. Verify the returned saved
editor and project identity before reporting success or opening the workspace.
No existing project can be overwritten or merged. No provider, asset, build,
export or deployment call is triggered.

A server-side save failure after successful create must be reported honestly:
the new empty project may remain and must not be silently deleted. Refresh the
project list when possible so the user can open or remove it. Successful import
means a saved editor draft, not a certified publishable site; existing P4
preview/build remains authoritative. Customer photographs are uploaded and
attached later through existing controls.

README guidance must provide a usable ChatGPT prompt for this exact JSON
shape, explain review and image limitations, and avoid instructions to paste
credentials or private customer data into Git.

## Acceptance

Test ADR-047 IM-05 with deterministic local files and fake P6 responses.
Cover valid import; 1 MiB and UTF-8 boundaries; invalid JSON/schema/IDs;
non-null asset references; no mutation on local rejection; one create and one
versioned editor save on success; save/create failure visibility; new-project
isolation; saved-state verification; no provider/deployment calls; and RU/EN
copy. Preserve all existing frontend regressions.

Run frozen pnpm install, TypeScript typecheck, Vitest, Vite build, repository
Ruff, Pyright and all discovered Pytest. Review exact file scope/imports and
required latest-head hosted CI. Produce one UI-007 module report and stop for
Tech Lead review. No live ChatGPT connection, customer-photo placement,
clean-Windows certification or paid-provider acceptance is claimed.
