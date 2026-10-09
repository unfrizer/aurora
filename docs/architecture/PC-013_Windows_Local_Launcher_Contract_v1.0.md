# AURORA — Windows Local Launcher Contract v1.0

- Document ID: PC-013
- Status: APPROVED — compiled from ADR-019 WL-01–WL-05
- Module: APP-001 — Windows Local Launcher and Same-Origin UI Host
- Date: 2026-10-09

## Authority and boundary

ADR-019 WL-01–WL-05 are incorporated in full following explicit Architecture
Authority approval on 2026-10-09. AGENTS, ADR-001/002/003 and PC-001/002/006
remain in force. APP-001 is application composition outside L0–L8. It does
not change P6 or create a frontend, Runtime, credential owner, project owner
or provider integration. The full Architecture Freeze is not in this checkout;
this contract cannot supersede an incompatible frozen fact.

## Exact file ownership

Only these implementation/acceptance files are authorized:

```text
src/launcher/__init__.py
src/launcher/desktop.py
src/launcher/server.py
src/launcher/__main__.py
tests/launcher/__init__.py
tests/launcher/test_desktop.py
tests/launcher/test_server.py
tests/integration/test_windows_launcher.py
tests/local_api/test_security.py # exact public-gateway admission only
pyproject.toml                 # Uvicorn dependency only
uv.lock                        # matching dependency resolution only
```

ADR-019 approval record and this contract are the only documentation
changes. No P1/P2/P6 source or test, existing Runtime, frontend, workflow,
README or other file may be edited, except for the explicitly approved
`tests/local_api/test_security.py` admission above. That guard must accept
exactly one outside consumer, `src/launcher/desktop.py` importing only the
public `src.local_api` gateway, and preserve all other prohibitions.
`src.launcher` exports exactly
`create_desktop_app` and `run` with ADR-019's signatures; `__main__` invokes
`run()` only under module execution. Production project imports are limited
to public `src.local_api` and `src.credentials` gateways. Uvicorn is the sole
new dependency; no client toolchain or unapproved provider package.

## App composition and static boundary

`create_desktop_app` calls P6's public `create_app` unchanged using the
caller-supplied project root, credential store and exact origin. It validates
the supplied built UI root and adds only GET/HEAD `/` and
`/assets/{asset_path:path}`. HEAD has GET's status and headers, no body.
Only regular, nonlinked build files can be served; traversal, encoded
traversal, reparse points, path escapes, source maps, unsupported file types
and every nonapproved UI path are 404. It exposes no directory listing or
project data. The accepted asset suffixes are `.js`, `.css`, `.png`, `.jpg`,
`.jpeg`, `.gif`, `.webp`, `.ico`, `.woff` and `.woff2`; active SVG and all
other suffixes are not served. File reads are request-local; no mutable global cache. Static
responses carry the three ADR-019 safety headers. P6's Host/Origin/header
middleware and API error behavior remain intact for the composed instance.
The factory has no socket, browser, project, credential or provider effect.

## Production startup

`run()` rejects non-Windows. It validates a real absolute USERPROFILE and
the fixed `Documents/AURORA/Projects` default, then the repository
`frontend/dist` bundle. It does not create this bundle. It constructs a
WindowsCredentialStore without reading a secret, pre-binds one ephemeral
socket on `127.0.0.1`, passes that same socket to Uvicorn and supplies its
actual port in P6's allowed origin. It opens that URL in the default browser
only after Uvicorn readiness. A false/failed browser-open logs a sanitized
warning and does not stop the foreground server. Startup or server failure
closes the socket, exits nonzero, and never falls back to another interface.
Ctrl+C/normal exit cleanly stops the server. No background resident service.

## Acceptance gate and deferrals

Tests cover ADR-019 WL-05 with temporary/synthetic assets, temporary project
roots, fake credential and browser boundaries, and a controlled server.
They must not access real user projects or credentials, launch an uncontrolled
browser, call OpenAI/Netlify, or publish a site. Windows and Linux CI use
strict Pyright and discovered tests; production run rejects Linux while the
factory remains testable with fakes. No skips or xfails. Run Ruff, Pyright,
full Pytest, exact diff/import review and latest-head CI. Produce one APP-001
module report and stop for Tech Lead review. Missing `frontend/dist` means
APP-001 cannot yet provide the ADR-002 usable-Windows experience; frontend,
generation, image creation, autosave, settings and installer remain separate.
