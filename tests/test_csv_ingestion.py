from app.services.csv_ingestion import parse_interactions_csv

def test_parse_valid_csv():
    content = b"external_id,author,channel,type,text,occurred_at\n1,Ana,general,comment,Hello,2026-09-18T12:00:00Z\n"
    items, errors = parse_interactions_csv(content)
    assert len(items) == 1
    assert errors == []

def test_csv_reports_invalid_record():
    content = b"external_id,author,channel,type,text,occurred_at\n1,,general,comment,Hello,\n"
    items, errors = parse_interactions_csv(content)
    assert items == []
    assert len(errors) == 1
