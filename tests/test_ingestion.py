from app.domain.fingerprint import interaction_fingerprint
from app.services.normalization import normalize_text

def test_fingerprint_is_stable_after_normalization():
    a = interaction_fingerprint("g10", "Ana", "general", normalize_text("Hola   mundo"))
    b = interaction_fingerprint("g10", "Ana", "general", normalize_text("Hola mundo"))
    assert a == b
