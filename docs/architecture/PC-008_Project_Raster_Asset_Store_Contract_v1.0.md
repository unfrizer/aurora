# AURORA — Project Raster Asset Store Contract v1.0

**Status:** APPROVED
**Module:** P1-002 Project Raster Asset Store
**Authority:** ADR-014 AS-01–AS-05 (approved 2026-10-08), PC-001
**Dependency:** Existing P1-001 project repository, Foundation validation

## Ownership and files

P1-002 extends the existing ProjectRepository owner. It is an
application service, not an L0–L8 Runtime. The implementation task may
modify only `src/projects/repository.py` and create
`tests/projects/test_assets.py` and
`tests/integration/test_project_assets.py`. It may not modify P4, P7,
P6, another production module, existing tests, dependencies, or the
public `src.projects` gateway. The existing constructor, JSON API,
metadata schema, directory naming and persistence semantics remain
unchanged. This is PC-001's explicit, narrow asset extension, not a
second project-path owner.

## Public methods

Add exactly these methods to ProjectRepository:

```python
def write_asset(
    self,
    project_id: str,
    data: bytes,
    media_type: Literal["image/png", "image/jpeg", "image/gif", "image/webp"],
) -> str: ...

def read_asset(self, project_id: str, path: str) -> bytes: ...

def delete_asset(self, project_id: str, path: str) -> bool: ...
```

The caller supplies a project ID, never a directory. `write_asset`
returns a relative reference for P7/P4. `read_asset` returns detached
immutable bytes. `delete_asset` returns True only when it removes a
file; an absent valid asset returns False. No method changes editor
state, creates a project, chooses an image model, or decodes full image
content.

## Canonical asset identity and limits

Generate only `assets/<lowercase-sha256-of-bytes>.<extension>`.
Map `image/png` to `.png`, `image/jpeg` to `.jpg`,
`image/gif` to `.gif`, and `image/webp` to `.webp`.
Read/delete accept only that exact complete format and reject all
absolute, drive, UNC, URI, traversal, backslash, alternate-stream,
mixed-case and unrelated references. Callers cannot supply a write
filename.

Write input is exact nonempty `bytes` no larger than 16 MiB. Its
declared media type must match the raster signature. This is a bounded
signature check, not decoding or malware scanning. A project may hold
at most 256 managed assets and 128 MiB of managed asset bytes. An
idempotent write of verified identical existing bytes remains allowed
at capacity and returns the same reference. No truncation, conversion,
overwrite or collision replacement is allowed.

## Filesystem and error boundary

Use the existing P1 identity/direct-path validation to find the
project. The project's `assets/` child must be a direct, non-linked
directory. Reject linked/reparse components and unsafe managed target
files without following them. Ignore and preserve unrelated entries.
Read validates canonical name, regular-file boundary, size, SHA-256
digest and raster signature before returning bytes. Corrupt/replaced
managed files fail safely.

Validate write input and capacity before publication. Write through a
same-directory temporary file, flush, and publish only when the final
name is absent. Clean up only this invocation's temporary file on
failure. Reuse a verified identical existing asset. Unknown temporary
entries left by a crash are not automatically removed. No recursive
deletion, arbitrary path reading, cross-process transaction,
symlink-race security certification or power-loss durability guarantee
is claimed.

Invalid input or corrupt managed data raises Foundation
`ValidationError` with fixed non-sensitive wording. Unknown project or
missing asset on read raises `FileNotFoundError`. Native I/O failures
remain `OSError`; a later HTTP owner must sanitize responses. Do not
log payloads, project content, credentials or filenames.

## Deletion and reference boundary

`delete_asset` never edits `state.json`. Before removing a present
managed asset, load the current P1 document and refuse deletion when
any string value anywhere in opaque JSON state exactly equals its
reference. This must not import or interpret P7. The caller saves a
dereferenced state before deletion. A failed delete may leave an
unreferenced asset; no cross-file transaction or concurrent-writer
guarantee is made. Never delete another project, unknown file,
`assets/` directory or linked target.

## Acceptance

Add unit tests under `tests/projects/test_assets.py` using synthetic
raster bytes and `tmp_path`: all four formats and signature mismatch;
deterministic names/idempotence; project isolation/reopen; malformed
references and linked/reparse paths; unknown entries; corrupt digest,
size and signature; 16 MiB, 256-file and 128 MiB boundaries; absent
targets; referenced/unreferenced deletion; validation-before-mutation;
temporary cleanup under injected I/O failure; safe fixed errors; and
unchanged existing JSON state.

Add `tests/integration/test_project_assets.py` for P1 save of a P7
image reference, reopen, P1 byte read, typed P7 projection and P4
build. Tests use no real user files, network, provider or UI. Run
Ruff, strict Pyright on Windows and Linux, full discovered Pytest,
ownership/import review and latest-head hosted CI. Produce one
P1-002 module report and stop for Tech Lead review. This module does
not implement upload HTTP, AI generation, preview, garbage collection,
Windows launch or React UI.
