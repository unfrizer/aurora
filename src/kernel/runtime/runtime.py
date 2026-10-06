"""KR-010 public Wave 1 runtime facade."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from src.core.exceptions import ContractValidationError, InvalidManifestError, RuntimeStateError
from src.core.logger import get_logger
from src.core.types import HealthStatus, Metadata, RuntimeLayer, RuntimeStatus, SessionId
from src.core.version import ARCHITECTURE_VERSION, KERNEL_RUNTIME_VERSION
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.lifecycle import LifecycleState
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
from src.kernel.runtime.pipeline import PipelineDefinition
from src.kernel.runtime.session import SessionRuntime


class RuntimeKernel(RuntimeContract):
    """Compose existing owners, guarding work until its cleanup has finished."""

    def __init__(
        self,
        *,
        container: ContainerRuntime,
        lifecycle: LifecycleRuntime,
        event_bus: EventBusRuntime,
        context: ContextRuntime,
        orchestrator: OrchestratorRuntime,
        session: SessionRuntime,
    ) -> None:
        self._container = container
        self._lifecycle = lifecycle
        self._event_bus = event_bus
        self._context = context
        self._orchestrator = orchestrator
        self._session = session
        self._busy = False
        self._logger = get_logger("aurora")

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
    def session(self) -> SessionRuntime:
        return self._session

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
        self._enter()
        try:
            await self._lifecycle.initialize()
        finally:
            self._busy = False

    async def start(self) -> None:
        self._enter()
        try:
            await self._lifecycle.start()
        finally:
            self._busy = False

    async def stop(self) -> None:
        self._enter()
        try:
            await self._abort_startup()
            await self._lifecycle.stop()
        finally:
            self._busy = False

    async def shutdown(self) -> None:
        self._enter()
        try:
            await self._abort_startup()
            if self.status() not in {
                RuntimeStatus.STOPPED,
                RuntimeStatus.FAILED,
                RuntimeStatus.TERMINATED,
            }:
                # Illegal admission is not permission to mutate Session storage.
                raise RuntimeStateError("Kernel shutdown requires stopped or failed lifecycle")
            primary: BaseException | None = None
            try:
                await self._lifecycle.shutdown()
            except BaseException as error:
                primary = error
            finally:
                for session_id in self._session.list():
                    try:
                        self._session.remove(session_id)
                    except BaseException as error:
                        if primary is None:
                            primary = error
                        else:
                            self._retain(primary, error)
            if primary is not None:
                raise primary
        finally:
            self._busy = False

    async def execute(self, pipeline: PipelineDefinition, *, context: RuntimeContext) -> None:
        self._enter()
        try:
            if self.status() is not RuntimeStatus.RUNNING:
                raise RuntimeStateError("Kernel execution requires RUNNING")
            if not isinstance(cast(object, pipeline), PipelineDefinition) or not isinstance(
                cast(object, pipeline.pipeline_id), UUID
            ):
                raise InvalidManifestError("A canonical pipeline ID is required")
            pipeline_id = pipeline.pipeline_id
            primary: BaseException | None = None
            try:
                await self._orchestrator.execute(pipeline, context=context)
            except BaseException as error:
                primary = error
                raise
            finally:
                try:
                    await self._container.clear_pipeline(pipeline_id)
                except BaseException as error:
                    if primary is None:
                        raise
                    self._retain(primary, error)
        finally:
            self._busy = False

    async def remove_session(self, session_id: SessionId) -> None:
        self._enter()
        try:
            if not isinstance(cast(object, session_id), UUID):
                raise ContractValidationError("A canonical session ID is required")
            self._session.get(session_id)
            try:
                await self._container.clear_session(session_id)
            except Exception as primary:
                try:
                    self._session.remove(session_id)
                except BaseException as error:
                    self._retain(primary, error)
                raise
            else:
                self._session.remove(session_id)
        finally:
            self._busy = False

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

    def _enter(self) -> None:
        if self._busy:
            raise RuntimeStateError("Kernel mutation is already active")
        self._busy = True

    async def _abort_startup(self) -> None:
        if self.status() in {
            RuntimeStatus.INITIALIZING,
            RuntimeStatus.READY,
            RuntimeStatus.STARTING,
        }:
            await self._lifecycle.transition(RuntimeStatus.FAILED)

    def _retain(self, primary: BaseException, secondary: BaseException) -> None:
        self._logger.warning("Kernel cleanup failed (%s)", type(secondary).__name__)
        if secondary is primary:
            return
        earlier = primary.__cause__
        errors: list[BaseException] = (
            [earlier] if earlier is not None and earlier is not primary else []
        ) + [secondary]
        primary.__cause__ = BaseExceptionGroup("Kernel cleanup failures", errors)
        primary.__suppress_context__ = True


__all__ = ["RuntimeKernel"]
