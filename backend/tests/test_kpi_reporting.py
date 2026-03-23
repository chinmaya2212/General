import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.db.mongodb import get_database
from mongomock_motor import AsyncMongoMockClient
from datetime import datetime
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse, RoleEnum

# Import services to patch them
import app.services.kpi_service

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]

# Root level overrides
fastapi_app.dependency_overrides[get_database] = lambda: mock_db

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_kpi_summary_aggregation(client: TestClient, monkeypatch):
    # Patch database calls
    monkeypatch.setattr("app.services.kpi_service.get_database", lambda: mock_db)
    
    # 1. Setup mock data: 2 alerts, 1 incident, 1 policy
    await mock_db["alerts"].insert_many([
        {"severity": "critical", "status": "new", "name": "Crit Alert"},
        {"severity": "medium", "status": "closed", "name": "Old Alert"}
    ])
    
    await mock_db["incidents"].insert_one({
        "status": "investigating",
        "name": "Live Breach"
    })
    
    await mock_db["policies"].insert_one({
        "name": "Cloud Security Policy",
        "objective": "Secure the cloud"
    })
    
    # 2. Test /summary route
    response = client.get("/api/v1/kpis/summary")
    assert response.status_code == 200
    res = response.json()
    
    assert res["alerts"]["open_count"] == 1
    assert res["alerts"]["critical_count"] == 1
    assert res["incidents"]["active_count"] == 1
    assert res["governance"]["total_policies"] == 1
    assert "executive_summary" in res
    
    # 3. Test /trends route
    response2 = client.get("/api/v1/kpis/trends")
    assert response2.status_code == 200
    res2 = response2.json()
    assert len(res2) == 7 # 7 days of trends
    assert "avg_exposure" in res2[0]
