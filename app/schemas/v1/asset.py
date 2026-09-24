from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field

class AssetStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class AssetChannel(StrEnum):
    LINKEDIN = "LINKEDIN"
    FAQ = "FAQ"

class Asset(BaseModel):
    schema_version: str = "v1"
    id: UUID
    opportunity_id: UUID
    channel: AssetChannel
    title: str
    body: str
    status: AssetStatus
    version: int = Field(ge=1)
