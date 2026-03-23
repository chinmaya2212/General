from fastapi import APIRouter, Depends, Query
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse
from app.db.mongodb import get_database
from typing import List
from app.models.base import Incident

router = APIRouter()

@router.get("/", response_model=List[Incident])
async def list_incidents(
    limit: number = Query(50, ge=1, le=100),
    status: str = Query(None),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    query = {}
    if status: query["status"] = status
    
    cursor = db["incidents"].find(query).sort("created_at", -1).limit(limit)
    incidents = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        incidents.append(Incident(**doc))
    return incidents

@router.get("/{incident_id}", response_model=Incident)
async def get_incident(
    incident_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    from bson import ObjectId
    try:
        doc = await db["incidents"].find_one({"_id": ObjectId(incident_id)})
    except:
        doc = await db["incidents"].find_one({"id": incident_id})
        
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Incident not found")
        
    doc["id"] = str(doc.pop("_id"))
    return Incident(**doc)
