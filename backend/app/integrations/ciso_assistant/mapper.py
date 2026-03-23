from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

def map_ciso_to_canonical(grc_data: Dict[str, List[Dict[str, Any]]]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    policies, controls, frameworks = [], [], []

    for p in grc_data.get("policies", []):
        policy = {
            "title": p.get("name") or p.get("title") or "Unnamed Policy",
            "version": str(p.get("version", "1.0")),
            "status": p.get("status", "draft"),
            "objective": p.get("description") or "No objective defined",
            "source_metadata": {
                "ciso_id": p.get("id"),
                "ciso_type": "policy"
            }
        }
        policies.append(policy)

    for c in grc_data.get("controls", []):
        control = {
            "name": c.get("name") or c.get("ref") or "Unnamed Control",
            "description": c.get("description") or "No description",
            # Strict mapping expectation
            "policy_id": str(c.get("policy_id") or "unmapped_policy"), 
            "implementation_status": c.get("status", "not_implemented"),
            "source_metadata": {
                "ciso_id": c.get("id"),
                "ciso_type": "control"
            }
        }
        controls.append(control)

    for f in grc_data.get("frameworks", []):
        framework = {
            "name": f.get("name") or "Unnamed Framework",
            "version": str(f.get("version", "latest")),
            "description": f.get("description") or "No description",
            "source_metadata": {
                "ciso_id": f.get("id"),
                "ciso_type": "framework"
            }
        }
        frameworks.append(framework)

    return policies, controls, frameworks
