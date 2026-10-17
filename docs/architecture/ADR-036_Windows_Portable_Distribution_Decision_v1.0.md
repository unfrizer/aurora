# AURORA — Windows Portable Distribution Decision v1.0

- Document ID: ADR-036
- Status: APPROVED — Architecture Authority approved portable ZIP and PyInstaller one-folder on 2026-10-17
- Module: PKG-001 — Windows Portable Distribution
- Baseline: Architecture Freeze v1.0, ADR-001/002/003/019/020, PC-013/014

## Decision and authority

The Architecture Authority explicitly approved a portable Windows ZIP built
with PyInstaller in one-folder mode, with PyInstaller used only at build time.
There is no MSI installer. This decision closes the packaging deferral in
ADR-019, ADR-020 and PC-013 without changing the Python Runtime Engine,
L0–L8 ownership, local API, project location or credential boundary.

PKG-001 is a build/distribution module, not a new Runtime or application
service. It builds the existing Vite client, freezes the existing Windows
launcher with Python 3.13 and its existing runtime dependencies, includes
only the built client files, and creates a portable ZIP containing the complete
one-folder application. The ZIP can be extracted and `AURORA.exe` run without
installing Python, uv, Node or pnpm on the target Windows machine. Building
the ZIP still requires the approved developer toolchain and network access
for first-time dependency installation.

The existing `src.launcher.server._ui_root()` path is retained: the bundled
`src/launcher/server.py` resolves `frontend/dist` relative to the frozen
module location. A developer-only root-level analysis entrypoint calls the
public `src.launcher.run` gateway so PyInstaller does not put `src/` ahead of
the Python standard library and accidentally shadow standard `platform` with
`src/platform`. It adds no application behavior. No application/runtime
source change is authorized merely for packaging. Build output is never used
as project storage.

## Distribution and security boundary

The target is Windows x64 only. Build on Windows with Python 3.13, uv, Node 24
and pnpm 11; cross-compilation is not claimed. PyInstaller is a separate,
locked build dependency and is not imported by application code. The build
must fail closed if the UI bundle is absent, malformed or contains unsupported
files. It must never package project directories, settings, raw credentials,
`.env`, frontend source, tests, source maps or repository metadata.

The executable retains the existing foreground loopback-only launcher and
default-browser behavior. It adds no auto-update, background service,
privileged installer, code signing claim, provider request, Netlify publish,
new API route, remote access or direct filesystem ownership. A portable ZIP
is not a claim that the full clean-PC ADR-002 user acceptance path has been
manually certified.

CI may create a downloadable workflow artifact for review, but this decision
does not authorize a GitHub Release, public release publication, signed
binary claim or production deployment. Those remain separate actions.

## Acceptance

PC-031 fixes exact file ownership and tests. Run Python Ruff, strict Pyright,
all discovered Pytest tests, frontend typecheck/tests/build, and a Windows
PyInstaller build. Inspect the generated ZIP layout and ensure the packaged
UI is at the path expected by the existing launcher. A Windows CI smoke test
must extract the ZIP, launch its executable with an isolated temporary profile
and a no-op browser handler, verify the loopback health endpoint and UI root,
and stop only that test process. Required latest-head CI must pass before
routine PR merge under ADR-003. Report any unperformed clean-PC or live-provider
acceptance explicitly.
