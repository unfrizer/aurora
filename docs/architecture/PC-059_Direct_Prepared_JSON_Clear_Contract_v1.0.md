# AURORA — Direct Prepared JSON Clear Contract v1.0

- Document ID: PC-059
- Status: APPROVED — compiled from ADR-064 under ADR-001
- Date: 2026-10-26
- Module: UI-018 — Direct Prepared JSON Clear
- Authority: ADR-001/003/020/047/051/061/064;
  PC-014/042/046/056

## Exact scope

UI-018 may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

It may create only ADR-064 and this contract under `docs/architecture/`.
No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change.

## Required behavior

When the direct prepared-JSON textarea contains at least one character, render
a localized **Clear pasted JSON** button beside the existing explicit paste
import action. Do not render that button for the empty string. Activation sets
only the transient `pastedJson` component state to the empty string, after
which the clear control disappears and the existing paste-import button follows
its current disabled-state rule.

Disable the clear control while `busy` is true. Preserve whitespace as content
until the user explicitly clears it; therefore whitespace-only input shows the
clear control even though the existing import action remains disabled. Preserve
project name, one-prompt input, staged file and its errors, external brief,
guide-copy result, projects and all other local or persisted state.

No validation, import, API/provider/asset call, navigation, clipboard access,
browser-storage write, project mutation, build, export or deploy may occur.
Do not change the import parser, P7 schema, file import, one-MiB limit,
strict-JSON rule, null-asset rule, project creation flow or any L0–L8 owner.
No new dependency or public API is authorized.

## Acceptance

UI tests cover EN and RU labels, absent/visible states, clearing valid and
whitespace-only text, disabled behavior while busy, adjacent-input preservation
and absence of project/provider side effects. Preserve every existing test.
Run frozen frontend install, TypeScript, Vitest, Vite build, browser regressions,
Ruff, Pyright and all discovered Pytest. Inspect exact scope and latest-head CI
before ADR-003 merge. Produce one UI-018 module report and stop.
