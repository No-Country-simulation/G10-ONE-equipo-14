from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.v1.process import (
    ProcessRequest,
    ProcessResponse,
    RecordErrorResponse,
    RunSummary,
)
from app.services.csv_ingestion import parse_interactions_csv
from app.services.idempotency import (
    IdempotencyConflictError,
    get_or_create_run,
    mark_run_failed,
    save_run_response,
)
from app.services.ingestion import ingest_interactions


router = APIRouter()


def _response(
    payload: ProcessRequest,
    idempotency_key: str,
    db: Session,
    pre_errors=None,
) -> ProcessResponse:
    """Process once and replay the stored response for repeated requests."""
    try:
        idem = get_or_create_run(db, payload, idempotency_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    run = idem.run

    # Same key + same request: return the exact original response.
    if idem.replay:
        if run.response_json is not None:
            return ProcessResponse.model_validate(run.response_json)

        # A concurrent/previous request owns this run but has not completed.
        raise HTTPException(
            status_code=409,
            detail={
                "code": "idempotency_request_in_progress",
                "message": "A request with this Idempotency-Key is already processing.",
                "run_id": str(run.id),
            },
        )

    try:
        result = ingest_interactions(
            db,
            payload.organization_id,
            payload.community_id,
            payload.interactions,
        )

        all_errors = list(pre_errors or []) + result.errors
        response = ProcessResponse(
            schema_version="v1",
            run_id=run.id,
            status="ACCEPTED" if not all_errors else "ACCEPTED_WITH_ERRORS",
            summary=RunSummary(
                received=result.received + len(pre_errors or []),
                accepted=result.accepted,
                duplicates=result.duplicates,
                errors=len(all_errors),
            ),
            record_errors=[
                RecordErrorResponse(**vars(error))
                for error in all_errors
            ],
        )

        save_run_response(
            db,
            run,
            response.model_dump(mode="json"),
            response.status,
        )
        return response

    except Exception:
        mark_run_failed(db, run)
        raise


@router.post(
    "/process",
    response_model=ProcessResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def process_json(
    payload: ProcessRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
) -> ProcessResponse:
    return _response(payload, idempotency_key, db)


@router.post(
    "/process/csv",
    response_model=ProcessResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
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
        raise HTTPException(
            status_code=415,
            detail="A .csv file is required",
        )

    content = await file.read()
    items, parse_errors = parse_interactions_csv(content)

    if not items and parse_errors:
        raise HTTPException(
            status_code=422,
            detail=[vars(error) for error in parse_errors],
        )

    assets = [
        value.strip().upper()
        for value in requested_assets.split(",")
        if value.strip()
    ]

    payload = ProcessRequest(
        organization_id=organization_id,
        community_id=community_id,
        reference_period=reference_period,
        requested_assets=assets,
        interactions=items,
    )

    return _response(
        payload,
        idempotency_key,
        db,
        parse_errors,
    )
