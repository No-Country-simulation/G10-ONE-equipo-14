from copy import deepcopy
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.approval import ApprovalRecord
from app.db.models.asset import AssetRecord, AssetVersion, AssetVersionSource
from app.db.models.manifest import ManifestRecord
from app.db.models.run import Run
from app.db.session import get_db
from app.schemas.v1.asset import Asset, AssetDecisionRequest, AssetEditRequest, AssetStatus
from app.schemas.v1.manifest import Manifest
from app.services.object_storage import configured_storage
import hashlib
import json

router = APIRouter()

def _current(db: Session, asset: AssetRecord) -> AssetVersion:
    version = db.get(AssetVersion, asset.current_version_id) if asset.current_version_id else None
    if version is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Asset has no current version.")
    return version

def _response(db: Session, asset: AssetRecord) -> Asset:
    version = _current(db, asset)
    claims = version.content.get("claims", [])
    body = claims[0].get("text", "") if claims else ""
    return Asset(id=asset.id, opportunity_id=asset.opportunity_id, channel=asset.asset_type, title=version.title, body=body, status=asset.status, version=version.version_number)

@router.get("/assets", response_model=list[Asset])
def list_assets(status_filter: AssetStatus | None = Query(default=None, alias="status"), db: Session = Depends(get_db)) -> list[Asset]:
    statement = select(AssetRecord).order_by(AssetRecord.created_at.desc())
    if status_filter is not None:
        statement = statement.where(AssetRecord.status == status_filter.value)
    return [_response(db, asset) for asset in db.scalars(statement).all()]

@router.patch("/assets/{asset_id}", response_model=Asset)
def edit_asset(asset_id: UUID, payload: AssetEditRequest, db: Session = Depends(get_db)) -> Asset:
    asset = db.get(AssetRecord, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found.")
    if asset.status == "APPROVED":
        raise HTTPException(status.HTTP_409_CONFLICT, "Approved assets are immutable.")
    current = _current(db, asset)
    content = deepcopy(current.content)
    content["title"] = payload.title
    content["claims"][0]["text"] = payload.body
    version = AssetVersion(asset_id=asset.id, version_number=current.version_number + 1, title=payload.title, content=content, model=current.model, prompt_version=current.prompt_version, created_by=payload.editor)
    db.add(version)
    db.flush()
    for source in db.scalars(select(AssetVersionSource).where(AssetVersionSource.asset_version_id == current.id)).all():
        db.add(AssetVersionSource(asset_version_id=version.id, interaction_id=source.interaction_id, excerpt=source.excerpt))
    asset.current_version_id = version.id
    asset.status = "PENDING_REVIEW"
    db.commit()
    db.refresh(asset)
    return _response(db, asset)

def _decide(asset_id: UUID, payload: AssetDecisionRequest, decision: str, db: Session) -> Asset:
    asset = db.get(AssetRecord, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found.")
    version = _current(db, asset)
    db.add(ApprovalRecord(asset_id=asset.id, asset_version_id=version.id, reviewer=payload.reviewer, decision=decision, comment=payload.comment))
    asset.status = decision
    db.commit()
    db.refresh(asset)
    return _response(db, asset)

@router.post("/assets/{asset_id}/approve", response_model=Asset)
def approve_asset(asset_id: UUID, payload: AssetDecisionRequest, db: Session = Depends(get_db)) -> Asset:
    return _decide(asset_id, payload, "APPROVED", db)

@router.post("/assets/{asset_id}/reject", response_model=Asset)
def reject_asset(asset_id: UUID, payload: AssetDecisionRequest, db: Session = Depends(get_db)) -> Asset:
    return _decide(asset_id, payload, "REJECTED", db)

@router.post("/assets/{asset_id}/publish", response_model=Manifest)
def publish_asset(asset_id: UUID, db: Session = Depends(get_db)) -> Manifest:
    asset = db.get(AssetRecord, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found.")
    if asset.status != "APPROVED":
        raise HTTPException(status.HTTP_409_CONFLICT, "Only approved assets can be published.")
    version = _current(db, asset)
    run = db.get(Run, asset.run_id)
    package = {"schema_version": asset.schema_version, "asset_id": str(asset.id), "version": version.version_number, "channel": asset.asset_type, "title": version.title, "content": version.content}
    content = json.dumps(package, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    object_key = f"{run.organization_id}/{run.community_id}/{asset.asset_type.lower()}/{asset.id}/v{version.version_number}.json"
    stored = configured_storage().put(object_key, content, "application/json")
    digest = hashlib.sha256(content).hexdigest()
    if stored.sha256 != digest:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Storage checksum verification failed.")
    record = ManifestRecord(run_id=asset.run_id, asset_id=asset.id, schema_version="v1", bucket=stored.bucket, object_key=stored.object_key, content_type="application/json", sha256=digest, etag=stored.etag)
    db.add(record); db.commit(); db.refresh(record)
    return Manifest(run_id=record.run_id, object_key=record.object_key, content_type=record.content_type, sha256=record.sha256, etag=record.etag, created_at=record.created_at)
