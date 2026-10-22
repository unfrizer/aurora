# AURORA — Portable Offline Paste, Photo and Export Journey Contract v1.0

- Document ID: PC-050
- Status: APPROVED — delegated compilation of ADR-055 under ADR-001
- Date: 2026-10-22
- Module: QA-017 — Portable Offline Paste, Photo and Export Journey
- Authority: ADR-055; ADR-001/003/044/045/050/053/054;
  PC-039/040/045/048/049

## Exact ownership

QA-017 may create or change only:

```text
docs/architecture/ADR-055_Portable_Offline_Paste_Photo_Export_Journey_Decision_v1.0.md
docs/architecture/PC-050_Portable_Offline_Paste_Photo_Export_Journey_Contract_v1.0.md
frontend/e2e/portable-paste-photo-export.spec.ts
.github/workflows/windows-portable.yml  # invoke the new spec; verify it after restart
```

No production source, other test/workflow, README, dependency, lockfile,
launcher, build script, user project or generated source file may change.

## Required gate

Run the new spec after the existing packaged Playwright journeys against the
same running EXE and isolated profile. Use in-memory synthetic P7 JSON and
one synthetic PNG. Preserve every preexisting project. Pasting creates one
new project; selecting the image uploads nothing until manual attachment to
the stable section target. Verify original asset bytes and saved reference.

Use the UI to export a project-local site folder and download a ZIP. Permit
reading the folder only after proving its resolved path is under the workflow's
isolated project root and corresponds to the newly created project. Check
rendered text, SEO and image reference/bytes. Use the existing read-only ZIP
helper to compare exact root members and each digest with the folder, without
project state, settings or credentials in the artifact. Reload and reopen the
same project. Observe no provider, generation, deployment or external HTTP
request; only the explicit local asset upload is permitted.

After the existing EXE restart, read the same project through the packaged
public API and verify its ID, brand, section body and image reference. Keep
all previous ZIP/API/browser/restart assertions. The spec skips unless both
packaged origin and isolated project root are provided. No live ChatGPT,
automatic photo placement or clean-PC claim follows.

Run frozen pnpm install, typecheck, Vitest, build and source browser tests;
Ruff, Pyright and all discovered Pytest. Run an isolated packaged check locally
when safe and require latest-head hosted CI, exact scope review and one module
report before routine merge under ADR-003.
