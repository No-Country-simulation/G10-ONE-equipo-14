from uuid import NAMESPACE_URL, uuid5
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.v1.process import ProcessRequest, ProcessResponse, RecordErrorResponse, RunSummary
from app.services.csv_ingestion import parse_interactions_csv
from app.services.ingestion import ingest_interactions

router = APIRouter()


def _response(payload: ProcessRequest, idempotency_key: str, db: Session, pre_errors=None) -> ProcessResponse:
    run_id = uuid5(NAMESPACE_URL, f"{payload.organization_id}:{payload.community_id}:{idempotency_key}")
    result = ingest_interactions(db, payload.organization_id, payload.community_id, payload.interactions)
    all_errors = list(pre_errors or []) + result.errors
    return ProcessResponse(
        schema_version="v1",
        run_id=run_id,
        status="ACCEPTED" if not all_errors else "ACCEPTED_WITH_ERRORS",
        summary=RunSummary(
            received=result.received + len(pre_errors or []),
            accepted=result.accepted,
            duplicates=result.duplicates,
            errors=len(all_errors),
        ),
        record_errors=[RecordErrorResponse(**vars(e)) for e in all_errors],
    )


@router.post("/process", response_model=ProcessResponse, status_code=status.HTTP_202_ACCEPTED)
def process_json(
    payload: ProcessRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
) -> ProcessResponse:
    return _response(payload, idempotency_key, db)


@router.post("/process/csv", response_model=ProcessResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_csv(
    file: UploadFile = File(...),
    organization_id: str = Form(...),
    community_id: str = Form(...),
    reference_period: str = Form(...),
    requested_assets: str = Form("LINKEDIN,FAQ"),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
) -> ProcessResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="A .csv file is required")
    content = await file.read()
    items, parse_errors = parse_interactions_csv(content)
    if not items and parse_errors:
        raise HTTPException(status_code=422, detail=[vars(e) for e in parse_errors])
    assets = [x.strip().upper() for x in requested_assets.split(",") if x.strip()]
    payload = ProcessRequest(
        organization_id=organization_id,
        community_id=community_id,
        reference_period=reference_period,
        requested_assets=assets,
        interactions=items,
    )
    return _response(payload, idempotency_key, db, parse_errors)
