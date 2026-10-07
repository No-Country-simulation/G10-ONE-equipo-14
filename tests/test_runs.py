"""Integration tests for persisted run queries."""

from uuid import uuid4

from app.db.models.run import Run


PAYLOAD = {
    "organization_id": "run-query-org",
    "community_id": "run-query-community",
    "reference_period": "2026-W41",
    "requested_assets": ["LINKEDIN"],
    "interactions": [
        {
            "author": "Ana",
            "channel": "general",
            "type": "achievement",
            "text": "La comunidad completó el proyecto.",
        }
    ],
}


def test_get_run_returns_the_persisted_process_response(client):
    process_response = client.post(
        "/api/v1/process",
        json=PAYLOAD,
        headers={"Idempotency-Key": "run-query-success"},
    )
    assert process_response.status_code == 202

    body = process_response.json()
    query_response = client.get(f"/api/v1/runs/{body['run_id']}")

    assert query_response.status_code == 200
    assert query_response.json() == body


def test_get_run_returns_not_found_for_unknown_id(client):
    response = client.get(f"/api/v1/runs/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found."


def test_get_run_reports_an_unfinished_run(client, db_session):
    run = Run(
        organization_id="run-query-org",
        community_id="run-query-community",
        idempotency_key="run-query-processing",
        request_hash="c" * 64,
        status="PROCESSING",
    )
    db_session.add(run)
    db_session.commit()

    response = client.get(f"/api/v1/runs/{run.id}")

    assert response.status_code == 409
    assert response.json()["detail"] == "Run is still being processed."
