"""Transactional enqueue and claim operations for the PostgreSQL job queue."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.processing_job import ProcessingJob
from app.schemas.v1.process import ProcessRequest
from app.services.idempotency import IdempotencyConflictError, request_hash


@dataclass
class EnqueueResult:
    job: ProcessingJob
    replay: bool


def _find_job(db: Session, payload: ProcessRequest, key: str) -> ProcessingJob | None:
    return db.scalar(
        select(ProcessingJob).where(
            ProcessingJob.organization_id == payload.organization_id,
            ProcessingJob.community_id == payload.community_id,
            ProcessingJob.idempotency_key == key,
        )
    )


def enqueue_job(
    db: Session, payload: ProcessRequest, idempotency_key: str
) -> EnqueueResult:
    key = idempotency_key.strip()
    if not key:
        raise ValueError("Idempotency-Key cannot be empty")
    payload_hash = request_hash(payload)
    existing = _find_job(db, payload, key)
    if existing is not None:
        if existing.request_hash != payload_hash:
            raise IdempotencyConflictError(
                "Idempotency-Key was already used with a different request."
            )
        return EnqueueResult(existing, True)

    job = ProcessingJob(
        organization_id=payload.organization_id,
        community_id=payload.community_id,
        idempotency_key=key,
        request_hash=payload_hash,
        request_json=payload.model_dump(mode="json"),
    )
    db.add(job)
    try:
        db.commit()
        db.refresh(job)
        return EnqueueResult(job, False)
    except IntegrityError:
        db.rollback()
        existing = _find_job(db, payload, key)
        if existing is None:
            raise
        if existing.request_hash != payload_hash:
            raise IdempotencyConflictError(
                "Idempotency-Key was already used with a different request."
            )
        return EnqueueResult(existing, True)
