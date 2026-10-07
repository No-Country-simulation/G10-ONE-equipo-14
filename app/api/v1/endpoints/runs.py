from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.run import Run
from app.db.session import get_db
from app.schemas.v1.process import ProcessResponse

router = APIRouter()


@router.get("/runs/{run_id}", response_model=ProcessResponse)
def get_run(run_id: UUID, db: Session = Depends(get_db)) -> ProcessResponse:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found.",
        )

    if run.response_json is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Run is still being processed.",
        )

    return ProcessResponse.model_validate(run.response_json)
