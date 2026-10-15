from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.security import require_mutation_access
from app.db.models.processing_job import ProcessingJob
from app.db.session import get_db
from app.schemas.v1.job import ProcessingJobResponse
from app.schemas.v1.process import ProcessRequest
from app.services.idempotency import IdempotencyConflictError
from app.services.processing_queue import enqueue_job

router = APIRouter()


def _job_response(job: ProcessingJob) -> ProcessingJobResponse:
    return ProcessingJobResponse(
        job_id=job.id,
        status=job.status,
        status_url=f"/api/v1/jobs/{job.id}",
        run_id=job.run_id,
        attempts=job.attempts,
        error_type=job.error_type,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )


@router.post(
    "/process/async",
    response_model=ProcessingJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_mutation_access)],
)
def process_async(
    payload: ProcessRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
) -> ProcessingJobResponse:
    try:
        return _job_response(enqueue_job(db, payload, idempotency_key).job)
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> ProcessingJobResponse:
    job = db.get(ProcessingJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return _job_response(job)
