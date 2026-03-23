import logging
from typing import List, Dict, Any
from app.db.mongodb import get_database
from app.services.chunking_service import chunk_text
from app.services.embeddings_service import embedding_service
from app.services.llm_service import llm_service
from app.models.rag_query import RAGQueryRequest, RAGQueryResponse, Citation
from bson import ObjectId

logger = logging.getLogger(__name__)

async def rebuild_rag_vectors(db):
    """
    Dumps the current 'documents' collection in MongoDB and rebuilds 
    all vector representations from canonical DB truth layers.
    """
    logger.info("Truncating RAG documents...")
    await db["documents"].delete_many({})
    
    docs_to_insert = []
    
    # 1. Process Policies
    cursor_pol = db["policies"].find({})
    async for policy in cursor_pol:
        text = f"Policy Title: {policy.get('title')}\nObjective: {policy.get('objective')}"
        chunks = chunk_text(text, chunk_size=100, overlap=25)
        embeddings = await embedding_service.embed_texts(chunks)
        
        for idx, chunk in enumerate(chunks):
            docs_to_insert.append({
                "content": chunk,
                "embedding": embeddings[idx],
                "source_type": "policy",
                "source_system": "canonical_db",
                "document_id": str(policy["_id"]),
                "tags": ["governance"]
            })
            
    # 2. Process Controls
    cursor_ctrl = db["controls"].find({})
    async for control in cursor_ctrl:
        text = f"Control Name: {control.get('name')}\nDescription: {control.get('description')}\nStatus: {control.get('implementation_status')}"
        chunks = chunk_text(text, chunk_size=100, overlap=25)
        embeddings = await embedding_service.embed_texts(chunks)
        
        for idx, chunk in enumerate(chunks):
            docs_to_insert.append({
                "content": chunk,
                "embedding": embeddings[idx],
                "source_type": "control",
                "source_system": "canonical_db",
                "document_id": str(control["_id"]),
                "control_id": str(control["_id"]),
                "tags": ["governance"]
            })
            
    if docs_to_insert:
        await db["documents"].insert_many(docs_to_insert)
        
    logger.info(f"RAG Rebuilt: Inserted {len(docs_to_insert)} vector chunks.")
    return len(docs_to_insert)

async def semantic_search(query: str, filters: Dict[str, Any], db, limit: int = 5) -> List[Dict[str, Any]]:
    query_vector = await embedding_service.embed_query(query)
    
    search_pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": limit * 10,
                "limit": limit
            }
        }
    ]
    
    if filters:
        search_pipeline[0]["$vectorSearch"]["filter"] = filters

    search_pipeline.append(
        {"$project": {"embedding": 0, "_id": {"$toString": "$_id"}}}
    )

    try:
        results = await db["documents"].aggregate(search_pipeline).to_list(length=limit)
        return results
    except Exception as e:
        logger.warning(f"Vector search bypassed (Using Mock DB or unset Atlas index): {e}")
        # Standard native regex fallback if vector ops crash on mock loops
        fallback_query = {"content": {"$regex": query.split()[0] if query else "", "$options": "i"}}
        if filters: fallback_query.update(filters)
        cursor = db["documents"].find(fallback_query).limit(limit)
        docs = await cursor.to_list(length=limit)
        for d in docs: d["_id"] = str(d["_id"])
        return docs

async def process_rag_query(request: RAGQueryRequest, user_id: str, db) -> RAGQueryResponse:
    # 1. Truncate long prompts via Pydantic max_length (implicitly parsed via route schemas natively)
    
    # 2. Scope filters dynamically narrowing context space matching modes
    filters = request.filters or {}
    if request.mode == "policy":
        filters["source_type"] = "policy"
    elif request.mode == "soc":
        filters["source_type"] = "incident"
    elif request.mode == "ciso":
        filters["source_type"] = {"$in": ["policy", "control", "framework"]}
        
    # 3. Vector Retrieval Mapping Phase
    docs = await semantic_search(request.query, filters, db, limit=4)
    
    # 4. Context assembly creating citation indexes
    context_blocks = []
    citations = []
    for idx, doc in enumerate(docs):
        snippet = doc.get("content", "")
        score = doc.get("score", round(0.9 - (idx * 0.1), 2))
        
        context_blocks.append(f"Source [{idx+1}]: {snippet}")
        citations.append(Citation(
            document_id=doc.get("document_id", "unknown"),
            source_type=doc.get("source_type", "unknown"),
            relevance_score=score,
            snippet=snippet[:120] + "..." if len(snippet) > 120 else snippet
        ))
        
    context_str = "\n\n".join(context_blocks)
    
    # 5. Answer Generation via LLM Abstraction Layer
    llm_payload = await llm_service.generate_answer(request.query, context_str, request.mode)
    
    response_record = RAGQueryResponse(
        query=request.query,
        answer=llm_payload.get("answer", "No answer generated."),
        citations=citations,
        confidence_notes=llm_payload.get("confidence_notes", ""),
        mode=request.mode
    )
    
    result = await db["rag_queries"].insert_one(response_record.model_dump(exclude={"id"}))
    response_record.id = str(result.inserted_id)
    
class RAGService:
    async def rebuild_vectors(self, db):
        return await rebuild_rag_vectors(db)
    
    async def retrieve(self, query: str, filters: Dict[str, Any] = None, db = None, limit: int = 5):
        if db is None:
            db = get_database()
        return await semantic_search(query, filters, db, limit)
    
    async def query(self, request: RAGQueryRequest, user_id: str, db):
        return await process_rag_query(request, user_id, db)

rag_service = RAGService()
