from fastapi import APIRouter, Depends, Query
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse
from app.db.mongodb import get_database
from typing import List
from app.models.base import Alert

router = APIRouter()

@router.get("/", response_model=List[Alert])
async def list_alerts(
    limit: number = Query(50, ge=1, le=100),
    severity: str = Query(None),
    status: str = Query(None),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    query = {}
    if severity: query["severity"] = severity
    if status: query["status"] = status
    
    cursor = db["alerts"].find(query).sort("created_at", -1).limit(limit)
    alerts = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        alerts.append(Alert(**doc))
    return alerts

@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    # For MVP, we use string IDs or convert for Mongo
    from bson import ObjectId
    try:
        doc = await db["alerts"].find_one({"_id": ObjectId(alert_id)})
    except:
        doc = await db["alerts"].find_one({"id": alert_id})
        
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
        
    doc["id"] = str(doc.pop("_id"))
    return Alert(**doc)
