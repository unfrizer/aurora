# KR-006 — Lifecycle Contract v1.0

**Status:** APPROVED — compiled ADR-004 P-05 lifecycle reconciliation.

**Authority:** Architecture Freeze v1.0, AB-00A/B/D, M-06, ADR-001 and
explicitly approved ADR-004. Tech Lead accepted KR-005 with “утверждаю,дальше”.
This contract compiles existing decisions; it does not approve new architecture.

## Purpose, Dependencies and Authorized Files

KR-006 coordinates deterministic, sequential, in-memory participant lifecycle,
best-effort cleanup and cancellation. StateRuntime remains the sole status owner.
Dependencies are Foundation KR-001 and the approved KR-004 lifecycle/runtime
contracts. No DI, events, context, pipeline, business logic or higher-layer import.

Existing production scope:

- `src/kernel/runtime/lifecycle.py`
- `src/kernel/runtime/state.py` only for a demonstrated local compatibility defect
- `src/kernel/runtime/hooks.py`

Only `tests/kernel/test_lifecycle.py` may change under ADR-004's canonical test
permission; test ownership remains KR-011. Governance registries may be reconciled
under ADR-001. No other source, test, configuration or dependency file may change.

## Exact API and Ownership

LifecycleRuntime implements existing LifecycleContract and AB-00D RuntimeContract:

```python
def __init__(self) -> None: ...
@property
def runtime_name(self) -> str: ...
@property
def runtime_layer(self) -> RuntimeLayer: ...
@property
def status(self) -> RuntimeStatus: ...
def register(self, runtime: RuntimeContract) -> None: ...
def hooks(self) -> HookRuntime: ...
async def initialize(self) -> None: ...
async def start(self) -> None: ...
async def stop(self) -> None: ...
async def shutdown(self) -> None: ...
async def transition(self, target: RuntimeStatus) -> None: ...
def state(self) -> LifecycleState: ...
def health(self) -> HealthStatus: ...
```

Retain current name `lifecycle`, L0_KERNEL, status property consumed by RuntimeKernel,
and ERROR health only in FAILED, otherwise OK. No status() compatibility shim.
Register participants before initialization; repeated registration of the same
object does not duplicate work. Reject self-registration and concurrent/re-entrant
mutating lifecycle operations with existing RuntimeStateError. Read-only status,
state, health and hook access remain available. Private busy/cleanup progress is
not a second RuntimeStatus source or a recovery API.

StateRuntime retains current(), previous(), snapshot(), can_transition(target)
and transition(target) -> LifecycleState. No reset/recover. Its legal matrix is
exactly AB-00B: eight normal edges and six failure edges, with FAILED/TERMINATED
terminal. Snapshots have current/previous/UTC entered_at/transition_count. The
class-level transition declaration must not be mutable shared runtime state.

HookRuntime retains register(hook, callback), unregister(hook, callback), async
execute(hook) and clear(). LifecycleHook remains exactly BEFORE/AFTER_INITIALIZE,
BEFORE/AFTER_START and BEFORE/AFTER_STOP with current values. No shutdown hooks,
register_initialize variants or new exception vocabulary. Callback lists are
instance-owned; execution captures registration order and awaits sequentially.
Initialization/start hooks fail fast. Stop hooks attempt every callback despite
ordinary errors and report an ordered ExceptionGroup. If cancellation interrupts
a stop-hook phase, already attempted callbacks are not repeated and remaining
callbacks can resume in that phase. No task, lock or shield is created.

## Lifecycle and Failure Semantics — ADR-004 P-05

Record participant attempts before awaiting initialize/start. Startup is forward
registration order; cleanup is reverse touched-participant order, not all merely
registered objects. Initialization/start remain single-use through AB-00B legality.

- Initialization failure: transition FAILED legally, shutdown all initialize-touched
  participants, clear final references/hooks, then report the original error.
- Start failure: transition FAILED legally, stop all start-touched participants,
  then shutdown all initialize-touched participants; report original error first.
- Normal stop: RUNNING -> STOPPING -> STOPPED on success. BEFORE_STOP and AFTER_STOP
  surround reverse stop cleanup and ordinary hook errors cannot prevent it.
- Normal shutdown: STOPPED -> SHUTTING_DOWN -> TERMINATED on success. Shutdown
  every initialize-touched participant; final attempts release participant and
  hook references even when ordinary disposal fails.
- Any ordinary cleanup failure marks FAILED where AB-00B permits it. FAILED stop/
  shutdown are cleanup-only, never transitions to a successful status. Explicit
  FAILED shutdown finishes outstanding stop cleanup before shutdown cleanup.
- Completed stop/shutdown cleanup is a no-op on repetition. A disposal that
  returned or raised an ordinary exception is a completed attempt, not retried.
  An interrupted disposal remains owned for explicit retry; completed attempts
  must not repeat. Untouched registrations have no allocated lifecycle resources.

RuntimeInitializationError chains its single original operation error directly;
if cleanup also fails, its ExceptionGroup cause has original first followed by
cleanup errors in attempt order. Stop/shutdown failures use RuntimeShutdownError
with an ordered ExceptionGroup cause. Messages never include participant payloads,
exception strings or secrets. Ordinary errors are reported, never silently swallowed.

CancelledError transitions to FAILED when legal, attempts the same remaining
cleanup and is re-raised, never wrapped as an ordinary runtime error or success.
Initialize cancellation performs shutdown; start cancellation performs stop then
shutdown; stop cancellation finishes stop; shutdown cancellation finishes remaining
stop/shutdown. A second cancellation may interrupt cleanup: retain remaining
ownership for a later explicit shutdown, without background work. Ordinary errors
encountered before/during cancellation remain available in its chained error group.

## Registry Precedence and Validation

This exact compiled contract replaces obsolete KR-006 sync methods, reset helpers,
shutdown hooks, fail-fast teardown and FAILED-to-STOPPED prose in M-01/M-03/M-04/
M-05/M-06/M-07/M-09 only to apply AB-00B/D and ADR-004 P-05. All other module
ownership/API/import declarations remain unchanged.

Canonical tests must cover all 100 source/target pairs, immutable UTC snapshots,
normal order, identity/registration rules, all six hook phases, partial initialize/
start, before/after hook failure, multiple cleanup failures with ordered causes,
terminal FAILED, reference release, idempotency, cancellation and interrupted
cleanup retry, and mutation/re-entrancy guards. No skipped/xfail tests. Test all
public APIs and meet the M-09 minimum 95% executable-line coverage per runtime file.
Run uv run pyright, uv run ruff check ., uv run pytest, scoped formatter check and
Kernel startup smoke. Required latest-commit Windows/Linux CI must pass before
ordinary merge under ADR-003. Report unrelated failures, do not fix outside scope.
Produce one full module report and stop for Tech Lead review.
