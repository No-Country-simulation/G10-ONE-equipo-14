from datetime import datetime
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel

class ApprovalDecision(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Approval(BaseModel):
    schema_version: str = "v1"
    asset_id: UUID
    reviewer: str
    decision: ApprovalDecision
    comment: str | None = None
    timestamp: datetime
