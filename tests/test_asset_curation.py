from uuid import uuid4

from app.db.models.approval import ApprovalRecord
from app.db.models.asset import AssetVersion

def _asset(client):
    response = client.post("/api/v1/process", headers={"Idempotency-Key": "curation-seed"}, json={"organization_id": "curation-org", "community_id": "curation-community", "reference_period": "2026-W41", "requested_assets": ["FAQ"], "interactions": [{"author": "Ana", "channel": "general", "type": "achievement", "text": "Gracias, conseguí usar FastAPI con PostgreSQL y Docker."}]})
    assert response.status_code == 202
    return response.json()["assets"][0]

def test_pending_assets_can_be_listed(client):
    asset = _asset(client)
    response = client.get("/api/v1/assets", params={"status": "PENDING_REVIEW"})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [asset["id"]]

def test_edit_creates_a_new_version(client, db_session):
    asset = _asset(client)
    response = client.patch(f"/api/v1/assets/{asset['id']}", json={"title": "FAQ revisada", "body": "Respuesta revisada con evidencia.", "editor": "Francis"})
    assert response.status_code == 200
    assert response.json()["version"] == 2
    assert db_session.query(AssetVersion).count() == 2

def test_approve_is_audited_and_asset_becomes_immutable(client, db_session):
    asset = _asset(client)
    approved = client.post(f"/api/v1/assets/{asset['id']}/approve", json={"reviewer": "Francis", "comment": "Listo"})
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"
    assert db_session.query(ApprovalRecord).one().decision == "APPROVED"
    edit = client.patch(f"/api/v1/assets/{asset['id']}", json={"title": "No", "body": "No", "editor": "Francis"})
    assert edit.status_code == 409

def test_unknown_asset_returns_not_found(client):
    response = client.post(f"/api/v1/assets/{uuid4()}/reject", json={"reviewer": "Francis"})
    assert response.status_code == 404
