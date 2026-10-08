# AURORA — Editor State and Site Projection Proposal v1.0

**Document ID:** ADR-013
**Status:** APPROVED — E-01–E-05 explicitly approved by Architecture Authority
**Date:** 2026-10-08
**Target module:** P7-001 — Editor State and Static-Site Projection
**Repository baseline:** `408d44c01981d17f0dfb9991a2f3da17ffa2ec3f`

## Approval boundary

On 2026-10-08 the Architecture Authority responded "утверждаю полностью,
дальше" to the request to approve E-01–E-05 together. This approves exactly
the editor-state schema, pure projection, ownership, import boundary and
acceptance gate below. PC-007 compiles those decisions. It does not approve
another module, waive its tests/review, or certify a usable Windows MVP.

### Approved P4 test-admission clarification

After the P7 preflight found that the existing P4 import-DAG test recognized
only Netlify as a public `src.site_export` consumer, the Architecture
Authority explicitly replied "разрешаю полностью, дальше" to the narrow
request to amend this ADR/PC-007 and update only
`tests/site_export/test_models.py` to admit
`src/editor/projection.py` as another public-gateway consumer. This is a
test-registry correction, not permission to change P4 production code,
P7's dependency direction, another P4 test, or any Runtime owner. It
supersedes E-01's original nine-file list for this one test file only.

## Why this decision is needed

ADR-002 requires a saved, editable site and a build/export path for the
Windows MVP. PC-001 deliberately treats `ProjectDocument.state` as opaque
JSON. PC-004 accepts only a detached `StaticSiteDocument` and requires a
future editor/generation owner to project saved state into that type. PC-006
deliberately does not interpret project state or expose a build route. An
application cannot build an arbitrary saved project without an approved
editor schema and projection.

This proposal defines that missing application boundary. It does **not**
approve code, change an L0–L8 Runtime, replace P1 persistence, or turn P6
into a builder. ADR-002's React/Vite client remains a separate follow-on
module; P7-001 would be its prerequisite, not a substitute.

## E-01 — Ownership and scope

P7-001 would be a pure application-domain module, not a Runtime. Proposed
ownership is limited to:

```text
src/editor/__init__.py
src/editor/models.py
src/editor/codec.py
src/editor/projection.py
tests/editor/__init__.py
tests/editor/test_models.py
tests/editor/test_codec.py
tests/editor/test_projection.py
tests/integration/test_editor_projection.py
```

`src.editor` would be the sole public gateway. Production P7 would read
or write no files, call no provider/network, own no process-global state,
and add no dependency. It would not modify P1, P4, P6, Kernel, Render, or
any other existing owner. A later approved application-composition module
would load/save through P1 and build through P4.

## E-02 — Versioned editor payload

The editor owns only `ProjectDocument.state["editor"]`; other top-level
state keys remain opaque to P7. Absence of `editor` means an uninitialized
project, matching P6's current empty-state creation. It does not mean an
empty but buildable site. An existing nonempty editor payload is never
silently migrated, replaced, or interpreted as another version.

Version 1 has **exactly** this nested shape. Arrays preserve page/section
order; example values are illustrative, not generated defaults:

```json
{
  "schema_version": 1,
  "language": "ru",
  "brand": {
    "name": "Example",
    "tagline": "",
    "primary_color": "#4F46E5",
    "secondary_color": "#0F172A",
    "font_family": "system",
    "logo_path": null
  },
  "pages": [{
    "id": "37d407e8-9af8-4ca4-9e57-c0c28cce4266",
    "slug": "index",
    "title": "Example",
    "meta_description": "",
    "heading": "Example",
    "sections": [{
      "id": "8bc80959-6e1d-4ad1-aa1e-9678e404c980",
      "heading": "Welcome",
      "body": "",
      "image_path": null,
      "image_alt": ""
    }]
  }]
}
```

`language` is exactly `ru` or `en`; `font_family` is exactly
`system`, `serif`, or `monospace`. Other displayed text/path fields
are strings, except nullable `logo_path`/`image_path`. IDs are
caller-supplied canonical lowercase UUID strings, unique among pages and
among all sections respectively. P7 does not generate IDs, timestamps,
content, images, or default project structure. Unknown keys *inside* the
versioned payload are rejected so a save cannot silently discard a newer
editor feature. Other top-level state keys are preserved without interpretation.

The payload stores asset references, not image bytes or external URLs.
Referenced raster bytes remain outside JSON in the project's `assets/`
tree. Asset-write/read security and image generation/upload require a later
approved owner; P7 never follows a reference or reads a path. Credentials,
provider responses, raw HTML/CSS/script, and deploy artifacts are not part
of this payload.

## E-03 — Public surface and behavior

The proposed gateway exports exactly four frozen, slotted, keyword-only
dataclasses (`EditorBrand`, `EditorSection`, `EditorPage`,
`EditorDocument`), `EditorStateError(ValueError)`, and three functions:

```text
load_editor_state(state: JSONDict) -> EditorDocument | None
save_editor_state(state: JSONDict, editor: EditorDocument) -> JSONDict
to_static_site_document(
    editor: EditorDocument,
    assets: tuple[StaticSiteAsset, ...] = (),
) -> StaticSiteDocument
```

`EditorDocument` contains the schema version, language, brand and ordered
pages; brand/page/section fields correspond exactly to E-02. Dataclasses
hold tuples, not mutable lists. The codec validates runtime shape and IDs,
rejects unknown editor keys and unsupported versions, and never silently
coerces values. Load/save return detached data; save preserves opaque outer
state keys without aliasing caller-owned nested containers. Malformed input
raises `EditorStateError` with a fixed sanitized message that echoes no
content, IDs, or paths. Missing `editor` is the only `None` case.

`to_static_site_document` maps presentation fields into P4's public
dataclasses, discards stable editor-only IDs, preserves order and passes
through supplied immutable `StaticSiteAsset` values. It does no I/O or
asset lookup. `StaticSiteBuilder.build` remains the authority for safe
slugs/asset names, raster signatures, required homepage, references, content
limits and HTML compilation. A saved draft may be structurally valid but
not currently buildable; callers must report P4's sanitized failure rather
than silently repair, truncate or publish it. If image references exist, a
future asset owner must supply matching typed bytes before building.

No P1 or P4 service is called implicitly. P7 adds no editing-command API;
the later UI contract will determine how user actions and autosave construct
and replace immutable snapshots.

## E-04 — Dependency and integration boundary

Production P7 may import standard library, `JSONDict` from
`src.core.types`, and only the public `src.site_export` gateway for P4
model types. It may not import private P4 modules, P1 repository internals,
P6 internals, concrete L0–L8 Runtime implementations, or provider/credential
adapters. P1/P4 and lower Runtime layers never import P7. Integration tests
may use public P1/P4 gateways under `tmp_path`.

PC-006's `PUT /api/v1/projects/{project_id}` stays an opaque-state route.
This ADR changes neither its shape nor concurrency semantics. A later
approved API/UI contract must specify editor-aware routes, autosave, asset
loading, preview, build/export and deploy orchestration; it must not quietly
reinterpret existing P6 routes.

## E-05 — Acceptance and publication

The later PC-007 would test exact schema/exports, missing/unknown/unsupported
state, deep detachment, strict runtime types, UUID uniqueness, ordered
round-trip, opaque outer-key preservation, fixed errors, image-reference
handoff and exact P4 field mapping. An integration test would create/save/
reopen a temporary P1 project, decode/encode P7 state, project to P4 and
build a synthetic text-only static site. Invalid P4 slugs, references,
homepage and limits must fail in P4, not be silently fixed by P7.

No skipped/xfail acceptance tests, real project/credential mutation, paid
OpenAI call, Netlify deploy, or browser launch. Ruff, strict Windows/Linux
Pyright, full discovered Pytest, ownership/import review and latest-head
hosted CI precede normal publication. A P7 module report and Tech Lead
review remain mandatory. P7 alone does not satisfy the ADR-002 usable-Windows
acceptance path.

## Decision and deferred work

**E-01–E-05 are approved together.** PC-007 is the exact P7 implementation
contract. P7 may be built only under that contract in its own module task;
approval of this ADR alone does not waive the module review or CI gate.

Separate later contracts are still needed for structured one-prompt and
image generation, asset storage/read safety, editor-aware HTTP composition,
React/Vite workspace and RU/EN onboarding, local server/browser launcher,
preview, autosave, build/export/deploy routes and end-to-end Windows acceptance.
Their details cannot be inferred from this proposal or declared complete by
a green pure-projection test.
