from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.dependencies import get_current_user
from app.db.mongodb import get_database
from app.models.user import UserResponse
from app.models.chat import CopilotChatRequest, CopilotChatResponse
from app.services.copilot_service import copilot_service

router = APIRouter()

@router.post("/copilot", response_model=CopilotChatResponse)
async def chat_with_copilot(
    request: CopilotChatRequest,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        result = await copilot_service.process_chat(
            db, 
            current_user.id, 
            request.message, 
            request.session_id, 
            request.mode
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
