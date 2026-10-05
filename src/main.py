"""AURORA Wave 1 asynchronous process entrypoint."""

from __future__ import annotations

import asyncio

from src.core.types import RuntimeStatus
from src.kernel.runtime.bootstrap import BootstrapRuntime


async def main() -> None:
    """Build, initialize, start, stop and release the Wave 1 runtime."""
    runtime = await BootstrapRuntime().build()
    try:
        await runtime.initialize()
        await runtime.start()
    finally:
        if runtime.status() in {RuntimeStatus.RUNNING, RuntimeStatus.STARTING}:
            await runtime.stop()
        if runtime.status() is RuntimeStatus.STOPPED:
            await runtime.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
