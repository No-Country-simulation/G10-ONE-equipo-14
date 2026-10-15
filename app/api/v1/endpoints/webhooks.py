from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.security import require_mutation_access
from app.api.v1.endpoints.process import _response
from app.db.session import get_db
from app.schemas.v1.process import ProcessRequest, ProcessResponse
from app.schemas.v1.webhook import WebhookInteractionEvent

router = APIRouter(dependencies=[Depends(require_mutation_access)])


@router.post(
    "/webhooks/interactions",
    response_model=ProcessResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def process_webhook(
    event: WebhookInteractionEvent,
    db: Session = Depends(get_db),
) -> ProcessResponse:
    """Normalize one provider event and run the existing idempotent pipeline."""
    external_id = event.interaction.external_id or f"{event.source}:{event.event_id}"
    interaction = event.interaction.model_copy(update={"external_id": external_id})
    payload = ProcessRequest(
        schema_version=event.schema_version,
        organization_id=event.organization_id,
        community_id=event.community_id,
        reference_period=event.reference_period,
        requested_assets=event.requested_assets,
        interactions=[interaction],
    )
    return _response(
        payload=payload,
        idempotency_key=f"webhook:{event.source}:{event.event_id}",
        db=db,
    )
