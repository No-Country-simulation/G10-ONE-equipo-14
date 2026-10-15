from sqlalchemy import select

from app.api.security import mutation_rate_limiter
from app.core.config import settings
from app.db.models.interaction import Interaction


def _event(event_id: str = "discord-message-100") -> dict:
    return {
        "source": "discord",
        "event_id": event_id,
        "organization_id": "one",
        "community_id": "g10",
        "reference_period": "2026-W42",
        "requested_assets": ["LINKEDIN"],
        "interaction": {
            "author": "Miembro con consentimiento",
            "channel": "logros",
            "type": "message",
            "text": "Completé un proyecto automático con CommunityLab.",
            "publication_consent": True,
        },
    }


def test_webhook_runs_existing_pipeline_and_derives_external_id(client, db_session):
    response = client.post("/api/v1/webhooks/interactions", json=_event())

    assert response.status_code == 202
    assert response.json()["summary"]["received"] == 1
    interaction = db_session.execute(select(Interaction)).scalar_one()
    assert interaction.external_id == "discord:discord-message-100"


def test_webhook_retry_replays_same_run_without_duplicates(client):
    first = client.post("/api/v1/webhooks/interactions", json=_event("retry-1"))
    second = client.post("/api/v1/webhooks/interactions", json=_event("retry-1"))

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["run_id"] == second.json()["run_id"]


def test_webhook_conflicting_retry_is_rejected(client):
    event = _event("conflict-1")
    first = client.post("/api/v1/webhooks/interactions", json=event)
    event["interaction"]["text"] = "El proveedor reutilizó el ID para otro contenido."
    second = client.post("/api/v1/webhooks/interactions", json=event)

    assert first.status_code == 202
    assert second.status_code == 409


def test_webhook_obeys_mutation_protection(client):
    previous = settings.mutations_enabled
    settings.mutations_enabled = False
    mutation_rate_limiter.clear()
    try:
        response = client.post("/api/v1/webhooks/interactions", json=_event("blocked"))
        assert response.status_code == 403
    finally:
        settings.mutations_enabled = previous
        mutation_rate_limiter.clear()
