# AURORA — Windows Portable Distribution Contract v1.0

- Document ID: PC-031
- Status: APPROVED — compiled from ADR-036
- Module: PKG-001 — Windows Portable Distribution
- Date: 2026-10-17

## Exact ownership

PKG-001 may create or change only:

```text
docs/architecture/ADR-036_Windows_Portable_Distribution_Decision_v1.0.md
docs/architecture/PC-031_Windows_Portable_Distribution_Contract_v1.0.md
scripts/__init__.py
scripts/build_windows_bundle.py
scripts/launcher_entry.py
packaging/AURORA.spec
tests/packaging/__init__.py
tests/packaging/test_build_windows_bundle.py
.github/workflows/windows-portable.yml
.gitignore                         # generated packaging artifacts only
pyproject.toml                     # isolated PyInstaller build group only
uv.lock                            # corresponding locked resolution only
README.md                          # portable build/run instructions and limits only
```

No `src/`, existing tests, frontend source, other workflow, Runtime owner,
API route or project/credential source may change. The new `scripts` package
is a developer-only build entrypoint, not an importable application gateway.

## Build behavior

`uv run --frozen --group build python -m scripts.build_windows_bundle` runs
only on Windows x64. It invokes frozen-lockfile pnpm install and production
build, validates `frontend/dist/index.html` and permitted flat `assets/`
members, invokes the pinned PyInstaller in one-folder mode, validates its
output and creates `build/portable/AURORA-Windows-x64.zip`. The archive has
one top-level `AURORA/` directory containing `AURORA.exe`, its `_internal/`
dependencies and `_internal/frontend/dist/`. Build artifacts are Git-ignored.
The destination ZIP may be atomically replaced by another successful build;
unrelated files and user data are never deleted or moved.

The PyInstaller specification uses the developer-only
`scripts/launcher_entry.py` entrypoint, which calls the existing public
`src.launcher.run` without changing its behavior. It must not put the
repository `src/` directory on top-level Python's module search path because
that would shadow standard-library `platform`. The specification collects
Uvicorn's dynamic modules and includes only the validated built UI as explicit
data. It does not add a new application
dependency or change launcher behavior. Packaging validation must reject
links/reparse points and unexpected UI files; archive paths must be relative,
deterministic and traversal-free.

## Tests and publication gate

Unit tests use temporary synthetic bundles and fake executable bytes, not
real user profiles, credentials, browser launches or external providers.
They cover UI file allowlisting, missing files, link rejection, archive
layout/content, and failure without replacing a previous archive. The Windows
workflow builds and checks the actual PyInstaller output, launches the
extracted executable against an isolated temporary profile and no-op browser,
checks its loopback health and UI root, and uploads the ZIP as a CI artifact;
it must not create a GitHub Release. Existing Python and frontend workflows
remain required. All latest-head checks must pass before
merge under ADR-003. No clean-PC manual test or live-provider acceptance is
claimed solely from these checks.
