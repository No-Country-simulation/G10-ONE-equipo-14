import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.db.models import (
    Analysis,
    AnalysisEvidence,
    ApprovalRecord,
    AssetRecord,
    AssetVersion,
    AssetVersionSource,
    Interaction,
    ManifestRecord,
    Opportunity,
    OpportunitySource,
    Run,
)


EXPECTED_TABLES = {
    "analyses",
    "analysis_evidence",
    "opportunities",
    "opportunity_sources",
    "assets",
    "asset_versions",
    "asset_version_sources",
    "approvals",
    "manifests",
}


def _base_records(db_session):
    run = Run(
        organization_id="one",
        community_id="g10",
        idempotency_key=str(uuid.uuid4()),
        request_hash="a" * 64,
    )
    interaction = Interaction(
        organization_id="one",
        community_id="g10",
        author="Ana",
        channel="general",
        type="comment",
        text="Una interacción trazable",
        fingerprint=uuid.uuid4().hex * 2,
    )
    db_session.add_all([run, interaction])
    db_session.flush()
    return run, interaction


def _analysis(db_session, run, interaction):
    analysis = Analysis(
        run_id=run.id,
        interaction_id=interaction.id,
        sentiment="POSITIVE",
        topics=["community"],
        entities=[],
        relevance=0.9,
        confidence=0.95,
        model="mock-analysis-v1",
        prompt_version="v1",
    )
    db_session.add(analysis)
    db_session.flush()
    return analysis


def test_content_models_are_registered():
    assert EXPECTED_TABLES.issubset(Base.metadata.tables)


def test_analysis_evidence_and_opportunity_keep_source_fks(db_session):
    run, interaction = _base_records(db_session)
    analysis = _analysis(db_session, run, interaction)
    opportunity = Opportunity(
        run_id=run.id,
        analysis_id=analysis.id,
        kind="LINKEDIN",
        priority=0.8,
        reason="Relevant community achievement",
        status="PENDING",
    )
    db_session.add_all(
        [
            AnalysisEvidence(
                analysis_id=analysis.id,
                interaction_id=interaction.id,
                excerpt="interacción trazable",
            ),
            opportunity,
        ]
    )
    db_session.flush()
    db_session.add(
        OpportunitySource(
            opportunity_id=opportunity.id,
            interaction_id=interaction.id,
        )
    )
    db_session.commit()

    assert db_session.query(AnalysisEvidence).count() == 1
    assert db_session.query(OpportunitySource).count() == 1


def test_postgres_rejects_invalid_opportunity_status(db_session):
    run, interaction = _base_records(db_session)
    analysis = _analysis(db_session, run, interaction)
    db_session.add(
        Opportunity(
            run_id=run.id,
            analysis_id=analysis.id,
            kind="FAQ",
            priority=0.5,
            reason="Question with reusable answer",
            status="INVALID",
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_asset_version_approval_and_manifest_are_persisted(db_session):
    run, interaction = _base_records(db_session)
    analysis = _analysis(db_session, run, interaction)
    opportunity = Opportunity(
        run_id=run.id,
        analysis_id=analysis.id,
        kind="LINKEDIN",
        priority=0.9,
        reason="Strong evidence",
        status="PENDING",
    )
    db_session.add(opportunity)
    db_session.flush()

    asset = AssetRecord(
        run_id=run.id,
        opportunity_id=opportunity.id,
        asset_type="LINKEDIN",
        status="PENDING_REVIEW",
    )
    db_session.add(asset)
    db_session.flush()

    version = AssetVersion(
        asset_id=asset.id,
        version_number=1,
        title="Community achievement",
        content={"claims": [{"text": "A verified achievement"}]},
        model="mock-generator-v1",
        prompt_version="v1",
        created_by="SYSTEM",
    )
    db_session.add(version)
    db_session.flush()
    asset.current_version_id = version.id

    db_session.add_all(
        [
            AssetVersionSource(
                asset_version_id=version.id,
                interaction_id=interaction.id,
                excerpt="interacción trazable",
            ),
            ApprovalRecord(
                asset_id=asset.id,
                asset_version_id=version.id,
                reviewer="reviewer@example.test",
                decision="APPROVED",
            ),
            ManifestRecord(
                run_id=run.id,
                asset_id=asset.id,
                bucket="communitylab-test",
                object_key=f"approved/{asset.id}.json",
                content_type="application/json",
                sha256="b" * 64,
                etag="test-etag",
            ),
        ]
    )
    db_session.commit()

    assert db_session.get(AssetRecord, asset.id).current_version_id == version.id
    assert db_session.query(ApprovalRecord).one().decision == "APPROVED"
    assert db_session.query(ManifestRecord).one().etag == "test-etag"


def test_postgres_rejects_duplicate_asset_version_number(db_session):
    run, interaction = _base_records(db_session)
    analysis = _analysis(db_session, run, interaction)
    opportunity = Opportunity(
        run_id=run.id,
        analysis_id=analysis.id,
        kind="FAQ",
        priority=0.8,
        reason="Reusable question",
        status="PENDING",
    )
    db_session.add(opportunity)
    db_session.flush()
    asset = AssetRecord(
        run_id=run.id,
        opportunity_id=opportunity.id,
        asset_type="FAQ",
        status="PENDING_REVIEW",
    )
    db_session.add(asset)
    db_session.flush()

    for title in ("Version A", "Version B"):
        db_session.add(
            AssetVersion(
                asset_id=asset.id,
                version_number=1,
                title=title,
                content={"answer": title},
                created_by="SYSTEM",
            )
        )

    with pytest.raises(IntegrityError):
        db_session.commit()
