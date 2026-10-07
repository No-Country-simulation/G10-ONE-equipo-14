from app.services.pii_detection import contains_pii

def test_detects_email():
    assert contains_pii("Contacto: ana@example.com")

def test_detects_phone():
    assert contains_pii("Teléfono +52 668 123 4567")

def test_normal_text_has_no_pii():
    assert not contains_pii("Duda sobre FastAPI y PostgreSQL.")

def test_empty_text_has_no_pii():
    assert not contains_pii("")
