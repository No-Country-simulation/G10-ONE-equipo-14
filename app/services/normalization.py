import re
import unicodedata
from app.schemas.v1.interaction import InteractionRequest

_WHITESPACE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Normalize Unicode and collapse whitespace without changing meaning."""
    return _WHITESPACE.sub(" ", unicodedata.normalize("NFKC", value).strip())


def normalize_interaction(item: InteractionRequest) -> InteractionRequest:
    return item.model_copy(update={
        "external_id": normalize_text(item.external_id) if item.external_id else None,
        "author": normalize_text(item.author),
        "channel": normalize_text(item.channel),
        "type": normalize_text(item.type),
        "text": normalize_text(item.text),
    })
