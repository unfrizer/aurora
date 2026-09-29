# AURORA — MVP Product & Platform Decisions v1.0

**Document ID:** ADR-002  
**Status:** APPROVED  
**Scope:** First usable Windows MVP  
**Authority:** Architecture Authority product decision, 29 September 2026

## Boundary

This ADR does not change the L0–L8 ownership, RuntimeLayer vocabulary, or
Architecture Freeze v1.0. It approves product requirements that must be
compiled into separate, owned implementation contracts before code is written.

## Application Form

The MVP is a Windows-focused local desktop-web application:

```text
React + TypeScript + Vite browser UI
        ↓ localhost HTTP
Python 3.13 + FastAPI backend
        ↓
AURORA Runtime Engine
```

The backend listens only on `127.0.0.1` and opens the local UI in a browser.
Electron, Tauri, and a native desktop shell are out of scope.

## Persistence and Secrets

Projects live at `%USERPROFILE%\Documents\AURORA\Projects\`, one directory
per project containing `aurora.project.json`, `state.json`, `assets/`, `site/`,
and `exports/`. Global settings live at `%LOCALAPPDATA%\AURORA\settings.json`.
The project state is portable JSON; SQLite is excluded. JSON writes are atomic
through a temporary file replacement. Autosave occurs after confirmed editor
changes and Save remains explicit.

OpenAI and Netlify tokens are stored only in Windows Credential Manager. Raw
tokens must never be stored in projects, settings, source, Git, localStorage,
or a generated site. `OPENAI_API_KEY` is allowed only for developer mode.

## AI, Build, Export, and Deploy

OpenAI is the sole AI provider. Text and structured generation uses the
Responses API with configurable defaults `gpt-5.6-terra` (general) and
`gpt-5.6-sol` (complex); images use `gpt-image-2`. The model values are
configuration, never business-logic constants. The model choices are supported
by the [OpenAI model documentation](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4).

The site output is a self-contained static `dist/` directory. Users can export
a folder or a ZIP that contains `dist/`, never AURORA project state. Netlify is
the only integrated deployment target: build → ZIP → API deploy → poll until
ready → return public URL. Netlify documents this
[ZIP deploy flow](https://docs.netlify.com/api-and-cli-guides/api-guides/get-started-with-api/).

## MVP Experience

The required screens are onboarding (RU/EN), Projects, New Project, Generation,
main workspace/editor, Settings, and Export/Deploy. The workspace has
independently collapsible Project/Pages and Inspector/AI side panels.

The usable acceptance path is: launch → select RU/EN → add OpenAI key → create
one-prompt project → generate brand/site/content/images/SEO → manually edit →
save/close/reopen → build → export folder or ZIP → optionally deploy to Netlify.

Editing includes project rename, brand fields, pages/sections, selected text
regeneration, image generate/upload/replace/delete, per-page SEO, desktop and
mobile-width preview, build/export/deploy.

## Explicit Non-Goals

No native shell, mobile/macOS/Linux packaging, team collaboration, marketplaces,
multiple AI providers, local LLMs, ecommerce/backend sites, CRM/payments,
source-code IDE, Git deployment, custom DNS, or autonomous business operation.

## Required Follow-on Contracts

Before implementation, prepare one approved module contract each for:

1. Project domain and atomic filesystem persistence.
2. Windows Credential Manager secret adapter.
3. OpenAI generation adapter and job/error model.
4. Static-site builder and folder/ZIP export.
5. Netlify deploy adapter.
6. Local FastAPI application API.
7. React/Vite workspace client.

Each contract must name owned files, public API, dependency direction, failures,
and tests. It must not introduce a new L0–L8 Runtime or move existing ownership.
