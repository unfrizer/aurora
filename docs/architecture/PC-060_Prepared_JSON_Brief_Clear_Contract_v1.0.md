# AURORA — Prepared JSON Brief Clear Contract v1.0

- Document ID: PC-060
- Status: APPROVED — compiled from ADR-065 under ADR-001
- Date: 2026-10-26
- Module: UI-019 — Prepared JSON Brief Clear
- Authority: ADR-001/003/020/047/056/062/063/064/065;
  PC-014/042/051/057/058/059

## Exact scope

UI-019 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

It may create only ADR-065 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

When the external-preparation brief contains at least one character, render a
localized **Clear brief** button beside the existing brief-copy action. Do not
render it for the empty string. Activation sets only `externalBrief` to the
empty string, resets `guideCopy` to `idle`, and leaves the existing brief-copy
button disabled through its current validator. Disable clear while `busy`.

Changing or clearing the brief invalidates the visible result of any earlier
guide-copy action. If an already-started clipboard write later resolves or
rejects, it must not publish a stale status after that invalidation. Existing
current-value static and brief copies retain their present success/failure
behavior.

Preserve project name, one-prompt input, staged file and its error, pasted JSON,
projects and all persisted state. Clearing performs no clipboard read/write,
validation, import, API/provider/asset call, navigation, browser-storage write,
project mutation, build, export or deployment. Do not change the preparation
template, 8-KiB/Unicode validation, P7 import behavior, dependency graph or any
L0–L8 owner. No new dependency or public API is authorized.

## Acceptance

UI tests cover EN/RU absent and visible states, ordinary/whitespace/invalid
brief recovery, preservation of adjacent inputs, reset of existing copy status,
suppression of stale pending-copy completion, busy-state gating and absence of
project/provider side effects. Preserve every existing test. Run frozen install,
TypeScript, Vitest, Vite build, browser regressions, Ruff, Pyright and all
discovered Pytest. Inspect exact scope and latest-head CI before ADR-003 merge.
Produce one UI-019 module report and stop.
