import json
import logging
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END
from app.db.mongodb import get_database
from app.services.vertex_llm import vertex_llm, LLMRequest, Message
from bson import ObjectId

logger = logging.getLogger(__name__)

class HuntingState(TypedDict):
    prompt: str
    intel_context: List[Dict[str, Any]]
    local_context: List[Dict[str, Any]]
    hypotheses: List[str]
    guidance: str
    error: str

async def search_intel_node(state: HuntingState) -> Dict[str, Any]:
    db = get_database()
    prompt = state.get("prompt", "")
    
    # 1. Search Threat Indicators and Events matching the prompt (keywords)
    # Simple keyword search for MVP
    intel = []
    keywords = prompt.split()
    query = {"$or": [
        {"name": {"$regex": keywords[0], "$options": "i"}},
        {"description": {"$regex": keywords[0], "$options": "i"}},
        {"value": {"$regex": keywords[0], "$options": "i"}}
    ]} if keywords else {}
    
    cursor = db["threat_indicators"].find(query).limit(10)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        intel.append({"type": "indicator", "data": doc})
        
    cursor = db["threat_events"].find(query).limit(5)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        intel.append({"type": "event", "data": doc})
        
    return {"intel_context": intel}

async def search_local_node(state: HuntingState) -> Dict[str, Any]:
    db = get_database()
    # Find recent high severity alerts and incidents
    local = []
    
    cursor = db["alerts"].find({"severity": "high"}).sort("created_at", -1).limit(5)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        local.append({"type": "alert", "data": doc})
        
    cursor = db["assets"].find({}).limit(5) # Random assets for context
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        local.append({"type": "asset", "data": doc})
        
    return {"local_context": local}

async def generate_hunt_node(state: HuntingState) -> Dict[str, Any]:
    prompt = state.get("prompt", "")
    intel = state.get("intel_context", [])
    local = state.get("local_context", [])
    
    context_text = f"USER HUNT PROMPT: {prompt}\n\n"
    context_text += "THREAT INTELLIGENCE:\n"
    for i in intel:
        context_text += f"- {i['type']}: {json.dumps(i['data'])}\n"
        
    context_text += "\nLOCAL ENVIRONMENT STATE:\n"
    for l in local:
        context_text += f"- {l['type']}: {json.dumps(l['data'])}\n"
        
    llm_prompt = f"""
    You are a professional Threat Hunting Agent. Based on the provided prompt and context, propose hunting hypotheses and provide guidance.
    
    HYPOTHESES:
    - Propose 3 distinct hunting hypotheses related to the prompt.
    - Each hypothesis should be specific and detection-focused.
    
    GUIDANCE:
    - Provide plain English steps for a human analyst to verify these hypotheses.
    - Provide optional simple query templates (e.g. JSON-like pseudo-queries) where applicable.
    
    CONSTRAINTS:
    - Do NOT generate offensive payloads or weaponized steps.
    - Keep output defensive and explainable.
    
    CONTEXT:
    {context_text}
    """
    
    req = LLMRequest(
        messages=[Message(role="user", content=llm_prompt)],
        temperature=0.2,
        max_tokens=1000
    )
    
    try:
        res = await vertex_llm.generate(req)
        return {"guidance": res.content}
    except Exception as e:
        return {"error": f"LLM Generation failed: {str(e)}"}

# Construction
workflow = StateGraph(HuntingState)
workflow.add_node("search_intel", search_intel_node)
workflow.add_node("search_local", search_local_node)
workflow.add_node("generate", generate_hunt_node)

workflow.add_edge(START, "search_intel")
workflow.add_edge("search_intel", "search_local")
workflow.add_edge("search_local", "generate")
workflow.add_edge("generate", END)

hunting_graph = workflow.compile()

async def execute_hunting_agent(prompt: str, user_id: str, db) -> Dict[str, Any]:
    from app.services.agent.state import AgentRun
    
    run_record = AgentRun(
        user_id=user_id,
        agent_type="hunting_agent",
        status="running",
        state_snapshot={}
    )
    res = await db["agent_runs"].insert_one(run_record.model_dump(exclude={"id"}))
    run_id = str(res.inserted_id)
    
    initial_state = {
        "prompt": prompt,
        "intel_context": [],
        "local_context": [],
        "hypotheses": [],
        "guidance": "",
        "error": ""
    }
    
    final_state = await hunting_graph.ainvoke(initial_state)
    
    run_status = "failed" if final_state.get("error") else "completed"
    
    await db["agent_runs"].update_one(
        {"_id": ObjectId(run_id)},
        {"$set": {
            "status": run_status,
            "state_snapshot": {
                "intel_count": len(final_state.get("intel_context", [])),
                "local_count": len(final_state.get("local_context", []))
            },
            "result": final_state.get("guidance", ""),
            "error": final_state.get("error", "")
        }}
    )
    
    return {
        "run_id": run_id,
        "status": run_status,
        "result": final_state.get("guidance"),
        "error": final_state.get("error")
    }
