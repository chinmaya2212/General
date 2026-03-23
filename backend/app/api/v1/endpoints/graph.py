from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.v1.dependencies import get_current_user, require_role
from app.models.user import UserResponse, RoleEnum
from app.services.graph_service import query_entity_neighborhood
from app.db.mongodb import get_database

router = APIRouter()

@router.get("/entity/{entity_id}")
async def get_entity_neighborhood(
    entity_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Returns UI-friendly summarizations representing an entities interconnected inbound and outbound relationships tracked.
    """
    neighborhood = await query_entity_neighborhood(entity_id, db)
    return neighborhood
