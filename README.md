# AURORA

Runtime-first UI Engine based on Architecture Freeze v1.0 and the canonical
Engineering Bible / Master Pack v1.1.

## Stack

- Python 3.13
- uv
- Pydantic v2
- Ruff
- Pyright
- Pytest

## Implemented Modules

The repository contains the Wave 1 Kernel and approved in-memory Wave 2–9
runtime modules, plus portable project persistence, a Windows Credential Manager
adapter, and a synchronous OpenAI Responses plain-text adapter.

These are building blocks, not a finished Windows application. The React/Vite
workspace, local FastAPI server, structured business/image generation, static-site
builder/export and Netlify deployment are not implemented yet. Known Kernel
contract gaps are recorded in the pre-MVP audit under `docs/architecture/`.

## Development and Validation

Install Python 3.13 and uv, then run from the repository root:

```powershell
uv sync --frozen --dev --python 3.13
uv run --frozen ruff check .
uv run --frozen pyright
uv run --frozen pytest
uv run --frozen python -m src.main
```

The last command runs the Kernel lifecycle smoke flow and exits; it does not open
a visual workspace. Tests substitute network and credential-manager boundaries
and do not require real OpenAI or Netlify keys. Passing these tests does not
certify a live provider call or the full usable-MVP scenario.

## Architecture Authority

Each implementation module requires an APPROVED canonical contract. Runtime
ownership and dependency direction remain frozen. See `AGENTS.md`, the AB-series
runtime contracts, ADR-001/002 and PC-series application contracts.
