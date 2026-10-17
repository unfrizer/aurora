# AURORA — React User Preferences Client Contract v1.0

- Document ID: PC-029
- Status: APPROVED — delegated compilation of ADR-034 under ADR-001
- Module: UI-006 — Persistent User Preferences Client
- Date: 2026-10-17

## Exact ownership

Only these frontend files may change:

```text
frontend/src/App.tsx
frontend/src/api.ts
frontend/src/types.ts
frontend/src/i18n.ts
frontend/src/components/Onboarding.tsx
frontend/src/components/Settings.tsx
frontend/tests/api.test.ts
frontend/tests/App.test.tsx
```

`frontend/tests/preferences.test.tsx` may be created. ADR-034, PC-029 and a
narrow PC-014 extension note are the only documentation changes. No P6/P8,
launcher, Python test, project/editor schema, other frontend component,
dependency, workflow, README or generated bundle may change.

## HTTP and UI

Use only `GET/PUT /api/v1/preferences` through existing same-origin fetch;
PUT uses the existing mutation header and exact PC-027 body. Validate GET's
five-field snapshot, 64-character lowercase revision and nonempty safe
absolute project path; validate PUT's exact two-field success shape. Do not
persist browser storage or secrets. The pathname is displayed only, never
sent back. 400/409/503 and network/contract failures get localized safe
messages, not raw response text/path or silent reset.

Initial load gates normal app content. Null language shows first-use
onboarding. Saved onboarding completion suppresses the automatic guide on
reopen; the user can reopen it manually. Language selection and guide close
each await a confirmed PUT before advancing. Settings edits remain local
until explicit Save; empty/invalid model IDs cannot be submitted. Successful
save updates App language/models. Failed save retains draft. 409 blocks
automatic retry and provides an explicit reload with discard confirmation;
other errors also require a new user action. No change to project save queues,
paid generation, credentials, export or deploy.

## Acceptance

Deterministic fake-fetch and React tests cover exact HTTP schema/headers,
fresh defaults, persisted reopen, first-use language/onboarding, saved model
use, read-only project path, no browser storage, malformed response fail
closed, damaged-store 503, failed PUT draft retention, 409 no retry and
explicit reload. Run frozen pnpm install, TypeScript, Vitest and Vite build;
also repository Ruff, Pyright and discovered Pytest. Inspect exact diff and
latest-head hosted CI; produce one UI-006 report and stop for Tech Lead
review. This does not claim packaged Windows end-user acceptance.
