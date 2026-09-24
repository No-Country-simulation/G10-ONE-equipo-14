from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.v1.interaction import InteractionRequest
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.opportunity import Opportunity
from app.schemas.v1.asset import Asset
from app.schemas.v1.approval import Approval
from app.schemas.v1.manifest import Manifest

class RequestedAsset(StrEnum):
    LINKEDIN = "LINKEDIN"
    FAQ = "FAQ"

class ProcessRequest(BaseModel):
    schema_version: str = "v1"
    organization_id: str = Field(min_length=1)
    community_id: str = Field(min_length=1)
    reference_period: str = Field(min_length=1)
    requested_assets: list[RequestedAsset] = Field(min_length=1)
    interactions: list[InteractionRequest] = Field(min_length=1, max_length=500)

class RunSummary(BaseModel):
    received: int = Field(ge=0)
    accepted: int = Field(ge=0)
    duplicates: int = Field(ge=0)
    errors: int = Field(ge=0)

class ProcessResponse(BaseModel):
    schema_version: str = "v1"
    run_id: UUID
    status: str
    summary: RunSummary
    analyses: list[Analysis] = Field(default_factory=list)
    opportunities: list[Opportunity] = Field(default_factory=list)
    assets: list[Asset] = Field(default_factory=list)
    approvals: list[Approval] = Field(default_factory=list)
    manifest: Manifest | None = None
