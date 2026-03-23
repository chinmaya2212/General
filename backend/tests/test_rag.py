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

async def test_rebuild_and_search_rag(client: TestClient):
    await mock_db["policies"].insert_one({
        "_id": "pol_1",
        "title": "Access Control",
        "objective": "Must use strong authentication everywhere."
    })
    
    res_rebuild = client.post("/api/v1/rag/rebuild-vectors")
    assert res_rebuild.status_code == 200
    assert res_rebuild.json()["vectors_created"] > 0
    
    res_search = client.get("/api/v1/rag/search?q=authentication&limit=5")
    assert res_search.status_code == 200
    data = res_search.json()
    assert len(data["results"]) > 0
    assert "authentication" in data["results"][0]["content"]
