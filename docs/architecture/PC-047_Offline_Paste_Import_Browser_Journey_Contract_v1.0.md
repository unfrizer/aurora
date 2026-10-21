# AURORA — Offline Paste Import Browser Journey Contract v1.0

- Document ID: PC-047
- Status: APPROVED — delegated compilation of ADR-052 under ADR-001
- Date: 2026-10-21
- Module: QA-014 — Offline Paste Import Browser Journey
- Authority: ADR-052, ADR-001/003/037/047/049/051, PC-032/042/044/046

## Exact ownership

QA-014 may create or modify only:

```text
docs/architecture/ADR-052_Offline_Paste_Import_Browser_Journey_Decision_v1.0.md
docs/architecture/PC-047_Offline_Paste_Import_Browser_Journey_Contract_v1.0.md
frontend/e2e/offline-paste-import.spec.ts
```

No source, existing test, documentation, workflow, dependency, lockfile,
launcher, credential, user project or generated source file may change.

## Required gate

Use only the existing composed browser-test server, actual built UI and
public loopback API with a fresh ignored test root. Reject an occupied
dedicated loopback port and stop the child server after execution. Use a
synthetic in-memory P7 v1 JSON document with null image references; no
external service or real customer data.

The browser spec must show malformed pasted JSON causes no project mutation;
an invalid selected file does not supersede a valid pasted document when the
paste button is chosen; exactly one new project and versioned editor save
persist the pasted P7 document; the saved site previews; and reload/reopen
recovers the same project. Observe no provider, asset upload, deployment or
network request outside loopback. Do not claim a live ChatGPT connection or
clean-target acceptance.

The spec must be discovered by the existing Windows browser CI workflow.
Run frozen pnpm install, TypeScript, Vitest, Vite build, browser tests, Ruff,
Pyright and discovered Pytest. Require latest-head hosted CI, exact scope
review and one module report.
