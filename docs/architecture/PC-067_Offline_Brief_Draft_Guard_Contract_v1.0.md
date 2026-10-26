# AURORA — Offline Brief Draft Guard Contract v1.0

- Document ID: PC-067
- Status: APPROVED — delegated compilation of ADR-072 under ADR-001
- Date: 2026-10-26
- Module: UI-024 — Offline Brief Draft Guard
- Authority: ADR-001/003/020/060/069/072; PC-014/055/064

## Exact ownership

UI-024 may create:

```text
docs/architecture/ADR-072_Offline_Brief_Draft_Guard_Decision_v1.0.md
docs/architecture/PC-067_Offline_Brief_Draft_Guard_Contract_v1.0.md
```

It may modify only:

```text
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
```

No backend, other frontend source/test, browser spec, README, workflow,
dependency, lockfile, project file or user data may change.

## Required behavior

The existing blank action retains its current disabled state and trimmed-name
callback when the offline brief is empty. If that transient field has any
characters, activating blank creation shows a synchronous RU/EN warning that
the brief will not be saved in the empty project. The warning must not echo
the brief. Declining leaves the Projects screen, name, brief and other fields
untouched and makes no create/save/provider request. Accepting makes one
ordinary blank create request, never a brief editor save. The separate
UI-023 brief-start action and its public-content confirmation are unchanged.

For every nonempty offline brief, including whitespace and invalid Unicode,
show a **Clear offline brief** button. It clears only that field and performs
no request or clipboard action. Disable it while the Projects screen is busy.
After clearing, blank creation again needs no draft-loss confirmation. Enter
in the shared name input remains inert. No browser storage or new state owner
is permitted.

## Acceptance

Add deterministic EN/RU frontend regressions for cancellation, acceptance,
clear, busy gating and unaffected paths. Preserve existing import, generation,
blank, offline brief and browser journeys. Run frozen pnpm install,
typecheck, Vitest, Vite build, browser tests, Ruff, Pyright and discovered
Pytest. Require exact scoped diff and latest-head hosted CI before routine
merge under ADR-003. Produce one UI-024 module report and stop.
