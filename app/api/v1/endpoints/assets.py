from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from app.schemas.v1.asset import Asset, AssetStatus
router = APIRouter()
@router.get('/assets', response_model=list[Asset])
def list_assets(status: AssetStatus | None = Query(default=None)): return []
@router.patch('/assets/{asset_id}', response_model=Asset)
def edit_asset(asset_id: UUID): raise HTTPException(501, 'Asset persistence is planned for a later phase.')
@router.post('/assets/{asset_id}/approve', response_model=Asset)
def approve_asset(asset_id: UUID): raise HTTPException(501, 'Approval persistence is planned for a later phase.')
@router.post('/assets/{asset_id}/reject', response_model=Asset)
def reject_asset(asset_id: UUID): raise HTTPException(501, 'Approval persistence is planned for a later phase.')
