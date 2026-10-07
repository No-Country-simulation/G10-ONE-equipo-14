import re

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")

def contains_pii(text: str) -> bool:
    """Deterministic backend PII check for basic email/phone signals."""
    if not text:
        return False
    return bool(EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text))
