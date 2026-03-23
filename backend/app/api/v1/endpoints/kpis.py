from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.db.mongodb import get_database
from app.services.kpi_service import kpi_service

router = APIRouter()

@router.get("/summary")
async def get_kpi_summary(
    db = Depends(get_database)
):
    try:
        return await kpi_service.get_summary(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_kpi_trends(
    db = Depends(get_database)
):
    try:
        return await kpi_service.get_trends(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
