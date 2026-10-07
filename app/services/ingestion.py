from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.interaction import Interaction
from app.domain.fingerprint import interaction_fingerprint
from app.schemas.v1.interaction import InteractionRequest
from app.services.normalization import normalize_interaction


@dataclass
class RecordError:
    index: int
    external_id: str | None
    code: str
    message: str


@dataclass
class IngestionResult:
    received: int
    accepted: int = 0
    duplicates: int = 0
    errors: list[RecordError] = field(default_factory=list)
    persisted: list[Interaction] = field(default_factory=list)


def ingest_interactions(
    db: Session,
    organization_id: str,
    community_id: str,
    interactions: list[InteractionRequest],
) -> IngestionResult:
    """Normalize, fingerprint, deduplicate and persist interactions.

    Duplicate protection exists at two levels:
    1. In-memory `seen` prevents duplicates inside the same request.
    2. PostgreSQL lookups + unique constraints prevent duplicates already stored.
    """
    result = IngestionResult(received=len(interactions))
    seen: set[str] = set()

    for index, raw in enumerate(interactions):
        # normalization.py returns a dictionary, so use model_dump first and
        # access the normalized values by key.
        normalized = normalize_interaction(raw.model_dump())

        fingerprint = interaction_fingerprint(
            community_id,
            normalized["author"],
            normalized["channel"],
            normalized["text"],
        )

        if fingerprint in seen:
            result.duplicates += 1
            continue
        seen.add(fingerprint)

        existing = db.scalar(
            select(Interaction.id).where(
                Interaction.organization_id == organization_id,
                Interaction.community_id == community_id,
                Interaction.fingerprint == fingerprint,
            )
        )
        if existing is not None:
            result.duplicates += 1
            continue

        external_id = normalized.get("external_id")
        if external_id:
            external = db.scalar(
                select(Interaction.id).where(
                    Interaction.organization_id == organization_id,
                    Interaction.community_id == community_id,
                    Interaction.external_id == external_id,
                )
            )
            if external is not None:
                result.duplicates += 1
                continue

        try:
            with db.begin_nested():
                interaction = Interaction(
                        organization_id=organization_id,
                        community_id=community_id,
                        external_id=external_id,
                        author=normalized["author"],
                        channel=normalized["channel"],
                        type=normalized["type"],
                        text=normalized["text"],
                        fingerprint=fingerprint,
                        occurred_at=normalized.get("occurred_at"),
                    )
                db.add(interaction)
                db.flush()

            result.accepted += 1
            result.persisted.append(interaction)

        except IntegrityError:
            # The DB unique constraints are the last line of defense against
            # concurrent inserts or duplicate external_id/fingerprint values.
            result.duplicates += 1

        except Exception as exc:
            result.errors.append(
                RecordError(
                    index=index,
                    external_id=external_id,
                    code="persistence_error",
                    message=str(exc),
                )
            )

    db.commit()
    return result
