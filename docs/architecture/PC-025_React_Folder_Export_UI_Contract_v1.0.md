# AURORA — React Folder Export UI Contract v1.0

- Document ID: PC-025
- Status: APPROVED — delegated compilation of approved ADR-002, ADR-028 FX-01–FX-05, and ADR-029 FE-01–FE-05 under ADR-001
- Module: UI-005 — Project-Local Folder Export Controls
- Date: 2026-10-17

## Authority and ownership

ADR-002 requires an Export Folder option. ADR-028 fixes its MVP destination
inside the selected project's `exports/` directory and requires display/copy
of the resulting path. ADR-029 and PC-023 approve the exact P6 operation and
its non-idempotent, single-attempt semantics. This contract only connects the
existing React publication screen to that approved same-origin operation. It
does not change any L0–L8 owner or infer an arbitrary destination picker.

This module may change only:

```text
frontend/src/api.ts
frontend/src/components/ExportDeploy.tsx
frontend/src/i18n.ts
frontend/tests/api.test.ts
frontend/tests/App.test.tsx
README.md                               # current-capability wording only
docs/architecture/PC-025_React_Folder_Export_UI_Contract_v1.0.md
```

No Python source/test, other frontend file, dependency, lockfile, workflow,
launcher, project file, or earlier architecture decision may change. UI-005
owns only browser interaction and response validation; P1 owns project paths,
P4 owns static artifacts, P6 owns HTTP composition, and P7 owns saved-editor
projection. Existing ZIP and Netlify behavior must remain intact.

## Interaction and transport

The Export & Deploy screen presents a distinct Export Folder action alongside
the existing ZIP action. Merely opening the screen sends no folder request.
Each click asks explicit user confirmation that a new folder will be created
inside the project. A cancellation sends no request. After confirmation, the
client flushes the current editor through the existing `ready()` boundary; if
that does not yield a saved timestamp, it sends no export request.

Exactly one same-origin request then uses the approved P6 route:

```text
POST /api/v1/projects/{project_id}/exports/folder
Content-Type: application/json
X-Aurora-Request: 1
{"expected_updated_at": <saved timestamp>, "confirm_export": true}
```

The shared client uses `credentials: same-origin` and `cache: no-store`. It
accepts only a 201 JSON response with exactly one nonempty string field,
`folder_path`. No browser path selection or path reconstruction is permitted.
The returned native absolute path may be displayed as selectable text and
copied through an explicit Copy action. It must never become a URL, provider
payload, log entry, project state, browser storage, or raw error message.

One confirmed request creates a new folder; neither network errors nor 409,
500, or malformed/uncertain responses are automatically retried. The UI must
not show success without a validated response. On failure it uses existing
safe error handling and advises inspecting the project's `exports/` directory
before a deliberate new request, because a lost response may leave an output.
No automatic deletion or folder enumeration is authorized. While an export is
pending, publication actions are disabled to avoid concurrent clicks within
this screen. RU and EN text communicate the fixed destination, new-folder
semantics, and copy/manual-selection fallback if clipboard access fails.

## Acceptance and deferrals

Deterministic frontend tests cover no request on render/cancellation, saved
timestamp flush, one exact confirmed body and same-origin headers, strict 201
response shape, path display/copy, clipboard failure with a selectable path,
pending-action gating, 409/network/malformed failure without auto-retry or
false success, RU/EN labels, and unchanged ZIP/Netlify controls. Use mocks;
do not touch real projects, browser filesystem, providers, or credentials.

Run frozen frontend dependency install, TypeScript typecheck, Vitest, and Vite
build; run repository Ruff, Pyright and all discovered Pytest. Inspect the
exact diff and latest-head hosted checks. Produce one UI-005 module report
and stop for Tech Lead review.

UI-005 does not add Explorer launch, arbitrary destination selection,
enumeration/deletion/download routes, settings persistence, an installer,
automatic retries, a new Runtime, or complete the full Windows MVP.
