# AURORA — React Unload Guard Timing Repair Contract v1.0

- Document ID: PC-024
- Status: APPROVED — delegated under ADR-001, compiled from ADR-030 UG-01–UG-03
- Module: UI-004R — Unload Guard Commit-Timing Repair
- Date: 2026-10-17

## Ownership and dependency boundary

ADR-030 UG-01–UG-03 apply in full. This is a narrow correction to the
approved UI-002/UI-003/UI-004 unload warnings, not a new Wave, Runtime,
browser service or user-facing workflow. Only `frontend/src/App.tsx` and
`frontend/src/components/ImageGeneration.tsx` may change in production.
Existing `frontend/tests/App.test.tsx`,
`frontend/tests/image_generation.test.tsx` and
`frontend/tests/guided_image_completion.test.tsx` may change only if a
non-weakening synchronization adjustment is required. ADR-030 and this
contract are the only documentation files. No other file is authorized.

The UI continues to use the same React and same-origin P6 interfaces.
No new dependency, API call, event vocabulary, project state, path,
provider request or lower-layer import is approved.

## Exact correction

Replace passive-effect timing with layout-effect timing for the existing
`beforeunload` listeners in App and ImageGeneration. Preserve each listener's
existing predicate, body, dependency list and cleanup. The warning must be
active when the rendered pending/candidate state becomes observable, and
must be removed when the state becomes idle or the component unmounts.
Do not use a global listener registry or change unrelated effects.

## Verification and release gate

The previously approved pending, review, guided, discard and idle tests
remain normative. Do not skip, xfail or relax them. Run frozen pnpm install,
TypeScript, all Vitest, Vite build, bundle compatibility; Ruff, strict
Pyright and full discovered Pytest. Review the exact diff. Hosted CI must
pass on the latest head, including both Linux and Windows Frontend, before
routine merge under ADR-003. Report and stop after this module. P6-008
remains separately unmerged until its own latest-head checks pass.
