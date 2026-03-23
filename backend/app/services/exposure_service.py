import logging
from typing import List, Dict, Any, Optional
from app.db.mongodb import get_database
from app.services.graph_service import query_entity_neighborhood
from bson import ObjectId

logger = logging.getLogger(__name__)

class ExposureService:
    async def get_top_exposures(self, db, limit: int = 10) -> List[Dict[str, Any]]:
        # This is a simplified exposure engine for the MVP.
        # It calculates scores on-the-fly for active assets.
        
        assets = await db["assets"].find({}).to_list(length=100)
        exposures = []
        
        for asset in assets:
            score_data = await self.calculate_exposure_score(asset, db)
            exposures.append(score_data)
            
        # Sort by total score descending
        exposures.sort(key=lambda x: x["base_score"], reverse=True)
        return exposures[:limit]

    async def get_asset_exposure(self, asset_id: str, db) -> Optional[Dict[str, Any]]:
        asset = await db["assets"].find_one({"_id": ObjectId(asset_id)})
        if not asset:
            # Try finding by string ID if ObjectId conversion failed in caller or if using external IDs
            asset = await db["assets"].find_one({"asset_id": asset_id})
            
        if not asset:
            return None
            
        return await self.calculate_exposure_score(asset, db)

    async def calculate_exposure_score(self, asset: Dict[str, Any], db) -> Dict[str, Any]:
        asset_id_str = str(asset["_id"])
        
        # 1. Base Multipliers
        criticality_map = {"low": 1.0, "medium": 1.5, "high": 2.0, "critical": 3.0}
        crit_factor = criticality_map.get(asset.get("criticality", "medium").lower(), 1.5)
        
        # 2. Vulnerability Severity
        # Find vulnerabilities affecting this asset
        vulns = await db["vulnerabilities"].find({"affected_asset_id": asset_id_str}).to_list(length=100)
        max_vuln_score = 0
        if vulns:
             max_vuln_score = max([v.get("cvss_score", 0) for v in vulns])
        
        # 3. Network Reachability (Knowledge Graph Check)
        neighborhood = await query_entity_neighborhood(asset_id_str, db)
        # Check if any inbound edges are from 'internet' or 'external' sources (mock logic)
        is_reachable = any(e["rel_type"] == "exposed_to" for e in neighborhood.get("inbound_edges", []))
        reachability_multiplier = 1.5 if is_reachable else 1.0
        
        # 4. Privilege Abuse Potential
        # Check if any identity has privilege on this asset
        has_privileged_access = any(e["rel_type"] == "has_privilege_on" for e in neighborhood.get("inbound_edges", []))
        privilege_multiplier = 1.2 if has_privileged_access else 1.0
        
        # Calculation
        # Base Score = Max Vuln Score * Criticality * Reachability * Privilege
        base_score = round(max_vuln_score * crit_factor * reachability_multiplier * privilege_multiplier, 2)
        
        # Explainability / Rationale
        rationale = []
        if max_vuln_score > 7: rationale.append(f"High-severity vulnerability detected (CVSS {max_vuln_score})")
        if crit_factor > 1.5: rationale.append(f"Asset is marked as {asset.get('criticality')} criticality")
        if is_reachable: rationale.append("Asset has direct external network exposure path")
        if has_privileged_access: rationale.append("Sensitive identity privileges mapped to this asset")
        
        remediation = []
        if vulns: remediation.append("Patch high-severity CVEs")
        if is_reachable: remediation.append("Restrict network ingress to known peering points")
        if has_privileged_access: remediation.append("Review and prune excessive administrative permissions")

        return {
            "asset_id": asset_id_str,
            "asset_name": asset.get("name") or asset.get("hostname"),
            "base_score": base_score,
            "metrics": {
                "criticality_factor": crit_factor,
                "max_cvss": max_vuln_score,
                "is_reachable": is_reachable,
                "privilege_risk": has_privileged_access
            },
            "rationale": rationale,
            "remediation_plan": remediation,
            "graph_summary": {
                "inbound_degree": neighborhood.get("degree", 0),
                "risk_edges": [e for e in neighborhood.get("inbound_edges", []) if e["rel_type"] in ["has_privilege_on", "exposed_to"]]
            }
        }

exposure_service = ExposureService()
