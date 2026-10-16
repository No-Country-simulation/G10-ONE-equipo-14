from app.schemas.v1.process import ProcessRequest


def test_process_schema_v1():
    r = ProcessRequest(
        organization_id="one",
        community_id="g10",
        reference_period="2026-W38",
        requested_assets=["LINKEDIN"],
        interactions=[
            {
                "author": "Ana",
                "channel": "general",
                "type": "testimonio",
                "text": "Un logro",
            }
        ],
    )
    assert r.schema_version == "v1"
    assert r.interactions[0].type == "achievement"


def test_process_schema_accepts_test_set_field_names():
    request = ProcessRequest(
        organization_id="one",
        community_id="g10",
        reference_period="2026-W40",
        requested_assets=["FAQ"],
        interactions=[
            {
                "author_alias": "miembro_01",
                "channel": "dudas",
                "interaction_type": "pregunta_tecnica",
                "text": "¿Cómo funciona?",
            }
        ],
    )

    assert request.interactions[0].author == "miembro_01"
    assert request.interactions[0].type == "question"


def test_process_schema_accepts_spanish_brief_field_names():
    request = ProcessRequest(
        organization_id="one",
        community_id="g10",
        reference_period="2026-W40",
        requested_assets=["LINKEDIN"],
        interactions=[
            {
                "autor": "Mariana",
                "canal": "logros",
                "tipo": "testimonio",
                "texto": "Conseguí mi primer empleo.",
            }
        ],
    )

    assert request.interactions[0].author == "Mariana"
    assert request.interactions[0].channel == "logros"
    assert request.interactions[0].type == "achievement"
    assert request.interactions[0].text == "Conseguí mi primer empleo."
