import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.db.mongodb import get_database
from mongomock_motor import AsyncMongoMockClient
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse, RoleEnum
from bson import ObjectId
from app.services.vertex_llm import vertex_llm

# Import services to patch them
import app.services.agent.policy_advisor_agent

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]

# Root level overrides
fastapi_app.dependency_overrides[get_database] = lambda: mock_db
vertex_llm.enabled = False

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_policy_advisor_flow(client: TestClient, monkeypatch):
    # Patch all the places get_database is used
    monkeypatch.setattr("app.services.agent.policy_advisor_agent.get_database", lambda: mock_db)
    
    # 1. Setup mock data: Policy and Control
    await mock_db["policies"].insert_one({
        "name": "AI Usage Policy",
        "description": "All LLM requests must be logged for audit."
    })
    
    await mock_db["controls"].insert_one({
        "control_id": "MOD-01",
        "name": "Model Auditing",
        "description": "Ensure every model invocation records telemetry."
    })
    
    # 2. Trigger Policy Advisor Agent
    response = client.post("/api/v1/agents/policy-advisor", json={
        "query": "auditing for LLM requests"
    })
    
    assert response.status_code == 200, response.text
    res = response.json()
    
    assert res["status"] == "completed"
    assert "result" in res
    
    # 3. Verify Agent Run persistence
    run_doc = await mock_db["agent_runs"].find_one({"_id": ObjectId(res["run_id"])})
    assert run_doc is not None
    assert run_doc["agent_type"] == "policy_advisor"
    assert run_doc["state_snapshot"]["policy_count"] >= 1
    assert run_doc["state_snapshot"]["control_count"] >= 1
