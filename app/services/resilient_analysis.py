"""Bounded retries and fallback for interchangeable analysis providers."""

from uuid import UUID

from app.ai.base import AnalysisProvider
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.interaction import InteractionRequest
from app.services.analysis import analyze_interaction


class AnalysisProviderUnavailable(RuntimeError):
    """Raised when the primary provider and its fallback cannot analyze."""


def analyze_with_resilience(
    *,
    provider: AnalysisProvider,
    interaction_id: UUID,
    interaction: InteractionRequest,
    max_attempts: int = 2,
    fallback: AnalysisProvider | None = None,
) -> Analysis:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            return analyze_interaction(provider, interaction_id, interaction)
        except Exception as exc:  # provider boundary: normalize external failures
            last_error = exc

    if fallback is not None:
        try:
            return analyze_interaction(fallback, interaction_id, interaction)
        except Exception as exc:
            last_error = exc

    raise AnalysisProviderUnavailable(
        "Analysis provider failed after all configured attempts."
    ) from last_error
