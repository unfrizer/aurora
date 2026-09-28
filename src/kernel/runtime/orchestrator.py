"""KR-009 module and pipeline orchestration."""

from __future__ import annotations

from src.core.exceptions import InvalidManifestError
from src.core.types import HealthStatus, ModuleId, RuntimeLayer
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.module import RuntimeModuleManifest
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.executor import ExecutorRuntime
from src.kernel.runtime.manifest import ManifestRuntime
from src.kernel.runtime.pipeline import PipelineDefinition


class OrchestratorRuntime(RuntimeContract):
    """Own module-manifest registration and pipeline coordination."""

    def __init__(self, executor: ExecutorRuntime) -> None:
        self._executor = executor
        self._validator = ManifestRuntime()
        self._modules: dict[ModuleId, RuntimeModuleManifest] = {}

    @property
    def runtime_name(self) -> str:
        return "orchestrator"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    def register_module(self, manifest: RuntimeModuleManifest) -> None:
        if manifest.module_id in self._modules:
            raise InvalidManifestError(
                "Runtime module is already registered", module_id=manifest.module_id
            )
        self._modules[manifest.module_id] = manifest

    def unregister_module(self, module_id: ModuleId) -> None:
        if module_id not in self._modules:
            raise InvalidManifestError("Runtime module is not registered", module_id=module_id)
        del self._modules[module_id]

    def modules(self) -> tuple[RuntimeModuleManifest, ...]:
        return tuple(self._modules.values())

    def contains(self, module_id: ModuleId) -> bool:
        return module_id in self._modules

    async def execute(self, pipeline: PipelineDefinition, *, context: RuntimeContext) -> None:
        await self._executor.execute(self._validator.validate(pipeline), context=context)

    async def initialize(self) -> None:
        return None

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        self._modules.clear()

    def health(self) -> HealthStatus:
        return HealthStatus.OK


__all__ = ["OrchestratorRuntime"]
