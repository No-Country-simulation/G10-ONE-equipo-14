"""Persistence helpers for Idempotency-Key handling."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.run import Run
from app.schemas.v1.process import ProcessRequest


class IdempotencyConflictError(Exception):
    """The same Idempotency-Key was reused with a different request body."""


@dataclass
class IdempotencyResult:
    run: Run
    replay: bool


def request_hash(payload: ProcessRequest) -> str:
    """Create a stable SHA-256 hash for the complete validated request."""
    canonical = json.dumps(
        payload.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _find_run(
    db: Session,
    organization_id: str,
    community_id: str,
    idempotency_key: str,
) -> Run | None:
    return db.scalar(
        select(Run).where(
            Run.organization_id == organization_id,
            Run.community_id == community_id,
            Run.idempotency_key == idempotency_key,
        )
    )


def get_or_create_run(
    db: Session,
    payload: ProcessRequest,
    idempotency_key: str,
) -> IdempotencyResult:
    """Return the existing run or persist exactly one new run.

    Reusing a key with a different payload is rejected. The database unique
    constraint is the final protection against concurrent duplicate requests.
    """
    key = idempotency_key.strip()
    if not key:
        raise ValueError("Idempotency-Key cannot be empty")

    payload_hash = request_hash(payload)

    existing = _find_run(
        db,
        payload.organization_id,
        payload.community_id,
        key,
    )
    if existing is not None:
        if existing.request_hash != payload_hash:
            raise IdempotencyConflictError(
                "Idempotency-Key was already used with a different request."
            )
        return IdempotencyResult(run=existing, replay=True)

    run = Run(
        organization_id=payload.organization_id,
        community_id=payload.community_id,
        idempotency_key=key,
        request_hash=payload_hash,
        status="PROCESSING",
    )
    db.add(run)

    try:
        db.commit()
        db.refresh(run)
        return IdempotencyResult(run=run, replay=False)
    except IntegrityError:
        # Another request may have inserted the same key concurrently.
        db.rollback()
        existing = _find_run(
            db,
            payload.organization_id,
            payload.community_id,
            key,
        )
        if existing is None:
            raise

        if existing.request_hash != payload_hash:
            raise IdempotencyConflictError(
                "Idempotency-Key was already used with a different request."
            )

        return IdempotencyResult(run=existing, replay=True)


def save_run_response(
    db: Session,
    run: Run,
    response_json: dict,
    status: str,
) -> None:
    """Persist the final response so a replay can return the original result."""
    run.response_json = response_json
    run.status = status
    db.add(run)
    db.commit()
    db.refresh(run)


def mark_run_failed(db: Session, run: Run) -> None:
    run.status = "FAILED"
    db.add(run)
    db.commit()
