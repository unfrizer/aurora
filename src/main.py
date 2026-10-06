"""AURORA Wave 1 asynchronous process entrypoint."""

from __future__ import annotations

import asyncio

from src.core.logger import get_logger
from src.core.types import RuntimeStatus
from src.kernel.runtime.bootstrap import BootstrapRuntime


async def main() -> None:
    """Run bounded Kernel smoke, independently attempting both cleanup phases."""
    runtime = await BootstrapRuntime().build()
    primary: BaseException | None = None
    try:
        await runtime.initialize()
        await runtime.start()
    except BaseException as error:
        primary = error
    finally:
        if runtime.status() in {
            RuntimeStatus.INITIALIZING,
            RuntimeStatus.READY,
            RuntimeStatus.STARTING,
            RuntimeStatus.RUNNING,
            RuntimeStatus.FAILED,
        }:
            try:
                await runtime.stop()
            except BaseException as error:
                if primary is None:
                    primary = error
                else:
                    _retain(primary, error)
        if runtime.status() is not RuntimeStatus.CREATED:
            try:
                await runtime.shutdown()
            except BaseException as error:
                if primary is None:
                    primary = error
                else:
                    _retain(primary, error)
    if primary is not None:
        raise primary


def _retain(primary: BaseException, secondary: BaseException) -> None:
    """Keep secondary teardown errors without importing Kernel implementation."""
    get_logger("aurora").warning("Process cleanup failed (%s)", type(secondary).__name__)
    if secondary is primary:
        return
    earlier = primary.__cause__
    errors: list[BaseException] = (
        [earlier] if earlier is not None and earlier is not primary else []
    ) + [secondary]
    primary.__cause__ = BaseExceptionGroup("Process cleanup failures", errors)
    primary.__suppress_context__ = True


if __name__ == "__main__":
    asyncio.run(main())
