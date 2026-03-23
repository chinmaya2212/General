import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from app.main import app
from app.db.mongodb import get_database
from app.models.user import RoleEnum
from app.core.security import get_password_hash
import asyncio

mock_client = AsyncMongoMockClient()
mock_db = mock_client["mock_db"]

# Override FastAPI dependency to use the mongomock database instead of an actual MongoDB server
app.dependency_overrides[get_database] = lambda: mock_db

pytestmark = pytest.mark.asyncio

async def test_seed_admin(client: TestClient):
    response = client.post("/api/v1/auth/seed-admin", json={
        "email": "admin@example.com",
        "password": "strongpassword123",
        "full_name": "Admin User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    assert "hashed_password" not in data

async def test_seed_admin_twice_fails(client: TestClient):
    response = client.post("/api/v1/auth/seed-admin", json={
        "email": "admin2@example.com",
        "password": "strongpassword123"
    })
    assert response.status_code == 400
    assert "already seeded" in response.text

async def test_successful_login(client: TestClient):
    response = client.post("/api/v1/auth/login", data={
        "username": "admin@example.com",
        "password": "strongpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
async def test_invalid_login(client: TestClient):
    response = client.post("/api/v1/auth/login", data={
        "username": "admin@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    
async def test_missing_token(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

async def test_current_user_and_role_access(client: TestClient):
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "admin@example.com",
        "password": "strongpassword123"
    })
    token = login_resp.json()["access_token"]
    
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "admin@example.com"
    
    admin_resp = client.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert admin_resp.status_code == 200

async def test_role_denied_access(client: TestClient):
    # Insert analyst user raw into mock db
    user_dict = {
        "email": "analyst@example.com",
        "hashed_password": get_password_hash("password123"),
        "role": "analyst"
    }
    await mock_db["users"].insert_one(user_dict)
    
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "analyst@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    
    admin_resp = client.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert admin_resp.status_code == 403
    assert "roles" in admin_resp.text
