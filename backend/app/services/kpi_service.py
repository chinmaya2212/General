import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.db.mongodb import get_database
from app.services.exposure_service import exposure_service

logger = logging.getLogger(__name__)

class KPIService:
    async def get_summary(self, db) -> Dict[str, Any]:
        # 1. Open Alerts & Incidents
        open_alerts = await db["alerts"].count_documents({"status": {"$in": ["new", "open", "triaged"]}})
        open_incidents = await db["incidents"].count_documents({"status": {"$in": ["new", "open", "investigating"]}})
        
        # 2. Exposure Metrics
        top_exposures = await exposure_service.get_top_exposures(db, limit=5)
        avg_exposure = 0
        if top_exposures:
            avg_exposure = round(sum([e["base_score"] for e in top_exposures]) / len(top_exposures), 2)
            
        # 3. Policy & Control Gaps
        total_policies = await db["policies"].count_documents({})
        # Mock gap calculation: assume controls missing mapping to policies
        # In a real system, we'd check the mapping collection
        control_count = await db["controls"].count_documents({})
        
        # 4. Threat Intel Activity
        misp_events = await db["threat_events"].count_documents({
            "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })

        return {
            "timestamp": datetime.utcnow(),
            "alerts": {
                "open_count": open_alerts,
                "critical_count": await db["alerts"].count_documents({"severity": "critical", "status": {"$ne": "closed"}})
            },
            "incidents": {
                "active_count": open_incidents,
                "mttr_hours_avg": 4.5 # Mock MTTR
            },
            "exposure": {
                "avg_top_score": avg_exposure,
                "highly_exposed_assets": len([e for e in top_exposures if e["base_score"] > 20])
            },
            "governance": {
                "total_policies": total_policies,
                "total_controls": control_count,
                "coverage_percent": 85 # Mock coverage
            },
            "threat_intel": {
                "recent_misp_events": misp_events,
                "new_indicators": 124 # Mock
            },
            "executive_summary": self.generate_executive_summary(open_alerts, open_incidents, avg_exposure)
        }

    def generate_executive_summary(self, alerts: int, incidents: int, exposure: float) -> str:
        status = "Healthy"
        if incidents > 5 or exposure > 25:
            status = "Elevated Risk"
        elif alerts > 50:
            status = "Caution"
            
        return f"Overall Security Posture: {status}. Active Incidents: {incidents}. Mean Exposure Score: {exposure}."

    async def get_trends(self, db) -> List[Dict[str, Any]]:
        # Mock trend data for last 7 days
        trends = []
        base_date = datetime.utcnow().date()
        for i in range(7):
            date = base_date - timedelta(days=6-i)
            trends.append({
                "date": date.isoformat(),
                "alert_count": 10 + (i * 2),
                "incident_count": 1 + (i % 2),
                "avg_exposure": 15 + i
            })
        return trends

kpi_service = KPIService()
