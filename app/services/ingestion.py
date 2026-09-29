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


def ingest_interactions(
    db: Session,
    organization_id: str,
    community_id: str,
    interactions: list[InteractionRequest],
) -> IngestionResult:
    result = IngestionResult(received=len(interactions))
    seen: set[str] = set()

    for index, raw in enumerate(interactions):
        item = normalize_interaction(raw)
        fingerprint = interaction_fingerprint(community_id, item.author, item.channel, item.text)

        if fingerprint in seen:
            result.duplicates += 1
            continue
        seen.add(fingerprint)

        existing = db.scalar(select(Interaction.id).where(
            Interaction.organization_id == organization_id,
            Interaction.community_id == community_id,
            Interaction.fingerprint == fingerprint,
        ))
        if existing is not None:
            result.duplicates += 1
            continue

        if item.external_id:
            external = db.scalar(select(Interaction.id).where(
                Interaction.organization_id == organization_id,
                Interaction.community_id == community_id,
                Interaction.external_id == item.external_id,
            ))
            if external is not None:
                result.duplicates += 1
                continue

        try:
            with db.begin_nested():
                db.add(Interaction(
                    organization_id=organization_id,
                    community_id=community_id,
                    external_id=item.external_id,
                    author=item.author,
                    channel=item.channel,
                    type=item.type,
                    text=item.text,
                    fingerprint=fingerprint,
                    occurred_at=item.occurred_at,
                ))
                db.flush()
            result.accepted += 1
        except IntegrityError:
            result.duplicates += 1
        except Exception as exc:
            result.errors.append(RecordError(
                index=index,
                external_id=item.external_id,
                code="persistence_error",
                message=str(exc),
            ))

    db.commit()
    return result
