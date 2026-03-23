from enum import Enum
from typing import List
from app.models.base import BaseDBModel

class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    partial_success = "partial_success"

class IngestionJob(BaseDBModel):
    user_id: str
    filename: str
    file_type: str
    entity_type: str
    status: JobStatus = JobStatus.pending
    total_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    errors: List[str] = []
