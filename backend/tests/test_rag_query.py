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

async def test_full_rag_context_query(client: TestClient):
    # Insert mock document context natively
    await mock_db["documents"].insert_one({
        "_id": "doc_1",
        "content": "All cloud instances must enforce 2FA immediately.",
        "source_type": "policy",
        "source_system": "canonical_db",
        "document_id": "pol_xyz"
    })
    
    query_payload = {
         "query": "cloud instance authentication",
         "mode": "policy"
    }
    
    response = client.post("/api/v1/rag/query", json=query_payload)
    assert response.status_code == 200, response.text
    res = response.json()
    
    assert res["query"] == query_payload["query"]
    assert res["mode"] == "policy"
    assert "Mocking Context" in res["answer"] or "2FA" in res["answer"]
    assert len(res["citations"]) > 0
    assert res["citations"][0]["document_id"] == "pol_xyz"
    
    answer_id = res["id"]
    
    # Test tracking route locally 
    res_source = client.get(f"/api/v1/rag/sources/{answer_id}")
    assert res_source.status_code == 200
    assert res_source.json()["id"] == answer_id
