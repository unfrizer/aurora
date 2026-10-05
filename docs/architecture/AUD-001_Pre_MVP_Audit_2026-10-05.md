# AURORA — Pre-MVP Audit and Hardening Report

**Module ID:** AUD-001 — existing-code audit and local hardening  
**Date:** 2026-10-05  
**Status:** LOCAL REPAIRS GREEN; KERNEL RECONCILIATION REQUIRES REVIEW  
**Base:** `2993761` — origin/master, PR #13 merged  
**Branch:** `codex/full-audit-hardening`

## Purpose and Authority

Review existing implementation before extending the MVP. The Architecture
Authority explicitly authorized a repository-wide audit and necessary repairs
before the next development step. This is a cross-module repair task, not a new
Runtime or a waiver of Architecture Freeze v1.0.

Applicable sources: AGENTS.md; ADR-001/002; AB-00B/C/D; approved AB-00E–L
runtime contracts; PC-001/002/003; the current filesystem; and the relevant
DI, metadata and executor entries in Master Pack v1.1 M-06.

No new Runtime, runtime layer, DI scope, event vocabulary or installed dependency
was introduced. No user project or real credential was opened or removed. No
paid OpenAI request was made. Pull-request creation and merge still require
explicit authority confirmation under ADR-001.

## Repository and Dependency Inventory

The production inventory contains 80 Python source files. Static AST analysis
found no upward imports between L0–L8 and no source-module import cycles.
This does not establish the safety of every dynamic behavior or complete public
API coverage.

| Production root | Owner / authority | Audit result |
| --- | --- | --- |
| `src/core/` | KR-001/002/003, approved Foundation decisions | Existing configuration caching preserved; RuntimeStatus reconciled to AB-00B. |
| `src/kernel/contracts/` | KR-004, AB-00B/C/D | No changes; unresolved implementation/API gaps below. |
| `src/kernel/runtime/` | KR-005–010, Wave 1 | No changes in this task; cannot certify completeness. |
| `src/main.py` | KR-010 entrypoint | Uses canonical enum comparisons; lifecycle smoke passes. |
| `src/state/` | W2-001, AB-00E | JSON boundary validation hardened. |
| `src/layout/` | W3-001, AB-00F | Deep-tree traversal repaired; stack geometry unchanged. |
| `src/theme/` | W4-001, AB-00G | Invalid string fields rejected safely. |
| `src/motion/` | W5-001, AB-00H | Invalid motion identifier rejected safely. |
| `src/interaction/` | W6-001, AB-00I | Added rejection/state-preservation tests; no source change. |
| `src/accessibility/` | W7-001, AB-00J | Iterative validation/audit preserves pre-order and semantic rule. |
| `src/platform/` | W8-001, AB-00K | Descriptor validation hardened; no native platform behavior added. |
| `src/render/` | W9-001, AB-00L | Deep-tree validation repaired; render still preserves the input root. |
| `src/projects/` | P1-001, PC-001 | Filesystem persistence hardened. |
| `src/credentials/` | P2-001, PC-002 | Native credential boundary hardened and tested with synthetic buffers. |
| `src/generation/` | P3-001, PC-003 | Plain-text Responses adapter hardened; not a business generator. |

No unowned production root was found in this inventory. `models.py` is present
only in the explicitly authorized projects and generation application modules.
No `src/utils/`, `helpers.py`, ORION, News, Research, Media or OpenRouter
implementation was found. `ProviderRuntime` is the canonical DI service factory,
not an unrelated AI-provider abstraction.

The existing immutable Settings cache, logger factory and context-local logging
fields were preserved; no competing configuration or logging implementation was
added. The audit is not a claim that all existing process-level objects are deeply
immutable or that every existing public method has full behavioral coverage.

## Changes Applied

### Confirmed Contract Requirement — KR-001 / KR-010

RuntimeStatus serialized values now match the exact uppercase declaration in
AB-00B Resolution-002. The ten member names and allowed transition matrix are
unchanged. AB-00B explicitly supersedes the older temporary KR-001 preservation
decision for this subject. EventPhase, EventPriority and DIScope remain unchanged.
The process entrypoint compares enums rather than obsolete lowercase strings.
Tests now assert the serialized vocabulary and all 100 source/target state pairs.
External consumers of the previous, non-canonical lowercase diagnostics must use
the canonical uppercase strings; no silent compatibility aliases were added.

### Local Implementation Defects — P1-001

- Project listing no longer truncates a UUID to its final hyphen-delimited part.
- IDs are validated before lookup/delete; glob injection and ambiguous duplicate
  directories are rejected.
- Project and JSON file links are rejected at the filesystem boundary.
- Metadata fields, format version, canonical identity, name and ordered UTC
  timestamps are validated on load/save.
- State rejects non-string object keys, cycles, non-finite numbers and invalid
  UTF-8 JSON; ingress/egress snapshots are detached.
- Both payloads are validated before replacement. A failed metadata replacement
  rolls state back when the process remains alive. Temporary files are cleaned up;
  failed creation removes only the exclusively created, not-yet-returned folder.
- UTC timestamps are sorted chronologically, including `Z` and fractional forms.
  A backwards clock cannot persist invalid creation/update ordering.

Atomicity remains **per file**, not a crash-safe transaction across both JSON
files. Process interruption may leave newer state with older metadata. Concurrent
writers and recovery journals are not implemented. Opaque JSON cannot recognize
arbitrary secret values: the future application must not put credentials in it.
These limits are now explicit in PC-001.

### Local Implementation Defects — P2-001

Invalid names and non-text, empty, invalid-Unicode or oversized secrets are
rejected before native writes. The documented Win32 encoded-blob size limit is
enforced. Malformed native buffers and decoding failures produce sanitized
CredentialStoreError messages. Read buffers are freed on success and decoding
failure; null unallocated pointers are not freed. The temporary native write
buffer is cleared after use. This does not promise erasure of Python strings.

Synthetic native-function tests cover UTF-16 roundtrips, Generic/local-machine
flags, buffer release and native failures. They do not access real stored keys.
PC-002 records the exact test boundary and links to the Microsoft API references.

### Local Implementation Defects — P3-001

The adapter accepts only completed, error-free Responses and completed assistant
messages. It rejects refusals, incomplete output and whitespace-only text.
Output fragments are concatenated exactly, without corrupting JSON by inserting
newlines. Redirects are rejected so credentials are not forwarded. Responses are
bounded to 8 MiB; timeouts must be positive and finite. HTTP error resources are
closed, transport truncation is mapped to a safe failure, and representations
omit prompts/instructions/generated text. PC-003 now accurately describes the
implemented plain-text boundary and canonical test filename.

Schema-constrained generation, image generation, retries and multi-stage business
generation are not implemented. Tests mock network I/O; they do not certify live
model access or account permissions.

### Local Implementation Defects — W2–W9

Shared State rejects non-finite/cyclic/non-JSON input and non-string keys before
mutation; deep unsupported input raises StateValidationError, not RecursionError.
Layout, Accessibility and Render no longer use the Python call stack to traverse
valid deep trees. Tree traversal order, geometry, output identity and public
schemas are preserved. Theme, Motion and Platform validate string fields before
calling string methods. Regression tests verify that rejection does not mutate
existing runtime state.

### Mechanical / Documentation

Python support is restricted to 3.13 in project metadata and lockfile, matching
AGENTS.md. All 18 locked package names/versions remain unchanged; unsupported
3.14 wheel entries were removed by the offline lock regeneration. Existing Linux
CI jobs retain their IDs and use frozen dependency synchronization with Python
3.13. A Windows verification job was added without changing branch protection.
README now distinguishes implemented building blocks from the missing usable
application. ADR-002's unrelated GPT-4 documentation link was corrected without
changing the approved model defaults. Ruff --fix was never run.

## Complete Source Files and Tests

No new production source file was created. Complete changed files, not patch
snippets, are available at:

| Owner | Complete source | Updated tests |
| --- | --- | --- |
| KR-001 / KR-010 | [types.py](../../src/core/types.py), [main.py](../../src/main.py) | [test_types.py](../../tests/core/test_types.py), [test_lifecycle.py](../../tests/kernel/test_lifecycle.py) |
| W2-001 | [store.py](../../src/state/store.py) | [test_runtime.py](../../tests/state/test_runtime.py) |
| W3-001 | [runtime.py](../../src/layout/runtime.py), [solver.py](../../src/layout/solver.py) | [test_runtime.py](../../tests/layout/test_runtime.py) |
| W4-001 | [runtime.py](../../src/theme/runtime.py) | [test_runtime.py](../../tests/theme/test_runtime.py) |
| W5-001 | [runtime.py](../../src/motion/runtime.py) | [test_runtime.py](../../tests/motion/test_runtime.py) |
| W6-001 | No source change | [test_runtime.py](../../tests/interaction/test_runtime.py) |
| W7-001 | [runtime.py](../../src/accessibility/runtime.py) | [test_runtime.py](../../tests/accessibility/test_runtime.py) |
| W8-001 | [runtime.py](../../src/platform/runtime.py) | [test_platform_behavior.py](../../tests/platform_runtime/test_platform_behavior.py) |
| W9-001 | [runtime.py](../../src/render/runtime.py) | [test_render_behavior.py](../../tests/render/test_render_behavior.py) |
| P1-001 | [repository.py](../../src/projects/repository.py) | [test_repository.py](../../tests/projects/test_repository.py) |
| P2-001 | [store.py](../../src/credentials/store.py) | [test_store.py](../../tests/credentials/test_store.py) |
| P3-001 | [models.py](../../src/generation/models.py), [openai_client.py](../../src/generation/openai_client.py) | [test_openai_client.py](../../tests/generation/test_openai_client.py) |

Other changed files: README.md, pyproject.toml, uv.lock, the two existing CI
workflows, ADR-002, PC-001/002/003. The only newly created file is this report.

## Validation

Local host: Windows, Python 3.13.15. Original baseline suite: 142 tests.

| Command / check | Result |
| --- | --- |
| `uv run --frozen ruff check .` | PASS |
| `uv run --frozen pyright` | 0 errors, warnings or informations |
| `uv run --frozen pyright --pythonplatform Linux` | 0 errors, warnings or informations |
| `uv run --frozen pytest -q` | 337 passed; no skipped/xfail tests |
| `uv run --frozen python -m src.main` | Exit 0, normal lifecycle smoke only |
| Static AST import scan | 80 sources; no upward L0–L8 imports or source cycles |
| Locked dependency comparison | Same 18 package names and versions |

Linux-mode Pyright is static checking on Windows, not execution on Linux.
Hosted CI results are not implied by these local results. Native Credential
Manager integration, real OpenAI calls, power-loss recovery and full GUI/product
acceptance were not tested. No coverage percentage is claimed.

## Remaining Kernel Findings — Not Silently Repaired

### K-01 — Contract Conflict: DI initialization and constructor injection

ServiceContract.initialize is async and documented as called once when the owning
scope creates an instance. M-06 ProviderRuntime.provide promises an initialized
service, but the approved resolve/provide surface is synchronous. The current
provider calls only `implementation()` and the resolver's validate method is a
no-op. Lazy services are returned uninitialized; constructor dependencies are not
resolved. A disposable in-memory diagnostic reproduced `initialized == False`.

Required authority: the exact async acquisition/initialization API, constructor
dependency-to-ServiceId mapping, failure cleanup and eager scoped-service policy.
Blocking a running event loop or using asyncio.run inside resolve is not a repair.
No new DI scope or hidden registry was introduced to bypass this gap.

### K-02 — Local Implementation Defect with Contract Reconciliation: removal

ContainerRuntime.remove unregisters the descriptor but leaves cached instances.
Remove followed by re-registration of the same ServiceId with another
implementation returns the old instance; this was reproduced in memory.
M-06 requires removal of descriptors and cached instances. ScopeRuntime's current
get/put/remove APIs take a descriptor, while M-06 specifies a ServiceId. The exact
scope-removal/disposal boundary needs reconciliation alongside K-01; no async
disposal was hidden inside the existing synchronous removal method.

### K-03 — Contract Gap: actual pipeline work

ExecutorRuntime.execute_stage publishes started/completed events but invokes no
module work. M-06 requires stage execution. AB-00D explicitly excludes execute
from universal RuntimeContract, and PipelineStage carries a module ID, not a
callable. No approved stage-to-executable binding exists in the current contract.
The existing pipeline test can therefore pass without any business operation.

Required authority: the explicit executable binding/call contract and its failure
semantics, while retaining sequential DAG execution and avoiding upward imports.
No universal RuntimeContract.execute method was invented.

### K-04 — Snapshot Conflict / Unresolved: nested context and event JSON

MetadataRuntime transformations and PublisherRuntime payload copying are shallow.
ContextRuntime returns the same frozen dataclass shell containing mutable nested
JSON. A diagnostic changed caller-owned nested metadata after create and observed
the active context change. AB-00D fixes a seven-field immutable context and exact
replacement semantics; JSONDict itself is mutable. The deep isolation/identity
boundary for Kernel snapshots needs an explicit reconciliation, not a new type
or a silent change to current/replace identity semantics.

### K-05 — Unresolved failure cleanup policy

LifecycleRuntime and ScopeRuntime stop releasing participants/services on the
first exception. Application cache clearing occurs after successful disposal;
failures can retain stale instances. AB-00B makes FAILED terminal, so the current
normal transition path cannot release resources after failed initialization/start.
Required authority: best-effort resource cleanup and aggregated-error behavior
that preserves terminal FAILED and does not create an illegal lifecycle transition.

These findings mean Kernel completeness is **not** established by passing the
present suite. They were not hidden by skips, xfail, fabricated success handlers
or altered frozen ownership.

## Integration Notes and Next Action

Project APIs, secret names, generation snapshots and L0–L8 module ownership remain
compatible with their approved boundaries, except the intentional correction of
RuntimeStatus serialized values to AB-00B. New validation failures use existing
approved exception/error vocabularies.

Under the AGENTS.md conflict-stop rule, further feature implementation stops for
Tech Lead review of the Kernel reconciliation findings. Codex can prepare the
needed resolution documents under ADR-001; the missing public behavior must not
be assumed or silently approved against contradictory existing contracts.

The follow-up [RCN-001 decision request](RCN-001_Kernel_Contract_Reconciliation_Request_v1.0.md)
records the exact open questions and planned regression test matrix. It is DRAFT,
not implementation authority; approving the audit PR does not approve those
unresolved Kernel contracts.

After reconciliation and review, the next product module is P4: an approved
static-site builder and folder/ZIP export contract and its separate implementation
branch. FastAPI, React/Vite, structured generation/images and Netlify remain later
owned modules. The first usable Windows acceptance path is still **MISSING**.
