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

async def test_misp_offline_sync(client: TestClient):
    mock_misp_data = {
        "response": [
            {
                "Event": {
                    "id": "1",
                    "uuid": "fake-uuid",
                    "info": "Suspicious login from APT29",
                    "date": "2026-03-24",
                    "Threat_Level_ID": "2",
                    "Tag": [{"name": "mitre:credential-access"}],
                    "Attribute": [
                        {"id": "10", "type": "ip-dst", "value": "192.168.10.1"}
                    ]
                }
            }
        ]
    }
    
    file_content = json.dumps(mock_misp_data).encode("utf-8")
    
    response = client.post(
        "/api/v1/ingest/misp/sync",
        files={"offline_file": ("misp_export.json", file_content, "application/json")}
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["events_fetched"] == 1
    
    event = await mock_db["threat_events"].find_one({"source_metadata.misp_id": "1"})
    assert event is not None
    assert event["ttp"] == "mitre:credential-access"
    
    indicator = await mock_db["threat_indicators"].find_one({"value": "192.168.10.1"})
    assert indicator is not None
    assert indicator["type"] == "ip"
