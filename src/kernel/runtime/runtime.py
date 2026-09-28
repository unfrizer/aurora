"""KR-010 public Wave 1 runtime facade."""

from __future__ import annotations

from src.core.types import HealthStatus, Metadata, RuntimeLayer, RuntimeStatus
from src.core.version import ARCHITECTURE_VERSION, KERNEL_RUNTIME_VERSION
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.lifecycle import LifecycleState
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
from src.kernel.runtime.pipeline import PipelineDefinition


class RuntimeKernel:
    """Immutable-reference facade for the composed Wave 1 runtime graph."""

    def __init__(
        self,
        *,
        container: ContainerRuntime,
        lifecycle: LifecycleRuntime,
        event_bus: EventBusRuntime,
        context: ContextRuntime,
        orchestrator: OrchestratorRuntime,
    ) -> None:
        self._container = container
        self._lifecycle = lifecycle
        self._event_bus = event_bus
        self._context = context
        self._orchestrator = orchestrator

    @property
    def container(self) -> ContainerRuntime:
        return self._container

    @property
    def lifecycle(self) -> LifecycleRuntime:
        return self._lifecycle

    @property
    def event_bus(self) -> EventBusRuntime:
        return self._event_bus

    @property
    def context(self) -> ContextRuntime:
        return self._context

    @property
    def orchestrator(self) -> OrchestratorRuntime:
        return self._orchestrator

    @property
    def runtime_name(self) -> str:
        return "kernel"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    @property
    def version(self) -> str:
        return KERNEL_RUNTIME_VERSION

    @property
    def architecture_version(self) -> str:
        return ARCHITECTURE_VERSION

    async def initialize(self) -> None:
        await self._lifecycle.initialize()

    async def start(self) -> None:
        await self._lifecycle.start()

    async def stop(self) -> None:
        await self._lifecycle.stop()

    async def shutdown(self) -> None:
        await self._lifecycle.shutdown()

    async def execute(self, pipeline: PipelineDefinition, *, context: RuntimeContext) -> None:
        await self._orchestrator.execute(pipeline, context=context)

    def status(self) -> RuntimeStatus:
        return self._lifecycle.status

    def state(self) -> LifecycleState:
        return self._lifecycle.state()

    def health(self) -> HealthStatus:
        statuses = (
            self._container.health(),
            self._lifecycle.health(),
            self._event_bus.health(),
            self._context.health(),
            self._orchestrator.health(),
        )
        if HealthStatus.ERROR in statuses:
            return HealthStatus.ERROR
        if HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        return HealthStatus.OK

    def diagnostics(self) -> Metadata:
        return {
            "architecture_version": self.architecture_version,
            "runtime_layer": self.runtime_layer.value,
            "runtime_status": self.status().value,
            "version": self.version,
        }


__all__ = ["RuntimeKernel"]
