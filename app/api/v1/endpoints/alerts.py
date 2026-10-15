from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.alert import AlertRecord
from app.db.session import get_db
from app.schemas.v1.alert import Alert

router = APIRouter()


@router.get("/alerts", response_model=list[Alert])
def list_alerts(
    status_filter: str | None = Query(default="OPEN", alias="status"),
    db: Session = Depends(get_db),
) -> list[AlertRecord]:
    statement = select(AlertRecord).order_by(AlertRecord.created_at.desc())
    if status_filter:
        statement = statement.where(AlertRecord.status == status_filter.upper())
    return list(db.scalars(statement).all())
