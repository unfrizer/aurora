"""KR-010 canonical Wave 1 runtime assembly."""

from __future__ import annotations

from src.core.config import get_settings, validate_configuration
from src.core.exceptions import ConfigurationError, RuntimeInitializationError
from src.core.logger import get_logger
from src.core.logging_config import LoggingConfig
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
from src.kernel.runtime.runtime import RuntimeKernel
from src.kernel.runtime.session import SessionRuntime


class BootstrapRuntime:
    """Construct the complete runtime graph without starting its lifecycle."""

    async def build(self) -> RuntimeKernel:
        """Return an independent CREATED graph; never initialize its resources."""
        try:
            self.validate_environment()
            settings = get_settings()
            get_logger("aurora", LoggingConfig(level=settings.log_level))
            context = self.build_context()
            session = SessionRuntime(context)
            container = self.build_container()
            event_bus = self.build_event_bus()
            orchestrator = self.build_orchestrator(event_bus)
            lifecycle = self.build_lifecycle(container, event_bus, context, orchestrator)
            return RuntimeKernel(
                container=container,
                lifecycle=lifecycle,
                event_bus=event_bus,
                context=context,
                orchestrator=orchestrator,
                session=session,
            )
        except ConfigurationError:
            raise
        except Exception as error:
            raise RuntimeInitializationError("Kernel construction failed") from error

    def validate_environment(self) -> None:
        validate_configuration()

    def build_context(self) -> ContextRuntime:
        return ContextRuntime()

    def build_container(self) -> ContainerRuntime:
        return ContainerRuntime()

    def build_event_bus(self) -> EventBusRuntime:
        return EventBusRuntime()

    def build_orchestrator(self, event_bus: EventBusRuntime) -> OrchestratorRuntime:
        return OrchestratorRuntime(event_bus)

    def build_lifecycle(
        self,
        container: ContainerRuntime,
        event_bus: EventBusRuntime,
        context: ContextRuntime,
        orchestrator: OrchestratorRuntime,
    ) -> LifecycleRuntime:
        lifecycle = LifecycleRuntime()
        lifecycle.register(context)
        lifecycle.register(container)
        lifecycle.register(event_bus)
        lifecycle.register(orchestrator)
        return lifecycle


__all__ = ["BootstrapRuntime"]
