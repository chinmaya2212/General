from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.base import BaseDBModel

class RAGQueryRequest(BaseModel):
    query: str = Field(..., max_length=500, description="User query trimmed at 500 characters defending against prompt injection bloat.")
    mode: str = Field(default="general", pattern='^(general|policy|soc|ciso|exposure)$')
    filters: Optional[dict] = None

class Citation(BaseModel):
    document_id: str
    source_type: str
    relevance_score: float
    snippet: str

class RAGQueryResponse(BaseDBModel):
    query: str
    answer: str
    citations: List[Citation] = []
    confidence_notes: str
    mode: str
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
