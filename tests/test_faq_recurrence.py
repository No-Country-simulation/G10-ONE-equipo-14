def _payload(interactions):
    return {
        "organization_id": "faq-org",
        "community_id": "faq-community",
        "reference_period": "2026-W41",
        "requested_assets": ["FAQ"],
        "interactions": interactions,
    }


def _question(external_id, text):
    return {
        "external_id": external_id,
        "author": "Miembro",
        "channel": "community",
        "type": "question",
        "text": text,
    }


def test_isolated_question_does_not_generate_faq(client):
    response = client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": "faq-isolated"},
        json=_payload([_question("q1", "¿Cómo conecto FastAPI con PostgreSQL?")]),
    )
    assert response.status_code == 202
    assert response.json()["assets"] == []


def test_recurring_questions_generate_one_faq_with_all_sources(client):
    response = client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": "faq-recurring"},
        json=_payload([
            _question("q1", "¿Cómo conecto FastAPI con PostgreSQL usando Docker?"),
            _question("q2", "¿Cómo configuro FastAPI y PostgreSQL dentro de Docker?"),
            _question("q3", "¿Cómo ejecuto FastAPI con PostgreSQL en Docker Compose?"),
        ]),
    )
    assert response.status_code == 202
    assets = response.json()["assets"]
    assert len(assets) == 1
    assert assets[0]["channel"] == "FAQ"
    assert len(assets[0]["source_interaction_ids"]) == 3
    assert len(assets[0]["evidence"]) == 3


def test_non_question_interactions_never_count_toward_faq(client):
    interactions = [
        {**_question("q1", "¿Cómo conecto FastAPI con PostgreSQL?"), "type": "achievement"},
        {**_question("q2", "¿Cómo configuro FastAPI con PostgreSQL?"), "type": "achievement"},
    ]
    response = client.post(
        "/api/v1/process",
        headers={"Idempotency-Key": "faq-not-questions"},
        json=_payload(interactions),
    )
    assert response.status_code == 202
    assert response.json()["assets"] == []
