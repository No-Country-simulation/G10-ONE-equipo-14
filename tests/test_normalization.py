"""Tests for deterministic cleaning, normalization and alias mapping."""

from app.services.normalization import (
    normalize_channel,
    normalize_interaction,
    normalize_text,
    normalize_type,
)


def test_normalize_text_collapses_whitespace():
    assert normalize_text("  Hola   mundo\n") == "Hola mundo"


def test_normalize_text_is_reproducible():
    value = "  Hola   mundo\n"

    first = normalize_text(value)
    second = normalize_text(value)

    assert first == second == "Hola mundo"


def test_channel_aliases_map_to_canonical_value():
    assert normalize_channel("Discord") == "discord"
    assert normalize_channel("DISCORD") == "discord"
    assert normalize_channel("discord_app") == "discord"
    assert normalize_channel(" Slack ") == "slack"
    assert normalize_channel("slack_app") == "slack"


def test_type_aliases_map_to_canonical_value():
    assert normalize_type("Pregunta") == "question"
    assert normalize_type("question_post") == "question"
    assert normalize_type("Duda") == "question"
    assert normalize_type("Logro") == "achievement"
    assert normalize_type("success") == "achievement"
    assert normalize_type("Testimonio") == "testimonial"


def test_unknown_alias_is_normalized_without_data_loss():
    assert normalize_channel("  FORUM  ") == "forum"
    assert normalize_type("  Announcement  ") == "announcement"


def test_normalize_interaction_applies_cleaning_and_aliases():
    raw = {
        "external_id": "  msg-001  ",
        "author": "  Ana   Pérez ",
        "channel": " DISCORD_APP ",
        "type": " Pregunta ",
        "text": "  ¿Cómo   funciona?\n",
    }

    normalized = normalize_interaction(raw)

    assert normalized == {
        "external_id": "msg-001",
        "author": "Ana Pérez",
        "channel": "discord",
        "type": "question",
        "text": "¿Cómo funciona?",
    }


def test_normalize_interaction_does_not_mutate_input():
    raw = {
        "external_id": "msg-001",
        "author": "Ana",
        "channel": "Discord",
        "type": "Pregunta",
        "text": "Hola",
    }

    original = dict(raw)

    normalize_interaction(raw)

    assert raw == original
