"""PostgreSQL-backed asynchronous processing worker."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import sleep

from sqlalchemy import select

from app.api.v1.endpoints.process import _response
from app.db.models.processing_job import ProcessingJob
from app.db.session import SessionLocal
from app.schemas.v1.process import ProcessRequest

logger = logging.getLogger(__name__)


def process_next_job(session_factory=SessionLocal) -> bool:
    """Claim and process one job. Return False when the queue is empty."""
    with session_factory() as db:
        job = db.scalar(
            select(ProcessingJob)
            .where(ProcessingJob.status == "QUEUED")
            .order_by(ProcessingJob.created_at)
            .with_for_update(skip_locked=True)
        )
        if job is None:
            return False
        job.status = "RUNNING"
        job.attempts += 1
        job.started_at = datetime.now(timezone.utc)
        job_id = job.id
        payload_json = job.request_json
        key = job.idempotency_key
        db.commit()

    try:
        with session_factory() as processing_db:
            response = _response(
                ProcessRequest.model_validate(payload_json), key, processing_db
            )
        with session_factory() as result_db:
            job = result_db.get(ProcessingJob, job_id)
            job.status = "SUCCEEDED"
            job.run_id = response.run_id
            job.finished_at = datetime.now(timezone.utc)
            result_db.commit()
    except Exception as exc:  # worker boundary: persist a safe failure state
        logger.exception("Processing job %s failed", job_id)
        with session_factory() as failure_db:
            job = failure_db.get(ProcessingJob, job_id)
            job.status = "FAILED"
            job.error_type = type(exc).__name__[:100]
            job.finished_at = datetime.now(timezone.utc)
            failure_db.commit()
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    while True:
        if not process_next_job():
            sleep(1)


if __name__ == "__main__":
    main()
