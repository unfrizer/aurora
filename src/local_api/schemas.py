"""Private, strict HTTP request schemas for the local API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, SecretStr, field_validator


class RequestBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class CreateProjectBody(RequestBody):
    name: str


class SaveProjectBody(RequestBody):
    name: str
    state: dict[str, JsonValue]
    expected_updated_at: str


class SaveEditorBody(RequestBody):
    editor: dict[str, JsonValue]
    expected_updated_at: str


class ExportZipBody(RequestBody):
    expected_updated_at: str


class DeployNetlifyBody(RequestBody):
    expected_updated_at: str
    confirm_deploy: Literal[True]
    site_id: str | None = None

    @field_validator("confirm_deploy", mode="before")
    @classmethod
    def _require_literal_true(cls, value: object) -> Literal[True]:
        if value is not True:
            raise ValueError("Explicit confirmation is required.")
        return True


class CredentialBody(RequestBody):
    secret: SecretStr = Field(repr=False)


class TextGenerationBody(RequestBody):
    model: str
    prompt: str = Field(repr=False)
    instructions: str | None = Field(default=None, repr=False)
