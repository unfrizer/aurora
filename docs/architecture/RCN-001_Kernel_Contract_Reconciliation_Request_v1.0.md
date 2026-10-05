# AURORA — Kernel Contract Reconciliation Request v1.0

**Document ID:** RCN-001  
**Status:** RESOLVED BY APPROVED ADR-004 — IMPLEMENTATION PENDING
**Date:** 2026-10-05  
**Scope:** K-01–K-05 from AUD-001; existing Wave 1 owners only  
**Implementation baseline:** `6ddc1815dc1a0fbacdd33b39c41794f964af885d`

## Purpose

Record the exact decisions needed before Kernel reconciliation can be implemented.
This document is prepared under ADR-001 so the Architecture Authority does not
need to author a new file manually. It does not approve an alternative API,
supersede an approved resolution, declare the Kernel complete, or authorize
implementation. Approval or merge of the audit PR alone does not resolve these
questions.

Sources inspected: AGENTS.md; ADR-001; AB-00B; AB-00D; the relevant DI, metadata,
pipeline and failure-path entries in Master Pack M-06; AUD-001; and the current
Kernel implementation. AB-00B/AB-00D take precedence over conflicting M-06 prose
on their explicitly resolved subjects.

## Invariants That Are Not Open for Redesign

- Architecture Freeze v1.0, L0–L8 ownership and downward dependency direction.
- Existing Runtime owners and canonical production paths.
- The exact RuntimeLayer, RuntimeStatus, EventPhase, EventPriority and DI scope
  vocabularies. FAILED and TERMINATED remain terminal under AB-00B.
- RuntimeContract's identity, asynchronous lifecycle and read-only health surface;
  it has no universal execute method under AB-00D.
- PublisherRuntime as the sole production RuntimeEvent construction owner.
- Sequential pipeline DAG execution and abort on the first stage failure.
- Explicit instance ownership, Python 3.13, uv and strict typing.
- No hidden global registry, upward business-layer import, new dependency,
  background task, network access or persistence in Kernel reconciliation.

## Decision Register

### K-01 — DI Acquisition, Initialization and Constructor Injection

**Owners:** KR-004 service contracts; KR-005 DI implementation; KR-011 tests.

Current evidence:

- ServiceContract.initialize is asynchronous and documents initialization once
  when the owning scope creates an instance.
- M-06 DI-004 requires provide to return an initialized instance but declares
  provide synchronously. Container/Resolver resolution is also synchronous.
- ProviderRuntime currently calls implementation without arguments. Resolver
  validation does nothing. Lazy resolution returns an uninitialized instance.
- ServiceDescriptor has service_id, scope, implementation and eager fields; it
  contains no constructor-parameter-to-ServiceId mapping.

Required explicit decisions:

1. Define the exact acquisition API. Either asynchronous resolution/provider
   acquisition or synchronous access restricted to already asynchronously
   prepared instances requires an explicit reconciliation. Neither is approved
   by this request. Do not bridge with asyncio.run or block a running event loop.
2. Define how constructor parameters map unambiguously to ServiceId, including
   missing registrations, multiple implementations and invalid annotations.
   Do not infer IDs from names or introduce an implicit global type registry.
3. Specify dependency-graph validation timing, cycle detection and admissible
   dependencies across the existing scopes. Specify whether eager non-Application
   descriptors are rejected or prepared only when their scope/context exists.
4. Define initialize-once behavior, failed initialization rollback, visibility of
   partially initialized instances and retry semantics. Define who disposes
   transient services and constructor dependencies after failures.

Changing a sync public signature, adding descriptor fields or a binding contract
must be recorded explicitly with its superseded declarations and migration/tests.
No such change is selected here.

### K-02 — Descriptor Removal and Cached Instance Disposal

**Owners:** KR-005; KR-011 tests. This must be reconciled together with K-01.

Current evidence:

- ContainerRuntime.remove unregisters only the descriptor. Re-registering the
  same ServiceId can return the previous cached implementation.
- M-06 DI-001 requires descriptor and cached-instance removal.
- M-06 ScopeRuntime APIs use ServiceId; the implementation uses ServiceDescriptor
  to select scope. The lookup/ownership source must therefore be reconciled.
- Service shutdown is asynchronous; remove is currently synchronous.

Required explicit decisions:

1. Define whether removal itself awaits disposal or immediately evicts instances
   and disposes them through a separately specified lifecycle operation.
2. Define removal across every active Application, Session and Pipeline cache,
   including the order of descriptor removal, eviction and disposal.
3. Specify missing-ID behavior, disposal failures, re-registration after failure
   and whether dependent cached services must also be invalidated.
4. Resolve the exact ScopeRuntime signatures and how they obtain scope ownership
   without a second registry or dependence on an already removed descriptor.

Clearing a cache entry without a defined resource-disposal path is not sufficient.

### K-03 — Binding Pipeline Stages to Actual Work

**Owners:** KR-009 execution; KR-004 only if a contract there is explicitly
authorized; KR-010 composition; KR-011 tests.

Current evidence:

- PipelineStage contains stage_id, module_id and depends_on only.
- ExecutorRuntime.execute_stage emits start/completion events but calls no work.
- M-06 PIPELINE-003 requires executing stages. AB-00D explicitly excludes execute
  from universal RuntimeContract; a module identifier is not an executable API.

Required explicit decisions:

1. Define the typed stage-work/binding contract, exact signature and canonical
   owner/path. Keep it separate from universal RuntimeContract.
2. Define how composition binds module/stage identity to executable work, how
   missing/duplicate bindings are rejected, and the registration lifetime.
3. Define inputs, output/state ownership, context handling and exception behavior.
   Kernel must not import application or higher-layer implementations to find work.
4. Specify failure-event behavior if work or an event handler raises, preserving
   first-stage-failure abort, deterministic order and the original failure.

A test that only observes start/completion events cannot certify stage execution.

### K-04 — Nested JSON Isolation and Snapshot Identity

**Owners:** KR-004 context/event contracts; KR-007 publisher; KR-008 context,
metadata and session operations; KR-011 tests.

Current evidence:

- Metadata operations and PublisherRuntime payload copying are shallow.
- RuntimeContext is a frozen dataclass containing mutable JSON dictionaries and
  lists; nested caller mutation can change active context data.
- AB-00D requires an immutable seven-field context and replace to store/return
  the supplied snapshot. The implementation/current tests preserve that identity.

Required explicit decisions:

1. Distinguish deep immutability from detached mutable copies. Define the exact
   ingress and egress isolation guarantees for metadata, sessions and events.
2. Specify whether current/replace retain object identity. Any replacement of
   AB-00D's identity semantics must explicitly identify the superseded wording.
3. Define whether canonical JSON aliases remain dictionaries/lists or require a
   separately authorized representation change. Do not silently add wrappers.
4. Specify invalid JSON rejection, non-finite values, cycles, unsupported depth
   and the existing exception vocabulary to use at each boundary.

Copying only at construction does not isolate active data from mutation through
the returned object. A frozen dataclass alone does not freeze nested dictionaries.

### K-05 — Failure Cleanup With a Terminal FAILED State

**Owners:** KR-005 resource disposal; KR-006 lifecycle coordination; KR-010
entrypoint/composition; KR-011 tests.

Current evidence:

- Lifecycle and scope disposal stop at the first exception. Application cache
  clearing occurs only after successful disposal.
- Normal shutdown requires SHUTTING_DOWN, which is not reachable from FAILED.
- M-06's illustrative FAILED-to-STOPPED path is superseded by AB-00B. It must not
  be reinstated to make cleanup possible.

Required explicit decisions:

1. Define cleanup after partial initialize/start failure without changing FAILED
   or adding a lifecycle transition. Specify the exact existing or new public
   entry point, if one is required.
2. Define which participants are tracked as created, initialized and started,
   their reverse cleanup order and behavior for a partially initialized service.
3. Define whether cleanup continues after failures, how errors are aggregated
   using approved exceptions, and how the original operation failure is retained.
4. Specify repeat-cleanup/idempotency, hook behavior and cache/reference release
   even when one participant's shutdown fails.

## Required Reconciliation Artifacts

After the Architecture Authority supplies or explicitly approves the decisions:

1. Codex prepares a canonical resolution/ADR with exact signatures, field sets,
   ownership, behavior, exception mapping, migration and limited precedence.
2. The resolution identifies every superseded M-03/M-06 or AB-00D declaration;
   unaffected approved decisions remain unchanged.
3. The API registry, affected module decisions and canonical test matrix are
   reconciled. Ownership of contracts, implementation and tests remains explicit.
4. Each affected module is implemented as its own authorized task/branch in
   dependency order. Cross-module changes are not implicitly authorized by this
   request.
5. Ruff, strict Pyright, discovered Pytest tests and Windows/Linux CI must pass.
   Routine PR creation/merge follows ADR-003; unresolved architecture decisions
   still require explicit acceptance and are not approved by routine PR handling.

No AGENTS waiver or change to Runtime ownership is necessary or proposed.

## Planned Regression Test Matrix — Not Yet Implemented

| Finding | Canonical tests | Required behavioral evidence |
| --- | --- | --- |
| K-01 | tests/kernel/test_contracts.py; tests/kernel/test_container.py | Lazy/eager initialization once; constructor injection; missing/ambiguous dependencies; cycles; scope restrictions; initialization failure rollback; transient disposal. |
| K-02 | tests/kernel/test_container.py | Remove/re-register returns new implementation; eviction across active scopes; disposal errors; dependent-instance policy; canonical ScopeRuntime signature. |
| K-03 | tests/kernel/test_pipeline.py; tests/integration/test_runtime_startup.py | Actual observable work invoked once in topological order; missing bindings rejected; first failure skips remaining work; failure event and original error preserved. |
| K-04 | tests/kernel/test_contracts.py; tests/kernel/test_context.py; tests/kernel/test_event_bus.py | Nested ingress/egress mutation isolation; explicitly approved identity behavior; session metadata; invalid/cyclic JSON; unchanged canonical schemas. |
| K-05 | tests/kernel/test_container.py; tests/kernel/test_lifecycle.py; tests/kernel/test_bootstrap.py; tests/integration/test_runtime_startup.py | Partial startup and multiple shutdown failures still release resources; deterministic order; retained terminal FAILED; original/cleanup errors; repeat cleanup. |

These are acceptance requirements for a future approved reconciliation, not tests
claimed to pass today. The current 337 passing tests do not cover all of them.

## Concrete Proposal Prepared

[ADR-004](ADR-004_Kernel_Reconciliation_Proposal_v1.0.md) proposes concrete P-01–P-05
decisions, signatures, migration/ownership boundaries and acceptance tests. It
also records the current Scope-to-Provider and Bootstrap-to-Executor import
conflicts against M-04. The Architecture Authority explicitly approved ADR-004
in full on 2026-10-05, including P-01–P-05, the P-03 M-04 clarification and
contract-required canonical test adjustments. The direct reply to the approval
question was "го дальше". This resolves the decision request, not the code defects.

Routine PR creation/merge now follows ADR-003. That standing workflow permission
does not replace architecture acceptance of ADR-004 or any unresolved contract.

## Next Authorized Action

The local-hardening PR #14 is merged; standing workflow permission is recorded
in ADR-003, merged through PR #15. ADR-004 now supplies the separately approved
K-01–K-05 decisions. Compile/reconcile the active KR-004 module contract and
registries, implement that module, validate and return one module report.
Codex will maintain the documents; no manual file creation by the user is required.
Other Kernel modules and dependent features remain frozen until their corresponding
approved module contracts and preceding module review gates are satisfied.
