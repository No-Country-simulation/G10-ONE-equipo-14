import hashlib

from app.db.models.manifest import ManifestRecord
from app.services.object_storage import LocalObjectStorage

def test_local_adapter_persists_and_verifies_content(tmp_path):
    storage = LocalObjectStorage(str(tmp_path), "test-bucket")
    stored = storage.put("org/community/asset.json", b"payload", "application/json")
    assert (tmp_path / "test-bucket" / "org/community/asset.json").read_bytes() == b"payload"
    assert stored.sha256 == hashlib.sha256(b"payload").hexdigest()
    assert stored.etag == stored.sha256

def test_only_approved_assets_can_be_published(client, db_session):
    processed = client.post("/api/v1/process", headers={"Idempotency-Key": "publish-seed"}, json={"organization_id": "publish-org", "community_id": "publish-community", "reference_period": "2026-W41", "requested_assets": ["FAQ"], "interactions": [{"author": "Ana", "channel": "general", "type": "achievement", "text": "Gracias, conseguí usar FastAPI con PostgreSQL y Docker."}]})
    asset = processed.json()["assets"][0]
    assert client.post(f"/api/v1/assets/{asset['id']}/publish").status_code == 409
    client.post(f"/api/v1/assets/{asset['id']}/approve", json={"reviewer": "Francis"})
    published = client.post(f"/api/v1/assets/{asset['id']}/publish")
    assert published.status_code == 200
    assert len(published.json()["sha256"]) == 64
    assert published.json()["etag"] == published.json()["sha256"]
    assert db_session.query(ManifestRecord).count() == 1
