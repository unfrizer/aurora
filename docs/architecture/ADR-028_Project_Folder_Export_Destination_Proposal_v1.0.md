# AURORA — Project Folder Export Destination Proposal v1.0

- Document ID: ADR-028
- Status: APPROVED — Architecture Authority approved FX-01–FX-05 in full
- Date: 2026-10-16
- Proposed first module: P1-003 — Project Export Directory Boundary
- Repository baseline: `36f6882874f1e1c533bc4c4d61be84bd5046c133`

## Decision boundary

ADR-002 requires an Export Folder operation. P4-001 already compiles a
self-contained site and can write a new folder through
`StaticSiteExporter.export_folder`. P6-004 exposes only a ZIP download, and
the browser currently says folder export is unavailable. PC-001 creates a
project-local `exports/` directory but provides no public, validated way for
an application caller to address it. Reconstructing a project path in P6 or
the browser would duplicate P1's ownership and identity checks.

The first approved module below changes P1 only. P6 folder-export HTTP and
React UI require their own later approved contracts and module tasks. PC-022
is the exact P1-003 implementation contract. The full Architecture Freeze and
Master Pack are not present in this checkout; an incompatible frozen fact
requires reconciliation rather than treating this proposal as superior.

## FX-01 — Destination product decision

For the first Windows MVP, **Export Folder** would create a new, self-contained
static-site directory inside the selected project's existing `exports/` child.
It would not ask the browser for an arbitrary filesystem path. This keeps the
artifact with the portable project and avoids accepting an untrusted path
over HTTP. A later UI would disclose the resulting absolute folder path and
offer to copy it; the user can move the exported folder with Windows Explorer.

This is an explicit proposed resolution of ADR-017's deferred destination
question, not an inference from it. Approval means a fixed project-local
destination is acceptable for the first usable version. If the Authority
requires an arbitrary user-selected destination or a native folder picker,
FX-01 must be rejected and a different design approved before code.

Each export would use a newly generated, collision-resistant folder name
within `exports/`. Existing exports, unknown entries, `state.json`, assets,
and site/ would never be overwritten or removed by a new export. The result
contains only P4 build members at its root, without a `dist/` wrapper or
AURORA project metadata. ZIP export remains available independently.

## FX-02 — P1 ownership and exact first-module scope

P1-003 would add exactly one method to the existing public
`ProjectRepository` class:

```text
export_directory(project_id: str) -> Path
```

It returns the absolute, validated existing `exports/` directory for one
loaded P1 project. It neither creates an export nor chooses an output name,
builds a site, interprets editor state, or exposes an HTTP route. P1 retains
ownership of project identity and directory resolution; a future P6 task
would use this public method and pass a new child destination to P4. P4
retains artifact and exclusive-output ownership. No L0–L8 Runtime or lower
owner imports an application consumer.

Proposed P1-003 implementation/acceptance files only:

```text
src/projects/repository.py
tests/projects/test_export_directory.py          # create
tests/integration/test_project_export_directory.py # create
```

The existing `src/projects` gateway, models, constructor, JSON/asset methods,
project naming and format remain unchanged. PC-001 would receive only a narrow
approved-extension note, and a new PC-022 contract would compile FX-01–FX-05
before implementation. No P4, P6, frontend, dependency, workflow, launcher,
or existing test file changes are part of P1-003.

## FX-03 — Validation and failure boundary

`export_directory` would validate the canonical project ID through P1's
existing rules, locate exactly one project, and load its metadata/state to
verify identity and supported format. It then verifies that `exports/` is a
direct, existing, regular directory inside that project, without a symlink,
junction, reparse point, or resolved path escape. It returns a `Path` only
after those checks. It does not follow or inspect unknown export children.

Malformed IDs, ambiguous or invalid project structure, and unsafe `exports/`
raise P1's existing `ValidationError`; an absent project raises
`FileNotFoundError`; native I/O errors remain `OSError`. It returns no
project state, credential, or arbitrary path from caller input. As with
P1-002, this is validation at the call boundary, not a guarantee against a
separate process replacing filesystem components after return. The future
P4 call must independently validate its destination before writing.

## FX-04 — Later composition, not first-module authority

A separate P6-008 proposal/contract would be needed for a same-origin
`POST /api/v1/projects/{project_id}/exports/folder` operation. It would
specify exact request/response schemas, explicit user consent, timestamp
conflict handling, server-chosen new child name, P1/P7/P4 composition,
error translation, local-path disclosure and cleanup policy. No browser
supplied destination would be accepted under FX-01. Another separate UI-005
contract would expose the operation in the React Export/Deploy screen,
including clear display/copy of the created path and existing ZIP fallback.
Neither route nor UI behavior is approved merely by approving P1-003.

An export is a snapshot of saved project state; it must not mutate the
editor, mark a project saved, trigger a paid call, deploy a site, or silently
delete old artifacts. P1's `exports/` directory is an artifact location, not
an alternate canonical project state. Windows packaging and global settings
remain separate MVP work.

## FX-05 — First-module acceptance gate

P1-003 tests would use temporary project roots only. They would cover a
created and reopened project, absolute direct `exports/` result, renamed
project, malformed/missing/duplicate identity, missing/file/linked/reparse
export child, linked project, native I/O failure, unrelated export children,
unchanged JSON/asset contents, and no creation/deletion by the method.
The integration case would prove that a public P4 exporter can accept a new
child destination under the returned parent without importing P4 into P1.
No real user project, provider, credential, deployment, or browser launch.

After approval and compilation of PC-022, run Ruff, strict Pyright and all
discovered Pytest; inspect the exact diff and import direction; require
latest-head hosted CI before routine merge. Produce one P1-003 report and
stop for Tech Lead review. Passing P1-003 alone does not make the Export
Folder UI or the full Windows MVP usable.

## Approval record

On 2026-10-16, the Architecture Authority replied «полностью утверждаю,
дальше» to the explicit request to approve FX-01–FX-05, including the fixed
project-local `exports/` destination in FX-01. PC-022 compiles the exact
P1-003 implementation boundary. This approval does not authorize the later
P6 route, UI, arbitrary folder selection, Windows packaging, or a claim of
complete usable-Windows acceptance.
