import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.db.mongodb import get_database
from mongomock_motor import AsyncMongoMockClient
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse, RoleEnum
from bson import ObjectId
from app.services.vertex_llm import vertex_llm
from app.services.embeddings_service import embedding_service

# Import services to patch them
import app.services.copilot_service
import app.services.rag_service

pytestmark = pytest.mark.asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]

# Root level overrides
fastapi_app.dependency_overrides[get_database] = lambda: mock_db
vertex_llm.enabled = False
embedding_service.enabled = False

def mock_get_current_user():
    return UserResponse(email="admin@example.com", id="admin_id", role=RoleEnum.admin)
fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_copilot_chat_flow(client: TestClient, monkeypatch):
    # Patch all the places get_database is used
    monkeypatch.setattr("app.services.copilot_service.get_database", lambda: mock_db)
    monkeypatch.setattr("app.services.rag_service.get_database", lambda: mock_db)
    
    # 1. Setup mock data: 1 document in RAG
    await mock_db["documents"].insert_one({
        "content": "AI Security Policy: All models must be audited.",
        "metadata": {"source_type": "policy", "document_id": "POL-001"},
        "embedding": [0.1] * 768
    })
    
    # 2. Trigger Copilot Chat
    response = client.post("/api/v1/chat/copilot", json={
        "message": "What is our policy on AI?",
        "mode": "policy"
    })
    
    assert response.status_code == 200, response.text
    res = response.json()
    
    assert res["session_id"] is not None
    assert res["message"]["role"] == "assistant"
    
    # 3. Verify Session Persistence
    session_id = res["session_id"]
    session_doc = await mock_db["chat_sessions"].find_one({"_id": ObjectId(session_id)})
    assert session_doc is not None
    assert len(session_doc["messages"]) == 2 # User + Assistant
    assert session_doc["mode"] == "policy"
    
    # 4. Trigger second message in same session
    response2 = client.post("/api/v1/chat/copilot", json={
        "message": "Tell me more.",
        "session_id": session_id,
        "mode": "policy"
    })
    
    assert response2.status_code == 200
    res2 = response2.json()
    assert res2["session_id"] == session_id
    
    session_doc_updated = await mock_db["chat_sessions"].find_one({"_id": ObjectId(session_id)})
    assert len(session_doc_updated["messages"]) == 4 # User + Assistant + User + Assistant
