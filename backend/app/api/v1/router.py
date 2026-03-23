from fastapi import APIRouter
from app.api.v1.endpoints import (
    health, auth, ingest, misp, ciso_assistant, 
    graph, rag, agents, chat, exposures, kpis,
    alerts, incidents, system
)



api_router = APIRouter()

# Grouping tags logic for OpenAPI
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
api_router.include_router(misp.router, prefix="/ingest/misp", tags=["MISP Integration"])
api_router.include_router(ciso_assistant.router, prefix="/ingest/ciso-assistant", tags=["GRC Integration"])
api_router.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG & Knowledge Retrieval"])
api_router.include_router(agents.router, prefix="/agents", tags=["AI Agents"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Copilot"])
api_router.include_router(exposures.router, prefix="/exposures", tags=["Exposure Management"])
api_router.include_router(kpis.router, prefix="/kpis", tags=["KPIs & Reporting"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(system.router, prefix="/system", tags=["System Management"])



