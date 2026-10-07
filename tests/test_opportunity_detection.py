from uuid import uuid4

from app.schemas.v1.analysis import Analysis, Evidence
from app.schemas.v1.content_opportunity import ContentOpportunityStatus
from app.services.opportunity_detection import detect_content_opportunity


def make_analysis(
    *,
    sentiment: str = "neutral",
    relevance: float = 0.90,
    confidence: float = 0.90,
    with_evidence: bool = True,
) -> Analysis:
    interaction_id = uuid4()

    evidence = (
        [
            Evidence(
                source_interaction_id=interaction_id,
                excerpt="FastAPI con PostgreSQL usando Docker.",
            )
        ]
        if with_evidence
        else []
    )

    return Analysis(
        interaction_id=interaction_id,
        sentiment=sentiment,
        topics=["fastapi", "postgresql", "docker"],
        entities=["FastAPI", "PostgreSQL", "Docker"],
        relevance=relevance,
        confidence=confidence,
        evidence=evidence,
        model="mock-analysis-v1",
        prompt_version="v1",
    )


def test_creates_content_opportunity_from_qualified_analysis():
    analysis_id = uuid4()

    opportunity = detect_content_opportunity(
        analysis_id,
        make_analysis(),
    )

    assert opportunity is not None
    assert opportunity.analysis_id == analysis_id
    assert opportunity.kind == "educational_content"
    assert opportunity.priority == 0.9


def test_backend_assigns_pending_status():
    opportunity = detect_content_opportunity(
        uuid4(),
        make_analysis(),
    )

    assert opportunity is not None
    assert opportunity.status == ContentOpportunityStatus.PENDING


def test_status_is_not_taken_from_prompt_or_analysis():
    analysis = make_analysis()

    opportunity = detect_content_opportunity(
        uuid4(),
        analysis,
    )

    assert opportunity is not None
    assert not hasattr(analysis, "status")
    assert opportunity.status == ContentOpportunityStatus.PENDING


def test_low_relevance_does_not_create_opportunity():
    opportunity = detect_content_opportunity(
        uuid4(),
        make_analysis(relevance=0.79),
    )

    assert opportunity is None


def test_low_confidence_does_not_create_opportunity():
    opportunity = detect_content_opportunity(
        uuid4(),
        make_analysis(confidence=0.79),
    )

    assert opportunity is None


def test_evidence_is_required():
    opportunity = detect_content_opportunity(
        uuid4(),
        make_analysis(with_evidence=False),
    )

    assert opportunity is None


def test_negative_sentiment_creates_support_content():
    opportunity = detect_content_opportunity(
        uuid4(),
        make_analysis(sentiment="negative"),
    )

    assert opportunity is not None
    assert opportunity.kind == "support_content"


def test_positive_sentiment_creates_success_content():
    opportunity = detect_content_opportunity(
        uuid4(),
        make_analysis(sentiment="positive"),
    )

    assert opportunity is not None
    assert opportunity.kind == "success_content"


def test_priority_is_calculated_by_backend():
    opportunity = detect_content_opportunity(
        uuid4(),
        make_analysis(
            relevance=1.0,
            confidence=0.8,
        ),
    )

    assert opportunity is not None
    assert opportunity.priority == 0.9


def test_source_ids_come_from_analysis_evidence():
    analysis = make_analysis()

    opportunity = detect_content_opportunity(
        uuid4(),
        analysis,
    )

    assert opportunity is not None
    assert opportunity.source_ids == [
        analysis.evidence[0].source_interaction_id
    ]
