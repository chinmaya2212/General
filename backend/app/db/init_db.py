from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

async def init_db_indexes(db: AsyncIOMotorDatabase):
    """
    Database Initialization Hook.
    Creates necessary indexes for the MVP to function efficiently.
    Note: Index creation is idempotent in MongoDB.
    """
    logger.info("Initializing database indexes...")
    
    # Auth
    await db["users"].create_index("email", unique=True)
    
    # Assets & Infrastructure
    await db["assets"].create_index("hostname")
    await db["assets"].create_index("ip_address")
    
    # Threats & Vulns
    await db["vulnerabilities"].create_index("cve_id")
    await db["incidents"].create_index("status")
    await db["alerts"].create_index("severity")
    await db["threat_indicators"].create_index("value")
    
    # Graph & Relationships
    await db["graph_edges"].create_index([("source_id", 1), ("target_id", 1)])
    
    # Agents
    await db["chat_sessions"].create_index("user_id")
    await db["agent_runs"].create_index("status")
    
    # RAG Atlas Vector Search Mapping (Must be configured in MongoDB Dashboard or via specialized driver commands in cluster)
    # {
    #   "fields": [
    #     {
    #       "numDimensions": 768,
    #       "path": "embedding",
    #       "similarity": "cosine",
    #       "type": "vector"
    #     }
    #   ]
    # }
    
    logger.info("Database indexes successfully verified/created.")
