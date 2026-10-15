import re

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
REDACTED_EMAIL = "[EMAIL]"
REDACTED_PHONE = "[PHONE]"
REDACTED_PERSON = "[PERSON]"

def contains_pii(text: str) -> bool:
    """Deterministic backend PII check for basic email/phone signals."""
    if not text:
        return False
    return bool(EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text))


def redact_pii(text: str, author: str | None = None, redact_author: bool = False) -> str:
    """Remove deterministic PII before persistence and model processing."""
    redacted = EMAIL_PATTERN.sub(REDACTED_EMAIL, text)
    redacted = PHONE_PATTERN.sub(REDACTED_PHONE, redacted)
    if redact_author and author and author.strip():
        redacted = re.sub(re.escape(author.strip()), REDACTED_PERSON, redacted, flags=re.IGNORECASE)
    return redacted
