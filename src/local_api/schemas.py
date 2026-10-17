"""Private, strict HTTP request schemas for the local API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, SecretStr, field_validator


class RequestBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class UserPreferencesBody(RequestBody):
    schema_version: Literal[1]
    language: Literal["ru", "en"] | None
    general_model: str
    image_model: str
    onboarding_completed: bool

    @field_validator("schema_version", mode="before")
    @classmethod
    def _require_schema_version(cls, value: object) -> Literal[1]:
        if type(value) is not int or value != 1:
            raise ValueError("Unsupported preferences schema.")
        return 1


class SavePreferencesBody(RequestBody):
    preferences: UserPreferencesBody
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")


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


class ExportFolderBody(RequestBody):
    expected_updated_at: str
    confirm_export: Literal[True]

    @field_validator("confirm_export", mode="before")
    @classmethod
    def _require_literal_true(cls, value: object) -> Literal[True]:
        if value is not True:
            raise ValueError("Explicit confirmation is required.")
        return True


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


class ProjectDraftGenerationBody(RequestBody):
    business_prompt: str = Field(repr=False)
    language: Literal["ru", "en"]
    model: str
    expected_updated_at: str
    confirm_generation: Literal[True]

    @field_validator("business_prompt", mode="before")
    @classmethod
    def _valid_business_prompt(cls, value: object) -> str:
        if type(value) is not str or not value.strip():
            raise ValueError("A nonblank business prompt is required.")
        try:
            if len(value.encode("utf-8")) > 8 * 1024:
                raise ValueError("The business prompt is too large.")
        except UnicodeError:
            raise ValueError("A UTF-8 business prompt is required.") from None
        return value

    @field_validator("model", mode="before")
    @classmethod
    def _valid_model(cls, value: object) -> str:
        if type(value) is not str or not value.strip():
            raise ValueError("A nonblank model is required.")
        return value

    @field_validator("confirm_generation", mode="before")
    @classmethod
    def _require_literal_true(cls, value: object) -> Literal[True]:
        if value is not True:
            raise ValueError("Explicit confirmation is required.")
        return True


class ImageGenerationBody(RequestBody):
    prompt: str = Field(repr=False)
    model: str
    expected_updated_at: str
    confirm_generation: Literal[True]

    @field_validator("prompt", mode="before")
    @classmethod
    def _valid_prompt(cls, value: object) -> str:
        if type(value) is not str or not value.strip():
            raise ValueError("A nonblank image prompt is required.")
        try:
            if len(value.encode("utf-8")) > 8 * 1024:
                raise ValueError("The image prompt is too large.")
        except UnicodeError:
            raise ValueError("A UTF-8 image prompt is required.") from None
        return value

    @field_validator("model", mode="before")
    @classmethod
    def _valid_model(cls, value: object) -> str:
        if type(value) is not str or not value.strip():
            raise ValueError("A nonblank image model is required.")
        try:
            value.encode("utf-8")
        except UnicodeError:
            raise ValueError("A UTF-8 image model is required.") from None
        return value

    @field_validator("confirm_generation", mode="before")
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
