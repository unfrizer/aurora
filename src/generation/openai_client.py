"""A narrow, synchronous client for OpenAI's Responses API."""

from __future__ import annotations

import json
from typing import Final, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from src.generation.models import (
    GenerationErrorCategory,
    GenerationFailure,
    GenerationJob,
    GenerationRequest,
    GenerationResult,
)

_RESPONSES_URL: Final[str] = "https://api.openai.com/v1/responses"
_DEFAULT_TIMEOUT_SECONDS: Final[float] = 60.0


class GenerationConfigurationError(ValueError):
    """Raised when a local generation request cannot safely be sent."""


class OpenAIResponsesClient:
    """Submit one stateless text-generation request to the OpenAI Responses API."""

    def __init__(self, api_key: str, *, timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS) -> None:
        if not api_key.strip():
            raise GenerationConfigurationError("An OpenAI API key is required for generation.")
        if timeout_seconds <= 0:
            raise GenerationConfigurationError("The generation timeout must be greater than zero.")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def generate(self, request: GenerationRequest) -> GenerationJob:
        """Execute one request and return its terminal success or sanitized failure."""
        self._validate_request(request)
        job_id = str(uuid4())

        try:
            result = self._send(request)
        except HTTPError as error:
            return GenerationJob(
                job_id=job_id,
                request=request,
                status="failed",
                failure=self._http_failure(error.code),
            )
        except (OSError, TimeoutError, URLError):
            return GenerationJob(
                job_id=job_id,
                request=request,
                status="failed",
                failure=GenerationFailure(
                    category="network",
                    message="The OpenAI request could not reach the service.",
                    retryable=True,
                ),
            )
        except _InvalidResponseError:
            return GenerationJob(
                job_id=job_id,
                request=request,
                status="failed",
                failure=GenerationFailure(
                    category="invalid_response",
                    message="OpenAI returned a response without usable output text.",
                    retryable=False,
                ),
            )

        return GenerationJob(job_id=job_id, request=request, status="completed", result=result)

    def _send(self, request: GenerationRequest) -> GenerationResult:
        payload: dict[str, object] = {
            "model": request.model,
            "input": request.prompt,
            "store": False,
        }
        if request.instructions is not None:
            payload["instructions"] = request.instructions

        encoded_payload = json.dumps(payload).encode("utf-8")
        http_request = Request(
            _RESPONSES_URL,
            data=encoded_payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(http_request, timeout=self._timeout_seconds) as response:
            raw_response = response.read()
        return self._parse_response(raw_response)

    @staticmethod
    def _validate_request(request: GenerationRequest) -> None:
        if not request.model.strip():
            raise GenerationConfigurationError("A generation model is required.")
        if not request.prompt.strip():
            raise GenerationConfigurationError("A generation prompt is required.")

    @staticmethod
    def _parse_response(raw_response: bytes) -> GenerationResult:
        try:
            parsed_response = cast(object, json.loads(raw_response))
        except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise _InvalidResponseError from error

        if not isinstance(parsed_response, dict):
            raise _InvalidResponseError
        response_data = cast(dict[str, object], parsed_response)
        response_id = response_data.get("id")
        model = response_data.get("model")
        output_text = _extract_output_text(response_data.get("output"))
        if not isinstance(response_id, str) or not isinstance(model, str) or output_text is None:
            raise _InvalidResponseError
        return GenerationResult(response_id=response_id, model=model, output_text=output_text)

    @staticmethod
    def _http_failure(status_code: int) -> GenerationFailure:
        category, message, retryable = _failure_details_for(status_code)
        return GenerationFailure(category=category, message=message, retryable=retryable)


class _InvalidResponseError(ValueError):
    """Private sentinel for malformed or textless Responses API payloads."""


def _extract_output_text(output: object) -> str | None:
    if not isinstance(output, list):
        return None

    text_parts: list[str] = []
    output_items = cast(list[object], output)
    for output_item in output_items:
        if not isinstance(output_item, dict):
            continue
        output_data = cast(dict[str, object], output_item)
        content = output_data.get("content")
        if not isinstance(content, list):
            continue
        content_items = cast(list[object], content)
        for content_item in content_items:
            if not isinstance(content_item, dict):
                continue
            content_data = cast(dict[str, object], content_item)
            if content_data.get("type") != "output_text":
                continue
            text = content_data.get("text")
            if isinstance(text, str):
                text_parts.append(text)

    return "\n".join(text_parts) if text_parts else None


def _failure_details_for(status_code: int) -> tuple[GenerationErrorCategory, str, bool]:
    if status_code in {401, 403}:
        return "authentication", "OpenAI rejected the configured credential.", False
    if status_code == 429:
        return "rate_limited", "OpenAI rate-limited the generation request.", True
    if status_code >= 500:
        return "remote", "OpenAI could not complete the generation request.", True
    return "remote", "OpenAI rejected the generation request.", False
