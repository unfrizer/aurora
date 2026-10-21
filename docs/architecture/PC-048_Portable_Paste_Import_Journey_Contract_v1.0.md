# AURORA — Portable Paste Import Journey Contract v1.0

- Document ID: PC-048
- Status: APPROVED — delegated compilation of ADR-053 under ADR-001
- Date: 2026-10-21
- Module: QA-015 — Portable Paste Import Journey
- Authority: ADR-053; ADR-001/003/044/045/050/051/052;
  PC-039/040/045/046/047

## Exact ownership

QA-015 may create or change only:

```text
docs/architecture/ADR-053_Portable_Paste_Import_Journey_Decision_v1.0.md
docs/architecture/PC-048_Portable_Paste_Import_Journey_Contract_v1.0.md
frontend/e2e/portable-paste-import.spec.ts
.github/workflows/windows-portable.yml  # invoke new spec and verify its project after restart
```

No production source, other test, other workflow, README, dependency,
lockfile, launcher, build script or user project may change.

## Required gate

Run the new spec only after the existing packaged browser journeys against
the same running EXE and isolated profile. Use only synthetic in-memory P7 v1
JSON with null image paths. Malformed paste must cause no project mutation.
With an invalid file selected, the paste action must create one separate new
project with the valid pasted P7 content; preserve all preexisting projects.
Verify saved editor state through the public API, preview the resulting site,
reload and reopen it, and observe no provider, asset mutation, deployment or
external HTTP request. No credential or paid action is involved.

After the workflow's existing process restart, read the same pasted project
through the packaged public API and verify its ID, brand and section body.
Keep all previous ZIP, API, browser and restart checks. The spec skips when
the packaged origin is absent so the source-browser workflow remains green.
Use the existing pinned Playwright dependency. No live ChatGPT or clean-target
claim follows from this gate.

Run frozen frontend install, typecheck, Vitest, Vite build, source browser
tests, Ruff, Pyright and discovered Pytest. Run the packaged spec locally if
a safe isolated portable executable is available; require latest-head hosted
CI, exact scope review and one QA-015 module report before routine merge.
