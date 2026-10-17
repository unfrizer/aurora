"""Immutable, credential-free user preference snapshots."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Literal


class PreferencesError(Exception):
    """A sanitized invalid or unavailable preferences boundary."""


def _model_id(value: object) -> bool:
    if type(value) is not str:
        return False
    model = value
    if not model.strip() or any(unicodedata.category(character) == "Cc" for character in model):
        return False
    try:
        model.encode("utf-8")
    except UnicodeError:
        return False
    return True


@dataclass(frozen=True, slots=True)
class UserPreferences:
    """The complete supported version-one settings document."""

    schema_version: Literal[1] = 1
    language: Literal["ru", "en"] | None = None
    general_model: str = "gpt-5.6-terra"
    image_model: str = "gpt-image-2"
    onboarding_completed: bool = False

    def __post_init__(self) -> None:
        if (
            type(self.schema_version) is not int
            or self.schema_version != 1
            or (
                self.language is not None
                and (type(self.language) is not str or self.language not in ("ru", "en"))
            )
            or not _model_id(self.general_model)
            or not _model_id(self.image_model)
            or type(self.onboarding_completed) is not bool
        ):
            raise PreferencesError("Invalid user preferences.")


__all__ = ["PreferencesError", "UserPreferences"]
