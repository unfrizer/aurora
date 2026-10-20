# AURORA — Offline Browser Editor and Preview Contract v1.0

- Document ID: PC-035
- Status: APPROVED — compiled from ADR-040 under ADR-001
- Module: QA-005 — Offline Browser Editor and Preview Journey
- Date: 2026-10-19

## Exact ownership

QA-005 may create or change only:

```text
docs/architecture/ADR-040_Offline_Browser_Editor_Preview_Decision_v1.0.md
docs/architecture/PC-035_Offline_Browser_Editor_Preview_Contract_v1.0.md
frontend/e2e/local-journey.spec.ts     # editor/preview assertions only
README.md                              # verified coverage/limitations only
```

No application source, other test, fake server, dependency, lockfile,
workflow, build artifact, credential, project data or release file may change.
Keep the existing QA-002/004 isolated root, fake credentials and providers,
explicit generation consent and Chrome CI gate intact.

## Browser assertions

After explicit acceptance of the synthetic text and image drafts, edit one
brand field, one page SEO field and the existing section body. Verify the
saved project state and reopen those values after a page reload. Independently
collapse and reopen both workspace side panels. In the saved preview, verify
the text, image and SEO metadata; switch mobile-width and desktop preview
modes, and open the preview in another local browser tab. Verify that the
folder export includes the edited SEO metadata and referenced image.

All assertions use the existing temporary project and fake services. The
preview tab stays on the loopback origin. No provider request, publication,
real profile access, paid action or acceptance certification occurs.

## Validation and delivery

Run frozen frontend install, TypeScript typecheck, Vitest, Vite build and
Windows Chrome browser spec; run repository Ruff, strict Pyright and all
discovered Pytest. Review exact diff and latest-head hosted CI. ADR-003 allows
routine merge only when required checks pass with no blocking conflict or
review. Report one QA-005 module and stop.
