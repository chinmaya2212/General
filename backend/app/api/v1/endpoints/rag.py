from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.v1.dependencies import get_current_user, require_role
from app.models.user import UserResponse, RoleEnum
from app.services.rag_service import rebuild_rag_vectors, semantic_search, process_rag_query
from app.models.rag_query import RAGQueryRequest, RAGQueryResponse
from app.db.mongodb import get_database
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/rebuild-vectors")
async def rebuild_vectors_endpoint(
    current_user: UserResponse = Depends(require_role([RoleEnum.admin])),
    db = Depends(get_database)
):
    """
    Synchronously extracts entities from the canonical collections,
    chunks their textual descriptions, generates LLM embeddings, 
    and saves them back into the vector store.
    """
    try:
        count = await rebuild_rag_vectors(db)
        return {"message": "RAG Vectors rebuilt successfully.", "vectors_created": count}
    except Exception as e:
        logger.error(f"RAG rebuild failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_documents_endpoint(
    q: str = Query(..., description="The semantic search query"),
    limit: int = Query(5, ge=1, le=50),
    source_type: str = Query(None, description="Optional filter by source_type (e.g. policy, control)"),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Executes a Vector similarity search against the RAG document store."""
    filters = {}
    if source_type:
        filters["source_type"] = source_type
        
    try:
        results = await semantic_search(query=q, filters=filters, db=db, limit=limit)
        return {"query": q, "results": results}
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=RAGQueryResponse)
async def submit_rag_query(
    request: RAGQueryRequest,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    try:
        response = await process_rag_query(request, current_user.id, db)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources/{answer_id}", response_model=RAGQueryResponse)
async def get_rag_sources(
    answer_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    from bson import ObjectId, errors
    try:
        doc = await db["rag_queries"].find_one({"_id": ObjectId(answer_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Answer not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Answer ID format")
