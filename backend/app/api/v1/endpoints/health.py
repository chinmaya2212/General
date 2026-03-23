from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/health", response_model=HealthResponse, summary="System Health", description="Returns standard application health metrics.")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
