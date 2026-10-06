# KR-008 — Runtime Context Runtime Contract v1.0

**Status:** APPROVED — COMPILED BEFORE IMPLEMENTATION
**Owner:** KR-008, L0 Kernel
**Authority:** AB-00B/D; approved ADR-004 P-04; explicitly approved ADR-006 C-01–C-04
**Approval record:** ADR-006, direct Architecture Authority reply on 2026-10-06
**Baseline:** 0a72c63f82dea53bb3b8e169dd4fbcb7b4203781

## Scope and Dependencies

Exactly three production files:

| File | Sole export | Responsibility |
| --- | --- | --- |
| src/kernel/runtime/context.py | ContextRuntime | Active validated detached RuntimeContext |
| src/kernel/runtime/metadata.py | MetadataRuntime | Stateless JSON validation and detached transformations |
| src/kernel/runtime/session.py | SessionRuntime | Private session-to-context registry and coordination |

Canonical tests: tests/kernel/test_context.py. KR-011 keeps test ownership;
ADR-004/006 explicitly authorize contract-required active-module test adjustments.
No Foundation/contracts/KR-007/KR-009/KR-010 or unrelated test edit.

Allowed project imports:
- metadata.py: Foundation JSONValue/Metadata and ContractValidationError only.
- context.py: Foundation IDs/RuntimeLayer/HealthStatus/Metadata, existing validation/
  state exceptions; contracts/context and contracts/runtime; MetadataRuntime.
- session.py: Foundation IDs/RuntimeLayer/Metadata/state exception; contracts/context;
  ContextRuntime and MetadataRuntime.
- Standard library copying/dataclasses/datetime/math/typing/UUID only as needed.

The actual DAG is Session → Context → Metadata, with Session → Metadata also
allowed. ADR-006 C-01 expressly reconciles the conflicting M-04 prohibition;
Context does not import Session. No reverse/upward import, generic shared helper,
DI, event dispatch, network, persistence, task or new dependency.

## Exact Public Surface

```python
class ContextRuntime(RuntimeContract):
    def __init__(self) -> None: ...
    @property
    def runtime_name(self) -> str: ...
    @property
    def runtime_layer(self) -> RuntimeLayer: ...
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
    async def initialize(self) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def shutdown(self) -> None: ...
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

No public validate/copy/set/clear-session/Session.clear, new alias, schema field or
constructor. Private typed copying/validation helpers within these owners are
implementation details, not a new external API.

## Context and Trace Boundary

RuntimeContext has exactly session_id, pipeline_id, runtime_layer, trace, metadata,
created_at, expires_at; derived is_expired/trace_id/root_trace_id/depth unchanged.
TraceContext stays trace_id, optional parent_trace_id and optional correlation_id.
Dataclass shells and Foundation JSON aliases remain unchanged.

Validate actual RuntimeContext/TraceContext instances; IDs use UUID runtime
representation; optional trace IDs/correlation are UUID or None; runtime_layer
must be an existing RuntimeLayer member. No coercion or NewType introspection.
created_at and present expires_at must be timezone-aware datetime with UTC offset
zero; invalid datetime/timezone results map safely to ContractValidationError.
No timestamp-order requirement or hidden validator in contract dataclasses.

Supplied trace is preserved, not regenerated; no UUIDv7 trace/root policy or stored
root/depth fields. create generates created_at UTC and expires_at None. Expired,
well-formed contexts stay readable/replaceable; is_expired is observational.

create/replace validate before storing a private detached snapshot and return an
independent snapshot; current independently detaches each output. JSON edits in
caller/results never affect active state or another result. Equality/field values
are guaranteed, not object identity. Validation failure leaves active state intact.
Missing current raises RuntimeStateError; clear is idempotent.

Name "context", layer L0_KERNEL and health OK are read-only. initialize/start/stop
keep no-op behavior; shutdown clears active context. No additional state/recovery/
shutdown gate. Clearing the active owner does not delete an independent session
registry, acquire/dispose DI or emit events.

## Metadata Boundary

Dict-root JSON with string keys, None/bool/int/finite float/valid Unicode str,
dict/list only. Reject cycles, non-string keys, non-JSON values, non-finite floats,
invalid Unicode and more than 256 dict/list levels (root counts as one). Failure
is safe ContractValidationError, never payload dump/coercion/RecursionError.
Repeated acyclic references are accepted and each occurrence detached.

merge validates/copies both inputs even if a malformed base value is overwritten.
Updates are shallow: replace whole values, preserve base key order, append new keys.
put validates source, key and value, including final-result nesting.
remove validates source/key even if missing; no input mutation.
contains validates source/key and is read-only, with no hidden storage/cache.
get validates source/key and detaches the selected value. Validate/copy default
only if key is absent and default is returned. All returned containers are detached.

## Session Boundary

Session owns dict[SessionId, RuntimeContext]; active Context is another owner.
create validates ingress before either owner changes; generated existing UUIDv4
PipelineId, L0_KERNEL, current UTC creation and no expiry remain. Successful create
becomes active and stores a separate session snapshot. Same-ID create replaces
that entry without changing insertion order; no new duplicate error.

get/update return independent detached snapshots. update_metadata uses shallow
merge, preserving session/pipeline/layer/trace/creation/expiry. Update active context
only when the active session_id matches; another active session stays unchanged.
Validation failure changes neither owner. Missing get/update/remove retains
RuntimeStateError. remove clears active context only on matching session_id.
contains is observational; list returns an insertion-ordered tuple of SessionIds,
not RuntimeContexts. No testing-only Session.clear or session/DI composition change.

## Reconciliation and Acceptance

ADR-006 supersedes only contradictory KR-008 Master entries: reverse DAG/prohibition,
context-valued list()/clear(), UUIDv7 trace generation, incompatible stored fields,
nonexistent context exceptions and obsolete test/API paths. ADR-004 P-04 supersedes
deep-frozen/shallow-copy/identity wording. All unaffected owners/decisions stay frozen.

Acceptance covers every public API, nested ingress/egress/session isolation,
value equality, shallow merge/order/defaults, invalid metadata/context/trace/date,
cycles/repeated references and 256/257/extreme depth; failed operations atomic;
active/non-active session update/removal, same-ID creation and lifetime/no globals.
Canonical tests remain tests/kernel/test_context.py, no skips/xfail hiding behavior.
At least 95% executable-line coverage per owned file, documented as line not branch
coverage; AST ownership/import DAG checks, kernel smoke and full regression.
Ruff (no --fix), strict Pyright Windows/Linux, discovered Pytest and latest-head
required CI must pass. One module/branch/report, then Tech Lead review; no KR-009 work.
