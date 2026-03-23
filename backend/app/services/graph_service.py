import logging
from app.db.mongodb import get_database
from app.models.domain import GraphEdge
from typing import List, Dict, Any
from bson import ObjectId, errors

logger = logging.getLogger(__name__)

async def drop_and_rebuild_graph(db):
    """Calculates all explicit logic edges continuously scanning relationships mapped implicitly."""
    
    # 1. Truncate Graph collection explicitly.
    logger.info("Truncating current Graph edges...")
    await db["graph_edges"].delete_many({})
    
    edges: List[dict] = []
    
    # Helper to generate an edge natively
    def add_edge(source, target, rel_type, meta_props=None):
        if not source or not target:
            return
        edges.append({
            "source_id": str(source),
            "target_id": str(target),
            "rel_type": rel_type,
            "properties": meta_props or {}
        })

    # A. Asset <- Vulnerability
    cursor = db["vulnerabilities"].find({})
    async for vuln in cursor:
        if "affected_asset_id" in vuln and vuln["affected_asset_id"]:
            add_edge(vuln["affected_asset_id"], str(vuln["_id"]), "has_vulnerability")
            
    # B. Identity -> Asset
    cursor = db["identities"].find({})
    async for ident in cursor:
        for aid in ident.get("privileged_asset_ids", []):
            add_edge(str(ident["_id"]), aid, "has_privilege_on")
            
    # C. Alert -> Asset
    # D. Alert -> Incident
    cursor = db["alerts"].find({})
    async for alert in cursor:
        if alert.get("asset_id"):
            add_edge(str(alert["_id"]), alert["asset_id"], "relates_to")

    cursor = db["incidents"].find({})
    async for incident in cursor:
        for alert_id in incident.get("related_alert_ids", []):
            add_edge(alert_id, str(incident["_id"]), "linked_to")
        for asset_id in incident.get("affected_asset_ids", []):
            add_edge(str(incident["_id"]), asset_id, "affects")

    # E. ThreatEvent -> ThreatIndicator
    # We map back implicitly natively resolving metadata footprints mapping directly
    cursor = db["threat_indicators"].find({})
    async for ind in cursor:
        if ind.get("threat_event_id"):
            add_edge(ind["threat_event_id"], str(ind["_id"]), "contains_indicator")
        # Also map MISP lineage tracking explicitly. 
        # Source metadata structure parsing
        elif ind.get("source_metadata", {}).get("misp_event_id"):
           misp_id = ind["source_metadata"]["misp_event_id"]
           # Scan events
           ev = await db["threat_events"].find_one({"source_metadata.misp_id": misp_id})
           if ev:
               add_edge(str(ev["_id"]), str(ind["_id"]), "contains_indicator")

    # F. ThreatEvent -> Technique (Virtual Node Extraction)
    cursor = db["threat_events"].find({})
    async for ev in cursor:
        if ev.get("ttp"):
            technique_id = f"technique:{ev['ttp']}"
            add_edge(str(ev["_id"]), technique_id, "uses_technique")

    # G. Policy -> Control
    # H. Control -> Technique
    cursor = db["controls"].find({})
    async for ctrl in cursor:
        if ctrl.get("policy_id"):
             # Technically 'policy maps_to control' -> Source: policy, Target: control
             add_edge(ctrl["policy_id"], str(ctrl["_id"]), "maps_to")
        for ttp in ctrl.get("mitigates_ttps", []):
             add_edge(str(ctrl["_id"]), f"technique:{ttp}", "mitigates")

    if edges:
        await db["graph_edges"].insert_many(edges)
        
    logger.info(f"Graph rebuild complete. Wrote {len(edges)} edges.")
    return len(edges)

async def query_entity_neighborhood(entity_id: str, db) -> Dict[str, Any]:
    sources = [doc async for doc in db["graph_edges"].find({"target_id": entity_id})]
    targets = [doc async for doc in db["graph_edges"].find({"source_id": entity_id})]
    
    def format_edge(row):
        return {
            "source_id": row["source_id"],
            "target_id": row["target_id"],
            "rel_type": row["rel_type"]
        }
        
    return {
        "entity_id": entity_id,
        "inbound_edges": [format_edge(r) for r in sources],
        "outbound_edges": [format_edge(r) for r in targets],
        "degree": len(sources) + len(targets)
    }
