import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.mongodb import get_database
from mongomock_motor import AsyncMongoMockClient
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse, RoleEnum

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]
app.dependency_overrides[get_database] = lambda: mock_db

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_rebuild_graph_and_query(client: TestClient):
    # Setup mock data relations
    await mock_db["vulnerabilities"].insert_one({
        "_id": "vuln_1",
        "affected_asset_id": "asset_1"
    })
    
    response = client.post("/api/v1/ingest/rebuild-graph")
    assert response.status_code == 200
    assert response.json()["edges_created"] == 1
    
    # Query Graph
    res_query = client.get("/api/v1/graph/entity/asset_1")
    assert res_query.status_code == 200
    neighborhood = res_query.json()
    assert neighborhood["entity_id"] == "asset_1"
    assert len(neighborhood["outbound_edges"]) == 1
    assert neighborhood["inbound_edges"] == []
