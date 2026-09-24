from uuid import UUID
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    source_interaction_id: UUID
    excerpt: str

class Analysis(BaseModel):
    schema_version: str = "v1"
    interaction_id: UUID
    sentiment: str
    topics: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    relevance: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence] = Field(default_factory=list)
    model: str
    prompt_version: str
