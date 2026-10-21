from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.security import require_private_access
from app.db.models.run import Run
from app.db.session import get_db
from app.schemas.v1.process import ProcessResponse
from app.schemas.v1.run import RunListItem

router = APIRouter()


def _optional_metadata(run: Run, key: str) -> str | None:
    value = (run.response_json or {}).get(key)
    return str(value).strip() if value else None


def _display_label(run: Run, source_name: str | None) -> str:
    safe_name = Path((source_name or "").replace("\\", "/")).name
    stem = Path(safe_name).stem.strip() if safe_name else ""
    prefix = stem or run.community_id
    return f"{prefix[:80]}-{run.created_at:%d%m%Y}-{run.id}"


def _to_list_item(run: Run) -> RunListItem:
    source_name = _optional_metadata(run, "source_name")
    return RunListItem(
        run_id=run.id,
        organization_id=run.organization_id,
        community_id=run.community_id,
        reference_period=_optional_metadata(run, "reference_period"),
        source_name=source_name,
        status=run.status,
        created_at=run.created_at,
        display_label=_display_label(run, source_name),
    )


@router.get(
    "/runs",
    response_model=list[RunListItem],
    dependencies=[Depends(require_private_access)],
)
def list_runs(
    organization_id: str | None = Query(default=None, min_length=1, max_length=100),
    community_id: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RunListItem]:
    """List recent completed executions without exposing their result payloads."""
    statement = select(Run).where(Run.response_json.is_not(None))
    if organization_id:
        statement = statement.where(Run.organization_id == organization_id)
    if community_id:
        statement = statement.where(Run.community_id == community_id)
    runs = db.scalars(statement.order_by(Run.created_at.desc()).limit(limit)).all()

    return [_to_list_item(run) for run in runs]


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
