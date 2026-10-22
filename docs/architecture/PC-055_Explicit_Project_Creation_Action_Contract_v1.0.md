# AURORA — Explicit Project Creation Action Contract v1.0

- Document ID: PC-055
- Status: APPROVED — compiled from ADR-060 under ADR-001
- Date: 2026-10-23
- Module: UI-014 — Explicit Project Creation Action
- Authority: ADR-001/003/020/023/047/051/058/059/060;
  PC-014/017/042/046/053/054

## Exact scope

UI-014 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/tests/App.test.tsx
frontend/e2e/offline-paste-import.spec.ts
```

It may create only ADR-060 and this contract under `docs/architecture/`.
No other production, test, documentation, style, dependency, lockfile,
workflow, launcher or user-data file may change.

## Required behavior

The shared project-name input is not a blank-project submit trigger. Enter
from that input, whether or not the user has typed a business prompt or
prepared import data, performs no P6 create or paid/provider request. The
visible blank-project button remains enabled only for a nonblank name and
when not busy; its pointer and focused-keyboard activation each invoke the
same trimmed-name `onCreate` callback exactly once. Existing generation,
file-import and paste-import buttons remain explicit, separate and unchanged.

Do not alter server routes, P7 schema, import parsing, paid-call consent,
project persistence, browser storage, navigation, language copy, or any
Runtime owner. No auto-selection of a path or hidden form submission.

## Acceptance

Add a deterministic frontend regression and a real-browser regression for
Enter in the shared name field. Preserve all existing project and import
tests. Run frozen frontend install, TypeScript, Vitest, Vite build, browser
tests, Ruff, Pyright and discovered Pytest. Inspect the exact diff and
latest-head hosted CI before ADR-003 merge. Produce one UI-014 module report
and stop.
