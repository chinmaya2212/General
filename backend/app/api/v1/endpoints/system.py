from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse
from app.db.mongodb import get_database

router = APIRouter()

@router.get("/status")
async def get_system_status(
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    # Mocking real connector checks for MVP
    return {
        "backend": {"status": "connected"},
        "mongodb": {"status": "connected"},
        "misp": {"status": "connected"},
        "ciso": {"status": "connected"},
        "llm": {"status": "connected"}
    }

@router.post("/admin/run")
async def run_admin_action(
    payload: dict,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    action = payload.get("action")
    # For MVP, we handle some sync actions
    if action == "seed_load":
        # Logic to trigger seed load
        return {"status": "initiated", "action": action}
    elif action == "rebuild_graph":
        return {"status": "success", "action": action}
    
    return {"status": "unknown", "action": action}
