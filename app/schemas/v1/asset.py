from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.v1.analysis import Evidence

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
    source_interaction_ids: list[UUID] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)

class AssetEditRequest(BaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    editor: str = Field(min_length=1)

class AssetDecisionRequest(BaseModel):
    reviewer: str = Field(min_length=1)
    comment: str | None = None
