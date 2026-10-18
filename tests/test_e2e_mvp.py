"""COMLAB-62 — Three required MVP journeys across API, DB, AI and storage.

Acceptance criteria from the roadmap:
- achievement -> LinkedIn (approved and published)
- technical question -> FAQ (approved)
- sensitive content -> blocked (no assets generated)
"""


def _process(client, key, text, assets, interaction_type="message"):
    texts = text if isinstance(text, list) else [text]
    return client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": key, "X-Request-ID": f"trace-{key}"},
        json={
            "organization_id": "e2e-org",
            "community_id": "e2e-community",
            "reference_period": "2026-W41",
            "requested_assets": assets,
            "interactions": [
                {
                    "author": "Ana",
                    "channel": "community",
                    "type": interaction_type,
                    "text": item,
                }
                for item in texts
            ],
        },
    )


# ---------------------------------------------------------------------------
# Recorrido 1: Logro -> LinkedIn aprobado y publicado
# ---------------------------------------------------------------------------

def test_achievement_to_approved_and_published_linkedin(client):
    response = _process(
        client,
        "achievement",
        "Gracias, conseguí entregar FastAPI con PostgreSQL y Docker.",
        ["LINKEDIN"],
    )

    # Contrato del endpoint.
    assert response.status_code == 202
    assert response.headers["X-Request-ID"] == "trace-achievement"
    body = response.json()
    assert body["schema_version"] == "v1"
    assert body["summary"]["accepted"] == 1
    assert body["summary"]["errors"] == 0

    # Debe generarse al menos un activo LinkedIn.
    assert body["assets"], "Expected at least one generated asset"
    asset = body["assets"][0]
    assert asset["channel"] == "LINKEDIN"
    assert asset["status"] == "PENDING_REVIEW"

    # La oportunidad debe tener evidencia vinculada.
    assert body["opportunities"], "Expected at least one opportunity"
    opportunity = body["opportunities"][0]
    assert opportunity["source_ids"]

    # Aprobar y publicar.
    approved = client.post(
        f"/api/v1/assets/{asset['id']}/approve",
        json={"reviewer": "e2e"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"

    manifest = client.post(f"/api/v1/assets/{asset['id']}/publish")
    assert manifest.status_code == 200
    manifest_body = manifest.json()
    assert len(manifest_body["sha256"]) == 64
    # El manifest debe declarar un object_key.
    assert manifest_body["object_key"]
    assert manifest_body["bucket"]


# ---------------------------------------------------------------------------
# Recorrido 2: Duda técnica -> FAQ aprobada
# ---------------------------------------------------------------------------

def test_technical_question_to_approved_faq(client):
    response = _process(
        client,
        "faq",
        [
            "¿Cómo conecto FastAPI con PostgreSQL usando Docker?",
            "¿Cómo puedo configurar FastAPI y PostgreSQL dentro de Docker?",
        ],
        ["FAQ"],
        interaction_type="question",
    )

    assert response.status_code == 202
    body = response.json()

    # Debe generarse un activo FAQ.
    assert body["assets"], "Expected at least one generated asset"
    asset = body["assets"][0]
    assert asset["channel"] == "FAQ"
    assert asset["status"] == "PENDING_REVIEW"

    # La FAQ debe estar formulada como pregunta.
    assert asset["title"].strip().endswith("?")

    approved = client.post(
        f"/api/v1/assets/{asset['id']}/approve",
        json={"reviewer": "e2e"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"


# ---------------------------------------------------------------------------
# Recorrido 3: Contenido sensible -> bloqueado sin activos
# ---------------------------------------------------------------------------

def test_sensitive_content_is_blocked_without_assets(client):
    response = _process(
        client,
        "blocked",
        "Mi correo ana@example.com falla al usar FastAPI con PostgreSQL.",
        ["FAQ", "LINKEDIN"],
    )

    assert response.status_code == 202
    body = response.json()

    # La oportunidad debe quedar BLOCKED.
    assert body["opportunities"], "Expected at least one opportunity"
    assert body["opportunities"][0]["status"] == "BLOCKED"

    # No debe generarse ningún activo.
    assert body["assets"] == []


def test_generated_request_id_is_returned(client):
    response = client.get("/api/v1/health")
    assert response.headers["X-Request-ID"]
