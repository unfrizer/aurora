# AURORA — Windows Local Launcher Proposal v1.0

- Document ID: ADR-019
- Status: APPROVED — Architecture Authority approved WL-01–WL-05
- Date: 2026-10-09
- Proposed module: APP-001 — Windows Local Launcher and Same-Origin UI Host
- Repository baseline: `ef59ef330598c73d78522a91bd44c5cdcccdf322`

## Decision boundary

ADR-002 requires a Windows desktop-web launch bound only to `127.0.0.1`, a
browser-open action, and one origin for React/Vite UI and Python FastAPI API.
PC-006 reserves socket binding and same-origin UI hosting for a later launcher
contract. P6 now owns its API routes but does not run a server; no frontend
bundle exists yet. This proposal changes no P1/P2/P6 or L0–L8 ownership.

The full Architecture Freeze v1.0 is not present in this checkout. This
proposal is limited to application composition already directed by ADR-002
and PC-006; it cannot settle an incompatible Master Pack fact. APP-001 is a
separate module task only after these decisions are approved and compiled
into PC-013.

## WL-01 — Ownership and public boundary

Proposed implementation scope, and no other files:

```text
src/launcher/__init__.py
src/launcher/desktop.py
src/launcher/server.py
src/launcher/__main__.py
tests/launcher/__init__.py
tests/launcher/test_desktop.py
tests/launcher/test_server.py
tests/integration/test_windows_launcher.py
tests/local_api/test_security.py # one narrow P6 import-consumer admission
pyproject.toml                 # APP-001 dependency declaration only
uv.lock                        # matching resolution only
```

`src.launcher` would export exactly `create_desktop_app` and `run`.
`create_desktop_app(*, project_root: Path, credential_store:
WindowsCredentialStore, allowed_origin: str, ui_root: Path) -> FastAPI`
composes public `src.local_api.create_app` and same-origin UI routes. It
does not bind, open a browser, create a project, read a credential or call
a provider. `run() -> None` is the blocking production entrypoint invoked
by `uv run python -m src.launcher`.

APP-001 may import standard library, FastAPI/Starlette types, Uvicorn, and
only public `src.local_api` and `src.credentials` project gateways. It may
not import P1/P3/P4/P5/P7, a P6/P2 private file, or any concrete Runtime.
No lower owner imports APP-001. One new application dependency, Uvicorn, is
proposed. No tray, native shell, service install or background worker.

## WL-02 — Production root, socket and lifecycle

`run()` is Windows-only. It resolves the project root exactly as
`%USERPROFILE%\Documents\AURORA\Projects\` without consulting project
state. Missing or invalid `USERPROFILE` fails before server startup. The
UI build root is `frontend/dist/`; the later React/Vite contract must
produce it. Missing/invalid `index.html` or `assets/` fails before binding
or browser launch. Tests may use a synthetic bundle; APP-001 does not
create a placeholder production UI.

The launcher asks the OS for a free ephemeral TCP port on `127.0.0.1`,
constructs the exact `http://127.0.0.1:<port>` P6 origin and passes the
already-bound socket to Uvicorn, avoiding a reserve/rebind race. It never
binds `0.0.0.0`, a public adapter, `localhost`, or a fixed port. One
foreground process exits and closes its socket on Ctrl+C or normal
shutdown. Unexpected bind/server errors do not fall back to another
interface. Startup does not read secrets or call OpenAI/Netlify.

After the server is ready, it attempts to open precisely this local URL
in the default browser. Browser failure logs a safe warning with that URL
and leaves the foreground server running. There is no remote fallback or
browser open on import/app construction.

## WL-03 — Same-origin static UI and security

The launcher adds only GET and HEAD at `/` for `frontend/dist/index.html`
and at `/assets/{asset_path:path}` for regular files under
`frontend/dist/assets/`. HEAD returns the same headers without a body.
No SPA catch-all, directory listing, source maps, arbitrary filesystem routes or
project/credential file serving. Traversal, encoded traversal,
symlinks/reparse points and paths escaping the build root are rejected.
Unknown/invalid UI paths return sanitized 404 without reflecting input.
No CDN or development-server fallback.

UI routes attach to the same P6 FastAPI instance after `/api/v1` routes.
P6's exact Host/Origin/request-header middleware and all existing API
behavior remain unchanged. No CORS, cookie, new auth or localhost alias.
Static responses set `Cache-Control: no-store`,
`X-Content-Type-Options: nosniff` and `Referrer-Policy: no-referrer`.
The future UI must call relative `/api/v1` and include
`X-Aurora-Request: 1` for mutations; it must keep secrets out of URLs,
localStorage and generated sites.

## WL-04 — Failures and non-goals

The launcher logs only fixed startup/bind/browser messages and the local
origin, never tokens, project state, prompts or native details that might
contain private paths. Invalid configuration or missing UI build terminates
nonzero without changing projects or credentials. UI asset 404s do not
alter P6's fixed API error envelope. Browser-open failure is not a server
failure.

APP-001 does not implement React screens, generation, image creation,
autosave, settings persistence, folder export, an installer, a Windows
service, remote access, paid calls or live deploy. `frontend/dist/` is a
build artifact owned by the later client module, not APP-001 source.
Launcher completion alone is not ADR-002 usable-Windows acceptance.

## WL-05 — Acceptance and publication gate

Tests use synthetic UI assets, temporary project roots, fake P2 store,
fake browser opener and controlled socket/server boundaries. Cover exact
exports/imports; root/asset/API coexistence; Host and mutation
Origin/header protection; traversal/symlink rejection; missing bundle
and Windows environment failures; actual-port/origin match; loopback-only
bind; readiness-before-browser; browser failure; shutdown/cleanup; and
absence of project/secret/provider effects. Linux CI may exercise the
testable factory with fakes; production `run()` rejects non-Windows.
No real user project, credential, paid API call, Netlify deploy or
uncontrolled browser launch in tests.

Run Ruff, strict Windows/Linux Pyright, full discovered Pytest, exact
scope/import review and latest-head hosted CI. Produce one APP-001 module
report and stop for Tech Lead review. A separate frontend contract must
specify client files, toolchain, screens, HTTP behavior and tests.

## Approval record

On 2026-10-09 the Architecture Authority replied «полностью утверждаю,
дальше» to the explicit request to approve WL-01–WL-05. All five decisions
are approved without amendment. PC-013 compiles their exact APP-001
implementation boundary. This approval does not authorize a real provider
request or waive module review and latest-head CI.

### Approved P6 test-admission correction

The first full APP-001 Pytest run found that the existing P6 AST guard in
`tests/local_api/test_security.py` prohibited every consumer of
`src.local_api`, contradicting the explicitly approved launcher-to-P6
public-gateway dependency. On 2026-10-09 the Architecture Authority replied
«полностью утверждаю, дальше» to the narrow request to amend this ADR and
PC-013 and change only that test. It may recognize exactly
`src/launcher/desktop.py` importing `src.local_api`, while continuing to
reject private P6 imports and every other outside consumer. No P6 source,
other P6 test, API behavior or Runtime ownership change is approved.
