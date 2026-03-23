import pytest
from app.db.repository import MongoRepository
from app.models.domain import Asset, AssetCriticality
from mongomock_motor import AsyncMongoMockClient

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_db():
    client = AsyncMongoMockClient()
    return client["test_db"]

async def test_repository_crud(mock_db):
    asset_repo = MongoRepository(mock_db, "assets", Asset)
    
    # Create
    new_asset = Asset(
        name="Core Router",
        type="network",
        ip_address="10.0.0.1",
        hostname="core-rt-01",
        criticality=AssetCriticality.critical
    )
    created = await asset_repo.create(new_asset)
    assert created.id is not None
    assert created.created_at is not None
    assert created.name == "Core Router"
    
    # Read
    fetched = await asset_repo.get(created.id)
    assert fetched.id == created.id
    
    # Find Filter
    filtered = await asset_repo.find({"type": "network"})
    assert len(filtered) == 1
    assert filtered[0].hostname == "core-rt-01"
    
    # Update
    updated = await asset_repo.update(created.id, {"hostname": "core-rt-01-updated"})
    from datetime import timezone
    assert updated.hostname == "core-rt-01-updated"
    assert updated.updated_at.replace(tzinfo=timezone.utc).timestamp() > created.created_at.replace(tzinfo=timezone.utc).timestamp()
    
    # Delete
    deleted = await asset_repo.delete(created.id)
    assert deleted is True
    
    # Verify Deletion
    fetched_after_delete = await asset_repo.get(created.id)
    assert fetched_after_delete is None
