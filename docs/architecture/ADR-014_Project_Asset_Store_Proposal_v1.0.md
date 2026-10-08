# AURORA — Project Asset Store Proposal v1.0

**Document ID:** ADR-014
**Status:** DRAFT — Architecture Authority decision required
**Date:** 2026-10-08
**Target module:** P1-002 — Project Raster Asset Store
**Repository baseline:** `a5a8441acc2c109c694e78ed737d550c2fb20890`

## Why this decision is needed

ADR-002 requires generated/uploaded images to survive close/reopen and to
appear in exported sites. PC-001 creates each project's `assets/` directory
but owns only JSON persistence and exposes no asset read/write API. PC-007
stores optional raster references in editor state but intentionally performs
no I/O. PC-004 accepts immutable raster bytes and explicitly refuses to
interpret arbitrary project paths. No approved component currently turns a
saved project reference into bytes for P4.

This proposal extends the **existing project-directory owner** rather than
creating a second path resolver or giving L8 Render/P4 filesystem ownership.
It changes no L0–L8 Runtime, provider integration, P7 schema, or P4 builder.
The decisions below are new public behavior and require explicit approval;
this DRAFT is not implementation authority.

## AS-01 — Ownership and bounded P1 extension

The proposed P1-002 module task would extend the existing
`ProjectRepository` in `src/projects/repository.py`, add
`tests/projects/test_assets.py`, and add a temporary integration test at
`tests/integration/test_project_assets.py`. No new public class, package,
generic filesystem helper, dependency or Runtime would be introduced.
The repository's existing constructor, JSON methods, metadata schema,
project-directory naming, and public gateway remain unchanged.

This is an explicit, narrow extension of PC-001's currently JSON-only
responsibility. On approval, PC-001 must record the extension and PC-008
must compile the exact file/API/test registry before code. P1-002 may
modify only those three source/test files plus ADR-014, PC-001 and PC-008.
No P4/P7/P6 code or existing tests are to change.

## AS-02 — Exact proposed public methods

Add only these methods to the already-public `ProjectRepository`:

```text
write_asset(
    project_id: str,
    data: bytes,
    media_type: Literal["image/png", "image/jpeg", "image/gif", "image/webp"],
) -> str

read_asset(project_id: str, path: str) -> bytes

delete_asset(project_id: str, path: str) -> bool
```

The caller supplies a P1 project ID, never a project directory. The
repository resolves that ID using its existing identity and direct-path
validation. `write_asset` returns a relative reference suitable for
P7/P4, not an absolute filesystem path. `read_asset` returns detached
immutable bytes. `delete_asset` returns whether a file was removed; a
missing valid asset returns `False`. No method mutates editor state,
creates a project, chooses an image model, or interprets image contents
beyond bounded format checks.

## AS-03 — Names, validation and write/read safety

The sole generated reference format is
`assets/<lowercase-sha256-of-bytes>.<extension>`. Media types map to
`.png`, `.jpg`, `.gif`, and `.webp` respectively. Callers cannot
choose a filename or extension. The resulting names fit P4's existing
asset-path grammar. `read_asset` and `delete_asset` accept only that
canonical complete format; absolute, drive, UNC, URI, traversal,
backslash, alternate stream, mixed-case and unrelated names reject.

Input must be exact nonempty `bytes` of at most 16 MiB. The declared
media type and filename extension must match the PNG/JPEG/GIF/WebP
signature. This is not full image decoding or malware scanning; P4 still
independently validates each build input. A project can store at most
256 managed assets and 128 MiB total managed asset bytes, matching P4's
build limits. An idempotent write of already present identical bytes is
allowed at the limit and returns the same reference. No truncation,
implicit conversion, overwrite or silent collision replacement.

Before I/O, resolve the existing project identity and verify that its
`assets/` child is a direct, non-linked directory. Reject linked/reparse
components and unsafe managed target files without following them.
Unrelated entries are ignored and left untouched, not interpreted as
managed assets. A read rechecks the name, regular-file boundary, size,
content digest and signature before returning bytes; corrupt or replaced
files fail safely. A write validates input and capacity before publication,
writes through a same-directory temporary file, flushes it, and publishes
only if the final name is absent; on failure, remove only this invocation's
temporary file. A verified identical existing file is reused. A process
crash can leave an unrecognized temporary entry, which is not automatically
deleted. No recursive deletion, arbitrary path reading, cross-process
transaction, symlink-race security certification or power-loss durability
guarantee is claimed.

Invalid input/corrupt managed data raises the existing Foundation
`ValidationError` with fixed non-sensitive wording. An unknown project
or missing asset raises `FileNotFoundError` on read. Native I/O failures
remain `OSError`; higher HTTP layers must sanitize them before response.
No filename, byte payload, credential or project content is logged.

## AS-04 — Deletion and state-reference boundary

`delete_asset` never edits `state.json`. Before deleting a present
managed asset, it loads the current P1 document and refuses deletion if
any string **value** anywhere in opaque project state exactly equals the
asset reference. This checks references without importing or interpreting
P7. The future editor/API owner must first save a new state that no longer
references the image, then request deletion. If a save succeeds but the
delete fails, an unreferenced asset remains and can be retried. An app
crash between state save and delete can likewise leave an orphan; no
cross-file atomic transaction or concurrent-writer guarantee is claimed.
The method never deletes `assets/`, another project, unknown files, or
other content. Deleting a referenced image or linked target is rejected.

## AS-05 — Acceptance and next integration

Tests use only `tmp_path` and synthetic raster bytes. Cover all four
formats and signature mismatches; deterministic content-addressed names;
idempotence; project-ID isolation; reopen/read byte equality; malformed
paths; linked/reparse directories and files; unknown entries; corrupt
digest/size/signature; 16 MiB, 256-file and 128 MiB boundaries; absent
targets; referenced/unreferenced deletion; validation-before-mutation;
temp cleanup on injected I/O failure; fixed safe errors; and no mutation
of existing P1 JSON state. The integration test saves a P7 image
reference in a temporary P1 project, reopens it, reads typed raster bytes
through P1-002, projects through P7 and builds with P4. No real user
files, provider calls, network, UI or deployment.

Run Ruff, strict Windows/Linux Pyright, full discovered Pytest, final
ownership/import review and required latest-head hosted CI. Produce one
P1-002 module report and stop for Tech Lead review. This task does not
implement upload HTTP, OpenAI image generation, preview, asset garbage
collection, a Windows launcher or React UI. Passing it would close the
filesystem-to-typed-build bridge, not ADR-002 usable-Windows acceptance.

## Decision requested

Architecture Authority approval is requested for **AS-01–AS-05 together**.
Only then may PC-001 be narrowly amended, PC-008 compiled, and P1-002
implemented in a separate module branch/task. If the product instead
requires different asset naming, limits, deletion semantics or a distinct
filesystem owner, that is a new decision rather than an implementation
assumption.
