from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Alert(BaseModel):
    id: UUID
    run_id: UUID
    interaction_id: UUID
    severity: str
    status: str
    message: str
    excerpt: str
    created_at: datetime | None = None
