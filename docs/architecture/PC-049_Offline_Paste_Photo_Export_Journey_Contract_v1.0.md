# AURORA — Offline Paste, Photo and Export Journey Contract v1.0

- Document ID: PC-049
- Status: APPROVED — delegated compilation of ADR-054 under ADR-001
- Date: 2026-10-22
- Module: QA-016 — Offline Paste, Photo and Export Journey
- Authority: ADR-054; ADR-001/003/037/042/047/048/049/051/052;
  PC-004/011/032/037/042/043/044/046/047

## Exact ownership

QA-016 may create or modify only:

```text
docs/architecture/ADR-054_Offline_Paste_Photo_Export_Journey_Decision_v1.0.md
docs/architecture/PC-049_Offline_Paste_Photo_Export_Journey_Contract_v1.0.md
frontend/e2e/offline-paste-photo-export.spec.ts
```

No production source, existing test, helper, workflow, README, dependency,
lockfile, launcher, user project or generated source file may change.

## Required gate

Use the existing composed browser-test server, actual built UI and public
loopback API with a fresh ignored test root. Use synthetic P7 v1 JSON and one
synthetic PNG only. Paste and explicitly import into a new project. Select the
image and verify no upload until the user manually attaches it to the section.
Verify the saved editor path and original image bytes.

Through the UI, export the saved site to a project-local folder and download
its ZIP. Verify the folder HTML contains the imported text, SEO and image
reference; its image bytes match the uploaded file. Use the existing read-only
ZIP helper to validate exact root members and digest equality with the folder,
with no project state/settings/credentials. Reload and reopen the same saved
project. Observe no provider, generation, deployment or external network
request; only the explicit local asset upload is allowed. No automatic image
placement or live ChatGPT call is implied.

The new spec must be discovered by the existing Windows browser workflow.
Run frozen pnpm install, TypeScript typecheck, Vitest, Vite build, browser
tests, Ruff, Pyright and all discovered Pytest. Require latest-head hosted CI,
exact scope review and one module report before routine merge.
