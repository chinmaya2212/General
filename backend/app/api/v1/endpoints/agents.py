from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel, Field
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse
from app.db.mongodb import get_database
from app.services.agent.triage_agent import execute_triage_agent
from app.services.agent.investigation_agent import execute_investigation_agent
from app.services.agent.hunting_agent import execute_hunting_agent
from app.services.agent.policy_advisor_agent import execute_policy_advisor_agent

router = APIRouter()

class TriageRequest(BaseModel):
    alert_id: str = Field(..., description="ID of the alert to triage and contextualize.")

class InvestigationRequest(BaseModel):
    entity_id: str = Field(..., description="ID of the alert or incident to investigate.")
    entity_type: str = Field(default="alert", pattern="^(alert|incident)$")

class HuntingRequest(BaseModel):
    prompt: str = Field(..., description="Natural language hunting prompt or specific campaign/technique.")

class PolicyAdvisorRequest(BaseModel):
    query: str = Field(..., description="Governance question or topic for AI security alignment.")

class AgentRunResponse(BaseModel):
    run_id: str
    status: str
    result: str = ""
    evidence_links: List[str] = []
    error: str = ""

@router.post("/triage", response_model=AgentRunResponse)
async def submit_triage_job(
    request: TriageRequest,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        result = await execute_triage_agent(request.alert_id, current_user.id, db)
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/investigate", response_model=AgentRunResponse)
async def submit_investigation_job(
    request: InvestigationRequest,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        result = await execute_investigation_agent(
            request.entity_id, 
            request.entity_type, 
            current_user.id, 
            db
        )
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hunt", response_model=AgentRunResponse)
async def submit_hunting_job(
    request: HuntingRequest,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        result = await execute_hunting_agent(
            request.prompt, 
            current_user.id, 
            db
        )
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/policy-advisor", response_model=AgentRunResponse)
async def submit_policy_advisor_job(
    request: PolicyAdvisorRequest,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        result = await execute_policy_advisor_agent(
            request.query, 
            current_user.id, 
            db
        )
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


