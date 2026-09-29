"""Tests for CommunityLab interaction ingestion.

Covers the Week 2 backend acceptance cases:
- valid interactions
- duplicate interactions in the same batch
- duplicate interactions already persisted
- normalization before persistence
- database persistence

Invalid request/schema validation is tested through the API/Pydantic layer,
because ingest_interactions receives already validated InteractionRequest
objects.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select

from app.db.models.interaction import Interaction
from app.schemas.v1.interaction import InteractionRequest
from app.services.ingestion import ingest_interactions


def make_interaction(
    *,
    external_id: str = "msg-001",
    author: str = "Ana",
    channel: str = "Discord",
    type_: str = "Pregunta",
    text: str = "¿Cómo funciona CommunityLab?",
) -> InteractionRequest:
    """Create a valid InteractionRequest for ingestion tests."""
    return InteractionRequest(
        external_id=external_id,
        author=author,
        channel=channel,
        type=type_,
        text=text,
        occurred_at=datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )


def interaction_count(db_session) -> int:
    """Return the number of persisted interactions."""
    return db_session.scalar(
        select(func.count()).select_from(Interaction)
    )


def test_valid_interaction_is_persisted(db_session):
    """A valid interaction must be accepted and stored once."""
    interaction = make_interaction()

    result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-demo",
        interactions=[interaction],
    )

    assert result.received == 1
    assert result.accepted == 1
    assert result.duplicates == 0
    assert result.errors == []

    assert interaction_count(db_session) == 1

    stored = db_session.scalar(select(Interaction))

    assert stored is not None
    assert stored.organization_id == "org-demo"
    assert stored.community_id == "community-demo"
    assert stored.external_id == "msg-001"


def test_interaction_is_normalized_before_persistence(db_session):
    """Aliases and whitespace must be normalized before storage."""
    interaction = make_interaction(
        external_id="  msg-002  ",
        author="  Ana   Pérez  ",
        channel=" DISCORD_APP ",
        type_=" Pregunta ",
        text="  ¿Cómo   funciona?\n",
    )

    result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-demo",
        interactions=[interaction],
    )

    assert result.accepted == 1
    assert result.duplicates == 0
    assert result.errors == []

    stored = db_session.scalar(select(Interaction))

    assert stored is not None
    assert stored.external_id == "msg-002"
    assert stored.author == "Ana Pérez"
    assert stored.channel == "discord"
    assert stored.type == "question"
    assert stored.text == "¿Cómo funciona?"


def test_duplicate_in_same_batch_is_not_persisted_twice(
    db_session,
):
    """Two equivalent interactions in one batch create one row."""
    first = make_interaction(
        external_id="msg-003",
        text="Necesito ayuda con Docker.",
    )

    second = make_interaction(
        external_id="msg-004",
        text="Necesito ayuda con Docker.",
    )

    result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-demo",
        interactions=[first, second],
    )

    assert result.received == 2
    assert result.accepted == 1
    assert result.duplicates == 1
    assert result.errors == []

    assert interaction_count(db_session) == 1


def test_existing_duplicate_is_not_persisted_again(
    db_session,
):
    """An interaction already stored must not create another row."""
    interaction = make_interaction(
        external_id="msg-005",
        text="¿Cómo configuro PostgreSQL?",
    )

    first_result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-demo",
        interactions=[interaction],
    )

    assert first_result.accepted == 1
    assert first_result.duplicates == 0
    assert interaction_count(db_session) == 1

    second_result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-demo",
        interactions=[interaction],
    )

    assert second_result.received == 1
    assert second_result.accepted == 0
    assert second_result.duplicates == 1
    assert second_result.errors == []

    assert interaction_count(db_session) == 1


def test_duplicate_external_id_is_not_persisted_again(
    db_session,
):
    """The same external_id in a community must not create two rows."""
    first = make_interaction(
        external_id="msg-006",
        text="Primer contenido.",
    )

    second = make_interaction(
        external_id="msg-006",
        text="Contenido diferente pero mismo external_id.",
    )

    first_result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-demo",
        interactions=[first],
    )

    second_result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-demo",
        interactions=[second],
    )

    assert first_result.accepted == 1

    assert second_result.accepted == 0
    assert second_result.duplicates == 1
    assert second_result.errors == []

    assert interaction_count(db_session) == 1


def test_same_interaction_can_exist_in_different_communities(
    db_session,
):
    """Fingerprint deduplication must be scoped by community."""
    interaction = make_interaction(
        external_id="msg-007",
        text="Pregunta compartida.",
    )

    first_result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-a",
        interactions=[interaction],
    )

    second_result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-b",
        interactions=[interaction],
    )

    assert first_result.accepted == 1
    assert second_result.accepted == 1

    assert interaction_count(db_session) == 2


def test_empty_batch_is_valid(db_session):
    """An empty validated batch must not create interactions."""
    result = ingest_interactions(
        db=db_session,
        organization_id="org-demo",
        community_id="community-demo",
        interactions=[],
    )

    assert result.received == 0
    assert result.accepted == 0
    assert result.duplicates == 0
    assert result.errors == []

    assert interaction_count(db_session) == 0
