"""Bounded retries and fallback for interchangeable analysis providers."""

from uuid import UUID
import logging
from time import perf_counter

from app.ai.base import AnalysisProvider
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.interaction import InteractionRequest
from app.services.analysis import analyze_interaction
from app.core.observability import log_event

logger = logging.getLogger("communitylab.analysis")


class AnalysisProviderUnavailable(RuntimeError):
    """Raised when the primary provider and its fallback cannot analyze."""


class AnalysisRateLimited(AnalysisProviderUnavailable):
    """Raised when Gemini rejects work because the project hit a rate limit."""


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
    for attempt in range(1, max_attempts + 1):
        started = perf_counter()
        try:
            result = analyze_interaction(provider, interaction_id, interaction)
            log_event(
                logger,
                "analysis_completed",
                provider=type(provider).__name__,
                attempt=attempt,
                duration_ms=round((perf_counter() - started) * 1000, 2),
            )
            return result
        except Exception as exc:  # provider boundary: normalize external failures
            last_error = exc
            log_event(
                logger,
                "analysis_retry",
                provider=type(provider).__name__,
                attempt=attempt,
                error_type=type(exc).__name__,
                error_code=getattr(exc, "code", getattr(exc, "status_code", None)),
                duration_ms=round((perf_counter() - started) * 1000, 2),
            )

    if fallback is not None:
        try:
            return analyze_interaction(fallback, interaction_id, interaction)
        except Exception as exc:
            last_error = exc
            log_event(
                logger,
                "analysis_fallback_failed",
                provider=type(fallback).__name__,
                error_type=type(exc).__name__,
                error_code=getattr(exc, "code", getattr(exc, "status_code", None)),
            )

    raise AnalysisProviderUnavailable(
        "Analysis provider failed after all configured attempts."
    ) from last_error
