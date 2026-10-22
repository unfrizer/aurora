# AURORA — In-App Prepared JSON Guide Contract v1.0

- Document ID: PC-051
- Status: APPROVED — delegated compilation of ADR-056 under ADR-001
- Date: 2026-10-22
- Module: UI-010 — In-App Prepared JSON Guide
- Authority: ADR-056; ADR-001/003/047/051; PC-042/046

## Exact ownership

UI-010 may create or modify only:

```text
docs/architecture/ADR-056_In_App_Prepared_JSON_Guide_Decision_v1.0.md
docs/architecture/PC-051_In_App_Prepared_JSON_Guide_Contract_v1.0.md
frontend/src/prepared_site_prompt.ts
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/prepared_site_prompt.test.ts
frontend/tests/App.test.tsx
```

No other source, test, documentation, workflow, dependency, lockfile,
launcher, project format, generated artifact or user project may change.

## Required behavior

The Projects screen provides a collapsed, keyboard-accessible guide with
localized RU/EN control labels. It displays a read-only selectable prompt
for a text-only P7 v1 JSON document. The example is a valid existing
`EditorDocument` with `schema_version: 1`, exactly one `index` page, distinct
lowercase UUIDs, null asset paths, supported font/colors, ordinary section
text and SEO. The prompt instructs the external preparer to replace sample
values, use 1–8 pages and 1–12 sections per page, keep unique IDs and slugs,
return raw JSON without Markdown, and avoid credentials. Its example language
matches the selected UI language; neither the entered business prompt nor
any other user data is interpolated.

The guide explicitly says that preparation occurs outside AURORA, that
external output needs review, and that customer images are attached
separately. It must not make a provider/network call, write the clipboard,
persist data or trigger the existing import action. The file/paste inputs,
their separate buttons and all existing validation/save semantics remain
unchanged. The template is only guidance, not an automatic JSON repair.

Tests cover both languages, exact parseable example shape, no hidden user
input in the prompt, no mutation from guide interaction, and regression of
the existing import actions. Run frozen pnpm install, typecheck, Vitest,
Vite build, source browser tests, Ruff, Pyright and all discovered Pytest.
Require exact scope review and latest-head hosted CI before routine merge.
