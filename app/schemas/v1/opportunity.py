from uuid import UUID
from pydantic import BaseModel, Field

class Opportunity(BaseModel):
    schema_version: str = "v1"
    analysis_id: UUID
    kind: str
    priority: float = Field(ge=0, le=1)
    reason: str
    source_ids: list[UUID]
