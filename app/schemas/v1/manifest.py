from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class Manifest(BaseModel):
    schema_version: str = "v1"
    run_id: UUID
    object_key: str
    content_type: str
    sha256: str
    etag: str | None = None
    created_at: datetime
