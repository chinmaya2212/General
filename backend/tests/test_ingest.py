import pytest
from fastapi.testclient import TestClient
from app.db.mongodb import get_database
from mongomock_motor import AsyncMongoMockClient
from app.main import app
import json

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]
app.dependency_overrides[get_database] = lambda: mock_db

# Patch auth mapping so we can upload as confirmed user without login step during pure ingest test
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse, RoleEnum

def mock_get_current_user():
    return UserResponse(email="test@example.com", id="60d5ecb8b311234567890123", role=RoleEnum.admin)
app.dependency_overrides[get_current_user] = mock_get_current_user


async def test_upload_json_ingest(client: TestClient):
    threat_data = [
        {
            "actor": "APT29",
            "ttp": "T1078",
            "timestamp": "2026-03-23T10:00:00Z",
            "description": "Exploit attempt"
        }
    ]
    file_content = json.dumps(threat_data).encode("utf-8")
    
    response = client.post(
        "/api/v1/ingest/files", 
        data={"entity_type": "threat_event"},
        files={"file": ("threats.json", file_content, "application/json")}
    )
    
    assert response.status_code == 200
    res_job = response.json()
    assert res_job["entity_type"] == "threat_event"
    assert res_job["status"] == "pending" # Before bg task changes it
    
    # We wait just a fraction since BackgroundTasks fire in event lifecycle,
    # but with test client, we might not get exact resolution easily unless we invoke the processor manually.
    # In Fastapi TestClient, BackgroundTasks are exhausted immediately after response!
    
    # So we can verify the DB updates immediately here via mock DB wrapper
    job = await mock_db["ingestion_jobs"].find_one()
    # Pydantic maps ID implicitly depending on wrapper, but motor keeps it as _id until mapped.
    assert job["successful_records"] == 1
    assert job["status"] == "completed"
    
    # Check if threat event was created
    threat = await mock_db["threat_events"].find_one({"actor": "APT29"})
    assert threat is not None
    assert threat["actor"] == "APT29"
    # Metadata mapped test
    assert threat["source_metadata"]["original_filename"] == "threats.json"
