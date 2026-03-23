from typing import Optional, List, Any, Dict
from pydantic import Field
from app.models.base import BaseDBModel
from enum import Enum

class AssetCriticality(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Asset(BaseDBModel):
    name: str
    type: str # e.g., "server", "workstation", "cloud_resource"
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    criticality: AssetCriticality = AssetCriticality.medium

class Identity(BaseDBModel):
    username: str
    email: str
    department: str
    is_active: bool = True
    privileged_asset_ids: List[str] = []

class Vulnerability(BaseDBModel):
    cve_id: Optional[str] = None
    severity: str
    cvss_score: Optional[float] = None
    description: str
    affected_asset_id: str

class Alert(BaseDBModel):
    title: str
    severity: str
    source: str
    detected_at: str
    status: str = "open"
    asset_id: Optional[str] = None

class Incident(BaseDBModel):
    title: str
    severity: str
    status: str = "investigating"
    related_alert_ids: List[str] = []
    affected_asset_ids: List[str] = []

class ThreatEvent(BaseDBModel):
    actor: Optional[str] = None
    ttp: str # MITRE ATT&CK technique code
    timestamp: str
    description: str

class ThreatIndicator(BaseDBModel):
    type: str # ip, domain, file_hash
    value: str
    confidence: str # low, medium, high
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    threat_event_id: Optional[str] = None

class Policy(BaseDBModel):
    title: str
    version: str
    status: str
    objective: str

class Control(BaseDBModel):
    name: str
    description: str
    policy_id: str
    implementation_status: str
    mitigates_ttps: List[str] = []

class Framework(BaseDBModel):
    name: str
    version: str
    description: str

class Assessment(BaseDBModel):
    target_id: str
    framework_id: str
    status: str
    findings_count: int = 0

class Document(BaseDBModel):
    title: str
    content: str
    document_type: str
    tags: List[str] = []

class GraphEdge(BaseDBModel):
    source_id: str
    target_id: str
    rel_type: str # e.g., "owns", "runs_on", "mitigates"
    properties: Dict[str, Any] = {}

class ChatSession(BaseDBModel):
    user_id: str
    title: str
    message_history: List[Dict[str, str]] = []

class AgentRun(BaseDBModel):
    agent_name: str
    status: str # running, failed, completed
    inputs: Dict[str, Any] = {}
    outputs: Dict[str, Any] = {}
    error: Optional[str] = None
