import json
import logging
from typing import TypedDict, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from app.db.mongodb import get_database
from app.services.agent.tools import (
    get_asset_context,
    get_identity_context,
    get_misp_context
)
from app.services.vertex_llm import vertex_llm, LLMRequest, Message
from bson import ObjectId

logger = logging.getLogger(__name__)

class TriageState(TypedDict):
    alert_id: str
    alert_data: Dict[str, Any]
    enriched_context: Dict[str, str]
    triage_result: str
    error: str

async def fetch_alert_node(state: TriageState) -> Dict[str, Any]:
    db = get_database()
    alert_id = state.get("alert_id")
    try:
        alert = await db["alerts"].find_one({"_id": ObjectId(alert_id)})
        if not alert:
            return {"error": f"Alert {alert_id} not found."}
        alert["_id"] = str(alert["_id"])
        return {"alert_data": alert}
    except Exception as e:
        return {"error": f"Invalid Alert ID or DB error: {str(e)}"}

async def enrich_context_node(state: TriageState) -> Dict[str, Any]:
    alert = state.get("alert_data", {})
    context_map = {}
    
    asset_id = alert.get("asset_id")
    if asset_id:
        context_map["asset"] = await get_asset_context(asset_id)
        
    identity_id = alert.get("identity_id")
    if identity_id:
        context_map["identity"] = await get_identity_context(identity_id)
        
    indicator = alert.get("indicator") # Assuming alert might carry generic IOC field
    if indicator:
        context_map["indicator"] = await get_misp_context(indicator)
        
    return {"enriched_context": context_map}

async def generate_triage_node(state: TriageState) -> Dict[str, Any]:
    alert = state.get("alert_data", {})
    context_map = state.get("enriched_context", {})
    
    context_text = f"ALERT DETAILS:\n{json.dumps(alert, indent=2)}\n\nCONTEXT:\n"
    for k, v in context_map.items():
        context_text += f"[{k.upper()}]: {v}\n"
        
    prompt = f"""
    Analyze the provided security alert and its enriched environment context.
    You are a defensive security responder. Do NOT generate offensive instructions or exploit steps.
    Ensure output is purely operational and structure cleanly.

    Provide a structured summary containing exactly:
    - Estimated Priority (Critical, High, Medium, Low)
    - Rationale (Why this priority was chosen citing context facts)
    - Next Actions (3-5 bullet points)
    
    ENVIRONMENT CONTEXT:
    {context_text}
    """
    
    req = LLMRequest(
        messages=[Message(role="user", content=prompt)],
        temperature=0.1,
        max_tokens=600
    )
    
    try:
        res = await vertex_llm.generate(req)
        return {"triage_result": res.content}
    except Exception as e:
        return {"error": f"LLM Generation failed: {str(e)}"}


def router_after_fetch(state: TriageState) -> str:
    if state.get("error"):
        return END
    return "enrich"

def router_after_enrich(state: TriageState) -> str:
    if state.get("error"):
        return END
    return "generate"


# Define explicit rigid DAG skipping LangChain unpredictable abstractions
workflow = StateGraph(TriageState)
workflow.add_node("fetch_alert", fetch_alert_node)
workflow.add_node("enrich_context", enrich_context_node)
workflow.add_node("generate_triage", generate_triage_node)

workflow.add_edge(START, "fetch_alert")
workflow.add_conditional_edges("fetch_alert", router_after_fetch, {"enrich": "enrich_context", END: END})
workflow.add_conditional_edges("enrich_context", router_after_enrich, {"generate": "generate_triage", END: END})
workflow.add_edge("generate_triage", END)

triage_graph = workflow.compile()

async def execute_triage_agent(alert_id: str, user_id: str, db) -> Dict[str, Any]:
    from app.services.agent.state import AgentRun
    
    run_record = AgentRun(
        user_id=user_id,
        agent_type="triage_agent",
        status="running",
        state_snapshot={}
    )
    res = await db["agent_runs"].insert_one(run_record.model_dump(exclude={"id"}))
    run_id = str(res.inserted_id)
    
    initial_state = {
        "alert_id": alert_id,
        "alert_data": {},
        "enriched_context": {},
        "triage_result": "",
        "error": ""
    }
    
    final_state = await triage_graph.ainvoke(initial_state)
    
    run_status = "failed" if final_state.get("error") else "completed"
    
    await db["agent_runs"].update_one(
        {"_id": ObjectId(run_id)},
        {"$set": {
            "status": run_status,
            "state_snapshot": {"enriched_context": final_state.get("enriched_context")},
            "result": final_state.get("triage_result", ""),
            "error": final_state.get("error", "")
        }}
    )
    
    return {
        "run_id": run_id,
        "status": run_status,
        "result": final_state.get("triage_result"),
        "error": final_state.get("error")
    }
