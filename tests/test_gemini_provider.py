from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import SecretStr

from app.ai.gemini_provider import (
    GeminiAnalysisPayload,
    GeminiAnalysisProvider,
)
from app.ai.mock_provider import MockAnalysisProvider
from app.ai.provider_factory import (
    configured_analysis_provider,
    configured_fallback_provider,
)
from app.core.config import Settings
from app.schemas.v1.interaction import InteractionRequest


class FakeModels:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(parsed=self.payload, text=self.payload.model_dump_json())


def _interaction(text="Gracias, logré desplegar FastAPI con Docker."):
    return InteractionRequest(
        author="Ana",
        channel="logros",
        type="testimonio",
        text=text,
    )


def test_gemini_provider_returns_valid_grounded_analysis():
    payload = GeminiAnalysisPayload(
        sentiment="positive",
        topics=["FastAPI", "Docker", "FastAPI"],
        entities=["FastAPI", "Docker"],
        relevance=0.95,
        confidence=0.9,
        evidence_excerpt="logré desplegar FastAPI con Docker",
    )
    models = FakeModels(payload)
    provider = GeminiAnalysisProvider(
        api_key="test-key",
        model_name="gemini-test",
        prompt_version="analysis-test-v1",
        client=SimpleNamespace(models=models),
    )
    interaction_id = uuid4()

    result = provider.analyze(interaction_id, _interaction())

    assert result.interaction_id == interaction_id
    assert result.model == "gemini-test"
    assert result.prompt_version == "analysis-test-v1"
    assert result.topics == ["FastAPI", "Docker"]
    assert result.evidence[0].excerpt in _interaction().text
    assert models.calls[0]["config"]["response_mime_type"] == "application/json"


def test_gemini_provider_rejects_ungrounded_evidence():
    payload = GeminiAnalysisPayload(
        sentiment="neutral",
        topics=[],
        entities=[],
        relevance=0.5,
        confidence=0.5,
        evidence_excerpt="text invented by the model",
    )
    provider = GeminiAnalysisProvider(
        api_key="test-key",
        model_name="gemini-test",
        prompt_version="analysis-test-v1",
        client=SimpleNamespace(models=FakeModels(payload)),
    )

    with pytest.raises(ValueError, match="exact excerpt"):
        provider.analyze(uuid4(), _interaction())


def test_provider_factory_defaults_to_mock():
    provider = configured_analysis_provider(Settings(_env_file=None))
    assert isinstance(provider, MockAnalysisProvider)


def test_provider_factory_builds_gemini_from_settings():
    config = Settings(
        _env_file=None,
        analysis_provider="gemini",
        gemini_api_key=SecretStr("secret"),
        gemini_model="gemini-test",
    )
    provider = configured_analysis_provider(config)

    assert isinstance(provider, GeminiAnalysisProvider)
    assert provider.model_name == "gemini-test"


def test_gemini_requires_api_key():
    config = Settings(
        _env_file=None,
        analysis_provider="gemini",
        gemini_api_key="",
    )
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        configured_analysis_provider(config)


def test_optional_mock_fallback_is_explicit():
    config = Settings(_env_file=None, analysis_fallback_provider="mock")
    assert isinstance(configured_fallback_provider(config), MockAnalysisProvider)
