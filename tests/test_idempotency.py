"""Integration tests for run and data idempotency."""

from app.db.models.interaction import Interaction
from app.db.models.run import Run


def _payload():
    return {
        "schema_version": "v1",
        "organization_id": "org-demo",
        "community_id": "community-demo",
        "reference_period": "2026-09",
        "requested_assets": ["LINKEDIN", "FAQ"],
        "interactions": [
            {
                "external_id": "msg-001",
                "author": "Ana",
                "channel": "Discord",
                "type": "Pregunta",
                "text": "¿Cómo funciona CommunityLab?",
                "occurred_at": "2026-09-20T12:00:00Z",
            }
        ],
    }


def test_same_request_and_key_reuses_run_and_does_not_duplicate_data(
    client,
    db_session,
):
    headers = {"Idempotency-Key": "idem-test-001"}

    first = client.post("/api/v1/process", json=_payload(), headers=headers)
    second = client.post("/api/v1/process", json=_payload(), headers=headers)

    assert first.status_code == 202
    assert second.status_code == 202

    first_body = first.json()
    second_body = second.json()

    assert first_body["run_id"] == second_body["run_id"]
    assert first_body == second_body

    assert db_session.query(Run).count() == 1
    assert db_session.query(Interaction).count() == 1


def test_same_key_with_different_payload_returns_conflict(client):
    headers = {"Idempotency-Key": "idem-test-002"}

    first_payload = _payload()
    second_payload = _payload()
    second_payload["reference_period"] = "2026-10"

    first = client.post(
        "/api/v1/process",
        json=first_payload,
        headers=headers,
    )
    second = client.post(
        "/api/v1/process",
        json=second_payload,
        headers=headers,
    )

    assert first.status_code == 202
    assert second.status_code == 409
