from __future__ import annotations

import asyncio
import gc
import weakref
from collections.abc import Awaitable, Callable
from dataclasses import FrozenInstanceError
from datetime import UTC
from itertools import pairwise
from typing import cast

import pytest

from src.core.exceptions import (
    RuntimeInitializationError,
    RuntimeShutdownError,
    RuntimeStateError,
)
from src.core.types import HealthStatus, RuntimeLayer, RuntimeStatus
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.hooks import HookRuntime, LifecycleHook
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.state import StateRuntime


class RecordingRuntime(RuntimeContract):
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls
        self.errors: dict[str, list[BaseException]] = {}
        self.callbacks: dict[str, Callable[[], Awaitable[None]]] = {}

    @property
    def runtime_name(self) -> str:
        return self.name

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    async def _record(self, operation: str) -> None:
        self.calls.append(f"{self.name}.{operation}")
        if self.errors.get(operation):
            raise self.errors[operation].pop(0)
        callback = self.callbacks.get(operation)
        if callback is not None:
            await callback()

    async def initialize(self) -> None:
        await self._record("initialize")

    async def start(self) -> None:
        await self._record("start")

    async def stop(self) -> None:
        await self._record("stop")

    async def shutdown(self) -> None:
        await self._record("shutdown")

    def health(self) -> HealthStatus:
        return HealthStatus.OK


def _participants(
    lifecycle: LifecycleRuntime, calls: list[str]
) -> tuple[RecordingRuntime, RecordingRuntime, RecordingRuntime]:
    runtimes = (
        RecordingRuntime("a", calls),
        RecordingRuntime("b", calls),
        RecordingRuntime("c", calls),
    )
    for runtime in runtimes:
        lifecycle.register(runtime)
    return runtimes


def _hook(
    calls: list[str], name: str, error: BaseException | None = None
) -> Callable[[], Awaitable[None]]:
    async def callback() -> None:
        calls.append(name)
        if error is not None:
            raise error

    return callback


def _group(error: BaseException) -> tuple[Exception, ...]:
    cause = error.__cause__
    assert isinstance(cause, ExceptionGroup)
    return cast("ExceptionGroup[Exception]", cause).exceptions


async def test_lifecycle_follows_resolved_transition_sequence() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _participants(lifecycle, calls)
    for hook in LifecycleHook:
        lifecycle.hooks().register(hook, _hook(calls, hook.value))
    assert lifecycle.runtime_name == "lifecycle"
    assert lifecycle.runtime_layer is RuntimeLayer.L0_KERNEL
    assert lifecycle.health() is HealthStatus.OK
    initial = lifecycle.state()
    assert initial.previous is None
    assert initial.transition_count == 0
    assert initial.entered_at.tzinfo is UTC
    await lifecycle.initialize()
    assert lifecycle.state().is_ready
    await lifecycle.start()
    assert lifecycle.state().is_running
    await lifecycle.stop()
    await lifecycle.stop()
    await lifecycle.shutdown()
    await lifecycle.shutdown()
    assert lifecycle.status is RuntimeStatus.TERMINATED
    assert lifecycle.state().transition_count == 8
    assert lifecycle.health() is HealthStatus.OK
    assert calls == [
        "before_initialize",
        "a.initialize",
        "b.initialize",
        "c.initialize",
        "after_initialize",
        "before_start",
        "a.start",
        "b.start",
        "c.start",
        "after_start",
        "before_stop",
        "c.stop",
        "b.stop",
        "a.stop",
        "after_stop",
        "c.shutdown",
        "b.shutdown",
        "a.shutdown",
    ]
    for hook in LifecycleHook:
        await lifecycle.hooks().execute(hook)
    assert len(calls) == 18


@pytest.mark.parametrize("source", tuple(RuntimeStatus))
@pytest.mark.parametrize("target", tuple(RuntimeStatus))
def test_state_runtime_accepts_only_the_ab00b_transition_matrix(
    source: RuntimeStatus, target: RuntimeStatus
) -> None:
    normal = (
        RuntimeStatus.CREATED,
        RuntimeStatus.INITIALIZING,
        RuntimeStatus.READY,
        RuntimeStatus.STARTING,
        RuntimeStatus.RUNNING,
        RuntimeStatus.STOPPING,
        RuntimeStatus.STOPPED,
        RuntimeStatus.SHUTTING_DOWN,
        RuntimeStatus.TERMINATED,
    )
    failure_sources = (
        RuntimeStatus.INITIALIZING,
        RuntimeStatus.READY,
        RuntimeStatus.STARTING,
        RuntimeStatus.RUNNING,
        RuntimeStatus.STOPPING,
        RuntimeStatus.SHUTTING_DOWN,
    )
    allowed: set[tuple[RuntimeStatus, RuntimeStatus]] = set(pairwise(normal))
    allowed.update((status, RuntimeStatus.FAILED) for status in failure_sources)
    state = StateRuntime()
    if source is RuntimeStatus.FAILED:
        state.transition(RuntimeStatus.INITIALIZING)
        state.transition(RuntimeStatus.FAILED)
    else:
        for status in normal[1:]:
            if state.current() is source:
                break
            state.transition(status)
    before = state.snapshot()
    assert state.previous() is before.previous
    assert state.can_transition(target) == ((source, target) in allowed)
    if (source, target) in allowed:
        after = state.transition(target)
        assert after.current is target
        assert after.previous is source
        assert after.transition_count == before.transition_count + 1
        assert after.entered_at.tzinfo is UTC
        assert state.snapshot() == after
        assert before.current is source
    else:
        with pytest.raises(RuntimeStateError):
            state.transition(target)
        assert state.snapshot() == before


@pytest.mark.parametrize("field_name", ("current", "previous", "entered_at", "transition_count"))
def test_snapshot_cannot_be_mutated(field_name: str) -> None:
    snapshot = StateRuntime().snapshot()
    with pytest.raises(FrozenInstanceError):
        setattr(snapshot, field_name, RuntimeStatus.FAILED)


@pytest.mark.parametrize("hook", tuple(LifecycleHook))
async def test_hook_identity_order_unregister_and_clear(hook: LifecycleHook) -> None:
    calls: list[str] = []
    hooks = HookRuntime()
    first = _hook(calls, "first")
    second = _hook(calls, "second")
    hooks.register(hook, first)
    hooks.register(hook, first)
    hooks.register(hook, second)
    hooks.unregister(hook, _hook(calls, "missing"))
    await hooks.execute(hook)
    assert calls == ["first", "second"]
    hooks.unregister(hook, first)
    await hooks.execute(hook)
    assert calls == ["first", "second", "second"]
    hooks.clear()
    await hooks.execute(hook)
    assert len(calls) == 3


@pytest.mark.parametrize("hook", tuple(LifecycleHook))
async def test_hooks_capture_registration_order_for_the_active_execution(
    hook: LifecycleHook,
) -> None:
    calls: list[str] = []
    hooks = HookRuntime()
    second = _hook(calls, "second")

    async def first() -> None:
        calls.append("first")
        hooks.unregister(hook, second)

    hooks.register(hook, first)
    hooks.register(hook, second)
    await hooks.execute(hook)
    assert calls == ["first", "second"]
    await hooks.execute(hook)
    assert calls == ["first", "second", "first"]


@pytest.mark.parametrize(
    "hook",
    (
        LifecycleHook.BEFORE_INITIALIZE,
        LifecycleHook.AFTER_INITIALIZE,
        LifecycleHook.BEFORE_START,
        LifecycleHook.AFTER_START,
    ),
)
async def test_startup_hooks_fail_fast(hook: LifecycleHook) -> None:
    calls: list[str] = []
    hooks = HookRuntime()
    failure = ValueError("original")
    hooks.register(hook, _hook(calls, "first", failure))
    hooks.register(hook, _hook(calls, "unattempted"))
    with pytest.raises(ValueError) as caught:
        await hooks.execute(hook)
    assert caught.value is failure
    assert calls == ["first"]


@pytest.mark.parametrize("operation", ("initialize", "start"))
async def test_partial_startup_failure_cleans_only_touched_in_reverse(
    operation: str,
) -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _, second, _ = _participants(lifecycle, calls)
    original = ValueError("original")
    second.errors[operation] = [original]
    if operation == "start":
        await lifecycle.initialize()
        calls.clear()
    with pytest.raises(RuntimeInitializationError) as caught:
        await getattr(lifecycle, operation)()
    assert caught.value.__cause__ is original
    assert lifecycle.status is RuntimeStatus.FAILED
    assert lifecycle.health() is HealthStatus.ERROR
    assert calls == (
        ["a.initialize", "b.initialize", "b.shutdown", "a.shutdown"]
        if operation == "initialize"
        else ["a.start", "b.start", "b.stop", "a.stop", "c.shutdown", "b.shutdown", "a.shutdown"]
    )
    before = lifecycle.state()
    await lifecycle.stop()
    await lifecycle.shutdown()
    assert lifecycle.state() == before
    with pytest.raises(RuntimeStateError):
        await lifecycle.initialize()
    with pytest.raises(RuntimeStateError):
        await lifecycle.start()


@pytest.mark.parametrize(
    ("hook", "initialized", "started"),
    [
        (LifecycleHook.BEFORE_INITIALIZE, False, False),
        (LifecycleHook.AFTER_INITIALIZE, True, False),
        (LifecycleHook.BEFORE_START, True, False),
        (LifecycleHook.AFTER_START, True, True),
    ],
)
async def test_lifecycle_startup_hook_failure_keeps_original_and_cleans_resources(
    hook: LifecycleHook, initialized: bool, started: bool
) -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _participants(lifecycle, calls)
    failure = ValueError("hook")
    lifecycle.hooks().register(hook, _hook(calls, "failing", failure))
    if hook in (LifecycleHook.BEFORE_START, LifecycleHook.AFTER_START):
        await lifecycle.initialize()
        calls.clear()
        operation = lifecycle.start
    else:
        operation = lifecycle.initialize
    with pytest.raises(RuntimeInitializationError) as caught:
        await operation()
    assert caught.value.__cause__ is failure
    assert lifecycle.status is RuntimeStatus.FAILED
    assert [call for call in calls if call.endswith(".shutdown")] == (
        ["c.shutdown", "b.shutdown", "a.shutdown"] if initialized else []
    )
    assert [call for call in calls if call.endswith(".stop")] == (
        ["c.stop", "b.stop", "a.stop"] if started else []
    )
    count = len(calls)
    for phase in LifecycleHook:
        await lifecycle.hooks().execute(phase)
    assert len(calls) == count


async def test_startup_cleanup_error_group_is_original_then_attempt_order() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    first, second, third = _participants(lifecycle, calls)
    original = ValueError("start")
    hook_error = ValueError("before stop")
    stop_error = ValueError("second stop")
    shutdown_error = ValueError("third shutdown")
    after_error = ValueError("after stop")
    first_shutdown = ValueError("first shutdown")
    second.errors["start"] = [original]
    second.errors["stop"] = [stop_error]
    third.errors["shutdown"] = [shutdown_error]
    first.errors["shutdown"] = [first_shutdown]
    lifecycle.hooks().register(LifecycleHook.BEFORE_STOP, _hook(calls, "before", hook_error))
    lifecycle.hooks().register(LifecycleHook.AFTER_STOP, _hook(calls, "after", after_error))
    await lifecycle.initialize()
    with pytest.raises(RuntimeInitializationError) as caught:
        await lifecycle.start()
    assert _group(caught.value) == (
        original,
        hook_error,
        stop_error,
        after_error,
        shutdown_error,
        first_shutdown,
    )
    assert lifecycle.status is RuntimeStatus.FAILED
    count = len(calls)
    await lifecycle.shutdown()
    assert len(calls) == count


async def test_initialization_cleanup_failure_does_not_skip_other_resources() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    first, second, _ = _participants(lifecycle, calls)
    original = ValueError("initialize")
    cleanup = ValueError("shutdown")
    second.errors["initialize"] = [original]
    second.errors["shutdown"] = [cleanup]
    with pytest.raises(RuntimeInitializationError) as caught:
        await lifecycle.initialize()
    assert _group(caught.value) == (original, cleanup)
    assert calls[-2:] == ["b.shutdown", "a.shutdown"]
    assert first.runtime_name == "a"


async def test_stop_hooks_and_participants_all_attempted_despite_multiple_errors() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    first, _, third = _participants(lifecycle, calls)
    errors = tuple(ValueError(str(index)) for index in range(6))
    hooks = lifecycle.hooks()
    hooks.register(LifecycleHook.BEFORE_STOP, _hook(calls, "before1", errors[0]))
    hooks.register(LifecycleHook.BEFORE_STOP, _hook(calls, "before2", errors[1]))
    third.errors["stop"] = [errors[2]]
    first.errors["stop"] = [errors[3]]
    hooks.register(LifecycleHook.AFTER_STOP, _hook(calls, "after1", errors[4]))
    hooks.register(LifecycleHook.AFTER_STOP, _hook(calls, "after2", errors[5]))
    await lifecycle.initialize()
    await lifecycle.start()
    calls.clear()
    with pytest.raises(RuntimeShutdownError) as caught:
        await lifecycle.stop()
    assert _group(caught.value) == errors
    assert calls == ["before1", "before2", "c.stop", "b.stop", "a.stop", "after1", "after2"]
    before = lifecycle.state()
    await lifecycle.stop()
    await lifecycle.shutdown()
    assert lifecycle.state() == before
    assert calls[-3:] == ["c.shutdown", "b.shutdown", "a.shutdown"]
    await hooks.execute(LifecycleHook.BEFORE_STOP)
    assert len(calls) == 10


async def test_shutdown_attempts_all_and_releases_participant_and_hook_references() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    first, second, third = _participants(lifecycle, calls)
    failures = (ValueError("third"), ValueError("first"))
    third.errors["shutdown"] = [failures[0]]
    first.errors["shutdown"] = [failures[1]]
    refs = tuple(weakref.ref(runtime) for runtime in (first, second, third))
    callback = _hook(calls, "unused")
    callback_ref = weakref.ref(callback)
    lifecycle.hooks().register(LifecycleHook.BEFORE_INITIALIZE, callback)
    await lifecycle.initialize()
    await lifecycle.start()
    await lifecycle.stop()
    with pytest.raises(RuntimeShutdownError) as caught:
        await lifecycle.shutdown()
    assert _group(caught.value) == failures
    assert calls[-3:] == ["c.shutdown", "b.shutdown", "a.shutdown"]
    before = lifecycle.state()
    await lifecycle.shutdown()
    assert lifecycle.state() == before
    del caught, failures, first, second, third, callback
    gc.collect()
    assert all(ref() is None for ref in refs)
    assert callback_ref() is None


@pytest.mark.parametrize("operation", ("initialize", "start", "stop", "shutdown"))
async def test_single_cancellation_cleans_pending_and_is_not_wrapped(operation: str) -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _, second, _ = _participants(lifecycle, calls)
    cancellation = asyncio.CancelledError("cancel")
    second.errors[operation] = [cancellation]
    if operation != "initialize":
        await lifecycle.initialize()
    if operation in ("stop", "shutdown"):
        await lifecycle.start()
    if operation == "shutdown":
        await lifecycle.stop()
    calls.clear()
    with pytest.raises(asyncio.CancelledError) as caught:
        await getattr(lifecycle, operation)()
    assert caught.value is cancellation
    assert lifecycle.status is RuntimeStatus.FAILED
    if operation in ("initialize", "start", "shutdown"):
        shutdown_before = calls.count("b.shutdown")
        await lifecycle.shutdown()
        assert calls.count("b.shutdown") == shutdown_before
    else:
        assert calls == ["c.stop", "b.stop", "b.stop", "a.stop"]
        await lifecycle.shutdown()
        assert calls[-3:] == ["c.shutdown", "b.shutdown", "a.shutdown"]


@pytest.mark.parametrize("operation", ("initialize", "start", "stop", "shutdown"))
async def test_second_cancellation_retains_remaining_ownership_for_shutdown(
    operation: str,
) -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _, second, third = _participants(lifecycle, calls)
    if operation == "initialize":
        second.errors["initialize"] = [asyncio.CancelledError()]
        second.errors["shutdown"] = [asyncio.CancelledError()]
    elif operation == "start":
        second.errors["start"] = [asyncio.CancelledError()]
        second.errors["stop"] = [asyncio.CancelledError()]
    else:
        second.errors[operation] = [asyncio.CancelledError(), asyncio.CancelledError()]
    if operation != "initialize":
        await lifecycle.initialize()
    if operation in ("stop", "shutdown"):
        await lifecycle.start()
    if operation == "shutdown":
        await lifecycle.stop()
    calls.clear()
    with pytest.raises(asyncio.CancelledError):
        await getattr(lifecycle, operation)()
    before = lifecycle.state()
    await lifecycle.shutdown()
    assert lifecycle.state() == before
    assert calls.count("a.shutdown") == 1
    assert calls.count("b.shutdown") == (
        3 if operation == "shutdown" else 2 if operation == "initialize" else 1
    )
    assert calls.count("c.shutdown") == (0 if operation == "initialize" else 1)
    assert calls.count("c.stop") <= 1
    assert third.runtime_name == "c"


async def test_real_repeated_task_cancellation_can_resume_explicit_shutdown() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _, second, _ = _participants(lifecycle, calls)
    entered = asyncio.Event()
    cleanup_entered = asyncio.Event()
    never = asyncio.Event()

    async def block_initialize() -> None:
        entered.set()
        await never.wait()

    async def block_shutdown() -> None:
        cleanup_entered.set()
        await never.wait()

    second.callbacks["initialize"] = block_initialize
    second.callbacks["shutdown"] = block_shutdown
    task = asyncio.create_task(lifecycle.initialize())
    await asyncio.wait_for(entered.wait(), timeout=2)
    task.cancel()
    await asyncio.wait_for(cleanup_entered.wait(), timeout=2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert lifecycle.status is RuntimeStatus.FAILED
    second.callbacks.clear()
    await lifecycle.shutdown()
    assert calls == ["a.initialize", "b.initialize", "b.shutdown", "b.shutdown", "a.shutdown"]


@pytest.mark.parametrize("phase", (LifecycleHook.BEFORE_STOP, LifecycleHook.AFTER_STOP))
async def test_cancelled_stop_hooks_resume_remaining_without_repeating_attempts(
    phase: LifecycleHook,
) -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _participants(lifecycle, calls)
    failure = ValueError("first hook")
    hook = lifecycle.hooks()
    hook.register(phase, _hook(calls, "first", failure))
    hook.register(phase, _hook(calls, "cancel1", asyncio.CancelledError()))
    hook.register(phase, _hook(calls, "cancel2", asyncio.CancelledError()))
    hook.register(phase, _hook(calls, "last"))
    await lifecycle.initialize()
    await lifecycle.start()
    with pytest.raises(asyncio.CancelledError) as caught:
        await lifecycle.stop()
    assert _group(caught.value) == (failure,)
    await lifecycle.shutdown()
    assert lifecycle.status is RuntimeStatus.FAILED
    for name in ("first", "cancel1", "cancel2", "last"):
        assert calls.count(name) == 1
    for name in ("a", "b", "c"):
        assert calls.count(f"{name}.stop") == 1
        assert calls.count(f"{name}.shutdown") == 1


async def test_cleanup_cancellation_preserves_original_startup_and_hook_errors() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _, second, _ = _participants(lifecycle, calls)
    original = ValueError("start failure")
    hook_error = ValueError("hook failure")
    second.errors["start"] = [original]
    hooks = lifecycle.hooks()
    hooks.register(LifecycleHook.BEFORE_STOP, _hook(calls, "first", hook_error))
    hooks.register(LifecycleHook.BEFORE_STOP, _hook(calls, "cancel", asyncio.CancelledError()))
    await lifecycle.initialize()
    with pytest.raises(asyncio.CancelledError) as caught:
        await lifecycle.start()
    assert _group(caught.value) == (original, hook_error)
    await lifecycle.shutdown()
    assert lifecycle.status is RuntimeStatus.FAILED
    assert calls.count("first") == 1
    assert calls.count("cancel") == 1


async def test_cancelled_initialization_retains_ordinary_cleanup_errors() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    first, second, _ = _participants(lifecycle, calls)
    failure = ValueError("shutdown")
    second.errors["initialize"] = [asyncio.CancelledError()]
    first.errors["shutdown"] = [failure]
    with pytest.raises(asyncio.CancelledError) as caught:
        await lifecycle.initialize()
    assert _group(caught.value) == (failure,)
    await lifecycle.shutdown()
    assert calls.count("a.shutdown") == 1


async def test_registration_is_identity_based_and_frozen_after_startup() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    first = RecordingRuntime("first", calls)
    lifecycle.register(first)
    lifecycle.register(first)
    with pytest.raises(RuntimeStateError):
        lifecycle.register(lifecycle)
    await lifecycle.initialize()
    with pytest.raises(RuntimeStateError):
        lifecycle.register(RecordingRuntime("late", calls))
    assert calls == ["first.initialize"]


@pytest.mark.parametrize("operation", ("initialize", "start", "stop", "shutdown", "transition"))
async def test_reentrant_mutation_rejected_without_corrupting_active_operation(
    operation: str,
) -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    participant = RecordingRuntime("first", calls)
    lifecycle.register(participant)

    async def reenter() -> None:
        assert lifecycle.status is RuntimeStatus.INITIALIZING
        assert lifecycle.health() is HealthStatus.OK
        with pytest.raises(RuntimeStateError):
            if operation == "transition":
                await lifecycle.transition(RuntimeStatus.READY)
            else:
                await getattr(lifecycle, operation)()
        with pytest.raises(RuntimeStateError):
            lifecycle.register(RecordingRuntime("late", calls))

    participant.callbacks["initialize"] = reenter
    await lifecycle.initialize()
    assert lifecycle.status is RuntimeStatus.READY


async def test_concurrent_mutation_is_rejected_not_queued() -> None:
    lifecycle = LifecycleRuntime()
    entered = asyncio.Event()
    release = asyncio.Event()

    async def block() -> None:
        entered.set()
        await release.wait()

    lifecycle.hooks().register(LifecycleHook.BEFORE_INITIALIZE, block)
    task = asyncio.create_task(lifecycle.initialize())
    await asyncio.wait_for(entered.wait(), timeout=2)
    with pytest.raises(RuntimeStateError):
        await lifecycle.start()
    release.set()
    await task
    assert lifecycle.status is RuntimeStatus.READY


async def test_public_transition_and_failed_cleanup_never_recover_status() -> None:
    lifecycle = LifecycleRuntime()
    await lifecycle.transition(RuntimeStatus.INITIALIZING)
    await lifecycle.transition(RuntimeStatus.FAILED)
    snapshot = lifecycle.state()
    await lifecycle.stop()
    await lifecycle.shutdown()
    assert lifecycle.state() == snapshot
    with pytest.raises(RuntimeStateError):
        await lifecycle.transition(RuntimeStatus.STOPPED)


async def test_invalid_order_preserves_state_and_allows_later_valid_operation() -> None:
    lifecycle = LifecycleRuntime()
    initial = lifecycle.state()
    for operation in (lifecycle.start, lifecycle.stop, lifecycle.shutdown):
        with pytest.raises(RuntimeStateError):
            await operation()
        assert lifecycle.state() == initial
    await lifecycle.initialize()
    with pytest.raises(RuntimeStateError):
        await lifecycle.initialize()
    await lifecycle.start()
    with pytest.raises(RuntimeStateError):
        await lifecycle.start()
    await lifecycle.stop()
    await lifecycle.shutdown()


async def test_cleanup_error_messages_do_not_expose_participant_secrets() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    participant = RecordingRuntime("first", calls)
    participant.errors["initialize"] = [ValueError("secret-api-key")]
    participant.errors["shutdown"] = [ValueError("secret-token")]
    lifecycle.register(participant)
    with pytest.raises(RuntimeInitializationError) as caught:
        await lifecycle.initialize()
    assert "secret" not in str(caught.value)
    cause = caught.value.__cause__
    assert cause is not None
    assert "secret" not in str(cause)


@pytest.mark.parametrize("phase", tuple(LifecycleHook))
async def test_hook_clear_during_execution_preserves_the_captured_batch(
    phase: LifecycleHook,
) -> None:
    calls: list[str] = []
    hooks = HookRuntime()

    async def first() -> None:
        calls.append("first")
        hooks.clear()

    hooks.register(phase, first)
    hooks.register(phase, _hook(calls, "second"))
    await hooks.execute(phase)
    await hooks.execute(phase)
    assert calls == ["first", "second"]


async def test_initialization_failure_cleanup_cancellation_preserves_original() -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _, second, _ = _participants(lifecycle, calls)
    original = ValueError("initialize")
    second.errors["initialize"] = [original]
    second.errors["shutdown"] = [asyncio.CancelledError()]
    with pytest.raises(asyncio.CancelledError) as caught:
        await lifecycle.initialize()
    assert _group(caught.value) == (original,)
    assert lifecycle.status is RuntimeStatus.FAILED
    await lifecycle.shutdown()
    assert calls[-2:] == ["b.shutdown", "a.shutdown"]
    assert calls.count("a.shutdown") == 1


@pytest.mark.parametrize("operation", ("stop", "shutdown"))
async def test_cleanup_error_before_repeated_cancellation_is_not_lost(operation: str) -> None:
    calls: list[str] = []
    lifecycle = LifecycleRuntime()
    _, second, third = _participants(lifecycle, calls)
    failure = ValueError("cleanup")
    third.errors[operation] = [failure]
    second.errors[operation] = [asyncio.CancelledError(), asyncio.CancelledError()]
    await lifecycle.initialize()
    await lifecycle.start()
    if operation == "shutdown":
        await lifecycle.stop()
    with pytest.raises(asyncio.CancelledError) as caught:
        await getattr(lifecycle, operation)()
    assert _group(caught.value) == (failure,)
    await lifecycle.shutdown()
    assert lifecycle.status is RuntimeStatus.FAILED
    assert calls.count(f"c.{operation}") == 1
    assert calls.count("a.shutdown") == 1
