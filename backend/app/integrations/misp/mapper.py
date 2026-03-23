from typing import List, Dict, Any, Tuple

def map_misp_events_to_canonical(misp_events: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    threat_events = []
    threat_indicators = []

    for item in misp_events:
        event = item.get("Event", item) if isinstance(item, dict) else item
        
        if not isinstance(event, dict) or "info" not in event:
            continue

        tags = event.get("Tag", [])
        ttps = [t["name"] for t in tags if "mitre" in t.get("name", "").lower() or "attack" in t.get("name", "").lower()]
        primary_ttp = ttps[0] if ttps else "Unknown TTP"

        threat_event = {
            "actor": str(event.get("Threat_Level_ID") or "Unknown"),
            "ttp": primary_ttp,
            "timestamp": event.get("date", "2026-01-01T00:00:00Z"),
            "description": event.get("info", "No information provided"),
            "source_metadata": {
                "misp_id": event.get("id"),
                "misp_uuid": event.get("uuid"),
                "misp_info": event.get("info")
            }
        }
        threat_events.append(threat_event)

        attributes = event.get("Attribute", [])
        for attr in attributes:
            indicator_type = map_misp_type_to_canonical(attr.get("type", ""))
            if indicator_type:
                indicator = {
                    "type": indicator_type,
                    "value": attr.get("value", ""),
                    "confidence": "high" if str(event.get("threat_level_id", "")) in ["1", "2"] else "medium",
                    "valid_from": event.get("date"),
                    "source_metadata": {
                        "misp_event_id": event.get("id"),
                        "misp_attribute_id": attr.get("id")
                    }
                }
                threat_indicators.append(indicator)

    return threat_events, threat_indicators

def map_misp_type_to_canonical(misp_type: str) -> str:
    misp_type = misp_type.lower()
    if "ip" in misp_type:
        return "ip"
    if "domain" in misp_type or "hostname" in misp_type:
        return "domain"
    if "md5" in misp_type or "sha" in misp_type:
        return "file_hash"
    if "url" in misp_type:
        return "url"
    return ""
