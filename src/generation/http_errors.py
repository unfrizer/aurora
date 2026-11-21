"""Bounded, sanitized classification of provider HTTP failures."""

from __future__ import annotations

import json
from http.client import HTTPException
from typing import cast
from urllib.error import HTTPError

from src.generation.models import GenerationFailure

_MAX_ERROR_BYTES = 64 * 1024
_QUOTA_CODES = frozenset(
    {
        "insufficient_quota",
        "credit_balance_exhausted",
        "organization_spend_limit_exceeded",
        "project_spend_limit_exceeded",
        "organization_usage_limit_exceeded",
        "usage_limit_exceeded",
        "billing_hard_limit_reached",
    }
)


def quota_failure(error: HTTPError) -> GenerationFailure | None:
    """Recognize explicit billing codes without retaining or exposing provider text."""
    if error.code != 429:
        return None
    try:
        raw = error.read(_MAX_ERROR_BYTES + 1)
        if len(raw) > _MAX_ERROR_BYTES:
            return None
        value = cast(object, json.loads(raw))
    except (OSError, HTTPException, ValueError, TypeError, RecursionError):
        return None
    if not isinstance(value, dict):
        return None
    detail = cast(dict[str, object], value).get("error")
    if not isinstance(detail, dict):
        return None
    fields = cast(dict[str, object], detail)
    code = fields.get("code")
    if (isinstance(code, str) and code in _QUOTA_CODES) or (
        code is None and fields.get("type") == "insufficient_quota"
    ):
        return GenerationFailure(
            category="rate_limited",
            message=(
                "OpenAI API credits or billing and usage limits must be updated before retrying."
            ),
            retryable=False,
        )
    return None
