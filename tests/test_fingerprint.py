from app.domain.fingerprint import interaction_fingerprint


def test_fingerprint_is_deterministic():
    a = interaction_fingerprint("g10", "Ana", "general", "Hola")
    b = interaction_fingerprint("g10", " Ana ", "GENERAL", " hola ")
    assert a == b
    assert len(a) == 64
