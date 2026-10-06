# AURORA — KR-008 Context Reconciliation Proposal v1.0

**Document ID:** ADR-006
**Status:** APPROVED — CANONICAL KR-008 RECONCILIATION DECISION
**Date:** 2026-10-06
**Task:** KR-008 — Runtime Context Runtime reconciliation
**Repository baseline:** `0a72c63f82dea53bb3b8e169dd4fbcb7b4203781`

## Explicit Approval Record — 2026-10-06

The Architecture Authority directly stated:

> Утверждаю ADR-006 полностью, включая C-01–C-04  , дальше

This explicitly approves C-01–C-04 and the contract-required KR-008 source/test
scope. It does not claim an independent human implementation review. The earlier
generic KR-007 acceptance did not supply this decision; this direct reply does.
ADR-003 governs routine PR/merge, not architecture approval.

## Implementation Gate

Compile the exact approved KR-008 contract and
reconcile its affected Master API/import/ownership/test entries before editing code.
Only then implement KR-008 as one module task, validate and stop for review.

## Purpose and Sources

Close implementation-facing contradictions without moving an owner, changing
L0–L8, adding a Runtime, dependency, scope or vocabulary member. Preserve the
existing constructors and APIs where the Authority selects that alternative.
ADR-004 P-04 remains the approved detached-snapshot requirement.

Sources inspected at the baseline:

- AGENTS.md; ADR-001/003; approved ADR-004, especially P-04 and module scope.
- AB-00A, its reconciliation/build amendment, AB-00B and AB-00D Resolution-003/006;
  the Wave 1 implementation handoff.
- Master M-01 KR-008 file/dependency matrix, M-03 Context/Metadata/Session APIs,
  M-03A KR-008 symbol index, M-04 context import graph and violation register,
  M-05 context/trace/lifetime entries, M-06 CONTEXT-001–003 and context flow,
  M-08 existing exception vocabulary and M-09 KR-008 test matrix.
- Current context.py, metadata.py, session.py, contracts/context.py, Foundation
  types/exceptions, Bootstrap construction and canonical test_context.py.

### Observed conflicts resolved by the approval below

| ID | Evidence | Classification |
| --- | --- | --- |
| C-01 | M-04 forbids SessionRuntime importing ContextRuntime and describes the opposite facade-to-storage DAG. M-06 CONTEXT-003 explicitly imports ContextRuntime and its creation flow calls ContextRuntime.create. Current session.py follows M-06. | Architecture / dependency conflict |
| C-02 | M-03 describes list() as a tuple of RuntimeContexts and includes testing-only clear(); M-03A also lists clear(). M-06 and current source specify tuple[SessionId, ...] and omit clear(). Constructor/coordination details are not uniform. | Public contract conflict |
| C-03 | P-04 specifies JSON rejection/detachment but not every malformed identity/timestamp or expired-context policy. Current create/replace have no field validation. Choosing rejection/expiry behavior silently would change public behavior. | Missing exact boundary behavior |
| C-04 | M-01/M-06 forbid trace generation in Context and propagate supplied trace, while M-05 says Context generates UUIDv7 trace/root identifiers and contains incompatible trace/context fields. AB-00D fixes seven context fields, not all trace-generation prose. | Authoritative ownership/behavior contradiction |

Already resolved, not reopened: seven RuntimeContext fields and four derived
properties; unchanged TraceContext contract fields; RuntimeContract lifecycle;
UUID-backed SessionId/PipelineId; JSON aliases; P-04 value rather than identity
guarantees; existing validation/state exceptions.

## Frozen Invariants

- Same three KR-008 files/classes: context.py/ContextRuntime,
  metadata.py/MetadataRuntime and session.py/SessionRuntime.
- Context owns only the active context reference; Session owns the private
  session-context registry; Metadata owns JSON transformations/validation.
- No contracts/Foundation edits, field additions, trace vocabulary extension,
  shared utility module, DI import, event dispatch, pipeline work or new exception.
- Immutable dataclass shells with recursively detached, locally mutable JSON
  snapshots, not deep-frozen JSON or object identity guarantees.
- No hidden globals, network, persistence, background work or new dependency.
- Python 3.13 standard library, uv, strict public typing; same L0 owners.
- Session-scoped DI disposal remains composition through Container in KR-010;
  SessionRuntime never imports ContainerRuntime.

## C-01 — Approved Limited Internal Dependency Clarification

**Approved decision:** Confirm M-06's existing Session-to-Context composition
within KR-008, retaining `ContextRuntime()`, `MetadataRuntime()` and
`SessionRuntime(context_runtime: ContextRuntime)`.

Allow session.py to import ContextRuntime for explicit creation, replacement and
clearing of the supplied active-context owner. Session still exclusively owns its
private session registry and delegates metadata transformation to MetadataRuntime.
ContextRuntime does not import or construct SessionRuntime. The resulting actual
DAG is Session → Context → Metadata, with Session → Metadata additionally allowed;
all three consume only allowed Foundation/contract dependencies.

This narrowly supersedes the conflicting M-04 Session-to-Context prohibition and
opposite KR-008 DAG, not any higher/lower-layer direction or ownership rule.
Do not add a callback/service-locator abstraction or constructor compatibility shim.

Alternative not selected: enforce M-04's facade-to-storage DAG, which requires
an explicitly redesigned composition/API and call-site migration. It cannot be
introduced as a mechanical typing repair.

## C-02 — Approved Exact Surface and Existing Session Coordination

**Approved decision:** Retain these signatures and current session-ID list
semantics, reconciling the conflicting M-03/M-03A entries:

```python
class ContextRuntime:
    def __init__(self) -> None: ...
    def create(
        self,
        *,
        session_id: SessionId,
        pipeline_id: PipelineId,
        runtime_layer: RuntimeLayer,
        metadata: Metadata,
        trace: TraceContext,
    ) -> RuntimeContext: ...
    def current(self) -> RuntimeContext: ...
    def replace(self, context: RuntimeContext) -> RuntimeContext: ...
    def clear(self) -> None: ...
    def has_context(self) -> bool: ...
    def health(self) -> HealthStatus: ...


class MetadataRuntime:
    def merge(self, base: Metadata, update: Metadata) -> Metadata: ...
    def put(self, metadata: Metadata, *, key: str, value: JSONValue) -> Metadata: ...
    def remove(self, metadata: Metadata, *, key: str) -> Metadata: ...
    def contains(self, metadata: Metadata, *, key: str) -> bool: ...
    def get(
        self,
        metadata: Metadata,
        *,
        key: str,
        default: JSONValue | None = None,
    ) -> JSONValue | None: ...


class SessionRuntime:
    def __init__(self, context_runtime: ContextRuntime) -> None: ...
    def create(
        self,
        *,
        session_id: SessionId,
        trace: TraceContext,
        metadata: Metadata | None = None,
    ) -> RuntimeContext: ...
    def get(self, session_id: SessionId) -> RuntimeContext: ...
    def update_metadata(
        self,
        session_id: SessionId,
        metadata: Metadata,
    ) -> RuntimeContext: ...
    def remove(self, session_id: SessionId) -> None: ...
    def contains(self, session_id: SessionId) -> bool: ...
    def list(self) -> tuple[SessionId, ...]: ...
```

ContextRuntime continues to implement the exact AB-00D RuntimeContract:
runtime_name/runtime_layer read-only properties, async initialize/start/stop/shutdown
and sync health. The name is "context", layer L0_KERNEL, health OK. No new lifecycle
state or post-shutdown gate. initialize/start/stop preserve their current no-op
behavior; shutdown clears the active context. No added set/get/clear-session facade.

Session.create validates/captures all ingress before changing either registry or
active context; successful create becomes active and stores a separately detached
session snapshot. Preserve current same-ID replacement behavior: no new duplicate
error or silent identity reuse; replace that registry entry without reordering it.
A new session creation uses the existing UUIDv4 PipelineId and L0_KERNEL, with
created_at generated by ContextRuntime and expires_at None.

update_metadata performs a shallow key update, preserving IDs, trace, timestamps
and expiry. It changes the active snapshot only if its session_id matches the
updated session; another active session stays unchanged. Validation failure leaves
both owners unchanged. remove of an existing session clears active context only
on the same session_id. Missing get/update/remove retains RuntimeStateError.

list() returns insertion-ordered session IDs, not contexts. contains is read-only.
No Session.clear() or clear alias is added. Context.clear()/shutdown do not secretly
delete an independently owned Session registry. Future composition lifetime work
is not implemented in this module.

Alternative not selected: context-valued list() or adding clear(), both of which
would expand/change the currently used surface without approved migration.

## C-03 — Approved Validation and Atomic Snapshot Boundaries

**Approved decision:** Runtime boundaries validate actual RuntimeContext /
TraceContext instances; session_id/pipeline_id/trace_id are UUID-backed values;
optional parent_trace_id/correlation_id are UUID or None; runtime_layer is an
actual member of the existing RuntimeLayer enum. Do not coerce strings/integers
or inspect NewType names at runtime; their representation remains UUID.

created_at and a present expires_at must be datetime values with timezone-aware
UTC offset zero. Preserve valid timestamp/trace/ID values without regenerating
them in replace or read snapshots. Invalid objects, timezone results or fields
raise existing ContractValidationError with a safe message, not an attribute/
recursion exception or payload dump. No new timestamp-order constraint is added.

An expired but well-formed context remains readable/replaceable; its existing
is_expired property remains observational. No automatic eviction, TTL task,
expiry denial or hidden policy is introduced. create has no expiration setting
and keeps expires_at None.

ADR-004 P-04 governs recursive JSON: dict-root Metadata, string keys, finite
floats, valid Unicode, no cycles/non-JSON objects/coercion; at most 256 dict/list
levels including root. Repeated acyclic references are independently detached.
Shallow merge/update order remains base order with updated values and appended
new keys; do not recursively merge nested maps.

All metadata methods validate their metadata inputs without mutating them.
merge validates both inputs even when a bad base value would be overwritten;
put validates the input, key and new value; remove/contains/get validate key
and source metadata. get validates/copies the default only when the key is
absent and that default will be returned. Every returned container is detached.
contains is observational and adds no hidden cache or persistent state.

Context create/replace validate and keep a private detached snapshot, then return
a separately detached snapshot; current detaches each result. Session create/get/
update also return detached data, independent of their registry and active owner.
No equality-to-identity conversion; invalid create/replace/update must be atomic.
Missing active context/session retains RuntimeStateError as P-04 requires.

This explicitly resolves the missing field/expiry choices, not a claim that
ADR-004 already specified every choice. Direct dataclass construction remains
contract-only and does not become an implicit validator.

## C-04 — Approved Trace Propagation and Limited Documentary Precedence

**Approved decision:** Confirm the existing supplied TraceContext is propagated
without generating a new trace/root/parent/correlation identifier. Context.create
and Session.create require that supplied trace; replace/session metadata updates
preserve it. Root/depth remain the existing derived contract properties, not
stored fields or a new trace tree builder.

This selects M-01/M-06 propagation and supersedes only M-05's contradictory KR-008
UUIDv7 trace-generation and incompatible stored trace/context field declarations.
No substitute trace-generation owner is invented. Other modules' trace behavior
is not redesigned. The existing UUIDv4 session PipelineId is not a trace ID.

On approval, the compiled KR-008 contract must identify and reconcile affected
M-01/M-03/M-03A/M-04/M-05/M-06/M-07/M-08/M-09 KR-008 entries only. ADR-004 P-04
supersedes shallow/deep-frozen/identity claims; AB-00B/D retain their precedence
on their explicit fields, layers, identifiers and lifecycle API. Metadata/
Context/Session data errors use ContractValidationError; missing state uses
RuntimeStateError, not nonexistent MetadataValidationError/SessionNotFoundError/
ContextNotAvailableError. No Foundation exception is added.

Canonical acceptance is tests/kernel/test_context.py, owned by KR-011 with the
active-module test changes explicitly permitted by ADR-004. Do not introduce
obsolete tests/runtime/test_context.py or implement M-09's unrelated set/get/
remove/contains context facade or DI lifetime operations inside KR-008.

## Required Acceptance — Implementation Evidence Must Be Produced

- Complete existing APIs/constructors/exports, unchanged contract schemas.
- Nested caller/output/current/replacement/session mutation isolation, independent
  snapshots and repeated acyclic references; source values preserved on failure.
- Shallow deterministic metadata merge/put/remove/get/contains, default isolation.
- Invalid keys/types/Unicode/non-finite numbers/cycles and depth 256 accepted,
  257/excessive depth rejected safely, no payload/secret disclosure.
- Mandatory context/trace IDs, enums, timestamps and observational expiration.
- Session creation/replacement/list order, active/non-active updates/removal,
  atomic failures, no session/active cross-contamination or global state.
- Lifecycle/health unchanged; no state reset, event construction or DI import.
- All permitted imports form a DAG, all public APIs exercised, at least 95%
  executable-line coverage per owned source file with no acceptance skips/xfail.
- Ruff, strict Pyright Windows/Linux, discovered Pytest, Kernel smoke and
  latest-head required CI. These are future acceptance gates, not current evidence.

## Historical DRAFT Preflight Validation — 2026-10-06

On the unchanged production/test baseline: Ruff check . passes; Pytest discovers
and passes 593 tests. Strict Pyright: 0 errors, 0 warnings, 0 informations.
The canonical KR-008 test file contains one test and asserts active-context identity, which
ADR-004 P-04 explicitly supersedes. Green regression commands do not prove the
new acceptance requirements or resolve C-01–C-04.

At DRAFT preparation no source, test, approved contract, dependency, CI or
repository protection changed; no commit/push/PR/merge or independent human
review was claimed. The implementation gate was BLOCKED until the explicit
approval recorded above. Baseline validation is not new acceptance evidence.

## Next Authorized Action

The project owner need not create another file or write technical code.
Explicit approval authorizes exact KR-008 contract/registry compilation and its
three-file implementation plus canonical tests; other modules remain untouched.
