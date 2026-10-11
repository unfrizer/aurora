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
requires the frontend build above; there is no installer or prebuilt bundle yet.

The current UI can create and reopen local projects, explicitly initialize a
blank website, edit its brand/pages/sections/SEO and local raster images,
preview the saved static site, save changes, export a site ZIP and explicitly
deploy through Netlify. It supports RU/EN interface choice, onboarding and
independently collapsible panels. OpenAI text assist applies only to a selected
section after user review. The API keys are stored through Windows Credential
Manager, not in the browser or project files.

This is **not** the complete one-prompt usable MVP. Structured brand/site/
content/SEO generation, AI image generation, persisted global settings,
folder export and Windows packaging still need separate approved contracts.
The UI does not claim these features exist. OpenAI and Netlify requests may
incur charges or publish content; they run only on explicit user actions.

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

Tests use temporary projects, fake credentials and fake provider responses.
They do not prove that a live OpenAI request, Netlify deployment or the full
Windows acceptance path works. Every implementation module requires its own
approved contract and latest-head CI before merge.
