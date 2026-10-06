"""KR-009 module bindings and validated pipeline coordination."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from src.core.exceptions import (
    InvalidManifestError,
    RuntimeDependencyError,
    RuntimeLayerError,
    RuntimeStateError,
)
from src.core.types import HealthStatus, ModuleId, RuntimeLayer
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.module import RuntimeModuleManifest
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.executor import ExecutorRuntime
from src.kernel.runtime.manifest import ManifestRuntime
from src.kernel.runtime.pipeline import PipelineDefinition


class OrchestratorRuntime(RuntimeContract):
    """Own instance-local registrations and operation bindings, not business results."""

    def __init__(self, event_bus: EventBusRuntime) -> None:
        self._executor = ExecutorRuntime(event_bus)
        self._validator = ManifestRuntime()
        self._modules: dict[ModuleId, RuntimeModuleManifest] = {}
        self._operations: dict[ModuleId, Callable[[RuntimeContext], Awaitable[None]]] = {}
        self._busy = False

    @property
    def runtime_name(self) -> str:
        return "orchestrator"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    def register_module(
        self,
        manifest: RuntimeModuleManifest,
        *,
        operation: Callable[[RuntimeContext], Awaitable[None]] | None = None,
    ) -> None:
        self._require_idle()
        self._validate_manifest(manifest)
        if manifest.module_id in self._modules:
            raise InvalidManifestError("Runtime module is already registered")
        if operation is not None and not callable(operation):
            raise InvalidManifestError("Runtime module operation must be callable")
        self._modules[manifest.module_id] = manifest
        if operation is not None:
            self._operations[manifest.module_id] = operation

    def unregister_module(self, module_id: ModuleId) -> None:
        self._require_idle()
        if module_id not in self._modules:
            raise InvalidManifestError("Runtime module is not registered")
        del self._modules[module_id]
        self._operations.pop(module_id, None)

    def modules(self) -> tuple[RuntimeModuleManifest, ...]:
        return tuple(self._modules.values())

    def contains(self, module_id: ModuleId) -> bool:
        return module_id in self._modules

    async def execute(self, pipeline: PipelineDefinition, *, context: RuntimeContext) -> None:
        self._require_idle()
        self._busy = True
        try:
            self._validator.validate(pipeline)
            for stage in pipeline.stages:
                if stage.module_id not in self._modules or stage.module_id not in self._operations:
                    raise InvalidManifestError(
                        "Every pipeline stage requires a registered operation"
                    )
            self._validate_module_graph(pipeline)
            await self._executor.execute(
                pipeline, context=context, operations=dict(self._operations)
            )
        finally:
            self._busy = False

    async def initialize(self) -> None:
        return None

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        self._require_idle()
        self._operations.clear()
        self._modules.clear()

    def health(self) -> HealthStatus:
        return HealthStatus.OK

    def _require_idle(self) -> None:
        if self._busy:
            raise RuntimeStateError("Pipeline orchestrator is busy")

    @staticmethod
    def _identifier(value: object) -> None:
        if not isinstance(value, str) or not value:
            raise InvalidManifestError("Module fields must be non-empty strings")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise InvalidManifestError("Module fields must contain valid Unicode") from None

    def _validate_manifest(self, manifest: RuntimeModuleManifest) -> None:
        if not isinstance(cast(object, manifest), RuntimeModuleManifest):
            raise InvalidManifestError("Runtime module manifest contract is required")
        self._identifier(manifest.module_id)
        self._identifier(manifest.version)
        if not isinstance(cast(object, manifest.runtime_layer), RuntimeLayer):
            raise InvalidManifestError("Runtime module layer is invalid")
        for items in (manifest.depends_on, manifest.provides):
            if not isinstance(cast(object, items), tuple):
                raise InvalidManifestError("Module dependencies and provides must be tuples")
            for item in items:
                self._identifier(item)

    def _validate_module_graph(self, pipeline: PipelineDefinition) -> None:
        visited: set[ModuleId] = set()
        visiting: set[ModuleId] = set()
        layers = tuple(RuntimeLayer)
        for stage in pipeline.stages:
            pending = [(stage.module_id, False)]
            while pending:
                module_id, expanded = pending.pop()
                if expanded:
                    visiting.remove(module_id)
                    visited.add(module_id)
                    continue
                if module_id in visited:
                    continue
                if module_id in visiting:
                    raise RuntimeDependencyError("Runtime module dependency cycle detected")
                manifest = self._modules[module_id]
                visiting.add(module_id)
                pending.append((module_id, True))
                for dependency in reversed(manifest.depends_on):
                    if dependency not in self._modules:
                        raise RuntimeDependencyError("Runtime module dependency is not registered")
                    if layers.index(self._modules[dependency].runtime_layer) > layers.index(
                        manifest.runtime_layer
                    ):
                        raise RuntimeLayerError(
                            "Runtime module dependency points to a higher layer"
                        )
                    pending.append((dependency, False))


__all__ = ["OrchestratorRuntime"]
