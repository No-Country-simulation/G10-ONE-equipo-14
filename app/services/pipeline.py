"""Analysis and opportunity pipeline with PostgreSQL persistence."""

import logging
import random
from time import sleep
from uuid import UUID

from app.ai.base import AnalysisProvider
from sqlalchemy.orm import Session

from app.ai.provider_factory import (
    configured_analysis_provider,
    configured_fallback_provider,
)
from app.core.config import settings
from app.db.models.analysis import Analysis as AnalysisRecord
from app.db.models.analysis import AnalysisEvidence
from app.db.models.alert import AlertRecord
from app.db.models.asset import AssetRecord, AssetVersion, AssetVersionSource
from app.db.models.interaction import Interaction
from app.db.models.opportunity import Opportunity as OpportunityRecord
from app.db.models.opportunity import OpportunitySource
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.alert import Alert
from app.schemas.v1.asset import Asset
from app.schemas.v1.interaction import InteractionRequest
from app.schemas.v1.opportunity import Opportunity
from app.services.opportunity_detection import detect_content_opportunity
from app.services.pii_detection import REDACTED_PERSON
from app.services.resilient_analysis import (
    AnalysisProviderUnavailable,
    AnalysisRateLimited,
    analyze_with_resilience,
)
from app.services.content_generation import generate_content
from app.ai.gemini_provider import MAX_SINGLE_BATCH_CHARS

logger = logging.getLogger("communitylab.pipeline")


def analyze_and_persist(
    db: Session,
    run_id: UUID,
    interactions: list[Interaction],
    requested_assets: list[str],
) -> tuple[list[Analysis], list[Opportunity], list[Asset], list[Alert]]:
    """Analyze newly persisted interactions and store traceable decisions."""
    provider = configured_analysis_provider()
    fallback = configured_fallback_provider()
    analyses: list[Analysis] = []
    opportunities: list[Opportunity] = []
    assets: list[Asset] = []
    alerts: list[Alert] = []
    faq_candidates: dict[str, list[tuple[OpportunityRecord, Analysis, str]]] = {}
    interaction_payloads = {
        interaction.id: InteractionRequest(
            external_id=interaction.external_id,
            author=REDACTED_PERSON,
            channel=interaction.channel,
            type=interaction.type,
            text=interaction.text,
            occurred_at=interaction.occurred_at,
            publication_consent=interaction.publication_consent,
            opt_out=interaction.opt_out,
        )
        for interaction in interactions
    }
    batch_analyses: dict[UUID, Analysis] = {}
    batch_drafts = []
    batch_generator = getattr(provider, "generate_batch", None)
    batch_mode = callable(batch_generator)
    if batch_mode:
        try:
            for batch in _interaction_batches(interactions, interaction_payloads):
                for attempt in range(1, settings.analysis_max_attempts + 1):
                    try:
                        batch_results, drafts = batch_generator(
                            interactions=[
                                (interaction.id, interaction_payloads[interaction.id])
                                for interaction in batch
                            ],
                            requested_assets=requested_assets,
                            faq_recurrence_threshold=settings.faq_recurrence_threshold,
                        )
                        batch_analyses.update(batch_results)
                        batch_drafts.extend(drafts)
                        break
                    except Exception as exc:
                        error_code = getattr(
                            exc, "code", getattr(exc, "status_code", None)
                        )
                        error_message = getattr(exc, "message", None)
                        if type(exc) is ValueError:
                            # Batch validation errors contain fixed messages,
                            # not interaction text or model response content.
                            error_message = str(exc)
                        input_chars = sum(
                            len(interaction_payloads[item.id].text) for item in batch
                        )
                        logger.warning(
                            "Gemini batch failed (attempt %s/%s, code=%s, "
                            "items=%s, input_chars=%s, message=%s): %s",
                            attempt,
                            settings.analysis_max_attempts,
                            error_code,
                            len(batch),
                            input_chars,
                            str(error_message)[:500] if error_message else None,
                            type(exc).__name__,
                        )
                        retryable = error_code in {408, 429, 500, 502, 503, 504}
                        if attempt == settings.analysis_max_attempts or not retryable:
                            raise
                        sleep(min(2 ** (attempt - 1), 4) + random.uniform(0, 0.25))
        except Exception as exc:
            batch_mode = False
            batch_analyses.clear()
            batch_drafts.clear()
            if fallback is not None:
                # A configured fallback is an explicit operator choice. Use it
                # directly so we do not repeat the rejected Gemini requests.
                provider, fallback = fallback, None
            elif getattr(exc, "code", getattr(exc, "status_code", None)) == 429:
                raise AnalysisRateLimited(
                    "Gemini rate or quota limit reached."
                ) from exc
            else:
                raise AnalysisProviderUnavailable(
                    "Gemini batch analysis failed."
                ) from exc

    opportunities_by_interaction: dict[UUID, OpportunityRecord] = {}
    interaction_by_id = {interaction.id: interaction for interaction in interactions}

    for interaction in interactions:
        analysis = batch_analyses.get(interaction.id)
        if analysis is None:
            analysis = analyze_with_resilience(
                provider=provider,
                interaction_id=interaction.id,
                interaction=interaction_payloads[interaction.id],
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

        internal_alert = analysis.sentiment == "negative"
        if internal_alert:
            alert_record = AlertRecord(
                run_id=run_id,
                interaction_id=interaction.id,
                severity="HIGH",
                status="OPEN",
                message="Negative sentiment or frustration requires internal attention.",
                excerpt=analysis.evidence[0].excerpt
                if analysis.evidence
                else interaction.text[:240],
            )
            db.add(alert_record)
            db.flush()
            alerts.append(
                Alert(
                    id=alert_record.id,
                    run_id=alert_record.run_id,
                    interaction_id=alert_record.interaction_id,
                    severity=alert_record.severity,
                    status=alert_record.status,
                    message=alert_record.message,
                    excerpt=alert_record.excerpt,
                    created_at=alert_record.created_at,
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

        opportunities_by_interaction[interaction.id] = opportunity_record

        if internal_alert:
            continue

        if decision.status.value != "PENDING":
            continue

        for channel in requested_assets:
            if channel == "FAQ":
                if interaction.type == "question":
                    topic = analysis.topics[0] if analysis.topics else "general"
                    faq_candidates.setdefault(topic, []).append(
                        (opportunity_record, analysis, interaction.text)
                    )
                continue
            if batch_mode:
                continue
            assets.append(
                _persist_asset(
                    db,
                    run_id,
                    opportunity_record,
                    analysis,
                    channel,
                    provider=provider,
                    fallback=fallback,
                )
            )

    if not batch_mode and "FAQ" in requested_assets:
        for candidates in faq_candidates.values():
            if len(candidates) < settings.faq_recurrence_threshold:
                continue
            opportunity_record, representative, _ = candidates[0]
            merged_evidence = list(
                {
                    (evidence.source_interaction_id, evidence.excerpt): evidence
                    for _, candidate, _ in candidates
                    for evidence in candidate.evidence
                }.values()
            )
            recurring_questions = [question for _, _, question in candidates]
            recurring_analysis = representative.model_copy(
                update={"evidence": merged_evidence}
            )
            assets.append(
                _persist_asset(
                    db,
                    run_id,
                    opportunity_record,
                    recurring_analysis,
                    "FAQ",
                    provider=provider,
                    fallback=fallback,
                    questions=recurring_questions,
                )
            )

    if batch_mode:
        seen_assets: set[tuple] = set()
        persisted_batch_drafts = 0
        for draft in batch_drafts:
            try:
                source_ids = [UUID(value) for value in draft.source_interaction_ids]
            except (TypeError, ValueError):
                logger.warning(
                    "Skipping Gemini draft with invalid source interaction id."
                )
                continue
            source_ids = list(dict.fromkeys(source_ids))
            if (
                not source_ids
                or any(source_id not in interaction_by_id for source_id in source_ids)
                or any(
                    interaction_by_id[source_id].opt_out
                    or interaction_by_id[source_id].pii_detected
                    for source_id in source_ids
                )
            ):
                continue
            if draft.channel not in requested_assets:
                continue
            source_interactions = [
                interaction_by_id[source_id] for source_id in source_ids
            ]
            source_analyses = [batch_analyses[source_id] for source_id in source_ids]
            opportunity_record = next(
                (
                    opportunities_by_interaction[source_id]
                    for source_id in source_ids
                    if source_id in opportunities_by_interaction
                ),
                None,
            )
            if opportunity_record is None:
                continue
            if draft.channel == "FAQ":
                asset_key = (draft.channel, tuple(sorted(source_ids)))
            else:
                normalized_title = " ".join(draft.title.split()).casefold()
                normalized_body = " ".join(draft.body.split()).casefold()
                asset_key = (draft.channel, normalized_title, normalized_body)
            if asset_key in seen_assets:
                continue
            seen_assets.add(asset_key)
            merged_evidence = list(
                {
                    (evidence.source_interaction_id, evidence.excerpt): evidence
                    for analysis in source_analyses
                    for evidence in analysis.evidence
                }.values()
            )
            representative = source_analyses[0].model_copy(
                update={"evidence": merged_evidence}
            )
            assets.append(
                _persist_asset(
                    db,
                    run_id,
                    opportunity_record,
                    representative,
                    draft.channel,
                    provider=provider,
                    fallback=fallback,
                    questions=[interaction.text for interaction in source_interactions]
                    if draft.channel == "FAQ"
                    else None,
                    draft=(draft.title, draft.body),
                )
            )
            persisted_batch_drafts += 1
        logger.info(
            "Gemini batch drafts processed (received=%s, persisted=%s).",
            len(batch_drafts),
            persisted_batch_drafts,
        )

    db.commit()
    return analyses, opportunities, assets, alerts


def _persist_asset(
    db: Session,
    run_id: UUID,
    opportunity_record: OpportunityRecord,
    analysis: Analysis,
    channel: str,
    *,
    provider: AnalysisProvider,
    fallback: AnalysisProvider | None,
    questions: list[str] | None = None,
    draft: tuple[str, str] | None = None,
) -> Asset:
    generated = generate_content(
        channel=channel,
        opportunity_id=opportunity_record.id,
        analysis=analysis,
        provider=provider,
        fallback=fallback,
        questions=questions,
        draft=draft,
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


def _interaction_batches(
    interactions: list[Interaction],
    payloads: dict[UUID, InteractionRequest],
) -> list[list[Interaction]]:
    """Keep Gemini structured responses bounded for larger uploads."""
    batches: list[list[Interaction]] = []
    current: list[Interaction] = []
    current_chars = 0
    for interaction in interactions:
        size = len(payloads[interaction.id].text) + 120
        if current and current_chars + size > MAX_SINGLE_BATCH_CHARS:
            batches.append(current)
            current = []
            current_chars = 0
        current.append(interaction)
        current_chars += size
    if current:
        batches.append(current)
    return batches
