from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


FIELD_ALIASES = {
    "author_alias": "author",
    "autor": "author",
    "canal": "channel",
    "interaction_type": "type",
    "tipo": "type",
    "texto": "text",
}

TYPE_ALIASES = {
    "alerta_privacidad": "privacy_alert",
    "conversacion": "message",
    "feedback_mixto": "feedback",
    "feedback_negativo": "problem",
    "feedback_positivo": "feedback",
    "pregunta_tecnica": "question",
    "problema": "problem",
    "proyecto_destacado": "achievement",
    "testimonio": "achievement",
}


class InteractionRequest(BaseModel):
    external_id: str | None = None
    author: str = Field(min_length=1, max_length=200)
    channel: str = Field(min_length=1, max_length=200)
    type: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=10000)
    occurred_at: datetime | None = None
    publication_consent: bool = False
    opt_out: bool = False

    @model_validator(mode="before")
    @classmethod
    def normalize_documented_fields(cls, value: Any) -> Any:
        """Accept the field variants used by the brief and test datasets."""
        if not isinstance(value, dict):
            return value

        normalized = dict(value)
        for alias, canonical in FIELD_ALIASES.items():
            if canonical not in normalized and alias in normalized:
                normalized[canonical] = normalized[alias]

        interaction_type = normalized.get("type")
        if isinstance(interaction_type, str):
            normalized["type"] = TYPE_ALIASES.get(
                interaction_type.strip().lower(),
                interaction_type,
            )

        occurred_at = normalized.get("occurred_at")
        if isinstance(occurred_at, str):
            try:
                normalized["occurred_at"] = datetime.strptime(
                    occurred_at,
                    "%d/%m/%Y %H:%M",
                )
            except ValueError:
                pass

        return normalized
