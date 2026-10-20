# AURORA

AURORA is a Windows-focused local visual workspace built around the approved
Python Runtime Engine. The browser UI uses React, TypeScript and Vite; the
loopback backend uses Python 3.13 and FastAPI. Architecture Freeze v1.0 and
the approved contracts in `docs/architecture/` define ownership.

## Run on Windows from source

Install Python 3.13, uv, Node 24 and pnpm 11. From the repository root:

```powershell
uv sync --frozen --dev --python 3.13
cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..
uv run --frozen python -m src.launcher
```

The launcher binds a temporary port on `127.0.0.1`, opens the default browser
after readiness and runs in the foreground. Ctrl+C stops it. A source checkout
requires the frontend build above.

## Portable Windows build

The **Portable Windows** GitHub Actions workflow builds a Windows x64 ZIP
containing `AURORA.exe`, its Python runtime dependencies and the compiled UI.
After a successful workflow run, download its `AURORA-Windows-x64` artifact,
extract the ZIP, and run `AURORA/AURORA.exe`. The target PC does not need
Python, uv, Node or pnpm. The app is foreground-only and opens its loopback UI
in the default browser; close it with Ctrl+C in the console. It is an unsigned
portable build, not an installer or a claim of clean-PC acceptance testing.

To create the same ZIP locally on Windows x64 with Python 3.13, uv, Node 24
and pnpm 11 installed, run from the repository root:

```powershell
uv sync --frozen --dev --group build --python 3.13
uv run --frozen --group build python -m scripts.build_windows_bundle
```

The output is `build/portable/AURORA-Windows-x64.zip`. A successful rebuild
atomically replaces only that generated ZIP. No project or credential data is
included. OpenAI generation needs a user-provided key and network access;
Netlify deployment is optional and requires its own token.

The current UI can create and reopen local projects, generate a text-only
brand/site/content/SEO draft from one prompt for explicit review and saving,
or initialize a blank website. It can edit brand/pages/sections/SEO and local
raster images, guide image completion after a saved text draft using visible
editor-derived suggestions and separate paid-call consent for each target,
or generate one image at a time for a logo or section with separate review
and attachment. It can preview the saved static site, save changes, export a
site folder inside the project's `exports/` directory or a ZIP, and explicitly
deploy through Netlify. It persists RU/EN interface choice, model settings and
onboarding completion in separate local application settings, and supports
independently collapsible panels. OpenAI text assist applies only to a selected
section after user review. API keys are stored through Windows Credential
Manager, not persisted in browser storage or project files.

This is **not** the complete one-prompt usable MVP. Image completion is a
guided optional step after accepting the text draft, not an unattended batch.
It offers at most five empty targets and requires user-entered alt text for
section images. Generated PNGs remain stored in the project even when
discarded and count toward its asset quota. The portable ZIP is available,
but the complete clean-PC journey is not yet certified. A generated draft is
not saved until accepted.
The UI does not claim the deferred features exist. OpenAI and Netlify requests
may incur charges or publish content; they run only on explicit user actions.

For a separate clean-PC check of the portable candidate, use the
[Windows MVP acceptance checklist](docs/acceptance/WINDOWS_MVP_ACCEPTANCE.md).
It records the exact artifact and mandatory results; no clean-PC or live-provider
PASS has been recorded yet.

## Validate

```powershell
uv run --frozen ruff check .
uv run --frozen pyright
uv run --frozen pytest
cd frontend
pnpm install --frozen-lockfile
pnpm typecheck
pnpm test
pnpm build
```

Tests include one offline local-app journey from first-use settings through
explicit draft/image acceptance, reopen and export, using temporary projects,
fake credentials and fake provider responses. They do not prove that a live
OpenAI request, Netlify deployment, or the full clean-PC Windows acceptance
path works. Every implementation module requires
its own approved contract and latest-head CI before merge.

The separate Windows browser gate runs the actual React build in Chrome
against an isolated local backend with fake OpenAI responses and fake
credentials. It checks first-run settings, one-prompt text draft review and
acceptance, separate guided image consent/review/attachment, brand/SEO/text
editing, independent panel collapse, desktop/mobile and separate-tab preview,
folder/ZIP export and reopening after reload.
Run it after a frontend build with `cd frontend; pnpm test:browser`. It does
not use real keys or certify image quality, live providers or a clean target PC.
