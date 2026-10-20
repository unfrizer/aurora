# AURORA — Offline Browser ZIP Integrity Contract v1.0

- Document ID: PC-037
- Status: APPROVED — compiled from ADR-042 under ADR-001
- Module: QA-007 — Offline Browser ZIP Integrity Journey
- Date: 2026-10-20

## Exact ownership

QA-007 may create or change only:

```text
docs/architecture/ADR-042_Offline_Browser_ZIP_Integrity_Decision_v1.0.md
docs/architecture/PC-037_Offline_Browser_ZIP_Integrity_Contract_v1.0.md
tests/browser/inspect_zip.py          # read-only standard-library test helper
frontend/e2e/local-journey.spec.ts    # downloaded-ZIP assertions only
README.md                             # verified coverage and limits only
```

No application `src/`, other test, browser server, dependency, lockfile,
workflow, generated bundle, credential, user project or release file may
change. Preserve existing QA-002/004/005/006 browser assertions and the
isolated fake-service server.

## Acceptance

The helper accepts only a downloaded ZIP path supplied by the test, opens it
read-only, checks CRC and returns a JSON inventory of member names and SHA-256
digests. It must not extract, execute, stage, delete or rewrite archive data.
The test expects exactly `index.html`, `assets/site.css` and the distinct
referenced raster paths already saved in the editor. Compare every ZIP member
digest with its matching file in the project-local folder export. No enclosing
`dist/`, project-state JSON, settings file, prompt or credential member is
allowed. The test still uses only synthetic assets and fake services.

Run frozen frontend install, TypeScript typecheck, Vitest, Vite build and the
Windows Chrome browser spec, plus repository Ruff, strict Pyright and all
discovered Pytest. Review exact diff and latest-head hosted CI. Routine merge
under ADR-003 requires all checks green and no blocking conflict/review.
Report one QA-007 module and stop.
