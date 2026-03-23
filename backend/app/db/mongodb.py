from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.db.init_db import init_db_indexes
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None

db = MongoDB()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    uri = settings.MONGODB_URI.get_secret_value() if settings.MONGODB_URI else ""
    if uri.startswith("mongodb"):
        db.client = AsyncIOMotorClient(uri)
        logger.info("Connected to MongoDB.")
        await init_db_indexes(db.client[settings.MONGODB_DB_NAME])
    else:
        logger.warning(f"Mock MONGODB_URI detected: {uri}. Disabling real DB connection.")

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    if db.client is None:
        raise ValueError("Database client not initialized")
    return db.client[settings.MONGODB_DB_NAME]
