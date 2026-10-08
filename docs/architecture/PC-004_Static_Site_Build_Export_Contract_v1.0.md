# AURORA — Static Site Build and Export Contract v1.0

Document ID: PC-004
Status: APPROVED — compiled from explicitly approved ADR-010 S-01–S-05
Module: P4-001 — Static Site Build and Folder/ZIP Export
Date: 2026-10-07

## Authority and normative specification

[ADR-010](ADR-010_Static_Site_Build_Export_Proposal_v1.0.md) is incorporated
in full, including its exact seven model schemas, eleven-symbol public surface,
method signatures, limits, path/HTML rules, failure policy and acceptance matrix.
The Authority approved all S-01–S-05 explicitly, then approved the exact
test-package-marker clarification recorded in ADR-010 on 2026-10-08. No other
schema, behavior or capacity value is changed here.
AGENTS, ADR-001 and the Build Protocol apply. Architecture Freeze v1.0 and
Master Pack v1.1 remain unchanged; this application contract is the exact P4
file/API/import/test registry, not a new Runtime or amendment of lower owners.

## Exact ownership registry

| File | Sole responsibility / exports |
| --- | --- |
| src/site_export/__init__.py | Gateway: exactly all eleven approved symbols |
| src/site_export/models.py | Seven immutable projections, SiteValidationError, SiteExportError; private boundary validation |
| src/site_export/builder.py | StaticSiteBuilder only; synchronous deterministic HTML/CSS/raster compilation |
| src/site_export/exporter.py | StaticSiteExporter only; exclusive folder/ZIP output and invocation-owned cleanup |
| tests/site_export/test_models.py | Exact schema/API/ownership assertions |
| tests/site_export/test_builder.py | Compilation, escaping, runtime validation and all capacities |
| tests/site_export/test_exporter.py | Artifact/destination validation, byte equality, ZIP determinism, exclusive writes, failure/cleanup |
| tests/site_export/__init__.py | Package marker only; resolves default-pytest module-name collision, no fixtures or runtime API |
| tests/integration/test_static_site_export.py | Real builder → folder/ZIP → reopen; immutable projection preservation |

Only these nine source/test files plus this contract, ADR approval record and
module report could change in the original P4 build. A later explicit
2026-10-08 Architecture Authority clarification in ADR-011 permits the P5
task to update **only** `tests/site_export/test_models.py` so its import-DAG
assertion recognizes `src/deployment/netlify.py` as an approved application
consumer of the public `src.site_export` gateway. Imports from P4 private
modules and all other unapproved production consumers remain forbidden;
lower Runtime layers must never import site_export. This is a test-boundary
correction, not a P4 production/API or Runtime ownership change.
No old tests/conftest, dependency/workflow, Kernel,
project storage, credential, AI generation, Render or other production edits.

## Exact API/import registry

Models: StaticSiteBrand, StaticSiteSection, StaticSitePage, StaticSiteAsset,
StaticSiteDocument, StaticSiteFile, StaticSiteBuild — frozen, slotted,
keyword-only dataclasses with precisely the ADR-010 fields/defaults. Byte data
is repr=False. No construction-time transformation, validation or I/O.

Errors: SiteValidationError(ValueError), SiteExportError(RuntimeError).

Services: StaticSiteBuilder(); build(document: StaticSiteDocument) → StaticSiteBuild.
StaticSiteExporter(); export_folder(build: StaticSiteBuild, destination: Path) → Path;
export_zip(build: StaticSiteBuild, destination: Path) → Path.
No additional public methods, aliases, constants, constructors or exports.

Dependencies: standard library only; builder/exporter may import models only,
never one another. Gateway may import all three. Models import neither service.
All imports absolute. Private stateless validators remain in the owned models
file, not a utility package. Lower layers never import site_export.

## Behavior and boundaries

The full S-02/S-03/S-04 rules are normative. Builder validates forged contents
before compilation and has no I/O/network/state. Exporter validates the entire
compiled artifact before filesystem mutation; it is not an HTML ingestion or
content-scanning API. Destination must be absolute with an existing non-linked
directory parent, no linked/reparse component, and absent even if empty.
Exclusive creation never overwrites. Fixed sanitized errors preserve local
I/O cause; best-effort cleanup removes only invocation-created entries, never
unrecognized contents. Incomplete cleanup is explicitly reported. No recursive
tree deletion, crash transaction or concurrent-writer security guarantee.

Limits (binary units): 100 pages; 100 sections/page; 256 assets; 16 MiB/asset;
128 MiB total assets; 64 KiB UTF-8/text field; 1 MiB total text; 150 MiB/build.
No truncation. Exactly one index page; safe unique local names; correct raster
signature only, not complete decoding. ZIP_STORED, sorted relative names, fixed
1980-01-01 timestamp and regular-file permissions. No enclosing dist directory.

## Acceptance and integration

All ADR-010 S-05 matrix rows require executable behavioral assertions. Preserve
1293 existing cases. Four canonical new test modules, no skips/xfail, temporary
outputs and synthetic inputs only. Measure 100% physical executable lines
individually for builder.py and exporter.py, without exclusions; this is not
branch coverage. Ruff, scoped formatter check, strict Windows/Linux Pyright,
full discovered Pytest, bounded Kernel smoke and latest-head hosted CI required.
Reviewed scope, commit/push, normal publication with mandatory confirmations,
one module report and STOP for Tech Lead review.

Future application composition supplies a detached typed projection from an
approved editor/generation contract; raw opaque project JSON or RenderNode.kind
is never interpreted here. UI, preview server, image generation, Netlify,
deployment, autosave and usable Windows acceptance remain separate tasks.
