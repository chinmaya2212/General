import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str # 'user', 'assistant', 'system'
    content: str

class LLMRequest(BaseModel):
    messages: List[Message]
    temperature: float = 0.2
    max_tokens: int = 2000
    structured_json: bool = False
    tools: Optional[List[Dict[str, Any]]] = None

class LLMResponse(BaseModel):
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    input_tokens: int = 0
    output_tokens: int = 0
    model_name: str = "gemini-2.5-flash"

class VertexLLMServiceError(Exception):
    pass

class VertexLLMService:
    def __init__(self):
        self.project = settings.VERTEX_AI_PROJECT
        self.location = settings.VERTEX_AI_LOCATION
        self.enabled = bool(self.project and self.location)
        self.model_name = "gemini-2.5-flash"
        self.max_retries = 3
        
    async def _mock_response(self, request: LLMRequest) -> LLMResponse:
        await asyncio.sleep(0.5) # Simulate slight network Latency for agent realistic delays
        response_content = f"Mock implementation resolving {len(request.messages)} messages."
        
        if request.structured_json:
            response_content = '{"status": "mocked", "message": "Success"}'
            
        return LLMResponse(
            content=response_content,
            input_tokens=len(" ".join([m.content for m in request.messages]).split()),
            output_tokens=15,
            model_name="mock-gemini"
        )
        
    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.enabled:
            logger.debug("Vertex AI disabled/missing credentials. Executing local offline mock.")
            return await self._mock_response(request)
            
        try:
            from langchain_google_vertexai import ChatVertexAI
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            
            lc_messages = []
            for m in request.messages:
                if m.role == "system": lc_messages.append(SystemMessage(content=m.content))
                elif m.role == "user": lc_messages.append(HumanMessage(content=m.content))
                elif m.role == "assistant": lc_messages.append(AIMessage(content=m.content))
                else: lc_messages.append(HumanMessage(content=m.content))
                
            model_kwargs = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
                "project": self.project,
                "location": self.location
            }
            if request.structured_json:
                # Forces Gemini to adhere strictly natively
                model_kwargs["response_mime_type"] = "application/json"
                
            llm = ChatVertexAI(model_name=self.model_name, **model_kwargs)
            
            if request.tools:
                llm = llm.bind_tools(request.tools)
                
            for attempt in range(self.max_retries):
                try:
                    res = await llm.ainvoke(lc_messages)
                    
                    # Extract usage metadata natively provided via LangChain payloads
                    metadata = res.usage_metadata if hasattr(res, "usage_metadata") and res.usage_metadata else {}
                    input_tokens = metadata.get("prompt_tokens", 0)
                    output_tokens = metadata.get("completion_tokens", 0)
                    
                    tool_calls = res.tool_calls if hasattr(res, "tool_calls") and res.tool_calls else None
                    
                    return LLMResponse(
                        content=res.content,
                        tool_calls=tool_calls,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        model_name=self.model_name
                    )
                except Exception as e:
                    logger.warning(f"Vertex AI retry attempt {attempt+1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise e
                    await asyncio.sleep(2 ** attempt)  # Exponential Backoff mitigates Rate Limiting drops
                    
        except ImportError:
            logger.warning("langchain_google_vertexai module not found! Enforcing local evaluation pipeline gracefully.")
            return await self._mock_response(request)
        except Exception as e:
            logger.error(f"Vertex invocation failed irreversibly: {str(e)}")
            raise VertexLLMServiceError(f"Vertex abstraction layer collapsed: {str(e)}")

vertex_llm = VertexLLMService()
