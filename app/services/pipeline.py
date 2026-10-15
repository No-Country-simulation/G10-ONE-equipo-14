"""Analysis and opportunity pipeline with PostgreSQL persistence."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.provider_factory import (
    configured_analysis_provider,
    configured_fallback_provider,
)
from app.core.config import settings
from app.db.models.analysis import Analysis as AnalysisRecord
from app.db.models.analysis import AnalysisEvidence
from app.db.models.asset import AssetRecord, AssetVersion, AssetVersionSource
from app.db.models.interaction import Interaction
from app.db.models.opportunity import Opportunity as OpportunityRecord
from app.db.models.opportunity import OpportunitySource
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.asset import Asset
from app.schemas.v1.interaction import InteractionRequest
from app.schemas.v1.opportunity import Opportunity
from app.services.opportunity_detection import detect_content_opportunity
from app.services.pii_detection import REDACTED_PERSON
from app.services.resilient_analysis import analyze_with_resilience
from app.services.content_generation import generate_content


def analyze_and_persist(
    db: Session,
    run_id: UUID,
    interactions: list[Interaction],
    requested_assets: list[str],
) -> tuple[list[Analysis], list[Opportunity], list[Asset]]:
    """Analyze newly persisted interactions and store traceable decisions."""
    provider = configured_analysis_provider()
    fallback = configured_fallback_provider()
    analyses: list[Analysis] = []
    opportunities: list[Opportunity] = []
    assets: list[Asset] = []
    faq_candidates: dict[str, list[tuple[OpportunityRecord, Analysis]]] = {}

    for interaction in interactions:
        interaction_payload = InteractionRequest(
            external_id=interaction.external_id,
            author=(
                interaction.author
                if interaction.publication_consent
                else REDACTED_PERSON
            ),
            channel=interaction.channel,
            type=interaction.type,
            text=interaction.text,
            occurred_at=interaction.occurred_at,
            publication_consent=interaction.publication_consent,
            opt_out=interaction.opt_out,
        )
        analysis = analyze_with_resilience(
            provider=provider,
            interaction_id=interaction.id,
            interaction=interaction_payload,
            max_attempts=settings.analysis_max_attempts,
            fallback=fallback,
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

        decision = detect_content_opportunity(
            analysis_record.id,
            analysis,
            opt_out=interaction.opt_out,
            pii_detected=interaction.pii_detected,
        )
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

        if decision.status.value != "PENDING":
            continue

        for channel in requested_assets:
            if channel == "FAQ":
                if interaction.type == "question":
                    topic = analysis.topics[0] if analysis.topics else "general"
                    faq_candidates.setdefault(topic, []).append(
                        (opportunity_record, analysis)
                    )
                continue
            assets.append(
                _persist_asset(db, run_id, opportunity_record, analysis, channel)
            )

    if "FAQ" in requested_assets:
        for candidates in faq_candidates.values():
            if len(candidates) < settings.faq_recurrence_threshold:
                continue
            opportunity_record, representative = candidates[0]
            merged_evidence = list({
                (evidence.source_interaction_id, evidence.excerpt): evidence
                for _, candidate in candidates
                for evidence in candidate.evidence
            }.values())
            recurring_analysis = representative.model_copy(
                update={"evidence": merged_evidence}
            )
            assets.append(
                _persist_asset(
                    db, run_id, opportunity_record, recurring_analysis, "FAQ"
                )
            )

    db.commit()
    return analyses, opportunities, assets


def _persist_asset(
    db: Session,
    run_id: UUID,
    opportunity_record: OpportunityRecord,
    analysis: Analysis,
    channel: str,
) -> Asset:
    generated = generate_content(
        channel=channel,
        opportunity_id=opportunity_record.id,
        analysis=analysis,
    )
    asset_record = AssetRecord(
        run_id=run_id,
        opportunity_id=opportunity_record.id,
        schema_version="v1",
        asset_type=channel,
        status="PENDING_REVIEW",
    )
    db.add(asset_record)
    db.flush()
    version = AssetVersion(
        asset_id=asset_record.id,
        version_number=1,
        title=generated.title,
        content=generated.content,
        model=analysis.model,
        prompt_version=generated.prompt_version,
        created_by="pipeline",
    )
    db.add(version)
    db.flush()
    for evidence in analysis.evidence:
        db.add(
            AssetVersionSource(
                asset_version_id=version.id,
                interaction_id=evidence.source_interaction_id,
                excerpt=evidence.excerpt,
            )
        )
    asset_record.current_version_id = version.id
    return Asset(
        id=asset_record.id,
        opportunity_id=opportunity_record.id,
        channel=channel,
        title=generated.title,
        body=generated.body,
        status="PENDING_REVIEW",
        version=1,
        source_interaction_ids=[
            evidence.source_interaction_id for evidence in analysis.evidence
        ],
        evidence=analysis.evidence,
    )
