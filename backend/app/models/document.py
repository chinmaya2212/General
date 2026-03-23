from pydantic import Field, ConfigDict
from typing import Optional, List
from app.models.base import BaseDBModel

class DocumentChunk(BaseDBModel):
    content: str
    embedding: Optional[List[float]] = None
    
    source_type: str # 'policy', 'control', 'incident', 'misp_report'
    source_system: str
    document_id: str
    
    control_id: Optional[str] = None
    framework: Optional[str] = None
    asset_id: Optional[str] = None
    incident_id: Optional[str] = None
    
    tags: List[str] = []
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
