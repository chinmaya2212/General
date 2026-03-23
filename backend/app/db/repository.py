from datetime import datetime, timezone
from typing import TypeVar, Generic, Type, Optional, List
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId, errors as bson_errors

ModelType = TypeVar("ModelType", bound=BaseModel)

class MongoRepository(Generic[ModelType]):
    """
    Lightweight generic async repository.
    Handles automatic mapping of _id to id and timestamps.
    """
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model: Type[ModelType]):
        self.collection = db[collection_name]
        self.model = model

    def _fix_id(self, doc: dict) -> dict:
        if not doc:
            return None
        if "_id" in doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    def _to_object_id(self, id_str: str) -> ObjectId:
        try:
            return ObjectId(id_str)
        except bson_errors.InvalidId:
            raise ValueError(f"Invalid ObjectId: {id_str}")

    async def get(self, id: str) -> Optional[ModelType]:
        doc = await self.collection.find_one({"_id": self._to_object_id(id)})
        return self.model(**self._fix_id(doc)) if doc else None

    async def create(self, obj_in: ModelType) -> ModelType:
        doc = obj_in.model_dump(exclude={"id"}, exclude_unset=True)
        now = datetime.now(timezone.utc)
        doc["created_at"] = doc.get("created_at") or now
        doc["updated_at"] = doc.get("updated_at") or now
        
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self.model(**self._fix_id(doc))

    async def update(self, id: str, obj_in: dict) -> Optional[ModelType]:
        obj_in["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.find_one_and_update(
            {"_id": self._to_object_id(id)},
            {"$set": obj_in},
            return_document=True
        )
        return self.model(**self._fix_id(result)) if result else None

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": self._to_object_id(id)})
        return result.deleted_count > 0

    async def find(self, query: dict = None, limit: int = 100, skip: int = 0) -> List[ModelType]:
        if query is None:
            query = {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self.model(**self._fix_id(d)) for d in docs]
