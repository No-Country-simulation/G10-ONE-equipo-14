"""End-to-end persistence tests for the local analysis pipeline."""

from app.db.models.analysis import Analysis, AnalysisEvidence
from app.db.models.opportunity import Opportunity, OpportunitySource


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
    assert len(body["opportunities"]) == 1
    assert body["opportunities"][0]["status"] == "PENDING"

    assert db_session.query(Analysis).count() == 1
    assert db_session.query(AnalysisEvidence).count() == 1
    assert db_session.query(Opportunity).count() == 1
    assert db_session.query(OpportunitySource).count() == 1


def test_pipeline_blocks_pii_and_persists_the_decision(client, db_session):
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
    assert response.json()["opportunities"][0]["status"] == "BLOCKED"
    assert db_session.query(Opportunity).one().status == "BLOCKED"
