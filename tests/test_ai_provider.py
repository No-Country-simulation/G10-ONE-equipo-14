import json
from uuid import uuid4

from app.ai.mock_provider import MockAnalysisProvider
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.interaction import InteractionRequest
from app.services.analysis import analyze_interaction


def make_interaction(
    text: str = (
        "Gracias. Conseguí conectar FastAPI con PostgreSQL "
        "usando Docker."
    ),
) -> InteractionRequest:
    return InteractionRequest(
        external_id="week3-001",
        author="Ana",
        channel="general",
        type="pregunta",
        text=text,
    )


def test_provider_is_decoupled_and_returns_analysis():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(),
    )

    assert isinstance(result, Analysis)
    assert result.schema_version == "v1"
    assert result.model == "mock-analysis-v1"


def test_produces_sentiment():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(),
    )
    assert result.sentiment == "positive"


def test_produces_topics():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(),
    )
    assert "fastapi" in result.topics
    assert "postgresql" in result.topics
    assert "docker" in result.topics


def test_produces_entities():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(),
    )
    assert "FastAPI" in result.entities
    assert "PostgreSQL" in result.entities
    assert "Docker" in result.entities


def test_produces_relevance():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(),
    )
    assert 0 <= result.relevance <= 1
    assert result.relevance == 1.0


def test_produces_confidence():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(),
    )
    assert 0 <= result.confidence <= 1
    assert result.confidence == 1.0


def test_produces_evidence():
    interaction_id = uuid4()
    result = analyze_interaction(
        MockAnalysisProvider(),
        interaction_id,
        make_interaction(),
    )

    assert len(result.evidence) == 1
    evidence = result.evidence[0]
    assert evidence.source_interaction_id == interaction_id
    assert "FastAPI" in evidence.excerpt
    assert "PostgreSQL" in evidence.excerpt
    assert "Docker" in evidence.excerpt


def test_analysis_is_structured_json():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(),
    )
    payload = json.loads(result.model_dump_json())

    assert payload["schema_version"] == "v1"
    assert isinstance(payload["sentiment"], str)
    assert isinstance(payload["topics"], list)
    assert isinstance(payload["entities"], list)
    assert isinstance(payload["relevance"], float)
    assert isinstance(payload["confidence"], float)
    assert isinstance(payload["evidence"], list)


def test_model_and_prompt_are_registered():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(),
    )

    assert result.model == "mock-analysis-v1"
    assert result.prompt_version == "v1"


def test_negative_sentiment():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(
            "Tengo problemas con Docker y PostgreSQL. "
            "La conexión falla con un error."
        ),
    )
    assert result.sentiment == "negative"


def test_neutral_sentiment():
    result = analyze_interaction(
        MockAnalysisProvider(),
        uuid4(),
        make_interaction(
            "¿Cómo conecto FastAPI con PostgreSQL?"
        ),
    )
    assert result.sentiment == "neutral"


def test_mock_provider_is_deterministic():
    provider = MockAnalysisProvider()
    interaction_id = uuid4()
    interaction = make_interaction()

    first = provider.analyze(interaction_id, interaction)
    second = provider.analyze(interaction_id, interaction)

    assert first.model_dump() == second.model_dump()
