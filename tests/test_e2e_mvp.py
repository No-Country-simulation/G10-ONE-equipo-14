"""The three required MVP journeys across API, DB, AI and storage."""

def _process(client, key, text, assets):
    return client.post("/api/v1/process", headers={"Idempotency-Key": key, "X-Request-ID": f"trace-{key}"}, json={"organization_id": "e2e-org", "community_id": "e2e-community", "reference_period": "2026-W41", "requested_assets": assets, "interactions": [{"author": "Ana", "channel": "community", "type": "message", "text": text}]})

def test_achievement_to_approved_and_published_linkedin(client):
    response = _process(client, "achievement", "Gracias, conseguí entregar FastAPI con PostgreSQL y Docker.", ["LINKEDIN"])
    assert response.status_code == 202
    assert response.headers["X-Request-ID"] == "trace-achievement"
    asset = response.json()["assets"][0]
    assert asset["channel"] == "LINKEDIN"
    assert client.post(f"/api/v1/assets/{asset['id']}/approve", json={"reviewer": "e2e"}).status_code == 200
    manifest = client.post(f"/api/v1/assets/{asset['id']}/publish")
    assert manifest.status_code == 200
    assert len(manifest.json()["sha256"]) == 64

def test_technical_question_to_approved_faq(client):
    response = _process(client, "faq", "Tengo un problema y necesito saber cómo conectar FastAPI con PostgreSQL en Docker.", ["FAQ"])
    assert response.status_code == 202
    asset = response.json()["assets"][0]
    assert asset["channel"] == "FAQ"
    approved = client.post(f"/api/v1/assets/{asset['id']}/approve", json={"reviewer": "e2e"})
    assert approved.json()["status"] == "APPROVED"

def test_sensitive_content_is_blocked_without_assets(client):
    response = _process(client, "blocked", "Mi correo ana@example.com falla al usar FastAPI con PostgreSQL.", ["FAQ", "LINKEDIN"])
    assert response.status_code == 202
    assert response.json()["opportunities"][0]["status"] == "BLOCKED"
    assert response.json()["assets"] == []

def test_generated_request_id_is_returned(client):
    response = client.get("/api/v1/health")
    assert response.headers["X-Request-ID"]
