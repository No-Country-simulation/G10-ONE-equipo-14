from app.services.csv_ingestion import parse_interactions_csv


def test_parse_valid_csv():
    content = b"external_id,author,channel,type,text,occurred_at\n1,Ana,general,comment,Hello,2026-09-18T12:00:00Z\n"
    items, errors = parse_interactions_csv(content)
    assert len(items) == 1
    assert errors == []


def test_csv_reports_invalid_record():
    content = (
        b"external_id,author,channel,type,text,occurred_at\n1,,general,comment,Hello,\n"
    )
    items, errors = parse_interactions_csv(content)
    assert items == []
    assert len(errors) == 1


def test_csv_accepts_test_set_headers_and_normalizes_type():
    content = (
        "external_id,author_alias,channel,interaction_type,text,occurred_at\n"
        "1,Ana,dudas,pregunta_tecnica,¿Cómo funciona?,2026-09-18T12:00:00Z\n"
    ).encode("utf-8")

    items, errors = parse_interactions_csv(content)

    assert errors == []
    assert items[0].author == "Ana"
    assert items[0].type == "question"


def test_csv_accepts_cp1252_content():
    content = (
        "external_id,author_alias,channel,interaction_type,text,occurred_at\n"
        "1,Ana,logros,testimonio,Conseguí mi primer empleo,18/09/2026 12:00\n"
    ).encode("cp1252")

    items, errors = parse_interactions_csv(content)

    assert errors == []
    assert items[0].text == "Conseguí mi primer empleo"
    assert items[0].type == "achievement"
