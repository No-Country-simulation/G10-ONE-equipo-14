"""Analysis and opportunity pipeline with PostgreSQL persistence."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.mock_provider import MockAnalysisProvider
from app.db.models.analysis import Analysis as AnalysisRecord
from app.db.models.analysis import AnalysisEvidence
from app.db.models.interaction import Interaction
from app.db.models.opportunity import Opportunity as OpportunityRecord
from app.db.models.opportunity import OpportunitySource
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.interaction import InteractionRequest
from app.schemas.v1.opportunity import Opportunity
from app.services.analysis import analyze_interaction
from app.services.opportunity_detection import detect_content_opportunity


def analyze_and_persist(
    db: Session,
    run_id: UUID,
    interactions: list[Interaction],
) -> tuple[list[Analysis], list[Opportunity]]:
    """Analyze newly persisted interactions and store traceable decisions."""
    provider = MockAnalysisProvider()
    analyses: list[Analysis] = []
    opportunities: list[Opportunity] = []

    for interaction in interactions:
        interaction_payload = InteractionRequest(
            external_id=interaction.external_id,
            author=interaction.author,
            channel=interaction.channel,
            type=interaction.type,
            text=interaction.text,
            occurred_at=interaction.occurred_at,
        )
        analysis = analyze_interaction(
            provider,
            interaction.id,
            interaction_payload,
        )
        analysis_record = AnalysisRecord(
            run_id=run_id,
            interaction_id=interaction.id,
            schema_version=analysis.schema_version,
            sentiment=analysis.sentiment,
            topics=analysis.topics,
            entities=analysis.entities,
            relevance=analysis.relevance,
            confidence=analysis.confidence,
            model=analysis.model,
            prompt_version=analysis.prompt_version,
        )
        db.add(analysis_record)
        db.flush()

        for evidence in analysis.evidence:
            db.add(
                AnalysisEvidence(
                    analysis_id=analysis_record.id,
                    interaction_id=evidence.source_interaction_id,
                    excerpt=evidence.excerpt,
                )
            )

        decision = detect_content_opportunity(analysis_record.id, analysis)
        analyses.append(analysis)
        if decision is None:
            continue

        opportunity_record = OpportunityRecord(
            run_id=run_id,
            analysis_id=analysis_record.id,
            schema_version=decision.schema_version,
            kind=decision.kind,
            priority=decision.priority,
            reason=decision.reason,
            status=decision.status.value,
        )
        db.add(opportunity_record)
        db.flush()
        for source_id in decision.source_ids:
            db.add(
                OpportunitySource(
                    opportunity_id=opportunity_record.id,
                    interaction_id=source_id,
                )
            )

        opportunities.append(
            Opportunity(
                schema_version=decision.schema_version,
                analysis_id=decision.analysis_id,
                kind=decision.kind,
                priority=decision.priority,
                reason=decision.reason,
                source_ids=decision.source_ids,
                status=decision.status.value,
            )
        )

    db.commit()
    return analyses, opportunities
