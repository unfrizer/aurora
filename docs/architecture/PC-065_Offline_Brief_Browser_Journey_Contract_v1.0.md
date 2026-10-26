# AURORA — Offline Brief Browser Journey Contract v1.0

- Document ID: PC-065
- Status: APPROVED — delegated compilation of ADR-070 under ADR-001
- Date: 2026-10-26
- Module: QA-018 — Offline Brief Browser Journey
- Authority: ADR-001/003/037/069/070; PC-006/007/032/064

## Exact ownership

QA-018 may create or modify only:

```text
docs/architecture/ADR-070_Offline_Brief_Browser_Journey_Decision_v1.0.md
docs/architecture/PC-065_Offline_Brief_Browser_Journey_Contract_v1.0.md
frontend/e2e/offline-brief-starter.spec.ts
```

No production source, existing test, helper, workflow, README, dependency,
lockfile, launcher, user project or generated source file may change.

## Required gate

Run the actual built UI in Chrome against a fresh isolated composed backend.
Use one synthetic non-confidential brief with surrounding whitespace and a
line break. Assert the UI states plainly that the brief is visible site content.
Before confirmation, pressing Enter in the project-name field and cancelling
the explicit public-content confirmation must make no create or save request
and leave the project root empty.

After acceptance, assert exactly one project-create and one versioned
editor-save request. Check the persisted P7 v1 editor: one page, the unchanged
first-section body, and the ordinary blank-starter brand/SEO/image defaults.
Check the browser preview contains the brief. Export a static site folder
through the UI and verify its resolved path is within the newly created
project's `exports/` directory; its HTML must contain the synthetic brief.
Reload the browser, reopen the same project and confirm the saved brief is
still available for editing. Observe no credential, generation, deployment,
asset upload or external network request.

The spec must be discovered by the existing Windows browser workflow without
changing it. Run frozen pnpm install, TypeScript typecheck, Vitest, Vite build,
browser tests, Ruff, Pyright and all discovered Pytest. Require latest-head
hosted CI, exact scope review and one QA-018 report before routine merge.
