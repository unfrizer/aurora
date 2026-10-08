"""Private, strict HTTP request schemas for the local API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, JsonValue, SecretStr


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


class CredentialBody(RequestBody):
    secret: SecretStr = Field(repr=False)


class TextGenerationBody(RequestBody):
    model: str
    prompt: str = Field(repr=False)
    instructions: str | None = Field(default=None, repr=False)
