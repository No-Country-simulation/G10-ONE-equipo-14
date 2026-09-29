"""Deterministic normalization and alias mapping for CommunityLab interactions."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

_WHITESPACE = re.compile(r"\s+")

# Canonical values used internally by CommunityLab.
# Keys are normalized to lowercase before lookup.
CHANNEL_ALIASES = {
    "discord": "discord",
    "discord_app": "discord",
    "discord app": "discord",
    "slack": "slack",
    "slack_app": "slack",
    "slack app": "slack",
    "linkedin": "linkedin",
    "linked_in": "linkedin",
    "linked in": "linkedin",
    "community": "community",
    "comunidad": "community",
}

TYPE_ALIASES = {
    "question": "question",
    "pregunta": "question",
    "question_post": "question",
    "doubt": "question",
    "duda": "question",
    "achievement": "achievement",
    "logro": "achievement",
    "success": "achievement",
    "testimonial": "testimonial",
    "testimonio": "testimonial",
    "feedback": "feedback",
    "comentario": "feedback",
    "comment": "feedback",
    "neutral": "neutral",
    "negative": "negative",
    "negativo": "negative",
}


def normalize_text(value: str) -> str:
    """Normalize Unicode, trim boundaries and collapse whitespace."""
    return _WHITESPACE.sub(
        " ",
        unicodedata.normalize("NFKC", value).strip()
    )


def normalize_alias(value: str, aliases: dict[str, str]) -> str:
    """Return the canonical alias, preserving unknown values in normalized lowercase form."""
    normalized = normalize_text(value).lower()
    return aliases.get(normalized, normalized)


def normalize_channel(value: str) -> str:
    return normalize_alias(value, CHANNEL_ALIASES)


def normalize_type(value: str) -> str:
    return normalize_alias(value, TYPE_ALIASES)


def _optional_text(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, str):
        normalized = normalize_text(value)
        return normalized or None

    return value


def normalize_interaction(raw: dict[str, Any]) -> dict[str, Any]:
    """Return a new, deterministically normalized interaction dictionary.

    The input dictionary is not mutated. This makes the transformation
    reproducible and safe to run before fingerprint generation.
    """
    item = dict(raw)

    if isinstance(item.get("external_id"), str):
        item["external_id"] = _optional_text(item["external_id"])

    if isinstance(item.get("author"), str):
        item["author"] = normalize_text(item["author"])

    if isinstance(item.get("channel"), str):
        item["channel"] = normalize_channel(item["channel"])

    if isinstance(item.get("type"), str):
        item["type"] = normalize_type(item["type"])

    if isinstance(item.get("text"), str):
        item["text"] = normalize_text(item["text"])

    return item
