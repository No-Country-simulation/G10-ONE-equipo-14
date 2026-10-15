from pydantic import BaseModel, Field

from app.schemas.v1.interaction import InteractionRequest
from app.schemas.v1.process import RequestedAsset


class WebhookInteractionEvent(BaseModel):
    """Provider-neutral event accepted from automation and chat connectors."""

    schema_version: str = "v1"
    source: str = Field(min_length=1, max_length=50, pattern=r"^[a-z0-9_-]+$")
    event_id: str = Field(min_length=1, max_length=255)
    organization_id: str = Field(min_length=1, max_length=100)
    community_id: str = Field(min_length=1, max_length=100)
    reference_period: str = Field(min_length=1, max_length=100)
    requested_assets: list[RequestedAsset] = Field(
        default_factory=lambda: [RequestedAsset.LINKEDIN, RequestedAsset.FAQ],
        min_length=1,
    )
    interaction: InteractionRequest
