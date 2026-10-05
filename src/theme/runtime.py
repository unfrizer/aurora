"""Deterministic in-memory implementation of the Wave 4 Theme Runtime."""

# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.theme.contracts import ThemeContract, ThemeDefinition, ThemeSnapshot


class ThemeRuntime(ThemeContract):
    """Own the active immutable theme for a single runtime lifetime."""

    def __init__(self) -> None:
        self._theme: ThemeDefinition | None = None
        self._revision = 0
        self._is_shutdown = False

    @property
    def runtime_name(self) -> str:
        return "theme"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L3_THEME

    async def initialize(self) -> None:
        if self._is_shutdown:
            self._theme = None
            self._revision = 0
            self._is_shutdown = False

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        self._theme = None
        self._is_shutdown = True

    def health(self) -> HealthStatus:
        return HealthStatus.OK

    def get(self) -> ThemeDefinition | None:
        self._require_active()
        return self._theme

    def snapshot(self) -> ThemeSnapshot:
        self._require_active()
        return ThemeSnapshot(revision=self._revision, theme=self._theme)

    def set(self, theme: ThemeDefinition) -> ThemeSnapshot:
        self._require_active()
        self._validate_theme(theme)
        self._theme = theme
        self._revision += 1
        return self.snapshot()

    def clear(self) -> ThemeSnapshot:
        self._require_active()
        if self._theme is not None:
            self._theme = None
            self._revision += 1
        return self.snapshot()

    def _require_active(self) -> None:
        if self._is_shutdown:
            raise RuntimeError("Theme Runtime is shut down")

    @staticmethod
    def _validate_theme(theme: ThemeDefinition) -> None:
        if not isinstance(theme, ThemeDefinition):
            raise ValidationError("Theme must be a ThemeDefinition")
        if not isinstance(theme.theme_id, str) or not theme.theme_id.strip():
            raise ValidationError("Theme ID must be non-empty")
        if not isinstance(theme.display_name, str) or not theme.display_name.strip():
            raise ValidationError("Theme display name must be non-empty")
        if not isinstance(theme.tokens, tuple):
            raise ValidationError("Theme tokens must be an immutable tuple")

        token_names: set[str] = set()
        for token in theme.tokens:
            if not isinstance(token, tuple) or len(token) != 2:
                raise ValidationError("Theme token must contain a name and value")
            name, value = token
            if not isinstance(name, str) or not name.strip():
                raise ValidationError("Theme token name must be non-empty")
            if not isinstance(value, str) or not value.strip():
                raise ValidationError("Theme token value must be non-empty")
            if name in token_names:
                raise ValidationError("Theme token names must be unique", token=name)
            token_names.add(name)


__all__ = ["ThemeRuntime"]
