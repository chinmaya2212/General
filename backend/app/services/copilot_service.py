import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.models.chat import ChatSession, ChatMessage, CopilotChatResponse
from app.services.rag_service import rag_service
from app.services.vertex_llm import vertex_llm, LLMRequest, Message

logger = logging.getLogger(__name__)

class CopilotService:
    def __init__(self):
        self.collection_name = "chat_sessions"

    async def get_or_create_session(self, db, user_id: str, session_id: Optional[str], mode: str) -> ChatSession:
        if session_id:
            doc = await db[self.collection_name].find_one({"_id": ObjectId(session_id), "user_id": user_id})
            if doc:
                doc["_id"] = str(doc["_id"])
                return ChatSession(**doc)
        
        # Create new session
        new_session = ChatSession(user_id=user_id, mode=mode)
        res = await db[self.collection_name].insert_one(new_session.model_dump(exclude={"id"}))
        new_session.id = str(res.inserted_id)
        return new_session

    async def process_chat(self, db, user_id: str, message_text: str, session_id: Optional[str], mode: str) -> CopilotChatResponse:
        session = await self.get_or_create_session(db, user_id, session_id, mode)
        
        # 1. Retrieval (RAG) based on mode
        # Mapping mode to RAG filter keywords or tags
        rag_query = message_text
        context_docs = await rag_service.retrieve(rag_query, limit=5, filters={"source_type": mode} if mode != "ciso" else {})
        
        context_str = "\n".join([f"[{d['metadata'].get('document_id', 'doc')}] {d['content']}" for d in context_docs])
        
        # 2. Prepare LLM Prompt
        history = "\n".join([f"{m.role}: {m.content}" for m in session.messages[-5:]]) # Last 5 messages for context
        
        system_prompts = {
            "ciso": "You are the CISO Executive Copilot. Provide strategic, risk-focused advice. Focus on business impact.",
            "soc": "You are the SOC Operational Copilot. Focus on incident response, detection engineering, and technical triage.",
            "policy": "You are the Policy & Compliance Advisor. Ground all answers in organizational policies and regulatory frameworks.",
            "exposure": "You are the Exposure Management Specialist. Focus on vulnerabilities, attack surface, and prioritization."
        }
        
        prompt = f"""
        {system_prompts.get(mode, system_prompts['ciso'])}
        
        CONTEXT FROM KNOWLEDGE BASE:
        {context_str}
        
        CONVERSATION HISTORY:
        {history}
        
        USER MESSAGE:
        {message_text}
        
        INSTRUCTIONS:
        1. Provide an executive summary if the answer is long.
        2. List specific action items if applicable.
        3. Cite your sources using the [doc_id] format from context.
        4. Return your response in structured JSON format if possible, otherwise clear markdown.
        """
        
        req = LLMRequest(
            messages=[Message(role="user", content=prompt)],
            temperature=0.2
        )
        
        res = await vertex_llm.generate(req)
        
        # 3. Update Session
        user_msg = ChatMessage(role="user", content=message_text)
        # Simple extraction for actions/citations (MVP logic)
        import re
        citations = list(set(re.findall(r'\[([^\]]+)\]', res.content)))
        actions = list(set(re.findall(r'- Action: (.*)', res.content)))
        
        assistant_msg = ChatMessage(
            role="assistant", 
            content=res.content,
            citations=citations,
            action_list=actions
        )
        
        session.messages.append(user_msg)
        session.messages.append(assistant_msg)
        session.updated_at = datetime.utcnow()
        
        if len(session.messages) <= 2:
             # Update title based on first message
             session.title = message_text[:50] + "..." if len(message_text) > 50 else message_text

        await db[self.collection_name].replace_one({"_id": ObjectId(session.id)}, session.model_dump(exclude={"id"}))
        
        return CopilotChatResponse(
            session_id=session.id,
            message=assistant_msg,
            summary=res.content[:200] + "..." if len(res.content) > 200 else ""
        )

copilot_service = CopilotService()
