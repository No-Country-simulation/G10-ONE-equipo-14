from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProcessingJobResponse(BaseModel):
    schema_version: str = "v1"
    job_id: UUID
    status: str
    status_url: str
    run_id: UUID | None = None
    attempts: int = 0
    error_type: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
