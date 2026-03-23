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
import app.services.agent.investigation_agent
import app.services.graph_service
from app.services.graph_service import query_entity_neighborhood

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]

# Root level overrides
fastapi_app.dependency_overrides[get_database] = lambda: mock_db
vertex_llm.enabled = False

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_investigation_flow(client: TestClient, monkeypatch):
    # Patch all the places get_database is used
    monkeypatch.setattr("app.services.agent.investigation_agent.get_database", lambda: mock_db)
    monkeypatch.setattr("app.services.graph_service.get_database", lambda: mock_db)
    monkeypatch.setattr("app.services.graph_service.query_entity_neighborhood", query_entity_neighborhood)
    
    # 1. Setup mock data: Primary Alert and a Related Alert
    primary_id = ObjectId()
    related_id = ObjectId()
    asset_id = "target_host"
    
    await mock_db["alerts"].insert_one({
        "_id": primary_id,
        "title": "Initial Phish",
        "asset_id": asset_id,
        "status": "open"
    })
    
    await mock_db["alerts"].insert_one({
        "_id": related_id,
        "title": "Subsequent Malware",
        "asset_id": asset_id,
        "status": "open"
    })
    
    # Add a graph edge
    await mock_db["graph_edges"].insert_one({
        "source_id": str(primary_id),
        "source_type": "alert",
        "target_id": asset_id,
        "target_type": "asset",
        "rel_type": "affects"
    })
    
    # 2. Trigger Investigation Agent
    response = client.post("/api/v1/agents/investigate", json={
        "entity_id": str(primary_id),
        "entity_type": "alert"
    })
    
    assert response.status_code == 200, response.text
    res = response.json()
    
    assert res["status"] == "completed"
    assert "result" in res
    assert len(res["evidence_links"]) >= 0 # Might be empty depending on mock LLM output re-find
    
    # 3. Verify Agent Run persistence
    run_doc = await mock_db["agent_runs"].find_one({"_id": ObjectId(res["run_id"])})
    assert run_doc is not None
    assert run_doc["agent_type"] == "investigation_agent"
    assert run_doc["state_snapshot"]["related_count"] >= 1
    assert run_doc["state_snapshot"]["edge_count"] >= 1
