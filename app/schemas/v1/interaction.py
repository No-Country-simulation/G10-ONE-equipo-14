from datetime import datetime
from pydantic import BaseModel, Field

class InteractionRequest(BaseModel):
    external_id: str | None = None
    author: str = Field(min_length=1, max_length=200)
    channel: str = Field(min_length=1, max_length=200)
    type: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=10000)
    occurred_at: datetime | None = None
