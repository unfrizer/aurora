# AURORA — Portable Offline Brief Journey Contract v1.0

- Document ID: PC-066
- Status: APPROVED — delegated compilation of ADR-071 under ADR-001
- Date: 2026-10-26
- Module: QA-019 — Portable Offline Brief Journey
- Authority: ADR-001/003/044/045/055/069/070/071; PC-039/040/050/064/065

## Exact ownership

QA-019 may create or change only:

```text
docs/architecture/ADR-071_Portable_Offline_Brief_Journey_Decision_v1.0.md
docs/architecture/PC-066_Portable_Offline_Brief_Journey_Contract_v1.0.md
frontend/e2e/portable-offline-brief.spec.ts
.github/workflows/windows-portable.yml  # invoke the spec and verify after restart
```

No production source, other test/workflow, README, dependency, lockfile,
launcher, build script, project schema, credential or user data may change.

## Required gate

The new spec uses only the packaged app's public loopback API, built UI and
the existing isolated profile from the portable workflow. It first snapshots
existing projects. Enter and cancelled public-content confirmation create no
project. Accepting the warning creates exactly one new project and makes one
versioned editor save. Verify its ID and unchanged synthetic brief, including
whitespace and a line break, with the ordinary blank-editor defaults. All
preexisting projects remain present.

Verify browser preview, UI folder export and downloaded ZIP. Resolve the
export's real path and check its parent under the workflow's isolated project
root and the new project's identity before reading files. Its HTML includes
the brief; ZIP contains only the static site's exact root members and matching
digests, with no project state, settings or credentials. Reload the browser,
reopen the same project and verify the brief is editable. Observe no provider,
credential, generation, deployment, upload or external HTTP request.

In the existing Windows workflow, invoke the new spec after existing portable
specs. Assert the new project and exact brief through the API before and after
the existing process restart without changing earlier smoke checks. The spec
skips locally unless both packaged origin and isolated project root are
provided; the source browser suite must remain green.

Run frozen pnpm install, TypeScript typecheck, Vitest, Vite build, browser
tests, Ruff, Pyright and all discovered Pytest. Require latest-head hosted CI,
exact scope review and one QA-019 report before routine merge.
