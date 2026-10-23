from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.security import require_mutation_access
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


@router.post(
    "/alerts/{alert_id}/resolve",
    response_model=Alert,
    dependencies=[Depends(require_mutation_access)],
)
def resolve_alert(alert_id: UUID, db: Session = Depends(get_db)) -> Alert:
    """Resolve an alert; repeated requests keep the same resolved state."""
    alert = db.get(AlertRecord, alert_id)
    if alert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found.")
    if alert.status == "OPEN":
        alert.status = "RESOLVED"
        db.commit()
        db.refresh(alert)
    return Alert.model_validate(alert, from_attributes=True)
