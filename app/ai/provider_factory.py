"""Construct analysis providers from environment-backed settings."""

from app.ai.base import AnalysisProvider
from app.ai.gemini_provider import GeminiAnalysisProvider
from app.ai.mock_provider import MockAnalysisProvider
from app.core.config import Settings, settings


def configured_analysis_provider(config: Settings = settings) -> AnalysisProvider:
    return _provider(config.analysis_provider, config)


def configured_fallback_provider(
    config: Settings = settings,
) -> AnalysisProvider | None:
    if config.analysis_fallback_provider is None:
        return None
    return _provider(config.analysis_fallback_provider, config)


def _provider(name: str, config: Settings) -> AnalysisProvider:
    normalized = name.strip().lower()
    if normalized == "mock":
        return MockAnalysisProvider()
    if normalized == "gemini":
        api_key = (
            config.gemini_api_key.get_secret_value()
            if config.gemini_api_key is not None
            else ""
        )
        return GeminiAnalysisProvider(
            api_key=api_key,
            model_name=config.gemini_model,
            prompt_version=config.analysis_prompt_version,
        )
    raise ValueError(f"Unsupported ANALYSIS_PROVIDER: {name}")
