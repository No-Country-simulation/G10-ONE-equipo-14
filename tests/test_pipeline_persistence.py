"""End-to-end persistence tests for the local analysis pipeline."""

from app.db.models.analysis import Analysis, AnalysisEvidence
from app.db.models.opportunity import Opportunity, OpportunitySource
from app.db.models.asset import AssetRecord, AssetVersion, AssetVersionSource
from app.db.models.interaction import Interaction
from app.db.models.alert import AlertRecord


def test_process_persists_analysis_evidence_and_opportunity(client, db_session):
    response = client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": "pipeline-persistence-success"},
        json={
            "organization_id": "pipeline-org",
            "community_id": "pipeline-community",
            "reference_period": "2026-W41",
            "requested_assets": ["LINKEDIN"],
            "interactions": [
                {
                    "external_id": "pipeline-001",
                    "author": "Ana",
                    "channel": "logros",
                    "type": "achievement",
                    "text": "Gracias, conseguí conectar FastAPI con PostgreSQL usando Docker.",
                }
            ],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert len(body["analyses"]) == 1
    assert body["analyses"][0]["model"] == "mock-analysis-v1"
    assert body["summary"]["predominant_sentiment"] == "positive"
    assert body["summary"]["top_topics"] == ["docker", "postgresql", "fastapi"]
    assert body["summary"]["processing_time_ms"] >= 0
    assert len(body["opportunities"]) == 1
    assert body["opportunities"][0]["status"] == "PENDING"
    assert {asset["channel"] for asset in body["assets"]} == {"LINKEDIN"}
    asset = body["assets"][0]
    analysis_evidence = body["analyses"][0]["evidence"]
    assert asset["evidence"] == analysis_evidence
    assert asset["source_interaction_ids"] == [
        analysis_evidence[0]["source_interaction_id"]
    ]

    assert db_session.query(Analysis).count() == 1
    assert db_session.query(AnalysisEvidence).count() == 1
    assert db_session.query(Opportunity).count() == 1
    assert db_session.query(OpportunitySource).count() == 1
    assert db_session.query(AssetRecord).count() == 1
    assert db_session.query(AssetVersion).count() == 1
    assert db_session.query(AssetVersionSource).count() == 1


def test_pipeline_redacts_pii_before_analysis_and_persistence(client, db_session):
    response = client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": "pipeline-pii-block"},
        json={
            "organization_id": "pipeline-org",
            "community_id": "pipeline-community",
            "reference_period": "2026-W41",
            "requested_assets": ["FAQ"],
            "interactions": [
                {
                    "author": "Ana",
                    "channel": "soporte",
                    "type": "question",
                    "text": "Mi correo ana@example.com tiene problemas con FastAPI y PostgreSQL.",
                }
            ],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["opportunities"][0]["status"] == "BLOCKED"
    assert body["assets"] == []
    stored = db_session.query(Interaction).one()
    assert stored.text == "Mi correo [EMAIL] tiene problemas con FastAPI y PostgreSQL."
    assert stored.pii_detected is True
    assert "ana@example.com" not in str(body)


def test_author_without_consent_is_anonymized_and_opt_out_blocks_publication(client, db_session):
    response = client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": "pipeline-opt-out"},
        json={
            "organization_id": "pipeline-org",
            "community_id": "pipeline-community",
            "reference_period": "2026-W41",
            "requested_assets": ["LINKEDIN"],
            "interactions": [{
                "author": "Ana Pérez",
                "channel": "logros",
                "type": "achievement",
                "text": "Ana Pérez consiguió usar FastAPI con PostgreSQL.",
                "publication_consent": False,
                "opt_out": True,
            }],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["opportunities"][0]["status"] == "BLOCKED"
    assert "opted out" in body["opportunities"][0]["reason"]
    assert body["assets"] == []
    assert "Ana Pérez" not in str(body)
    stored = db_session.query(Interaction).one()
    assert stored.author == "Ana Pérez"
    assert stored.text == "[PERSON] consiguió usar FastAPI con PostgreSQL."
    assert stored.publication_consent is False
    assert stored.opt_out is True


def test_negative_sentiment_creates_internal_alert_and_never_public_content(client, db_session):
    response = client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": "pipeline-negative-alert"},
        json={
            "organization_id": "pipeline-org",
            "community_id": "pipeline-community",
            "reference_period": "2026-W41",
            "requested_assets": ["LINKEDIN", "FAQ"],
            "interactions": [{
                "author": "Ana",
                "channel": "soporte",
                "type": "question",
                "text": "Tengo problemas con FastAPI y PostgreSQL; Docker falla con un error.",
            }],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["analyses"][0]["sentiment"] == "negative"
    assert body["opportunities"][0]["status"] == "BLOCKED"
    assert body["assets"] == []
    assert len(body["alerts"]) == 1
    assert body["alerts"][0]["status"] == "OPEN"
    assert db_session.query(AlertRecord).count() == 1

    listed = client.get("/api/v1/alerts", params={"status": "OPEN"})
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == body["alerts"][0]["id"]
