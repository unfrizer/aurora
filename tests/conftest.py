"""KR-011 function-scoped Kernel fixtures with explicit ownership and teardown."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio

from src.core.config import get_settings
from src.core.settings import Settings
from src.core.types import PipelineId, RuntimeLayer, RuntimeStatus, SessionId, TraceId
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[Settings]:
    names = {
        "app_name",
        "aurora_env",
        "aurora_log_level",
        "timezone",
        "aurora_config_path",
        "data_path",
        "cache_path",
        "logs_path",
    }
    for name in tuple(os.environ):
        if name.casefold() in names:
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()
    try:
        yield Settings()
    finally:
        get_settings.cache_clear()


@pytest.fixture
def trace_context() -> TraceContext:
    return TraceContext(trace_id=TraceId(uuid4()))


@pytest.fixture
def runtime_context(trace_context: TraceContext) -> RuntimeContext:
    return RuntimeContext(
        session_id=SessionId(uuid4()),
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=trace_context,
    )


@pytest_asyncio.fixture
async def container() -> AsyncIterator[ContainerRuntime]:
    instance = ContainerRuntime()
    try:
        yield instance
    finally:
        await instance.shutdown()


@pytest_asyncio.fixture
async def event_bus() -> AsyncIterator[EventBusRuntime]:
    instance = EventBusRuntime()
    try:
        yield instance
    finally:
        await instance.shutdown()


@pytest_asyncio.fixture
async def orchestrator(event_bus: EventBusRuntime) -> AsyncIterator[OrchestratorRuntime]:
    instance = OrchestratorRuntime(event_bus)
    try:
        yield instance
    finally:
        await instance.shutdown()


@pytest_asyncio.fixture
async def lifecycle(
    container: ContainerRuntime,
    event_bus: EventBusRuntime,
    orchestrator: OrchestratorRuntime,
) -> AsyncIterator[LifecycleRuntime]:
    instance = LifecycleRuntime()
    instance.register(container)
    instance.register(event_bus)
    instance.register(orchestrator)
    try:
        await instance.initialize()
        await instance.start()
        yield instance
    finally:
        try:
            if instance.status is RuntimeStatus.RUNNING:
                await instance.stop()
        finally:
            await instance.shutdown()
