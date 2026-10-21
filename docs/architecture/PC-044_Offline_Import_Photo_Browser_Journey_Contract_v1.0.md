# AURORA — Offline Import and Photo Browser Journey Contract v1.0

- Document ID: PC-044
- Status: APPROVED — delegated compilation of ADR-049 under ADR-001
- Date: 2026-10-21
- Module: QA-012 — Offline Import and Customer Photo Browser Journey
- Authority: ADR-049; ADR-001/002/003/037/047/048; PC-032/042/043

## Exact ownership

QA-012 may create or modify only:

```text
docs/architecture/ADR-049_Offline_Import_Photo_Browser_Journey_Decision_v1.0.md
docs/architecture/PC-044_Offline_Import_Photo_Browser_Journey_Contract_v1.0.md
frontend/e2e/offline-import-photos.spec.ts
```

No other production, test, documentation, workflow, dependency, lockfile,
launcher, project, credential or generated source file may change.

## Required gate

Use only the existing composed browser-test server, real built UI and public
loopback API with a fresh ignored test data root. Use synthetic in-memory
JSON and PNG files; no external provider, real credential, real customer
asset, network call outside loopback or deletion of unrelated data.

The browser spec must validate that malformed JSON cannot create a project;
valid P7 v1 JSON imports into one new saved project without an API key;
two locally selected photos do not upload until separate manual Attach
actions; logo and section targets are addressed by their current stable
IDs; attached file bytes and editor paths persist; `image_alt` remains
user-authored; the preview serves the saved images; and a reload/reopen
recovers the same project. Observe no provider/deployment request. Retain
existing no-overwrite, versioned-save and byte-preserving product contracts.

The new spec must be discovered by the existing Windows browser CI workflow.
Run frozen pnpm install, TypeScript, Vitest, Vite build, the new browser spec,
Ruff, Pyright and discovered Pytest. Require latest-head hosted CI, exact
scope review and one module report. No clean-target, portable-EXE,
live-provider or automatic-placement claim follows from this test.
