"""Contract tests for POST /api/v1/process.

Week 2 backend coverage:
- valid base contract is accepted
- run_id is returned
- missing required request fields return HTTP 422
- invalid interaction fields return HTTP 422
- missing Idempotency-Key returns HTTP 422

Duplicate persistence and request idempotency are covered separately in:
- tests/test_ingestion.py
- tests/test_idempotency.py
"""


def valid_payload() -> dict:
    """Return the minimum valid Week 2 process request."""
    return {
        "schema_version": "v1",
        "organization_id": "org-demo",
        "community_id": "community-demo",
        "reference_period": "2026-09",
        "requested_assets": ["LINKEDIN", "FAQ"],
        "interactions": [
            {
                "external_id": "msg-contract-001",
                "author": "Ana",
                "channel": "Discord",
                "type": "Pregunta",
                "text": "¿Cómo funciona CommunityLab?",
                "occurred_at": "2026-09-20T12:00:00Z",
            }
        ],
    }


def test_valid_contract_is_accepted_and_returns_run_id(client):
    """A valid request with Idempotency-Key must be accepted."""
    response = client.post(
        "/api/v1/process",
        json=valid_payload(),
        headers={"Idempotency-Key": "contract-valid-001"},
    )

    assert response.status_code == 202

    body = response.json()

    assert body["schema_version"] == "v1"
    assert body["run_id"]
    assert body["status"] in {"ACCEPTED", "ACCEPTED_WITH_ERRORS"}

    assert "summary" in body
    assert body["summary"]["received"] == 1


def test_missing_organization_id_returns_422(client):
    """organization_id is required by the process contract."""
    payload = valid_payload()
    payload.pop("organization_id")

    response = client.post(
        "/api/v1/process",
        json=payload,
        headers={"Idempotency-Key": "contract-invalid-org"},
    )

    assert response.status_code == 422


def test_missing_community_id_returns_422(client):
    """community_id is required by the process contract."""
    payload = valid_payload()
    payload.pop("community_id")

    response = client.post(
        "/api/v1/process",
        json=payload,
        headers={"Idempotency-Key": "contract-invalid-community"},
    )

    assert response.status_code == 422


def test_missing_interactions_returns_422(client):
    """The interactions field is required by the process contract."""
    payload = valid_payload()
    payload.pop("interactions")

    response = client.post(
        "/api/v1/process",
        json=payload,
        headers={"Idempotency-Key": "contract-invalid-interactions"},
    )

    assert response.status_code == 422


def test_interaction_without_text_returns_422(client):
    """An interaction without its required text must fail validation."""
    payload = valid_payload()
    payload["interactions"][0].pop("text")

    response = client.post(
        "/api/v1/process",
        json=payload,
        headers={"Idempotency-Key": "contract-invalid-text"},
    )

    assert response.status_code == 422


def test_interaction_without_author_returns_422(client):
    """An interaction without its required author must fail validation."""
    payload = valid_payload()
    payload["interactions"][0].pop("author")

    response = client.post(
        "/api/v1/process",
        json=payload,
        headers={"Idempotency-Key": "contract-invalid-author"},
    )

    assert response.status_code == 422


def test_invalid_occurred_at_returns_422(client):
    """An invalid occurred_at value must fail datetime validation."""
    payload = valid_payload()
    payload["interactions"][0]["occurred_at"] = "not-a-date"

    response = client.post(
        "/api/v1/process",
        json=payload,
        headers={"Idempotency-Key": "contract-invalid-date"},
    )

    assert response.status_code == 422


def test_missing_idempotency_key_returns_422(client):
    """Idempotency-Key is mandatory for POST /api/v1/process."""
    response = client.post(
        "/api/v1/process",
        json=valid_payload(),
    )

    assert response.status_code == 422
