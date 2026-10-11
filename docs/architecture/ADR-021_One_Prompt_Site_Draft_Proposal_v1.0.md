# AURORA — One-Prompt Site Draft Proposal v1.0

- Document ID: ADR-021
- Status: APPROVED — PG-01–PG-05 explicitly approved by Architecture Authority on 2026-10-11
- Date: 2026-10-11
- Module: PG-001 — One-Prompt Structured Site Draft
- Repository baseline: `81df971d15c66b1269e9469eec6b672f87fa3797`

## Decision boundary

ADR-002 requires a business prompt to produce an editable brand, site structure,
content and SEO. The merged UI-001 workspace currently supports manual editing
and selected-block text assistance, but not whole-project generation. PC-003
provides one stateless OpenAI Responses text call; PC-007 owns the exact editor
schema; PC-004 owns publishable static-site validation. PG-001 composes
these public application gateways. It is not a new L0–L8 Runtime and does not
change their ownership or the Architecture Freeze.

This decision is compiled into the separate APPROVED PC-015 implementation
contract. PG-001 may begin only within that exact ownership and acceptance
boundary. Approval does not authorize any deferred module.

## PG-01 — Scope and ownership

The module creates a **candidate** text-only `EditorDocument` from one prompt.
It does not create or mutate a project, persist a draft, use credentials,
expose an HTTP route, change the UI, generate/upload images, build/export a
folder or ZIP, deploy, run in the background, or automatically retry a paid
request. A successful draft is in memory until a separately approved caller
accepts and saves it through P7/P1. The user must initiate generation
explicitly; a later UI contract must not hide the paid request.

Approved production and acceptance ownership:

```text
src/project_generation/__init__.py
src/project_generation/models.py
src/project_generation/service.py
tests/project_generation/__init__.py
tests/project_generation/test_models.py
tests/project_generation/test_service.py
tests/integration/test_project_generation.py
tests/editor/test_models.py             # narrow public-gateway consumer admission
tests/site_export/test_models.py        # narrow public-gateway consumer admission
```

The two existing test edits only recognize `service.py` as an approved
consumer of the **public** `src.editor` and `src.site_export` gateways. They
must retain all existing forbidden-private-import and lower-owner assertions.
No P1–P7 production file, frontend file, Kernel/Runtime file, dependency,
configuration or CI workflow changes in PG-001.

## PG-02 — Public Python API

`src.project_generation` exports exactly three symbols:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectDraftRequest:
    project_name: str
    business_prompt: str = field(repr=False)
    language: Literal["ru", "en"]
    model: str

@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectDraftOutcome:
    job_id: str
    status: Literal["completed", "failed"]
    document: EditorDocument | None = None
    failure: GenerationFailure | None = None

class ProjectDraftGenerator:
    def __init__(self, text_client: OpenAIResponsesClient) -> None: ...
    def generate(self, request: ProjectDraftRequest) -> ProjectDraftOutcome: ...
```

`ProjectDraftOutcome` must have exactly one terminal outcome: completed with a
document and no failure, or failed with a sanitized `GenerationFailure` and no
document. It contains neither prompt, raw model output nor credential. The
caller supplies the model; PG-001 does not hard-code a model ID or retrieve a
key. Invalid local request fields raise the existing P3
`GenerationConfigurationError` with fixed non-input-bearing messages before
any provider call. The request requires a nonblank UTF-8 project name of at
most 256 bytes, a nonblank UTF-8 business prompt of at most 8 KiB, exact
`ru`/`en`, and a nonblank model string. No trimming or silent truncation.

## PG-03 — One request, bounded draft and failure policy

For one valid request, PG-001 makes exactly one call to the supplied P3 client
with a `GenerationRequest`. The fixed instructions ask for one JSON object
with exactly this shape, no Markdown or executable content:

```json
{
  "brand": {
    "name": "string",
    "tagline": "string",
    "primary_color": "#RRGGBB",
    "secondary_color": "#RRGGBB",
    "font_family": "system | serif | monospace"
  },
  "pages": [
    {
      "slug": "index-or-safe-ascii-slug",
      "title": "string",
      "meta_description": "string",
      "heading": "string",
      "sections": [{"heading": "string", "body": "string"}]
    }
  ]
}
```

The prompt and project name are data, never instructions to override the
response shape or AURORA rules. PG-001 accepts only a top-level JSON object
with the exact listed keys and exact runtime field types. Text fields remain
plain text, never executable content. No coercion, Markdown-fence removal,
schema repair, extra keys, non-finite number, empty required
title/heading/name, or unbounded collection is accepted.
There must be 1–8 pages and 1–12 sections per page, with exactly one `index`
page. P4 remains authoritative for safe/unique slugs, colors and text limits.
PG-001 creates no image references: `logo_path` and `image_path` are `None`,
and `image_alt` is empty. Language and schema version come from the request
and PC-007 respectively, not from model output.

PG-001 supplies canonical lowercase UUIDs for P7 page/section IDs using
`uuid5` over P3's response ID plus each positional page/section index. This
gives reproducible IDs for the same response without a process-global ID
generator, provider-supplied IDs or stored state. It validates the candidate
through public `save_editor_state({}, document)`, projects it with public
`to_static_site_document(document, ())`, and calls public
`StaticSiteBuilder.build` in memory. Only a P7-valid and P4-publishable draft
is a success. PG-001 does not reuse the compiled artifact or own P4 rules.

If P3 returns a failed terminal job, PG-001 passes through its sanitized
`GenerationFailure` and never parses output. Malformed/unsafe JSON, invalid
editor shape, or failed P4 validation becomes P3's existing
`invalid_response` category with a fixed safe message and `retryable=False`.
No raw response, prompt, path or native exception text is exposed or logged.
No automatic retry or second paid call occurs. A caller may show the failure
and offer a new explicit user-initiated attempt under a later contract.

## PG-04 — Dependency and acceptance boundary

Production imports: standard library plus the public `src.generation`,
`src.editor`, and `src.site_export` gateways. No private P1–P7 module, P6,
credential store, concrete Kernel or L1–L8 Runtime, frontend, generic provider
registry, reverse import or new dependency. PG-001 is a leaf application
composer; no lower owner imports it.

Deterministic tests replace `OpenAIResponsesClient.generate` with a fake and
use real P7/P4 public APIs. They cover exact request and terminal snapshots,
one-call/no-call conditions, two languages, multiple pages/sections, stable
UUIDs and uniqueness, response shape/type/count failures, P4-invalid slugs
and colors, Unicode and capacity boundaries, prompt-injection text treated as
data, safe failure representations, no mutation/persistence, and zero network
or credential access. No skipped or xfail acceptance tests. Run Ruff, strict
Pyright and all discovered Pytest; inspect the exact diff and import boundary.
Latest-head hosted checks are required before any routine merge. Passing these
tests does not certify a live OpenAI call or the ADR-002 usable-Windows path.

## PG-05 — Deferred modules and approval record

Later **separate** approved contracts are required for a P6 generation route
with same-origin security, project timestamp/conflict semantics and credential
retrieval; a UI generation screen with explicit paid-call consent and draft
acceptance; OpenAI image generation and project asset persistence; persisted
global settings; folder export; and Windows packaging. Those modules must
not reinterpret or silently overwrite an existing editor document. PG-001
does not authorize any of them.

Architecture Authority approved PG-01–PG-05 in full on 2026-10-11, including
the new application package, two narrow existing test admissions, exact draft
schema and limits, deterministic IDs, P4 validation, and safe failure policy.
This approval does not waive the PG-001 quality gates or approve later P6/UI,
image, settings, export, or packaging work.
