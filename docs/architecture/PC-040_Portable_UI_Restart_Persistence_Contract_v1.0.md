# AURORA — Portable UI Restart Persistence Contract v1.0

- Document ID: PC-040
- Status: APPROVED — compiled from ADR-045 under ADR-001
- Module: QA-010 — Portable UI Restart Persistence
- Date: 2026-10-20

## Exact ownership

QA-010 may create or change only:

```text
docs/architecture/ADR-045_Portable_UI_Restart_Persistence_Decision_v1.0.md
docs/architecture/PC-040_Portable_UI_Restart_Persistence_Contract_v1.0.md
.github/workflows/windows-portable.yml  # extend the existing smoke step after Playwright only
README.md                                # verified test scope and limits only
```

Do not change PKG-001's build, ZIP inspection or artifact upload; QA-008's
initial API save/restart; QA-009's browser spec and launch isolation; or any
production owner. No new dependency, provider call, credential, publication,
release, or user-data access is authorized.

## Acceptance

After the packaged Chrome journey completes, use its existing loopback API to
assert that the synthetic project's first editor section contains the exact
text saved in that journey and that user preferences record `language: ru` and
`onboarding_completed: true`. Stop only the test executable and children;
restart the same EXE with the same isolated `USERPROFILE` and `LOCALAPPDATA`.
Read the project and preferences again from the restarted origin and assert
the same project ID, editor text, language and onboarding completion. The
browser profile exception from PC-039 must not change the EXE's isolated
environment. Always stop the final test process. Use no real credential,
provider, deployment or user project.

Run repository Ruff, strict Pyright and all discovered Pytest; frozen frontend
install, typecheck, Vitest, production build and source browser gate; and a
real portable build with the exact extended smoke step locally. Review the
diff and latest-head hosted CI. Routine merge under ADR-003 requires green
checks and no blocking conflict or review. This test is not clean-PC or
live-provider acceptance.
