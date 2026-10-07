from uuid import UUID

from app.schemas.v1.analysis import Analysis
from app.schemas.v1.content_opportunity import (
    ContentOpportunity,
    ContentOpportunityStatus,
)


MIN_RELEVANCE = 0.80
MIN_CONFIDENCE = 0.80


def detect_content_opportunity(
    analysis_id: UUID,
    analysis: Analysis,
) -> ContentOpportunity | None:
    """Create a content opportunity using backend-owned deterministic rules.

    The AI provider supplies analysis signals only. It does not choose workflow
    states. Status is assigned here by backend business logic.
    """
    if analysis.relevance < MIN_RELEVANCE:
        return None

    if analysis.confidence < MIN_CONFIDENCE:
        return None

    source_ids = [
        evidence.source_interaction_id
        for evidence in analysis.evidence
    ]

    if not source_ids:
        return None

    priority = _calculate_priority(
        relevance=analysis.relevance,
        confidence=analysis.confidence,
    )

    return ContentOpportunity(
        analysis_id=analysis_id,
        kind=_determine_kind(analysis),
        priority=priority,
        reason=_build_reason(analysis),
        source_ids=source_ids,
        status=ContentOpportunityStatus.PENDING,
    )


def _calculate_priority(
    relevance: float,
    confidence: float,
) -> float:
    return round((relevance + confidence) / 2, 4)


def _determine_kind(analysis: Analysis) -> str:
    if analysis.sentiment == "negative":
        return "support_content"

    if analysis.sentiment == "positive":
        return "success_content"

    return "educational_content"


def _build_reason(analysis: Analysis) -> str:
    topics = ", ".join(analysis.topics) if analysis.topics else "general"

    return (
        f"Relevant analysis for topics: {topics}; "
        f"relevance={analysis.relevance:.2f}; "
        f"confidence={analysis.confidence:.2f}"
    )
