from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timezone

def generate_now():
    return datetime.now(timezone.utc)

class BaseDBModel(BaseModel):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source_metadata: Dict[str, Any] = {}
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
