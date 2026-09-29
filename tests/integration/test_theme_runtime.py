"""Integration test for the Wave 4 Theme Runtime."""

from __future__ import annotations

import pytest

from src.theme import ThemeContract, ThemeDefinition, ThemeRuntime


@pytest.mark.asyncio
async def test_theme_runtime_supports_a_complete_in_memory_lifecycle() -> None:
    runtime: ThemeContract = ThemeRuntime()
    theme = ThemeDefinition(
        theme_id="aurora",
        display_name="Aurora",
        tokens=(("color.primary", "#7c3aed"),),
    )

    await runtime.initialize()
    await runtime.start()
    snapshot = runtime.set(theme)

    assert snapshot.revision == 1
    assert runtime.get() == theme
    assert runtime.snapshot() == snapshot

    await runtime.stop()
    assert runtime.get() == theme
    await runtime.shutdown()
