import hashlib


def interaction_fingerprint(
    community_id: str,
    author: str,
    channel: str,
    text: str,
) -> str:
    normalized = "|".join(
        value.strip().lower()
        for value in (community_id, author, channel, text)
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
