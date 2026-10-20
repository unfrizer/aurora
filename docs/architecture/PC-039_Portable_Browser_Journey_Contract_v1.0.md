# AURORA — Portable Browser Journey Contract v1.0

- Document ID: PC-039
- Status: APPROVED — compiled from ADR-044 under ADR-001
- Module: QA-009 — Portable Browser Journey
- Date: 2026-10-20

## Exact ownership

QA-009 may create or change only:

```text
docs/architecture/ADR-044_Portable_Browser_Journey_Decision_v1.0.md
docs/architecture/PC-039_Portable_Browser_Journey_Contract_v1.0.md
frontend/e2e/portable-journey.spec.ts      # new test only
.github/workflows/windows-portable.yml      # invoke new test inside smoke step only
README.md                                   # verified test scope and limits only
```

The existing PKG-001 build/ZIP/artifact steps, QA-008 API/restart assertions,
QA-002 browser spec/config and all production owners are unchanged. This
contract grants no provider, credential, frontend feature, dependency, release
or deployment ownership.

## Acceptance

After QA-008 verifies API persistence across process restart, pass only that
process's loopback origin to a new Playwright spec and keep the process alive
until the spec finishes. The spec runs on installed Chrome with one worker and
uses a fresh browser context. It must select RU, complete onboarding, open the
single synthetic project, initialize the blank editor, edit and save one text
block, verify the saved preview, download a nonempty static-site ZIP, reload,
and reopen the edited project. It must reject unexpected external HTTP requests
and any generation/deployment mutation. The spec is skipped when the packaged
origin is absent so the existing source-browser gate remains unchanged.

The EXE uses the same isolated temporary `USERPROFILE` and `LOCALAPPDATA` as
QA-008. Because Chrome rejects a redirected `USERPROFILE`, the browser child
may use the hosted runner's original disposable profile only for launch, with
isolated `LOCALAPPDATA` and temporary directory and Playwright's fresh browser
data directory. The EXE's inherited environment must remain isolated. Use the
existing Playwright dependency and Chrome. Do not use real credentials,
provider APIs, user data, or publication. Always stop the test executable and
its children. Run frozen frontend install, TypeScript, Vitest, Vite build, the
source browser spec and the packaged browser spec, plus Ruff, strict Pyright,
all discovered Pytest and a real portable build/smoke. Review the exact diff
and latest-head hosted CI. Routine merge under ADR-003 requires green checks
and no blocking conflict/review. No clean-PC/live-provider acceptance is claimed.
