"""AURORA Wave 1 asynchronous process entrypoint."""

from __future__ import annotations

import asyncio

from src.kernel.runtime.bootstrap import BootstrapRuntime


async def main() -> None:
    """Build, initialize, start, stop and release the Wave 1 runtime."""
    runtime = await BootstrapRuntime().build()
    try:
        await runtime.initialize()
        await runtime.start()
    finally:
        if runtime.status().value in {"running", "starting"}:
            await runtime.stop()
        if runtime.status().value == "stopped":
            await runtime.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
