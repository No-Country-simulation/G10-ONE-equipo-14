from uuid import UUID
from fastapi import APIRouter, HTTPException
from app.schemas.v1.process import ProcessResponse
router = APIRouter()
@router.get('/runs/{run_id}', response_model=ProcessResponse)
def get_run(run_id: UUID): raise HTTPException(501, 'Run persistence is planned for the PostgreSQL ingestion phase.')
