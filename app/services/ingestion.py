from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.interaction import Interaction
from app.domain.fingerprint import interaction_fingerprint
from app.schemas.v1.interaction import InteractionRequest
from app.services.normalization import normalize_interaction
from app.services.pii_detection import contains_pii, redact_pii


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
    reprocessed: int = 0
    errors: list[RecordError] = field(default_factory=list)
    # New and already stored interactions to analyze for this run.
    interactions_to_process: list[Interaction] = field(default_factory=list)


def ingest_interactions(
    db: Session,
    organization_id: str,
    community_id: str,
    interactions: list[InteractionRequest],
) -> IngestionResult:
    """Persist new interactions and return existing ones for fresh analysis.

    Exact duplicates already stored remain a single database row, but are
    included in this run's analysis so a new upload always invokes the provider.
    Repeated copies within the same upload are only processed once.
    """
    result = IngestionResult(received=len(interactions))
    seen: set[str] = set()

    for index, raw in enumerate(interactions):
        # normalization.py returns a dictionary, so use model_dump first and
        # access the normalized values by key.
        normalized = normalize_interaction(raw.model_dump())
        consent = bool(normalized.get("publication_consent", False))
        opt_out = bool(normalized.get("opt_out", False))
        original_author = normalized["author"]
        pii_detected = contains_pii(normalized["text"])
        # Always omit the author's identity from text used for analysis/content.
        normalized["text"] = redact_pii(
            normalized["text"], original_author, redact_author=True
        )

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
            select(Interaction).where(
                Interaction.organization_id == organization_id,
                Interaction.community_id == community_id,
                Interaction.fingerprint == fingerprint,
            )
        )
        if existing is not None:
            result.duplicates += 1
            result.reprocessed += 1
            result.interactions_to_process.append(existing)
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
                    publication_consent=consent,
                    opt_out=opt_out,
                    pii_detected=pii_detected,
                )
                db.add(interaction)
                db.flush()

            result.accepted += 1
            result.interactions_to_process.append(interaction)

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

    return result
