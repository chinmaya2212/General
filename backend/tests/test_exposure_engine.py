import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.db.mongodb import get_database
from mongomock_motor import AsyncMongoMockClient
from bson import ObjectId
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse, RoleEnum

# Import services to patch them
import app.services.exposure_service
import app.services.graph_service

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]

# Root level overrides
fastapi_app.dependency_overrides[get_database] = lambda: mock_db

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_exposure_ranking(client: TestClient, monkeypatch):
    # Patch database calls in services
    monkeypatch.setattr("app.services.exposure_service.get_database", lambda: mock_db)
    monkeypatch.setattr("app.services.graph_service.get_database", lambda: mock_db)
    
    # 1. Setup mock data: 2 assets, 1 with vulnerability
    asset_1_id = ObjectId()
    asset_2_id = ObjectId()
    
    await mock_db["assets"].insert_many([
        {"_id": asset_1_id, "name": "Vulnerable Server", "criticality": "high"},
        {"_id": asset_2_id, "name": "Safe Workstation", "criticality": "low"}
    ])
    
    await mock_db["vulnerabilities"].insert_one({
        "name": "CVE-2024-1234",
        "cvss_score": 9.8,
        "affected_asset_id": str(asset_1_id)
    })
    
    # Add a graph edge for reachability
    await mock_db["graph_edges"].insert_one({
        "source_id": "internet",
        "source_type": "external",
        "target_id": str(asset_1_id),
        "target_type": "asset",
        "rel_type": "exposed_to"
    })
    
    # 2. Test /top route
    response = client.get("/api/v1/exposures/top")
    assert response.status_code == 200
    res = response.json()
    
    assert len(res) >= 1
    assert res[0]["asset_id"] == str(asset_1_id)
    assert res[0]["base_score"] > 0
    assert res[0]["metrics"]["is_reachable"] is True
    
    # 3. Test /{id} route
    response2 = client.get(f"/api/v1/exposures/{asset_1_id}")
    assert response2.status_code == 200
    res2 = response2.json()
    assert res2["asset_id"] == str(asset_1_id)
    assert "remediation_plan" in res2
