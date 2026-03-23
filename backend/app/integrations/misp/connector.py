import logging
import httpx
import json
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class MISPConnectorError(Exception):
    pass

class MISPConnector:
    def __init__(self):
        self.url = settings.MISP_URL.rstrip('/') if settings.MISP_URL else None
        self.api_key = settings.MISP_API_KEY.get_secret_value() if settings.MISP_API_KEY else None
        self.enabled = bool(self.url and self.api_key)

    async def check_health(self) -> bool:
        if not self.enabled:
            return False
            
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f"{self.url}/users/view/me",
                    headers={"Authorization": self.api_key, "Accept": "application/json"},
                    timeout=5.0
                )
                return response.status_code == 200
        except httpx.RequestError as e:
            logger.error(f"MISP Health check failed: {str(e)}")
            return False

    async def fetch_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.enabled:
            raise MISPConnectorError("MISP Connector is disabled in configuration.")

        logger.info(f"Fetching up to {limit} recent events from MISP")
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    f"{self.url}/events/restSearch",
                    headers={"Authorization": self.api_key, "Accept": "application/json", "Content-Type": "application/json"},
                    json={"returnFormat": "json", "limit": limit, "published": True},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", [])
        except httpx.HTTPStatusError as e:
            logger.error("MISP API HTTP error occurred (secrets omitted from logs)")
            raise MISPConnectorError("Failed to fetch events from MISP API")
        except Exception as e:
            logger.error(f"MISP Sync Error: {str(e)}")
            raise MISPConnectorError(f"MISP Connection failed: {str(e)}")

    def parse_offline_export(self, raw_data: bytes) -> List[Dict[str, Any]]:
        try:
            text_data = raw_data.decode('utf-8')
            parsed = json.loads(text_data)
            if isinstance(parsed, dict) and "response" in parsed:
                return parsed["response"]
            if isinstance(parsed, dict) and "Event" in parsed:
                return [parsed]
            if isinstance(parsed, list):
                return parsed
            return []
        except Exception as e:
            raise MISPConnectorError(f"Failed to parse offline MISP file: {str(e)}")
