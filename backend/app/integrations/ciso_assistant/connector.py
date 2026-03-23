import logging
import httpx
import json
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class CISOConnectorError(Exception):
    pass

class CISOConnector:
    def __init__(self):
        self.url = settings.CISO_ASSISTANT_URL.rstrip('/') if settings.CISO_ASSISTANT_URL else None
        self.api_key = settings.CISO_ASSISTANT_API_KEY.get_secret_value() if settings.CISO_ASSISTANT_API_KEY else None
        self.enabled = bool(self.url and self.api_key)

    async def check_health(self) -> bool:
        if not self.enabled:
            return False
            
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f"{self.url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5.0
                )
                return response.status_code == 200
        except httpx.RequestError as e:
            logger.error(f"CISO Assistant Health check failed: {str(e)}")
            return False

    async def fetch_compliance_data(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.enabled:
            raise CISOConnectorError("CISO Assistant Connector is disabled in configuration.")

        try:
            async with httpx.AsyncClient(verify=False) as client:
                headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
                
                # Fetch Policies (Using hypothetical standardized paths for MVP)
                r_policies = await client.get(f"{self.url}/api/v1/policies", headers=headers, timeout=10.0)
                r_policies.raise_for_status()
                policies = r_policies.json().get("items", []) if "items" in r_policies.json() else r_policies.json()
                
                # Fetch Controls
                r_controls = await client.get(f"{self.url}/api/v1/controls", headers=headers, timeout=10.0)
                r_controls.raise_for_status()
                controls = r_controls.json().get("items", []) if "items" in r_controls.json() else r_controls.json()
                
                # Fetch Frameworks
                r_fw = await client.get(f"{self.url}/api/v1/frameworks", headers=headers, timeout=10.0)
                r_fw.raise_for_status()
                frameworks = r_fw.json().get("items", []) if "items" in r_fw.json() else r_fw.json()
                
                return {
                    "policies": policies,
                    "controls": controls,
                    "frameworks": frameworks
                }

        except httpx.HTTPStatusError as e:
            logger.error("CISO API HTTP error occurred (secrets omitted from logs)")
            raise CISOConnectorError("Failed to fetch governance data from CISO Assistant")
        except Exception as e:
            logger.error(f"CISO Sync Error: {str(e)}")
            raise CISOConnectorError(f"CISO Assistant Connection failed: {str(e)}")

    def parse_offline_export(self, raw_data: bytes) -> Dict[str, List[Dict[str, Any]]]:
        try:
            text_data = raw_data.decode('utf-8')
            parsed = json.loads(text_data)
            
            policies = parsed.get("policies", [])
            controls = parsed.get("controls", [])
            frameworks = parsed.get("frameworks", [])
            
            return {
                "policies": policies,
                "controls": controls,
                "frameworks": frameworks
            }
        except Exception as e:
            raise CISOConnectorError(f"Failed to parse offline CISO export: {str(e)}")
