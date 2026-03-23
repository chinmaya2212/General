from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

class ChatMessage(BaseModel):
    role: str # 'user', 'assistant', 'system'
    content: str
    citations: List[str] = []
    action_list: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    mode: str # 'ciso', 'soc', 'policy', 'exposure'
    title: str = "New Conversation"
    messages: List[ChatMessage] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class CopilotChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: str = "ciso" # 'ciso', 'soc', 'policy', 'exposure'

class CopilotChatResponse(BaseModel):
    session_id: str
    message: ChatMessage
    summary: str = ""
