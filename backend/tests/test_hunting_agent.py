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
import app.services.agent.hunting_agent

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]

# Root level overrides
fastapi_app.dependency_overrides[get_database] = lambda: mock_db
vertex_llm.enabled = False

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_hunting_flow(client: TestClient, monkeypatch):
    # Patch all the places get_database is used
    monkeypatch.setattr("app.services.agent.hunting_agent.get_database", lambda: mock_db)
    
    # 1. Setup mock data: 1 high severity alert and 1 threat indicator
    await mock_db["alerts"].insert_one({
        "title": "Unusual Spike in Traffic",
        "severity": "high",
        "asset_id": "host_web_01",
        "status": "open",
        "created_at": "2026-03-23T10:00:00Z"
    })
    
    await mock_db["threat_indicators"].find_one_and_update(
         {"_id": ObjectId()},
         {"$set": {"name": "Exfiltrator Campaign", "value": "1.2.3.4", "type": "ipv4"}},
         upsert=True
    )
    
    # 2. Trigger Hunting Agent
    response = client.post("/api/v1/agents/hunt", json={
        "prompt": "Exfiltrator campaign"
    })
    
    assert response.status_code == 200, response.text
    res = response.json()
    
    assert res["status"] == "completed"
    assert "result" in res
    
    # 3. Verify Agent Run persistence
    run_doc = await mock_db["agent_runs"].find_one({"_id": ObjectId(res["run_id"])})
    assert run_doc is not None
    assert run_doc["agent_type"] == "hunting_agent"
    assert run_doc["state_snapshot"]["intel_count"] >= 1
    assert run_doc["state_snapshot"]["local_count"] >= 1
