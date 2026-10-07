from uuid import uuid4
from app.schemas.v1.analysis import Analysis, Evidence
from app.schemas.v1.content_opportunity import ContentOpportunityStatus
from app.services.opportunity_detection import detect_content_opportunity

def make_analysis(confidence=0.90, relevance=0.90, evidence_text="FastAPI con PostgreSQL.", with_evidence=True):
    interaction_id = uuid4()
    evidence = [Evidence(source_interaction_id=interaction_id, excerpt=evidence_text)] if with_evidence else []
    return Analysis(
        interaction_id=interaction_id,
        sentiment="neutral",
        topics=["fastapi", "postgresql"],
        entities=["FastAPI", "PostgreSQL"],
        relevance=relevance,
        confidence=confidence,
        evidence=evidence,
        model="mock-analysis-v1",
        prompt_version="v1",
    )

def test_qualified_analysis_is_pending():
    result = detect_content_opportunity(uuid4(), make_analysis())
    assert result is not None
    assert result.status == ContentOpportunityStatus.PENDING

def test_confidence_below_070_requires_review():
    result = detect_content_opportunity(uuid4(), make_analysis(confidence=0.69))
    assert result is not None
    assert result.status == ContentOpportunityStatus.REVIEW_REQUIRED

def test_confidence_equal_070_is_not_review():
    result = detect_content_opportunity(uuid4(), make_analysis(confidence=0.70))
    assert result is not None
    assert result.status == ContentOpportunityStatus.PENDING

def test_email_pii_blocks():
    result = detect_content_opportunity(uuid4(), make_analysis(evidence_text="Contacto ana@example.com"))
    assert result is not None
    assert result.status == ContentOpportunityStatus.BLOCKED

def test_phone_pii_blocks():
    result = detect_content_opportunity(uuid4(), make_analysis(evidence_text="Teléfono +52 668 123 4567"))
    assert result is not None
    assert result.status == ContentOpportunityStatus.BLOCKED

def test_pii_has_priority_over_low_confidence():
    result = detect_content_opportunity(uuid4(), make_analysis(confidence=0.40, evidence_text="ana@example.com"))
    assert result is not None
    assert result.status == ContentOpportunityStatus.BLOCKED

def test_without_evidence_does_not_generate():
    assert detect_content_opportunity(uuid4(), make_analysis(with_evidence=False)) is None

def test_low_relevance_does_not_generate():
    assert detect_content_opportunity(uuid4(), make_analysis(relevance=0.79)) is None

def test_status_is_not_owned_by_analysis_or_prompt():
    analysis = make_analysis()
    result = detect_content_opportunity(uuid4(), analysis)
    assert result is not None
    assert not hasattr(analysis, "status")
    assert result.status == ContentOpportunityStatus.PENDING

def test_priority_is_backend_calculated():
    result = detect_content_opportunity(uuid4(), make_analysis(confidence=0.80, relevance=1.0))
    assert result is not None
    assert result.priority == 0.90

def test_source_ids_come_from_evidence():
    analysis = make_analysis()
    result = detect_content_opportunity(uuid4(), analysis)
    assert result is not None
    assert result.source_ids == [analysis.evidence[0].source_interaction_id]
