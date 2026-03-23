import logging
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingsService:
    def __init__(self):
        self.project = settings.VERTEX_AI_PROJECT
        self.location = settings.VERTEX_AI_LOCATION
        self.enabled = bool(self.project and self.location)
        self.mock_dimension = 768

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        if self.enabled:
            try:
                from langchain_google_vertexai import VertexAIEmbeddings
                model = VertexAIEmbeddings(model_name="text-embedding-004")
                return await model.aembed_documents(texts)
            except ImportError:
                logger.warning("langchain_google_vertexai missing! Falling back to Mock Embeddings.")
                return [[0.1] * self.mock_dimension for _ in texts]
        else:
            return [[0.1] * self.mock_dimension for _ in texts]
            
    async def embed_query(self, query: str) -> List[float]:
        res = await self.embed_texts([query])
        return res[0] if res else []

embedding_service = EmbeddingsService()
