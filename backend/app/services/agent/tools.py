import json
import logging
from typing import Dict, Any, List
from app.db.mongodb import get_database
from bson import ObjectId

logger = logging.getLogger(__name__)

async def search_knowledge_base(query: str) -> str:
    db = get_database()
    from app.services.rag_service import semantic_search
    results = await semantic_search(query, None, db, limit=3)
    
    if not results:
        return "No relevant knowledge base entries found."
        
    out = []
    for r in results:
        out.append(f"Source Type: {r.get('source_type')} - Content: {r.get('content')}")
        
    return "\n\n".join(out)

async def _fetch_by_id(collection: str, doc_id: str) -> str:
    db = get_database()
    try:
        doc = await db[collection].find_one({"_id": ObjectId(doc_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return json.dumps(doc)
    except Exception:
        # Fallback to field-based heuristic lookup (like title/name match) if Id doesn't match ObjectId
        cursor = db[collection].find({"$or": [{"title": doc_id}, {"name": doc_id}]})
        docs = await cursor.to_list(length=1)
        if docs:
            docs[0]["_id"] = str(docs[0]["_id"])
            return json.dumps(docs[0])
            
    return f"No record found in {collection} for {doc_id}."

async def get_asset_context(asset_id: str) -> str:
    return await _fetch_by_id("assets", asset_id)
    
async def get_identity_context(username: str) -> str:
    db = get_database()
    doc = await db["identities"].find_one({"username": username})
    if doc:
        doc["_id"] = str(doc["_id"])
        return json.dumps(doc)
    return f"Identity {username} not found."

async def get_vulnerability_context(cve_id: str) -> str:
    db = get_database()
    doc = await db["vulnerabilities"].find_one({"cve_id": cve_id})
    if doc:
        doc["_id"] = str(doc["_id"])
        return json.dumps(doc)
    return await _fetch_by_id("vulnerabilities", cve_id)

async def get_misp_context(indicator: str) -> str:
    db = get_database()
    doc = await db["threat_indicators"].find_one({"value": indicator})
    if doc:
        doc["_id"] = str(doc["_id"])
        return json.dumps(doc)
    return f"MISP Context not found for indicator: {indicator}"

async def get_policy_control_context(policy_name: str) -> str:
    return await _fetch_by_id("policies", policy_name)

async def score_exposure(asset_id: str) -> str:
    # Deterministic mapping for MVP ensuring Graph bounds resolve strictly
    db = get_database()
    cursor = db["graph_edges"].find({"source_id": asset_id, "rel_type": "has_vulnerability"})
    edges = await cursor.to_list(length=5)
    if edges:
        return '{"exposure_score": "HIGH", "reason": "Asset has active associated vulnerabilities tracked."}'
    return '{"exposure_score": "LOW", "reason": "No direct active vulnerabilities identified."}'

async def create_incident_summary_draft(incident_id: str) -> str:
    val = await _fetch_by_id("incidents", incident_id)
    if "No record found" in val:
        return val
    try:
        parsed = json.loads(val)
        return f"DRAFT SUMMARY: Incident '{parsed.get('title')}' is currently {parsed.get('status')} with severity {parsed.get('severity')}."
    except Exception:
        return "Draft creation failed."

# Tool schema declarations binding directly for Vertex Parameter mappings
AGENT_TOOLS = [
    {"name": "search_knowledge_base", "description": "Search semantic chunked RAG knowledge base for policies, framework docs or control definitions.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "get_asset_context", "description": "Lookup full JSON parameters for an internal asset ID or hostname.", "parameters": {"type": "object", "properties": {"asset_id": {"type": "string"}}, "required": ["asset_id"]}},
    {"name": "get_identity_context", "description": "Lookup employee identity context resolving roles.", "parameters": {"type": "object", "properties": {"username": {"type": "string"}}, "required": ["username"]}},
    {"name": "get_vulnerability_context", "description": "Lookup Vulnerability context bridging CVE IDs.", "parameters": {"type": "object", "properties": {"cve_id": {"type": "string"}}, "required": ["cve_id"]}},
    {"name": "get_misp_context", "description": "Retrieve canonical indicators tracked from downstream MISP clusters.", "parameters": {"type": "object", "properties": {"indicator": {"type": "string"}}, "required": ["indicator"]}},
    {"name": "get_policy_control_context", "description": "Lookup rule constraints natively isolating GRC contexts.", "parameters": {"type": "object", "properties": {"policy_name": {"type": "string"}}, "required": ["policy_name"]}},
    {"name": "score_exposure", "description": "Iterative lookup evaluating graph boundaries summarizing asset exposure strings.", "parameters": {"type": "object", "properties": {"asset_id": {"type": "string"}}, "required": ["asset_id"]}},
    {"name": "create_incident_summary_draft", "description": "Parses attributes isolating preliminary Incident templates.", "parameters": {"type": "object", "properties": {"incident_id": {"type": "string"}}, "required": ["incident_id"]}}
]

async def execute_tool(name: str, args: dict) -> str:
    tools_map = {
        "search_knowledge_base": search_knowledge_base,
        "get_asset_context": get_asset_context,
        "get_identity_context": get_identity_context,
        "get_vulnerability_context": get_vulnerability_context,
        "get_misp_context": get_misp_context,
        "get_policy_control_context": get_policy_control_context,
        "score_exposure": score_exposure,
        "create_incident_summary_draft": create_incident_summary_draft
    }
    
    func = tools_map.get(name)
    if not func:
        return f"Tool {name} not found."
    try:
        return await func(**args)
    except Exception as e:
        logger.error(f"Tool execution failed Native Error: {str(e)}")
        return f"Tool execution failed: {str(e)}"
