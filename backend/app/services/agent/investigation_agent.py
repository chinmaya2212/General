import json
import logging
from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END
from app.db.mongodb import get_database
from app.services.vertex_llm import vertex_llm, LLMRequest, Message
from app.services.graph_service import query_entity_neighborhood
from bson import ObjectId

logger = logging.getLogger(__name__)

class InvestigationState(TypedDict):
    entity_id: str
    entity_type: str # 'alert' or 'incident'
    entity_data: Dict[str, Any]
    related_entities: List[Dict[str, Any]]
    graph_context: List[Dict[str, Any]]
    investigation_narrative: str
    evidence_links: List[str]
    error: str

async def load_entity_node(state: InvestigationState) -> Dict[str, Any]:
    db = get_database()
    eid = state.get("entity_id")
    etype = state.get("entity_type")
    
    collection = "alerts" if etype == "alert" else "incidents"
    try:
        doc = await db[collection].find_one({"_id": ObjectId(eid)})
        if not doc:
            return {"error": f"{etype.capitalize()} {eid} not found."}
        doc["_id"] = str(doc["_id"])
        return {"entity_data": doc}
    except Exception as e:
        return {"error": f"Invalid ID or DB error: {str(e)}"}

async def correlation_search_node(state: InvestigationState) -> Dict[str, Any]:
    db = get_database()
    entity = state.get("entity_data", {})
    eid = state.get("entity_id")
    
    # 1. Fetch Neighborhood from Knowledge Graph
    neighborhood = await query_entity_neighborhood(eid, db)
    
    # 2. Find siblings (alerts sharing the same asset or identity)
    asset_id = entity.get("asset_id")
    identity_id = entity.get("identity_id")
    
    related = []
    if asset_id:
        cursor = db["alerts"].find({"asset_id": asset_id, "_id": {"$ne": ObjectId(eid)}})
        async for a in cursor:
            a["_id"] = str(a["_id"])
            related.append({"type": "alert", "data": a, "reason": "shared_asset"})
            
    if identity_id:
        cursor = db["alerts"].find({"identity_id": identity_id, "_id": {"$ne": ObjectId(eid)}})
        async for a in cursor:
            a["_id"] = str(a["_id"])
            related.append({"type": "alert", "data": a, "reason": "shared_identity"})
            
    return {
        "related_entities": related,
        "graph_context": neighborhood.get("inbound_edges", []) + neighborhood.get("outbound_edges", [])
    }

async def generate_narrative_node(state: InvestigationState) -> Dict[str, Any]:
    entity = state.get("entity_data", {})
    related = state.get("related_entities", [])
    graph_edges = state.get("graph_context", [])
    
    context_text = f"PRIMARY ENTITY:\n{json.dumps(entity, indent=2)}\n\n"
    context_text += f"RELATED ENTITIES ({len(related)}):\n"
    for r in related[:5]:
        context_text += f"- [{r['reason']}] {r['type']}: {r['data'].get('title')}\n"
        
    context_text += f"\nGRAPH RELATIONSHIPS:\n"
    for edge in graph_edges[:10]:
        context_text += f"- {edge.get('source_type')} ({edge.get('source_id')}) --[{edge.get('rel_type')}]--> {edge.get('target_type')} ({edge.get('target_id')})\n"
        
    prompt = f"""
    Perform a deep investigation and correlation analysis for the provided security data.
    Identify likely shared indicators, techniques, or campaigns.
    Produce a concise investigation narrative and a summary timeline of events.
    Highlight linked evidence clearly.

    INVESTIGATION DATA:
    {context_text}

    Format your response as:
    1. Investigation Narrative (The story of what happened)
    2. Correlation Findings (Shared patterns identified)
    3. Suggested Timeline
    4. Evidence Links (List of linked entity IDs)
    5. Confidence Notes
    """
    
    req = LLMRequest(
        messages=[Message(role="user", content=prompt)],
        temperature=0.2,
        max_tokens=1000
    )
    
    try:
        res = await vertex_llm.generate(req)
        # Extract ID-like strings for evidence links as a simple heuristic
        import re
        links = list(set(re.findall(r'[0-9a-fA-F]{24}', res.content)))
        
        return {
            "investigation_narrative": res.content,
            "evidence_links": links
        }
    except Exception as e:
        return {"error": f"LLM Generation failed: {str(e)}"}

def should_continue(state: InvestigationState) -> str:
    if state.get("error"):
        return END
    return "correlate"

def should_generate(state: InvestigationState) -> str:
    if state.get("error"):
        return END
    return "generate"

# Construction
workflow = StateGraph(InvestigationState)
workflow.add_node("load", load_entity_node)
workflow.add_node("correlate", correlation_search_node)
workflow.add_node("generate", generate_narrative_node)

workflow.add_edge(START, "load")
workflow.add_conditional_edges("load", should_continue, {"correlate": "correlate", END: END})
workflow.add_conditional_edges("correlate", should_generate, {"generate": "generate", END: END})
workflow.add_edge("generate", END)

investigation_graph = workflow.compile()

async def execute_investigation_agent(entity_id: str, entity_type: str, user_id: str, db) -> Dict[str, Any]:
    from app.services.agent.state import AgentRun
    
    run_record = AgentRun(
        user_id=user_id,
        agent_type="investigation_agent",
        status="running",
        state_snapshot={}
    )
    res = await db["agent_runs"].insert_one(run_record.model_dump(exclude={"id"}))
    run_id = str(res.inserted_id)
    
    initial_state = {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "entity_data": {},
        "related_entities": [],
        "graph_context": [],
        "investigation_narrative": "",
        "evidence_links": [],
        "error": ""
    }
    
    final_state = await investigation_graph.ainvoke(initial_state)
    
    run_status = "failed" if final_state.get("error") else "completed"
    
    await db["agent_runs"].update_one(
        {"_id": ObjectId(run_id)},
        {"$set": {
            "status": run_status,
            "state_snapshot": {
                "related_count": len(final_state.get("related_entities", [])),
                "edge_count": len(final_state.get("graph_context", []))
            },
            "result": final_state.get("investigation_narrative", ""),
            "error": final_state.get("error", "")
        }}
    )
    
    return {
        "run_id": run_id,
        "status": run_status,
        "result": final_state.get("investigation_narrative"),
        "evidence_links": final_state.get("evidence_links"),
        "error": final_state.get("error")
    }
