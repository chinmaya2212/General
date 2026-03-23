import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.db.mongodb import get_database
from mongomock_motor import AsyncMongoMockClient
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse, RoleEnum
from bson import ObjectId

# Import services to patch them
from app.services.vertex_llm import vertex_llm
import app.services.agent.triage_agent
import app.services.agent.tools

pytestmark = pytest.mark.asyncio

vertex_llm.enabled = False

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]

# Root level overrides
fastapi_app.dependency_overrides[get_database] = lambda: mock_db

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_alert_triage_flow(client: TestClient, monkeypatch):
    # Patch the direct function calls inside the services
    monkeypatch.setattr("app.services.agent.triage_agent.get_database", lambda: mock_db)
    monkeypatch.setattr("app.services.agent.tools.get_database", lambda: mock_db)
    
    # 1. Setup mock data: Alert, Asset, Identity
    alert_id = ObjectId()
    asset_id = "asset_123"
    identity_id = "user_456"
    
    await mock_db["alerts"].insert_one({
        "_id": alert_id,
        "title": "Suspicious Login",
        "severity": "high",
        "asset_id": asset_id,
        "identity_id": identity_id,
        "status": "open"
    })
    
    await mock_db["assets"].insert_one({
        "_id": ObjectId(),
        "name": asset_id,
        "type": "workstation",
        "owner": "Finance"
    })
    
    await mock_db["identities"].insert_one({
        "_id": ObjectId(),
        "username": identity_id,
        "role": "Analyst"
    })
    
    # 2. Trigger Triage Agent
    response = client.post("/api/v1/agents/triage", json={"alert_id": str(alert_id)})
    
    assert response.status_code == 200, response.text
    res = response.json()
    
    assert res["status"] == "completed"
    assert "run_id" in res
    assert "result" in res
    
    # 3. Verify Agent Run persistence
    run_doc = await mock_db["agent_runs"].find_one({"_id": ObjectId(res["run_id"])})
    assert run_doc is not None
    assert run_doc["agent_type"] == "triage_agent"
    assert run_doc["status"] == "completed"
    assert "asset" in run_doc["state_snapshot"]["enriched_context"]
    assert "identity" in run_doc["state_snapshot"]["enriched_context"]
