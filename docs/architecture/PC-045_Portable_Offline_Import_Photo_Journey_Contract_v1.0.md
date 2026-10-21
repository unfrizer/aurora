# AURORA — Portable Offline Import and Photo Journey Contract v1.0

- Document ID: PC-045
- Status: APPROVED — delegated compilation of ADR-050 under ADR-001
- Date: 2026-10-21
- Module: QA-013 — Portable Offline Import and Photo Journey
- Authority: ADR-050; ADR-001/002/003/044/045/047/048/049;
  PC-039/040/042/043/044

## Exact ownership

QA-013 may create or change only:

```text
docs/architecture/ADR-050_Portable_Offline_Import_Photo_Journey_Decision_v1.0.md
docs/architecture/PC-045_Portable_Offline_Import_Photo_Journey_Contract_v1.0.md
frontend/e2e/portable-import-photos.spec.ts
.github/workflows/windows-portable.yml  # invoke new spec after existing spec;
                                       # verify imported project after restart
```

No source owner, other test, other workflow, README, dependency, lockfile,
launcher, build script or project data may change.

## Acceptance

Keep the existing packaged ZIP inspection, API save/restart, original
Playwright journey, existing post-browser assertions and final restart
assertions. Run the new spec afterward against that same running EXE and
isolated profile. It must import valid text-only P7 JSON to a distinct new
project, leave the existing smoke project unchanged, show no asset upload
on selection alone, manually attach two synthetic raster files to stable
logo/section targets, verify returned bytes and saved P7 references,
preserve authored `image_alt`, preview and reopen after browser reload.
No provider/deployment mutation or external HTTP request is allowed.

After the existing process restart, read the imported project through the
packaged public API and verify the same identity, body and two image paths.
Never use a real credential or customer file. The spec skips when no packaged
origin is supplied. Use the existing Playwright dependency; no new runtime
dependency or production output.

Run frozen frontend install, typecheck, Vitest and build; source browser
tests; Ruff, Pyright and discovered Pytest. Run the spec against an isolated
portable build when safely available, and require the latest-head Windows
portable CI before merge. Review exact scope and produce one QA-013 report.
