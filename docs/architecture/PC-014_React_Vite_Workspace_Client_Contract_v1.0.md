# AURORA — React/Vite Workspace Client Contract v1.0

- Document ID: PC-014
- Status: APPROVED — compiled from ADR-020 UI-01–UI-05
- Module: UI-001 — Local Browser Workspace on Existing P6 API
- Date: 2026-10-09
- Authority: explicit Architecture Authority approval of UI-01–UI-05

## Boundary and ownership

ADR-020 UI-01–UI-05 are normative in full. UI-001 is a browser application
client, not an L0–L8 Runtime or a second implementation of any P1–P7 owner.
Only the following files may be created or changed in this module task:

```text
frontend/package.json
frontend/pnpm-lock.yaml
frontend/tsconfig.json
frontend/vite.config.ts
frontend/index.html
frontend/src/main.tsx
frontend/src/App.tsx
frontend/src/api.ts
frontend/src/types.ts
frontend/src/editor.ts
frontend/src/i18n.ts
frontend/src/config.ts
frontend/src/styles.css
frontend/src/components/Onboarding.tsx
frontend/src/components/Projects.tsx
frontend/src/components/Workspace.tsx
frontend/src/components/Settings.tsx
frontend/src/components/ExportDeploy.tsx
frontend/src/components/TextAssist.tsx
frontend/tests/setup.ts
frontend/tests/api.test.ts
frontend/tests/editor.test.ts
frontend/tests/App.test.tsx
.github/workflows/frontend.yml
.gitignore
README.md
```

No existing Python source, Python test, dependency lock, architecture owner,
generated artifact, secret or project data may change. This contract and the
ADR-020 approval record are the only architecture-document changes preceding
UI-001. React/ReactDOM are the only browser runtime dependencies; the exact
build/test-only dependency classes, pnpm lock and Node 24/pnpm 11 gates are
those of UI-01. The frontend uses only the public same-origin P6 HTTP routes.

## HTTP, editor and security contract

UI-02 defines the exact HTTP boundary. Strictly validate unknown JSON before
use; preserve the five P1 metadata fields and opaque outer project state.
Only an explicit blank-site command creates the exact P7 v1 editor document
from UI-02. No implicit migration, project generation, asset generation or
unapproved route is permitted. All mutation requests carry P6's Origin-managed
same-origin browser context and `X-Aurora-Request: 1`; raw raster upload alone
uses its canonical MIME type and bytes. Numeric P6 errors receive safe localized
messages, with only ND-03 recovery IDs shown after uncertain deployment.

UI-03 defines edit confirmation, serialized autosave, 409 draft retention,
reload/decision, navigation warning, immutable edits and pre-action save flush.
P7 remains the schema owner, P1 the persistence and asset owner, and P4 the
static-site publication validator. A client draft must never be presented as
a successfully saved snapshot. The client may not send paid generation or
deployment requests without the distinct explicit user actions in UI-03/04.

UI-04 defines preview sandbox, credential handling, ZIP-only export and
single-attempt explicit Netlify deployment. No browser secret persistence,
project-state secret, provider response leakage, automatic deployment retry,
unsandboxed generated HTML or fake folder-export behavior is permitted.

## Acceptance gate

Implement the UI-05 deterministic frontend test matrix without skipped or
xfail acceptance tests. Run frozen pnpm install, strict TypeScript, Vitest,
Vite production build and check its PC-013-compatible output. Test one built
bundle through the launcher factory using temporary/fake project and credential
boundaries, without a real browser, real project or provider request. Also run
repository Ruff, Pyright and all discovered Pytest. The dedicated frontend CI
must run on Windows and Linux; required latest-head hosted checks must pass
before a routine merge. Inspect the exact diff, produce one UI-001 report and
stop for Tech Lead review.

UI-001 is only the approved manual-workspace subset. Structured one-prompt
brand/site/content/SEO generation, image generation, persisted global settings,
folder export and end-user packaging require separate approved contracts. This
contract cannot override an incompatible fact in the frozen architecture.
