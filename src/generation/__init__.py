"""OpenAI text-generation application adapter for AURORA."""

from src.generation.models import (
    GenerationErrorCategory,
    GenerationFailure,
    GenerationJob,
    GenerationRequest,
    GenerationResult,
)
from src.generation.openai_client import GenerationConfigurationError, OpenAIResponsesClient

__all__ = [
    "GenerationConfigurationError",
    "GenerationErrorCategory",
    "GenerationFailure",
    "GenerationJob",
    "GenerationRequest",
    "GenerationResult",
    "OpenAIResponsesClient",
]
