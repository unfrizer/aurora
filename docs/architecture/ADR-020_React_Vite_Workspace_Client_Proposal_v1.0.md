# AURORA — React/Vite Workspace Client Proposal v1.0

- Document ID: ADR-020
- Status: DRAFT — product/contract decisions requested; no implementation authority
- Date: 2026-10-09
- Proposed module: UI-001 — Local Browser Workspace on Existing P6 API
- Repository baseline: `7ba3744fc5e82dff323539e77e9b5c21ef5dc618`

## Decision boundary

ADR-002 requires a React + TypeScript + Vite Windows browser UI. PC-013 now
serves a built `frontend/dist/` bundle on the same loopback origin as P6.
PC-006/007/009/010/011/012 approve the existing project, editor, asset,
preview, ZIP and explicit Netlify HTTP boundaries. No approved route yet
performs structured one-prompt project generation, image generation, folder
export or global settings persistence. UI-001 must not pretend those exist.

This is an application client, not a new L0–L8 Runtime. The full Architecture
Freeze v1.0 is not in this checkout; this proposal cannot supersede an
incompatible frozen fact. UI-001 starts only after this ADR is approved and
compiled into PC-014 as a separate module task.

## UI-01 — Ownership, toolchain and publication

Proposed implementation scope, with no backend source or test edits:

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
.gitignore                     # frontend generated files only
README.md                      # Windows build/launch and limitations only
```

React/ReactDOM are the only browser runtime packages. TypeScript, Vite,
Vitest, jsdom, React testing utilities, React/Node type declarations and
the Vite React plugin are build/test-only packages. Pin resolved versions
in `pnpm-lock.yaml`; use the available Node 24 and pnpm 11 toolchain for
development and CI. No CDN, remote font, analytics, router, state store,
CSS framework, generated-site script or second backend dependency.

The client exports no reusable library API. `main.tsx` mounts `App` at `/`;
navigation is in-memory UI state, not deep-link routes (PC-013 has no SPA
catch-all). Vite production build must emit `frontend/dist/index.html` and
only permitted `/assets/` suffixes from PC-013, with no source maps or
root-level favicon. Generated `node_modules/`, `dist/` and coverage files
are ignored, not committed. The source checkout needs a build before
`uv run python -m src.launcher`; a later packaging task may bundle it.

## UI-02 — HTTP and state boundary

All requests use relative same-origin `/api/v1` paths, browser-managed
`Origin`, no CORS and no manually forged Origin header. Mutations set
`X-Aurora-Request: 1`; JSON mutations use `application/json`. Raster
uploads send raw file bytes with one of the four PC-009 MIME types, not
multipart. Parse server JSON as `unknown` and validate the P6/P7 shape
before using it; strict TypeScript has no implicit `any`. The fixed P6
numeric error body is mapped to localized UI messages, never raw provider
or filesystem detail. The ND-03 recovery IDs may be displayed exactly
after a failed Netlify attempt, without automatic retry.

Project list/open/create/delete use only the approved P6 routes. New project
creation sends only a name and receives empty state. UI-001 offers an
explicit **Start blank site** action, not a fake one-prompt generator. On
that action, the browser creates canonical lowercase IDs with
`crypto.randomUUID()` and saves exactly one P7 v1 editor payload through
`PUT /api/v1/projects/{id}/editor`. The initial document is:

```text
schema_version = 1; language = chosen ru/en
brand: project name, empty tagline, #4F46E5, #0F172A, system, null logo
one page: UUID, index slug, project-name title and heading, empty SEO
one section: UUID, heading "О нас" (ru) or "About" (en), empty body, null image,
             empty image_alt
```

This is a visible user command; P7 still generates no IDs or defaults.
Unsupported/malformed existing editor state is shown as an error and never
silently migrated or overwritten. Other top-level project state remains
opaque. Rename uses the existing project PUT with the last loaded state
preserved exactly and `expected_updated_at`; editor mutations use only the
editor PUT. No direct filesystem, P1, P4, P5 or credential access from UI.

## UI-03 — Screens and editing behavior

The module includes session-only RU/EN language choice and replayable
onboarding, Projects/New blank project, structured Workspace, Settings,
selected-block Text Assist, and Export/Deploy. This is a partial ADR-002
experience; no Generation screen may claim a full project pipeline until
its backend contract exists. UI language and model choice remain in memory
for this session; no localStorage/sessionStorage project or secret cache,
and no claim of `%LOCALAPPDATA%` settings persistence.

Workspace has independently collapsible Pages and Inspector/AI panels,
responsive desktop/mobile-width preview, and manual editing of brand
fields, page title/slug/SEO/heading, sections and their order. Page and
section add/delete/reorder use browser UUIDs and immutable client copies;
the `index` homepage slug is fixed and that page cannot be deleted, and
the editor never has zero pages. Text changes are confirmed on blur
or an explicit action, not on each keystroke. Confirmed edits serialize
through one in-flight editor PUT at a time, using the last successful
`updated_at`; Save flushes the same queue. A 409 retains the unsaved draft,
stops automatic retries and requires an explicit reload/decision. Other
failed saves likewise retain the draft and show a safe error. Navigation
away with unsaved data warns the user. Preview/export/deploy first flush
confirmed edits and are blocked if any unsaved draft remains; they use only
the latest successfully saved snapshot, never a local approximation.

Upload/replace/dereference of local raster images use PC-009; deletion
uses its explicit DELETE only after references are saved away, and P1
remains the authority if an asset is still referenced. There is no image
generation or remote-image URL in UI-001. Text Assist calls only the
existing synchronous `/api/v1/generation/text` after an explicit click,
with the configurable session model initialized from ADR-002's general
default. It displays a terminal text result for user review and applies
it to the selected section body only after a second explicit acceptance; no
automatic paid request, whole-project regeneration or schema parsing.

## UI-04 — Preview, secrets, export and deployment

Preview uses the saved P6 `/preview/index.html` URL in a sandboxed iframe
without script permission; the mobile toggle changes only its viewport
width. Open-in-browser uses the same local URL. P6/P4 remain the source
of HTML/CSS and their CSP/escaping rules; UI never inserts project HTML
with `dangerouslySetInnerHTML`.

Settings may inspect, set and delete only the `openai_api_key` and
`netlify_token` credential names via P6. Secret fields use password input,
are cleared after submission, never re-rendered, persisted in the browser
or included in diagnostics. Model ID input is session configuration,
not a project field or new model-policy owner.

Export ZIP sends the saved timestamp to PC-011, downloads only its returned
artifact with a temporary browser object URL, then revokes that URL. No
folder export button claims availability. Netlify deployment requires an
explicit per-attempt confirmation, sends exactly PC-012's body and never
retries on its own. An optional user-entered canonical site ID selects
redeploy; empty site ID requests a new site. On uncertain failure, show
only approved recovery IDs and instruct the user to inspect Netlify
before a new attempt. Project deletion requires the user to type the
project name before the P6 DELETE; no automatic deletion on navigation.

## UI-05 — Validation and deferred acceptance

Frontend CI runs on Windows and Linux: frozen pnpm install, strict
TypeScript check, Vitest with deterministic fake fetch and jsdom, and a
production Vite build whose output is checked against PC-013. Python
Ruff, strict Pyright and all discovered Pytest remain required and must
stay green. UI tests cover RU/EN and onboarding; project CRUD and the
explicit blank editor shape; field/structure operations; serialized
autosave and 409 draft retention; unsafe/unsupported API response
handling; same-origin mutation headers; credential non-retention; raster
upload/dereference; text-assist explicit acceptance; preview sandbox;
ZIP object-URL cleanup; deploy confirmation/recovery/no retry; and panel
collapse/responsive states. At least one built-bundle smoke through
PC-013 uses a fake P2 store and no real user project, paid AI, Netlify
request or uncontrolled browser. No skipped/xfail acceptance tests.

Run scoped frontend checks, repository Ruff/Pyright/Pytest, exact diff and
latest-head hosted CI. Produce one UI-001 module report and stop for Tech
Lead review. UI-001 still does not meet ADR-002 usable-Windows acceptance:
structured one-prompt brand/site/content/SEO generation, image generation,
settings persistence, folder export and packaging need separately approved
owners/contracts. No existing L0–L8 or backend ownership changes here.

## Approval requested

UI-01–UI-05 are one product/implementation decision set. Approval would
authorize compiling PC-014 and implementing UI-001 as its own module.
This DRAFT does not authorize a frontend dependency install or source edit.
