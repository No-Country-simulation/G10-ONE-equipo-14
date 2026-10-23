"""Persistence and access checks for resolving internal alerts."""

from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr

from app.api.security import mutation_rate_limiter
from app.core.config import settings
from app.db.models.alert import AlertRecord


@pytest.fixture(autouse=True)
def reset_mutation_limiter():
    mutation_rate_limiter.clear()
    yield
    mutation_rate_limiter.clear()


@pytest.fixture
def open_alert(client):
    response = client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": "resolve-alert-seed"},
        json={
            "organization_id": "alerts-org",
            "community_id": "alerts-community",
            "reference_period": "2026-W43",
            "requested_assets": ["FAQ"],
            "interactions": [
                {
                    "author": "Ana",
                    "channel": "soporte",
                    "type": "question",
                    "text": "Tengo problemas con Docker y PostgreSQL; falla con un error.",
                }
            ],
        },
    )
    assert response.status_code == 202, response.json()
    return response.json()["alerts"][0]


def test_resolve_alert_is_persisted_and_reflected_in_status_filters(
    client, db_session, open_alert
):
    response = client.post(f"/api/v1/alerts/{open_alert['id']}/resolve")

    assert response.status_code == 200
    assert response.json() == {**open_alert, "status": "RESOLVED"}
    db_session.expire_all()
    assert db_session.get(AlertRecord, UUID(open_alert["id"])).status == "RESOLVED"
    assert client.get("/api/v1/alerts", params={"status": "OPEN"}).json() == []
    assert client.get("/api/v1/alerts", params={"status": "RESOLVED"}).json() == [
        response.json()
    ]
    assert client.get("/api/v1/alerts", params={"status": ""}).json() == [
        response.json()
    ]


def test_resolve_alert_is_idempotent(client, db_session, open_alert):
    endpoint = f"/api/v1/alerts/{open_alert['id']}/resolve"

    first = client.post(endpoint)
    repeated = client.post(endpoint)

    assert first.status_code == repeated.status_code == 200
    assert first.json() == repeated.json()
    assert db_session.query(AlertRecord).count() == 1


def test_resolve_missing_alert_returns_not_found(client):
    response = client.post(f"/api/v1/alerts/{uuid4()}/resolve")
    assert response.status_code == 404


def test_resolve_alert_rejects_invalid_identifier(client):
    assert client.post("/api/v1/alerts/invalid/resolve").status_code == 422


def test_resolve_alert_requires_configured_key(
    client, db_session, open_alert, monkeypatch
):
    monkeypatch.setattr(settings, "api_write_key", SecretStr("alert-secret"))
    endpoint = f"/api/v1/alerts/{open_alert['id']}/resolve"

    assert client.post(endpoint).status_code == 401
    assert client.post(endpoint, headers={"X-API-Key": "wrong"}).status_code == 401
    db_session.expire_all()
    assert db_session.get(AlertRecord, UUID(open_alert["id"])).status == "OPEN"
    assert (
        client.post(endpoint, headers={"X-API-Key": "alert-secret"}).status_code == 200
    )


def test_resolve_alert_respects_disabled_mutations(
    client, db_session, open_alert, monkeypatch
):
    monkeypatch.setattr(settings, "mutations_enabled", False)

    response = client.post(f"/api/v1/alerts/{open_alert['id']}/resolve")

    assert response.status_code == 403
    db_session.expire_all()
    assert db_session.get(AlertRecord, UUID(open_alert["id"])).status == "OPEN"


def test_resolve_alert_respects_rate_limit(client, open_alert, monkeypatch):
    monkeypatch.setattr(settings, "mutation_rate_limit", 1)
    mutation_rate_limiter.clear()
    endpoint = f"/api/v1/alerts/{open_alert['id']}/resolve"

    assert client.post(endpoint).status_code == 200
    assert client.post(endpoint).status_code == 429
