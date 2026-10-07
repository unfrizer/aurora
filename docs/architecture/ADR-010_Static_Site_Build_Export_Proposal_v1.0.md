# AURORA — Static Site Build and Export Proposal v1.0

**Document ID:** ADR-010

**Status:** DRAFT — EXPLICIT AUTHORITY DECISION REQUIRED

**Date:** 2026-10-07

**Target module:** P4-001 — Static Site Build and Folder/ZIP Export

**Repository baseline:** `4c0c9d0cb89e23b4271517662c04371ae6711358`

## Approval boundary

This is a proposal prepared under ADR-001, not an APPROVED implementation
contract. The Authority's current message, "утверждаю и разрешаю, продолжай",
approves the completed KR-011 report and the requested merge of PR #25. It does
not constitute approval of S-01–S-05, which did not exist when that message was
sent. No independent human review or usable Windows MVP acceptance is claimed.

AGENTS and the Build Protocol require STOP when missing requirements would
change public behavior. Therefore no P4 source or tests are implemented here.
An explicit decision on S-01–S-05 is required before compiling PC-004 and
starting its separate implementation task. ADR-003 merge permission cannot
replace an architecture/contract decision.

## Sources and verified state

Inputs: AGENTS; complete M-00; AB-00A and its reconciliation/Build Protocol
amendment; ADR-001/002/003/009; PC-001/003; approved AB-00L; AUD-001's next
product-module recommendation; current source, tests, project configuration
and repository inventory. Earlier audit/completion matrices are historical
status reports, not evidence that their former Kernel gaps remain open.

PR #25 is normally merged in master at the baseline above. Its head is
`f9b45c5a5b0994c19d586934686a7a6c7501e491`; all six latest-head lint/test
checks passed, including actual hosted Linux and Windows test jobs. KR-011's
local suite collected and passed 1293 cases. These are Kernel/regression facts,
not P4 implementation evidence.

| Finding | Actual evidence | Classification |
| --- | --- | --- |
| Export is a required product feature | ADR-002 requires a self-contained static site and folder/ZIP export | Confirmed requirement |
| No builder/export contract or implementation exists | No PC-004, P4 production package or P4 tests in the baseline | Missing authority / implementation |
| Project state has no canonical site schema | PC-001 explicitly defines opaque JSON; ProjectDocument.state is JSONDict | Missing public behavior decision |
| Render is not an HTML compiler | AB-00L excludes HTML and filesystem I/O; RenderNode.kind is opaque | Frozen boundary, not a defect |
| Generation does not supply a validated business/site document | PC-003 explicitly provides plain text, not schema-constrained generation | Future scope, not a P4 prerequisite to invent |

The unresolved facts are the build input, HTML mapping, resource/path rules,
export overwrite/failure policy and exact owning API. They cannot be inferred
from arbitrary project JSON or a RenderNode.kind string.

## Frozen invariants

- No new Runtime or RuntimeLayer; no change to L0–L8 ownership or import direction.
- No changes to RuntimeStatus, EventPhase, EventPriority or DI scopes.
- Render remains read-only and acquires no HTML, filesystem or application imports.
- No Kernel, project persistence, credential or generation source change.
- No network, paid provider request, deployment, subprocess, background job,
  mutable singleton, new dependency or implicit application bootstrap.
- Python 3.13, uv, strict typing and immutable public data snapshots.
- One approved module per branch/task/report; passing required validation and
  latest-head hosted CI; normal protected publication; Tech Lead review gate.

## S-01 — Application ownership and exact scope

**Proposed decision — requires approval.**

P4-001 is an application compiler/export service, like the existing PC-series
application modules. It is not RenderRuntime, a tenth Runtime layer, or a
second owner of project/runtime state. Application callers supply a detached
typed site document; lower runtime layers never import this module.

Compile a separate PC-004 contract owning exactly:

```text
src/site_export/__init__.py
src/site_export/models.py
src/site_export/builder.py
src/site_export/exporter.py
tests/site_export/test_models.py
tests/site_export/test_builder.py
tests/site_export/test_exporter.py
tests/integration/test_static_site_export.py
```

Only these eight implementation/acceptance files may change in the subsequent
P4 task, plus its PC-004 contract/report record. No generic helpers or utilities,
changes to existing tests/conftest.py, dependencies or other production files.

Allowed dependencies are Python's standard library and sibling site_export
modules. Models do not import builder/exporter; builder and exporter import
models only. The package gateway re-exports exactly the public surface below.
No imports of concrete Runtime implementations, ProjectRepository, generation,
credentials, FastAPI or frontend code. A future application composition owner
may call the service; P4 does not create a ServiceDescriptor or manifest.

## S-02 — Typed build projection, not a new saved-project schema

**Proposed decision — requires approval.**

Define the following frozen, slotted, keyword-only dataclasses. All listed
fields are required unless an explicit default is shown. Collection values
are tuples; file data is immutable bytes, not a caller-owned Path or buffer.

| Model | Exact fields |
| --- | --- |
| StaticSiteBrand | name: str; tagline: str; primary_color: str = "#4F46E5"; secondary_color: str = "#0F172A"; font_family: Literal["system", "serif", "monospace"] = "system"; logo_path: str \| None = None |
| StaticSiteSection | heading: str; body: str; image_path: str \| None = None; image_alt: str = "" |
| StaticSitePage | slug: str; title: str; meta_description: str; heading: str; sections: tuple[StaticSiteSection, ...] |
| StaticSiteAsset | path: str; data: bytes (repr=False) |
| StaticSiteDocument | language: Literal["ru", "en"]; brand: StaticSiteBrand; pages: tuple[StaticSitePage, ...]; assets: tuple[StaticSiteAsset, ...] = () |
| StaticSiteFile | path: str; data: bytes (repr=False) |
| StaticSiteBuild | files: tuple[StaticSiteFile, ...] |

These are P4 build-input/output projections only. They do not replace
ProjectDocument.state, define a JSON persistence format, interpret existing
project keys, claim a complete brand/editor schema or add model settings.
Future structured generation/editor composition must explicitly project its
approved state into these models. P4 may be accepted using synthetic documents
without inventing that future projection or pretending plain AI text is valid.

Model construction itself performs no I/O or implicit transformation. Build
and export boundaries validate all runtime values, including forged model
contents, rather than relying on type hints alone. No Any/Unknown in public APIs.

The public surface consists of these seven models, StaticSiteBuilder,
StaticSiteExporter, SiteValidationError and SiteExportError only. The two errors
are application-local ValueError and RuntimeError subclasses respectively;
they do not extend the frozen core exception hierarchy or runtime vocabulary.

## S-03 — Deterministic self-contained compilation

**Proposed decision — requires approval.**

Public builder API:

```text
StaticSiteBuilder()
StaticSiteBuilder.build(document: StaticSiteDocument) -> StaticSiteBuild
```

The synchronous builder validates first and returns immutable files in sorted
relative-path order. It reads no files, retains no document state and makes no
network request. The same document produces exactly the same bytes.

- Exactly one page has slug "index", producing index.html. Other slugs produce
  <slug>.html at the site root. Navigation follows input page order.
- A page contains UTF-8 HTML with doctype, language, viewport, escaped title and
  meta description; a brand header/logo, relative navigation, one h1, ordered
  sections containing h2, plain-text body and optional image with its alt text.
- All user strings are text, not HTML/template/CSS/JavaScript. Escape element
  content and attribute values; body line breaks use CSS white-space: pre-wrap.
  Slugs/resources are validated paths, never arbitrary URL attributes.
- Generate assets/site.css with a fixed responsive template, valid #RRGGBB
  primary/secondary colors and one approved local font stack per font choice.
  No CDN, web font download, script, inline user CSS, form submission or tracker.
- Copy declared raster assets byte-for-byte into the build. Every referenced
  logo/section image must exist; an image requires non-empty alt text. Logo alt
  uses the brand name. Assets are local; unused declared valid assets are allowed.
- No layout/motion/interaction/runtime tree reinterpretation. This is a minimal
  semantic static site, not a browser-side implementation of the Runtime Engine.

Validation policy proposed for approval:

- Non-empty brand name, page title/heading and section heading; bodies, tagline
  and meta description may be empty but must be valid UTF-8 text without NUL.
- Slugs match [a-z][a-z0-9-]{0,63}; assets match
  assets/[a-z0-9_-]+\.(png|jpg|jpeg|gif|webp). Match the complete string.
- Reject Windows reserved device basenames, absolute/drive/UNC/URI paths,
  backslashes, dot/traversal/empty segments, trailing dots/spaces, collisions
  after case folding and file/directory prefix conflicts.
- Asset extension must agree with its PNG/JPEG/GIF/WebP signature. This is a
  signature check, not full decoding, malware scanning or a guarantee that an
  arbitrary image is browser-decodable. SVG/HTML/script assets are excluded.
- Maximum 100 pages, 100 sections per page, 256 assets, 16 MiB per asset,
  128 MiB combined asset bytes, 64 KiB UTF-8 per text field and 1 MiB combined
  text bytes. No silent truncation. Pages cannot be empty and must include the
  one homepage; asset and section tuples may be empty.
- Invalid input raises a fixed, sanitized SiteValidationError without echoing
  text, asset bytes or arbitrary supplied paths. It causes no output mutation.

The numeric limits and exact mapping above are proposed public behavior, not
facts already mandated by ADR-002. Approval or replacement is needed.

## S-04 — Explicit, non-overwriting folder and ZIP exports

**Proposed decision — requires approval.**

Public exporter API:

```text
StaticSiteExporter()
StaticSiteExporter.export_folder(build: StaticSiteBuild, destination: Path) -> Path
StaticSiteExporter.export_zip(build: StaticSiteBuild, destination: Path) -> Path
```

The caller supplies an absolute output destination with an existing directory
parent. There is no default project path, directory picker, implicit Save,
project lookup or path derived from a project name. A future application owner
chooses a project exports/ destination or user-approved export directory.

Revalidate an entire build BEFORE filesystem changes: exact typed files,
immutable non-empty byte payloads, safe unique relative names, one index.html,
only page HTML, assets/site.css and declared raster asset paths. Limit the
compiled build to 150 MiB. Reject linked/reparse output components, missing
parents and existing destinations, including empty directories, without
changing them. Detect a destination appearing before exclusive creation and
fail rather than overwriting it. Concurrent modification after exclusive
creation is outside this single-writer MVP contract, not falsely certified safe.

StaticSiteBuild is a compiled-artifact boundary, not an arbitrary HTML ingestion
API. The exporter validates shape, paths and resource limits; it does not parse,
sanitize or rewrite file contents. Future HTTP/frontend code must obtain these
builds from StaticSiteBuilder rather than accepting raw browser-supplied bundles.
Content escaping/no-network-resource assertions apply to builder-produced output,
not to a promise of scanning arbitrary bytes for scripts or secrets.

Folder export exclusively creates the destination and writes build files
relative to it. It does not add an extra dist/ nesting level. ZIP export
exclusively creates the destination file and contains the same relative file
contents, with no enclosing project/dist directory, absolute member names,
metadata JSON, settings, prompts or credentials. ZIP uses sorted file order,
fixed 1980-01-01 timestamp, fixed regular-file permissions and ZIP_STORED;
no dependency on ambient compression versions or current time. Equal builds
produce equal ZIP bytes.

There is no overwrite/replace/delete-export API. On I/O failure, report a fixed
SiteExportError chained from the local failure without exposing a raw path or
data in its own message. Cleanup is best-effort and limited to files/directories
created by this invocation; never recursively delete a pre-existing tree or
unrecognized content. Report cleanup failure safely; do not claim rollback if
partial files remain. Input-validation failures use SiteValidationError.

No crash-safe folder/ZIP transaction, power-loss guarantee, concurrent-writer
coordination, symlink-race security certification, archive import/extraction,
deploy, project save or automatic build after edits is promised. PC-001's
per-JSON-file atomic persistence remains unchanged and is not used to claim
atomic publication of an entire export. There is no reliable generic test for
whether arbitrary supplied content contains a secret; callers must keep secrets
out of site projections. P4 never reads the credential store or project files.

## S-05 — Acceptance, compilation and phased authorization

**Proposed decision — requires approval.**

After an explicit approval of S-01–S-05:

1. Record the exact Authority decision in this ADR and compile PC-004 from it.
   Do not silently change these proposed values while recording approval.
2. Implement P4-001 in one separate branch/task, only its eight owned files.
3. Preserve all 1293 baseline tests; run the entire discovered suite plus the
   new canonical P4 tests. Do not weaken a lower module to make export green.
4. Run Ruff, scoped formatter check, strict Windows/Linux Pyright, Pytest,
   bounded Kernel smoke and latest-head hosted Linux/Windows CI.
5. Review final scope; commit/push; publish only through ADR-003 and mandatory
   action-time confirmations; report and STOP for Tech Lead review.

Required acceptance matrix:

| Area | Required evidence |
| --- | --- |
| Models/API | Exact seven schemas/defaults/annotations, frozen/slotted/keyword-only construction, tuple/bytes isolation, precise exports/error hierarchy/signatures, no hidden state or upward imports |
| Compiler | RU/EN UTF-8, multi-page/homepage navigation, SEO, brand/colors/fonts/logo, ordered sections/images, desktop/mobile CSS, deterministic bytes/order, zero I/O/network |
| Rejection | Wrong runtime types, unsafe/duplicate paths/slugs, absent homepage, broken references, invalid colors/font/language/image signatures, reserved Windows names, non-UTF-8/NUL text and every capacity limit |
| Content safety | Text/attribute injection escaped; no external resource URLs, raw HTML/CSS/script, copied project/settings/prompt files, or logged asset bytes |
| Folder | Exact output tree/bytes, explicit absolute destination, no nested dist/, linked/reparse/existing targets rejected without mutation, exclusive creation and failure/cleanup tripwires |
| ZIP | Exact member set/bytes/CRC, relative safe members, fixed metadata/order and reproducible ZIP, existing targets unchanged, I/O/cleanup failures sanitized and observable |
| Integration | Real builder -> folder/ZIP -> reopen/check files under tmp_path, source projection unchanged; no OpenAI/Netlify/credential calls or user project mutation |

P4 public APIs require complete behavioral assertions; builder/exporter require
100% measured executable-line coverage per file with no source exclusions.
Distinguish physical lines from branches and report rather than lower any gate.
Tests use synthetic bytes and temporary directories, not real user exports.

## Alternatives and next boundary

Rejected for this proposed module: mapping opaque RenderNode.kind to HTML,
adding filesystem behavior to L8, accepting arbitrary raw project JSON/HTML,
reading project assets by caller-provided paths, overwriting existing exports,
adding a generic provider/plugin abstraction or introducing a build toolchain.

The future editor/project-schema projection, structured business/images
generation, FastAPI/React application, preview server and Netlify integration
remain separate approved-contract tasks. Successful synthetic P4 acceptance
would establish a builder/export building block, not the full one-prompt
Windows usability path.

**Current gate: DRAFT DECISIONS; P4 SOURCE/TEST IMPLEMENTATION BLOCKED.**

Requested decision: approve ADR-010 completely, including S-01–S-05, or state
the exact changes to the proposed input schema, mapping, limits and export policy.

## Preflight validation — not P4 acceptance

On 2026-10-07, after preparing this document on the merged baseline:

- uv run ruff check .: PASS.
- uv run pyright: 0 errors, 0 warnings, 0 informations.
- uv run pyright --pythonplatform Linux: the same zero result; static mode,
  not a new local Linux execution.
- uv run pytest -q: 1293 passed in 4.58 seconds; no skipped/xfail tests.
- uv run python -m src.main: bounded lifecycle smoke, exit 0.
- Source, tests, dependency metadata and workflows are unchanged.

Pyright's newer-version notice is not a diagnostic; no tool upgrade occurred.
No P4 test or production file exists yet. Green baseline validation does not
establish P4 coverage, output correctness or first usable Windows acceptance.
