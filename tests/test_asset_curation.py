from uuid import uuid4

from app.db.models.approval import ApprovalRecord
from app.db.models.asset import AssetVersion

def _asset(client):
    response = client.post("/api/v1/process", headers={"Idempotency-Key": "curation-seed"}, json={"organization_id": "curation-org", "community_id": "curation-community", "reference_period": "2026-W41", "requested_assets": ["LINKEDIN"], "interactions": [{"author": "Ana", "channel": "general", "type": "achievement", "text": "Gracias, conseguí usar FastAPI con PostgreSQL y Docker."}]})
    assert response.status_code == 202
    return response.json()["assets"][0]

def test_pending_assets_can_be_listed(client):
    asset = _asset(client)
    response = client.get("/api/v1/assets", params={"status": "PENDING_REVIEW"})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [asset["id"]]
    listed = response.json()[0]
    assert listed["source_interaction_ids"] == asset["source_interaction_ids"]
    assert listed["evidence"] == asset["evidence"]

def test_edit_creates_a_new_version(client, db_session):
    asset = _asset(client)
    response = client.patch(f"/api/v1/assets/{asset['id']}", json={"title": "FAQ revisada", "body": "Respuesta revisada con evidencia.", "editor": "Francis"})
    assert response.status_code == 200
    assert response.json()["version"] == 2
    assert response.json()["source_interaction_ids"] == asset["source_interaction_ids"]
    assert response.json()["evidence"] == asset["evidence"]
    assert db_session.query(AssetVersion).count() == 2

def test_approve_is_audited_and_asset_becomes_immutable(client, db_session):
    asset = _asset(client)
    approved = client.post(f"/api/v1/assets/{asset['id']}/approve", json={"reviewer": "Francis", "comment": "Listo"})
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"
    assert db_session.query(ApprovalRecord).one().decision == "APPROVED"
    edit = client.patch(f"/api/v1/assets/{asset['id']}", json={"title": "No", "body": "No", "editor": "Francis"})
    assert edit.status_code == 409

def test_repeated_approval_is_rejected_without_duplicate_audit(client, db_session):
    asset = _asset(client)
    endpoint = f"/api/v1/assets/{asset['id']}/approve"
    assert client.post(endpoint, json={"reviewer": "Francis"}).status_code == 200
    repeated = client.post(endpoint, json={"reviewer": "Francis"})
    assert repeated.status_code == 409
    assert "APPROVED to APPROVED" in repeated.json()["detail"]
    assert db_session.query(ApprovalRecord).count() == 1

def test_approved_asset_cannot_be_rejected(client, db_session):
    asset = _asset(client)
    assert client.post(f"/api/v1/assets/{asset['id']}/approve", json={"reviewer": "Francis"}).status_code == 200
    rejected = client.post(f"/api/v1/assets/{asset['id']}/reject", json={"reviewer": "Francis"})
    assert rejected.status_code == 409
    assert db_session.query(ApprovalRecord).count() == 1

def test_rejected_asset_can_only_be_reopened_by_editing(client, db_session):
    asset = _asset(client)
    rejected = client.post(f"/api/v1/assets/{asset['id']}/reject", json={"reviewer": "Francis"})
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "REJECTED"
    assert client.post(f"/api/v1/assets/{asset['id']}/approve", json={"reviewer": "Francis"}).status_code == 409

    reopened = client.patch(f"/api/v1/assets/{asset['id']}", json={"title": "FAQ corregida", "body": "Contenido corregido.", "editor": "Francis"})
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "PENDING_REVIEW"
    assert reopened.json()["version"] == 2
    assert db_session.query(ApprovalRecord).count() == 1

def test_unknown_asset_returns_not_found(client):
    response = client.post(f"/api/v1/assets/{uuid4()}/reject", json={"reviewer": "Francis"})
    assert response.status_code == 404
