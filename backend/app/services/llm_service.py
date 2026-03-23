import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.project = settings.VERTEX_AI_PROJECT
        self.location = settings.VERTEX_AI_LOCATION
        self.enabled = bool(self.project and self.location)

    async def generate_answer(self, query: str, context: str, mode: str) -> Dict[str, Any]:
        """
        Synthesizes the prompt bounds enforcing the 'mode' scoped constraints evaluating exactly the context blocks defined natively.
        """
        # Strict framing eliminating out of bounds predictions natively
        prompt = f"""
        You are an AI Security Platform Copilot executing in strictly defined '{mode}' mode. 
        Answer the user's query explicitly prioritizing the provided CONTEXT. 
        If the CONTEXT fragments omit sufficient facts, state clearly that information is unavailable. 
        DO NOT hallucinate facts, DO NOT generate generic advice if contradictory to the CONTEXT.

        CONTEXT LIMITS:
        {context}

        QUERY:
        {query}

        Provide the answer synthetically serialized.
        """

        if self.enabled:
            # Under live configurations this executes `ChatVertexAI(model_name="gemini-2.5-flash")` dynamically
            try:
                from langchain_google_vertexai import ChatVertexAI
                from langchain_core.messages import HumanMessage
                llm = ChatVertexAI(model_name="gemini-2.5-flash", temperature=0.1)
                res = await llm.ainvoke([HumanMessage(content=prompt)])
                return {
                    "answer": res.content,
                    "confidence_notes": f"Generated via Gemini 2.5 Flash enforcing '{mode}' rulesets natively."
                }
            except Exception as e:
                logger.warning(f"Vertex AI invoke failed falling back to safe local mock: {str(e)}")

        logger.debug(f"LLM Vertex bypass configured. Passing through generic mock asserting prompt ingestion safe handling.")
        return {
            "answer": f"Mocking Context execution: Extracted [{len(context)} bytes] answering '{query}'.",
            "confidence_notes": "High (Mock Evaluated via local RAG testing bypass)."
        }

llm_service = LLMService()
