# AURORA — Offline Browser Journey Contract v1.0

- Document ID: PC-032
- Status: APPROVED — delegated compilation of ADR-037 under ADR-001
- Module: QA-002 — Offline Browser Journey
- Date: 2026-10-19

## Exact ownership

QA-002 may create or change only:

```text
docs/architecture/ADR-037_Offline_Browser_Journey_Decision_v1.0.md
docs/architecture/PC-032_Offline_Browser_Journey_Contract_v1.0.md
tests/browser/__init__.py
tests/browser/server.py
frontend/e2e/local-journey.spec.ts
frontend/playwright.config.ts
frontend/package.json          # pinned test-only Playwright dependency/script
frontend/pnpm-lock.yaml        # matching resolution
frontend/tsconfig.json         # test/config typechecking only
frontend/vite.config.ts        # keep browser specs out of Vitest discovery
.github/workflows/browser-e2e.yml
.gitignore                     # browser test artifacts only
README.md                      # verified scope and limits only
```

No `src/`, other test, application frontend source, Python dependency,
existing workflow, build/packaging logic, secret, or user project may change.

## Test server and browser contract

Use only the public launcher composition gateway with the actual Vite build.
Validate that the test data root is a newly created directory below ignored
`build/`; refuse an existing root and refuse a root outside that boundary.
Use process-local fake credentials and fake OpenAI generation methods; a
Netlify attempt must fail before external I/O. Bind a fixed loopback-only
test port with strict same-origin protection and no automatic browser open.
The test may leave its unique ignored data directory for inspection; it must
not delete or alter unrelated paths.

One deterministic Windows/Chrome spec must cover RU onboarding and persisted
preference, explicit fake-key entry, one-prompt draft creation, review before
save, explicit acceptance, editor text save, saved site preview, project-local
folder export, ZIP download, page reload, and reopening the persisted editor.
Confirm that the draft is not stored before acceptance, exported site content
is present, fake credentials are absent from project/settings files, and no
real provider or real user data is used. Do not claim image, live-provider,
clean-PC, or Netlify acceptance from this test.

The Windows CI gate builds the frontend, runs a single browser worker, and
executes the spec against the composed local app. The pinned Playwright
dependency is only a developer/CI test tool. Run frozen pnpm install,
TypeScript, Vitest, Vite build, the browser spec, Ruff, strict Pyright and
all discovered Pytest. Review exact diff and latest-head CI before routine
merge under ADR-003. Report one QA-002 module and stop for Tech Lead review.
