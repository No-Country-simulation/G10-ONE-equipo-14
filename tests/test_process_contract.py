"""Contract tests for POST /api/v1/process."""


def _payload():
    return {
        "schema_version": "v1",
        "organization_id": "one",
        "community_id": "g10",
        "reference_period": "2026-W38",
        "requested_assets": ["LINKEDIN", "FAQ"],
        "interactions": [
            {
                "author": "Mariana",
                "channel": "logros",
                "type": "testimonio",
                "text": "Conseguí mi primer empleo.",
            }
        ],
    }


def test_idempotency_required(client):
    response = client.post(
        "/api/v1/process",
        json=_payload(),
    )

    assert response.status_code == 422


def test_contract_returns_202(client):
    response = client.post(
        "/api/v1/process",
        json=_payload(),
        headers={"Idempotency-Key": "demo-001"},
    )

    assert response.status_code == 202

    body = response.json()

    assert body["schema_version"] == "v1"
    assert body["run_id"]
    assert body["status"] in {"ACCEPTED", "ACCEPTED_WITH_ERRORS"}
    assert "summary" in body


def test_same_key_same_run_id(client):
    headers = {"Idempotency-Key": "stable-key"}

    first = client.post(
        "/api/v1/process",
        json=_payload(),
        headers=headers,
    )

    second = client.post(
        "/api/v1/process",
        json=_payload(),
        headers=headers,
    )

    assert first.status_code == 202
    assert second.status_code == 202

    assert first.json()["run_id"] == second.json()["run_id"]
