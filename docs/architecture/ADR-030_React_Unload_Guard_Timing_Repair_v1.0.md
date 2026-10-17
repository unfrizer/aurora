# AURORA — React Unload Guard Timing Repair v1.0

- Document ID: ADR-030
- Status: APPROVED — delegated local defect reconciliation under ADR-001
- Date: 2026-10-17
- Module: UI-004R — Unload Guard Commit-Timing Repair
- Baseline: `31b335e5219eea71e16cb8c71710ef86e84f7c91`

## Evidence and authority

ADR-023 UD-04, ADR-026 IU-04 and ADR-027 GI-04 already require an unload
warning while a paid attempt or unaccepted draft/image candidate exists.
The current React components install their `beforeunload` handlers in
passive `useEffect`. On PR #51's unchanged frontend, three Ubuntu CI
attempts failed at immediate `defaultPrevented` assertions in three
different existing tests; the corresponding Windows jobs passed. The UI
can render a protected state before the passive effect installs its
handler. This is a local timing defect in an existing approved behavior,
not a new product decision or a reason to weaken CI.

ADR-001 delegates implementation-contract maintenance when consistent with
approved decisions. This repair narrows the render-to-guard gap without
altering L0–L8, ownership, routes, paid-call semantics, editor state or
the definition of a protected state. PC-024 is the exact module contract.

## UG-01 — Exact scope

The module may change only the two browser components that own the unload
listeners and, if required, their existing acceptance tests:

```text
frontend/src/App.tsx
frontend/src/components/ImageGeneration.tsx
frontend/tests/App.test.tsx
frontend/tests/image_generation.test.tsx
frontend/tests/guided_image_completion.test.tsx
```

This ADR and PC-024 are the only documentation changes. No P6-008 branch
file, other frontend source/test, backend, dependency, lockfile, workflow,
launcher or project data may change.

## UG-02 — Preserve the approved guard, close the gap

Install and remove the existing `beforeunload` callbacks with React's
layout-effect timing in App and ImageGeneration. Keep the exact risk
conditions, callback action, dependencies and cleanup. A protected state
must have its warning handler attached at commit before the user can act on
the rendered state. An idle state must not retain a stale warning handler.
Do not introduce a global event manager, new state, persistence or altered
navigation/paid-call behavior.

Tests must continue to assert warning in the existing pending/review states
and no warning after normal cleanup. If synchronization in an acceptance
test itself proves necessary, it may only wait for an observable state; it
must not skip, xfail, delete or weaken an assertion.

## UG-03 — Acceptance and sequencing

Use the existing synthetic jsdom/fake-provider tests only. Run frozen pnpm
install, TypeScript, Vitest, Vite build and launcher-compatible bundle
check; repository Ruff, strict Pyright and all discovered Pytest. Inspect
exact scope and imports. Require latest-head hosted CI on Ubuntu and
Windows before routine merge. Produce one UI-004R module report and stop.

PR #51 remains a separate P6-008 module. Its failed frontend check is not
waived by this repair. After UI-004R merges, P6-008 still needs its own
latest-head required checks before merge. UI-005 folder-export controls
remain a later, separately contracted module.
