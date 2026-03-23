import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.mongodb import get_database
from mongomock_motor import AsyncMongoMockClient
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse, RoleEnum
import json

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]
app.dependency_overrides[get_database] = lambda: mock_db

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_ciso_offline_sync(client: TestClient):
    mock_grc_data = {
        "policies": [
            {"id": "p1", "name": "Access Control Policy", "version": "1.2", "status": "approved"}
        ],
        "controls": [
            {"id": "c1", "ref": "AC-1", "description": "Implement RBAC", "policy_id": "p1", "status": "implemented"}
        ]
    }
    
    file_content = json.dumps(mock_grc_data).encode("utf-8")
    
    response = client.post(
        "/api/v1/ingest/ciso-assistant/sync",
        files={"offline_file": ("ciso_export.json", file_content, "application/json")}
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["source"] == "offline_file:ciso_export.json"
    
    policy = await mock_db["policies"].find_one({"title": "Access Control Policy"})
    assert policy is not None
    assert policy["source_metadata"]["ciso_id"] == "p1"
    
    control = await mock_db["controls"].find_one({"name": "AC-1"})
    assert control is not None
    assert control["implementation_status"] == "implemented"
