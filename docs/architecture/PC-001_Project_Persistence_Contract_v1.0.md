# AURORA — Project Persistence Contract v1.0

**Status:** APPROVED  
**Module:** P1-001 Project Domain & Persistence  
**Authority:** ADR-001 and ADR-002

P1-001 is an application service, not an L0–L8 Runtime. It owns portable project
directories and atomic JSON persistence only. It may create:

```text
src/projects/__init__.py
src/projects/models.py
src/projects/repository.py
tests/projects/test_models.py
tests/projects/test_repository.py
```

Public API is `ProjectMetadata`, `ProjectDocument`, and `ProjectRepository`.
Metadata has `project_id`, `name`, `format_version`, `created_at`, and
`updated_at`; the document adds JSON-compatible `state`. A repository receives
an explicit root path (default production root is resolved by the future app
bootstrap), creates `<slug>-<project-id>/assets`, `site`, and `exports`, stores
metadata in `aurora.project.json` and state in `state.json`, and lists, loads,
saves, renames, and deletes projects.

Writes serialize JSON to a same-directory temporary file and replace the target
only after successful write. Project IDs are UUID strings; timestamps are UTC
ISO-8601 strings. State is opaque JSON and cannot contain secrets. The module
does not generate sites, call AI, expose HTTP, manage credentials, or import a
Runtime implementation. Tests use `tmp_path`, including atomic write and
reopen flows. Ruff, Pyright, and Pytest are required.

## Audit Clarifications

The repository validates UUID identities before any lookup or deletion, rejects
ambiguous duplicate identities and linked project paths, and validates the
supported metadata format on reopen. JSON state uses string object keys, finite
numbers and acyclic containers. Persistence boundaries detach caller-owned data.
Invalid input cannot create a partial project or replace existing saved state.

Atomicity is per JSON file, not a crash-safe transaction spanning two files.
Both payloads are validated before writing. State is replaced first; metadata
replacement failure rolls state back while the process remains alive. A process
interruption between replacements may leave newer state with older metadata.
Multi-file transactions, concurrent writers and recovery journals are not
implemented by this contract. Opaque state cannot identify arbitrary secret values;
callers must keep credentials outside project state as required by ADR-002.
