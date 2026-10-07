from uuid import uuid4

import pytest

from app.ai.mock_provider import MockAnalysisProvider
from app.schemas.v1.interaction import InteractionRequest
from app.services.resilient_analysis import (
    AnalysisProviderUnavailable,
    analyze_with_resilience,
)


class FailingProvider:
    def __init__(self, failures: int):
        self.failures = failures
        self.calls = 0

    def analyze(self, interaction_id, interaction):
        self.calls += 1
        if self.calls <= self.failures:
            raise TimeoutError("temporary provider failure")
        return MockAnalysisProvider().analyze(interaction_id, interaction)


def _interaction():
    return InteractionRequest(
        author="Ana",
        channel="general",
        type="comment",
        text="FastAPI con PostgreSQL y Docker.",
    )


def test_primary_provider_is_retried_before_succeeding():
    provider = FailingProvider(failures=1)

    result = analyze_with_resilience(
        provider=provider,
        interaction_id=uuid4(),
        interaction=_interaction(),
        max_attempts=2,
    )

    assert provider.calls == 2
    assert result.model == "mock-analysis-v1"


def test_fallback_runs_only_after_primary_attempts_are_exhausted():
    provider = FailingProvider(failures=3)

    result = analyze_with_resilience(
        provider=provider,
        interaction_id=uuid4(),
        interaction=_interaction(),
        max_attempts=2,
        fallback=MockAnalysisProvider(),
    )

    assert provider.calls == 2
    assert result.model == "mock-analysis-v1"


def test_explicit_error_is_raised_when_every_provider_fails():
    with pytest.raises(AnalysisProviderUnavailable):
        analyze_with_resilience(
            provider=FailingProvider(failures=3),
            interaction_id=uuid4(),
            interaction=_interaction(),
            max_attempts=2,
            fallback=FailingProvider(failures=1),
        )


def test_zero_attempts_is_rejected():
    with pytest.raises(ValueError, match="max_attempts"):
        analyze_with_resilience(
            provider=MockAnalysisProvider(),
            interaction_id=uuid4(),
            interaction=_interaction(),
            max_attempts=0,
        )
