"""PostgreSQL integration tests for the updated_at database triggers."""

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models.analysis import Analysis
from app.db.models.asset import AssetRecord
from app.db.models.interaction import Interaction
from app.db.models.opportunity import Opportunity
from app.db.models.run import Run


def _run() -> Run:
    return Run(
        organization_id="org-trigger",
        community_id="community-trigger",
        idempotency_key="trigger-test",
        request_hash="a" * 64,
        status="PROCESSING",
    )


def test_expected_updated_at_triggers_are_installed(db_session: Session):
    rows = db_session.execute(
        text(
            """
            SELECT event_object_table, trigger_name
            FROM information_schema.triggers
            WHERE trigger_schema = current_schema()
              AND trigger_name LIKE 'trg_%_set_updated_at'
            ORDER BY event_object_table
            """
        )
    ).all()

    assert set(rows) == {
        ("assets", "trg_assets_set_updated_at"),
        ("opportunities", "trg_opportunities_set_updated_at"),
        ("runs", "trg_runs_set_updated_at"),
    }


def test_triggers_override_updated_at_for_direct_sql_updates(db_session: Session):
    run = _run()
    db_session.add(run)
    db_session.flush()

    interaction = Interaction(
        organization_id="org-trigger",
        community_id="community-trigger",
        author="Trigger test",
        channel="tests",
        type="comment",
        text="Interaction required by the approved relational model",
        fingerprint="b" * 64,
    )
    db_session.add(interaction)
    db_session.flush()

    analysis = Analysis(
        run_id=run.id,
        interaction_id=interaction.id,
        schema_version="v1",
        sentiment="NEUTRAL",
        topics=[],
        entities=[],
        relevance=0.8,
        confidence=0.8,
        model="trigger-test-model",
        prompt_version="v1",
    )
    db_session.add(analysis)
    db_session.flush()

    opportunity = Opportunity(
        run_id=run.id,
        analysis_id=analysis.id,
        schema_version="v1",
        kind="FAQ",
        priority=0.7,
        reason="Trigger test opportunity",
        status="PENDING",
    )
    db_session.add(opportunity)
    db_session.flush()

    asset = AssetRecord(
        run_id=run.id,
        opportunity_id=opportunity.id,
        schema_version="v1",
        asset_type="FAQ",
        status="PENDING_REVIEW",
    )
    db_session.add(asset)
    db_session.commit()

    stale_timestamp = datetime(2000, 1, 1, tzinfo=timezone.utc)
    updates = (
        ("runs", run.id, "status = 'COMPLETED'"),
        ("opportunities", opportunity.id, "status = 'REVIEW_REQUIRED'"),
        ("assets", asset.id, "status = 'REJECTED'"),
    )

    for table_name, row_id, assignment in updates:
        db_session.execute(
            text(
                f"UPDATE {table_name} "
                f"SET {assignment}, updated_at = :stale_timestamp "
                "WHERE id = :row_id"
            ),
            {"stale_timestamp": stale_timestamp, "row_id": row_id},
        )

    db_session.commit()

    for table_name, row_id, _ in updates:
        updated_at = db_session.execute(
            text(f"SELECT updated_at FROM {table_name} WHERE id = :row_id"),
            {"row_id": row_id},
        ).scalar_one()
        assert updated_at > stale_timestamp
