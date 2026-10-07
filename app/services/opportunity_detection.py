from uuid import UUID
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.content_opportunity import ContentOpportunity, ContentOpportunityStatus
from app.services.pii_detection import contains_pii

MIN_RELEVANCE = 0.80
REVIEW_CONFIDENCE_THRESHOLD = 0.70

def detect_content_opportunity(analysis_id: UUID, analysis: Analysis) -> ContentOpportunity | None:
    source_ids = [e.source_interaction_id for e in analysis.evidence]
    if not source_ids:
        return None

    if any(contains_pii(e.excerpt) for e in analysis.evidence):
        return _build(analysis_id, analysis, source_ids, ContentOpportunityStatus.BLOCKED,
                      "Blocked because PII was detected.")

    if analysis.confidence < REVIEW_CONFIDENCE_THRESHOLD:
        return _build(analysis_id, analysis, source_ids, ContentOpportunityStatus.REVIEW_REQUIRED,
                      "Human review required because confidence is below 0.70.")

    if analysis.relevance < MIN_RELEVANCE:
        return None

    return _build(analysis_id, analysis, source_ids, ContentOpportunityStatus.PENDING,
                  "Qualified by backend content rules.")

def _build(analysis_id, analysis, source_ids, status, prefix):
    return ContentOpportunity(
        analysis_id=analysis_id,
        kind=_kind(analysis),
        priority=round((analysis.relevance + analysis.confidence) / 2, 4),
        reason=f"{prefix} relevance={analysis.relevance:.2f}; confidence={analysis.confidence:.2f}",
        source_ids=source_ids,
        status=status,
    )

def _kind(analysis: Analysis) -> str:
    if analysis.sentiment == "negative":
        return "support_content"
    if analysis.sentiment == "positive":
        return "success_content"
    return "educational_content"
