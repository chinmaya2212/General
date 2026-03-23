from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from app.db.mongodb import get_database
from app.services.exposure_service import exposure_service

router = APIRouter()

@router.get("/top")
async def get_top_exposures(
    limit: int = 10,
    db = Depends(get_database)
):
    try:
        return await exposure_service.get_top_exposures(db, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{asset_id}")
async def get_asset_exposure(
    asset_id: str,
    db = Depends(get_database)
):
    try:
        result = await exposure_service.get_asset_exposure(asset_id, db)
        if not result:
            raise HTTPException(status_code=404, detail="Asset not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
