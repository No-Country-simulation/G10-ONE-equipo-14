from app.services.normalization import normalize_text

def test_normalize_text_collapses_whitespace():
    assert normalize_text("  Hola   mundo\n") == "Hola mundo"
