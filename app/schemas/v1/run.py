from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RunListItem(BaseModel):
    run_id: UUID
    organization_id: str
    community_id: str
    reference_period: str | None = None
    source_name: str | None = None
    status: str
    created_at: datetime
    display_label: str
