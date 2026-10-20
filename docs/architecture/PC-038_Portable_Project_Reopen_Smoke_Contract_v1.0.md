# AURORA — Portable Project Reopen Smoke Contract v1.0

- Document ID: PC-038
- Status: APPROVED — compiled from ADR-043 under ADR-001
- Module: QA-008 — Portable Project Reopen Smoke
- Date: 2026-10-20

## Exact ownership

QA-008 may create or change only:

```text
docs/architecture/ADR-043_Portable_Project_Reopen_Smoke_Decision_v1.0.md
docs/architecture/PC-038_Portable_Project_Reopen_Smoke_Contract_v1.0.md
.github/workflows/windows-portable.yml  # smoke step only
README.md                                # verified test scope and limits only
```

The existing PKG-001 build, ZIP inspection and artifact upload remain owned by
PKG-001 and must not change. QA-008 may extend only the executable smoke step;
it gains no production, project-repository, local-API, frontend, dependency,
credential or release ownership.

## Acceptance

On the hosted Windows runner, extract the built ZIP under a fresh temporary
directory. Override `USERPROFILE` and `LOCALAPPDATA` to children of that
directory and suppress the browser launch. Check the packaged executable's
loopback health and UI root, then create and save one synthetic project via its
existing local API using the required same-origin mutation headers. Assert the
saved response. Stop only the test executable and its children, launch the same
executable again with the same isolated profile, and assert that the project ID,
name and saved state reopen unchanged. Always stop the test process.

No real credential, provider, network API, deployment or user project is used.
Keep the existing ZIP privacy checks and artifact upload. Run repository Ruff,
strict Pyright, all discovered Pytest, frozen frontend install, typecheck,
Vitest and production build. Review the exact diff and latest-head hosted CI.
Routine merge under ADR-003 requires green checks and no blocking conflict or
review. This test does not establish clean-PC or live-provider acceptance.
