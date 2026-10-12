"""Single-attempt OpenAI Images API client with bounded PNG output."""

from __future__ import annotations

import base64
import binascii
import json
import math
from email.message import Message
from http.client import HTTPException, HTTPResponse
from typing import IO, Final, cast
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4

from src.generation.image_models import (
    ImageGenerationJob,
    ImageGenerationRequest,
    ImageGenerationResult,
)
from src.generation.models import GenerationFailure
from src.generation.openai_client import GenerationConfigurationError

_IMAGES_URL: Final[str] = "https://api.openai.com/v1/images/generations"
_DEFAULT_TIMEOUT_SECONDS: Final[float] = 120.0
_MAX_PROMPT_BYTES: Final[int] = 8 * 1024
_MAX_RESPONSE_BYTES: Final[int] = 24 * 1024 * 1024


class OpenAIImageClient:
    """Generate one in-memory PNG with no persistence or automatic retry."""

    def __init__(self, api_key: str, *, timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS) -> None:
        if (
            not isinstance(cast(object, api_key), str)
            or not api_key
            or any(not 33 <= ord(character) <= 126 for character in api_key)
        ):
            raise GenerationConfigurationError("A valid OpenAI API key is required for generation.")
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(cast(object, timeout_seconds), (int, float))
            or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0
        ):
            raise GenerationConfigurationError(
                "The generation timeout must be finite and positive."
            )
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def generate(self, request: ImageGenerationRequest) -> ImageGenerationJob:
        """Return a terminal result or a sanitized failure for one provider call."""
        self._validate_request(request)
        job_id = str(uuid4())
        try:
            result = self._send(request)
        except HTTPError as error:
            error.close()
            return ImageGenerationJob(
                job_id, request, "failed", failure=_http_failure(error.code)
            )
        except (OSError, URLError, HTTPException):
            return ImageGenerationJob(
                job_id,
                request,
                "failed",
                failure=GenerationFailure(
                    category="network",
                    message="The OpenAI image request could not reach the service.",
                    retryable=True,
                ),
            )
        except _InvalidImageResponseError:
            return ImageGenerationJob(
                job_id,
                request,
                "failed",
                failure=GenerationFailure(
                    category="invalid_response",
                    message="OpenAI returned no usable PNG image.",
                    retryable=False,
                ),
            )
        return ImageGenerationJob(job_id, request, "completed", result=result)

    def _send(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        payload: dict[str, object] = {
            "model": request.model,
            "prompt": request.prompt,
            "n": 1,
            "size": "1024x1024",
            "output_format": "png",
        }
        encoded_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = Request(
            _IMAGES_URL,
            data=encoded_payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with _open_response(http_request, timeout=self._timeout_seconds) as response:
            raw_response = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(raw_response) > _MAX_RESPONSE_BYTES:
            raise _InvalidImageResponseError
        return _parse_response(raw_response)

    @staticmethod
    def _validate_request(request: ImageGenerationRequest) -> None:
        if not isinstance(cast(object, request), ImageGenerationRequest):
            raise GenerationConfigurationError("A valid image generation request is required.")
        if not isinstance(cast(object, request.model), str) or not request.model.strip():
            raise GenerationConfigurationError("An image generation model is required.")
        if not isinstance(cast(object, request.prompt), str) or not request.prompt.strip():
            raise GenerationConfigurationError("An image generation prompt is required.")
        try:
            request.model.encode("utf-8")
            prompt_bytes = request.prompt.encode("utf-8")
        except UnicodeEncodeError:
            raise GenerationConfigurationError(
                "The image generation request must be valid UTF-8."
            ) from None
        if len(prompt_bytes) > _MAX_PROMPT_BYTES:
            raise GenerationConfigurationError("The image generation prompt is too large.")


class _InvalidImageResponseError(ValueError):
    """Private sentinel for malformed, ambiguous, or oversized image responses."""


class _RejectRedirects(HTTPRedirectHandler):
    """Never forward the bearer credential to a redirected location."""

    def redirect_request(
        self,
        req: Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: Message[str, str],
        newurl: str,
    ) -> None:
        return None


def _open_response(request: Request, *, timeout: float) -> HTTPResponse:
    return cast(HTTPResponse, build_opener(_RejectRedirects()).open(request, timeout=timeout))


def _parse_response(raw_response: bytes) -> ImageGenerationResult:
    try:
        parsed = cast(object, json.loads(raw_response))
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise _InvalidImageResponseError from error
    if not isinstance(parsed, dict):
        raise _InvalidImageResponseError
    response_data = cast(dict[str, object], parsed)
    if response_data.get("error") is not None or response_data.get("output_format", "png") != "png":
        raise _InvalidImageResponseError
    data = response_data.get("data")
    if not isinstance(data, list):
        raise _InvalidImageResponseError
    items = cast(list[object], data)
    if len(items) != 1 or not isinstance(items[0], dict):
        raise _InvalidImageResponseError
    encoded = cast(dict[str, object], items[0]).get("b64_json")
    if not isinstance(encoded, str) or not encoded:
        raise _InvalidImageResponseError
    try:
        image = base64.b64decode(encoded, validate=True)
        return ImageGenerationResult(data=image)
    except (binascii.Error, ValueError):
        raise _InvalidImageResponseError from None


def _http_failure(status_code: int) -> GenerationFailure:
    if status_code in {401, 403}:
        return GenerationFailure(
            "authentication", "OpenAI rejected the configured credential.", False
        )
    if status_code == 429:
        return GenerationFailure("rate_limited", "OpenAI rate-limited the image request.", True)
    if status_code >= 500:
        return GenerationFailure("remote", "OpenAI could not complete the image request.", True)
    return GenerationFailure("remote", "OpenAI rejected the image request.", False)
