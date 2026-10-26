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
extract the ZIP, and run `AURORA/AURORA.exe`. The target Windows OS does not need
Python, uv, Node or pnpm. The app is foreground-only and opens its loopback UI
in the default browser; close it with Ctrl+C in the console. It is an unsigned
portable build, not an installer or a claim of clean-target acceptance testing.

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

The Windows portable CI smoke extracts and runs the actual packaged EXE with
isolated temporary project/settings paths. It checks the bundled UI and local
API, saves a synthetic project, restarts the EXE and verifies that the same
project reopens. Chrome then opens that packaged UI, initializes a blank site,
edits and previews it, downloads a site ZIP and reopens the saved editor.
The smoke then restarts the EXE again and verifies that the browser-saved text
and RU/onboarding preferences survived. This does not exercise real
credentials or providers and is not a clean-target acceptance result.

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

## Start from a brief without an API key

On the Projects screen, enter a project name and paste an ordinary customer
brief into **Business brief for offline start**, then choose **Create project
with brief**. AURORA saves the unchanged text in the first section of a new
editable site. The text is visible in preview and will be included in site
exports or deployment until you edit it; do not enter confidential customer
material. AURORA asks you to confirm this consequence before creation. This
action makes no AI request and needs no OpenAI key. It does not generate
finished site copy, a visual brand, SEO or images: review and edit the starter
in the workspace before building or publishing. If creation or
saving reports an uncertain result, inspect the project list before retrying;
the new project is never automatically deleted.

## Import a text-only site prepared in ChatGPT

This is an optional no-API-key path. In ChatGPT, describe the business and
ask for JSON using the prompt below. In AURORA's Projects screen, enter a new
project name. Either paste the **raw JSON only** (no Markdown or code fences)
into **Paste prepared site JSON** and choose **Import pasted site**, or save
it as UTF-8 (`site.json`) and choose **Import prepared site** after selecting
the file. Both inputs accept at most 1 MiB of UTF-8 JSON and are separate
actions. Import creates a new project; it never replaces an existing one or
contacts OpenAI. Review the
brand, page text and SEO in the editor before building or publishing. An
imported editor is a draft; the existing preview/build checks whether it can
be published. Customer photographs are not imported by this JSON: upload and
attach them separately in the editor. Do not place API keys, secrets, or
private customer material in Git.

For customer photos, open the saved project in the editor and choose
**Project photos**. Select up to 20 local PNG/JPEG/GIF/WebP files (up to 16 MiB
each), then pick a logo or section destination and click **Attach photo** for
each image. Merely selecting files does not upload them. AURORA keeps their
original bytes and does not automatically analyze, compress, or place them.
Unattached selections disappear when the workspace closes or reloads; a
failed editor save can leave an uploaded but unattached asset in the project.

Copy this prompt into ChatGPT, then add your own business brief:

```text
Prepare a text-only AURORA website draft from the business brief below.
Return ONLY a UTF-8 JSON object, without Markdown, comments, HTML or code fences.
Use exactly this structure and these field names; do not add other fields:
{
  "schema_version": 1,
  "language": "ru",
  "brand": {
    "name": "Brand name",
    "tagline": "Short tagline",
    "primary_color": "#4F46E5",
    "secondary_color": "#F59E0B",
    "font_family": "system",
    "logo_path": null
  },
  "pages": [
    {
      "id": "00000000-0000-4000-8000-000000000001",
      "slug": "index",
      "title": "Page SEO title",
      "meta_description": "Page meta description",
      "heading": "Visible page heading",
      "sections": [
        {
          "id": "00000000-0000-4000-8000-000000000002",
          "heading": "Section heading",
          "body": "Section text",
          "image_path": null,
          "image_alt": ""
        }
      ]
    }
  ]
}
Choose "ru" or "en" for language. Write meaningful ordinary text for the
brand, pages, sections and SEO; use 1–8 pages with exactly one "index" slug
and 1–12 sections per page. Use a unique lowercase UUID in the shown format
for every page and section; never reuse the sample IDs. Other page slugs must
be distinct lowercase ASCII URL slugs. Keep logo_path and every image_path
null, even if photographs were supplied in the brief. Use "system", "serif"
or "monospace" for font_family and #RRGGBB colors. Do not include credentials.

Business brief:
[Paste only the brief you are permitted to share here.]
```

This is **not** the complete one-prompt usable MVP. Image completion is a
guided optional step after accepting the text draft, not an unattended batch.
It offers at most five empty targets and requires user-entered alt text for
section images. Generated PNGs remain stored in the project even when
discarded and count toward its asset quota. The portable ZIP is available,
but the complete clean-target journey is not yet certified. A generated draft is
not saved until accepted.
The UI does not claim the deferred features exist. OpenAI and Netlify requests
may incur charges or publish content; they run only on explicit user actions.

For a separate clean physical PC or fresh isolated Windows VM check, use the
[Windows MVP acceptance checklist](docs/acceptance/WINDOWS_MVP_ACCEPTANCE.md).
It records the exact artifact and mandatory results; no clean-target or
live-provider PASS has been recorded yet.

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
OpenAI request, Netlify deployment, or the full clean-target Windows acceptance
path works. Every implementation module requires
its own approved contract and latest-head CI before merge.

The separate Windows browser gate runs the actual React build in Chrome
against an isolated local backend with fake OpenAI responses and fake
credentials. It checks first-run settings, one-prompt text draft review and
acceptance, separate guided image consent/review/attachment, brand/SEO/text
editing, independent panel collapse, desktop/mobile and separate-tab preview,
folder export, downloaded-ZIP member/byte integrity, reopening after reload,
persisted RU/EN language switching and guide replay.
Run it after a frontend build with `cd frontend; pnpm test:browser`. It does
not use real keys or certify image quality, live providers, process restart or
a clean target PC.
