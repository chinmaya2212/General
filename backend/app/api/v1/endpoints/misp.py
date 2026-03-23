from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from app.api.v1.dependencies import get_current_user, require_role
from app.models.user import UserResponse, RoleEnum
from app.models.ingest import IngestionJob, JobStatus
from app.integrations.misp.connector import MISPConnector, MISPConnectorError
from app.integrations.misp.mapper import map_misp_events_to_canonical
from app.models.domain import ThreatEvent, ThreatIndicator
from app.db.mongodb import get_database
from pydantic import ValidationError
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

connector = MISPConnector()

@router.get("/health")
async def misp_health_check(current_user: UserResponse = Depends(require_role([RoleEnum.admin, RoleEnum.analyst]))):
    is_healthy = await connector.check_health()
    return {"status": "ok" if is_healthy else "unavailable", "enabled": connector.enabled}

@router.post("/sync")
async def sync_misp(
    background_tasks: BackgroundTasks,
    offline_file: UploadFile = File(None),
    current_user: UserResponse = Depends(require_role([RoleEnum.admin, RoleEnum.analyst])),
    db = Depends(get_database)
):
    if offline_file:
        raw_data = await offline_file.read()
        if len(raw_data) > 20 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Offline file too large (>20MB)")
        try:
            events = connector.parse_offline_export(raw_data)
        except MISPConnectorError as e:
            raise HTTPException(status_code=400, detail=str(e))
        job_source = f"offline_file:{offline_file.filename}"
    else:
        if not connector.enabled:
            raise HTTPException(status_code=400, detail="MISP Connector is disabled in .env")
        try:
            events = await connector.fetch_recent_events(limit=500)
            job_source = "live_misp_api"
        except MISPConnectorError as e:
            raise HTTPException(status_code=502, detail=str(e))

    job = IngestionJob(
        user_id=current_user.id,
        filename=job_source,
        file_type="json",
        entity_type="misp_composite"
    )
    result = await db["ingestion_jobs"].insert_one(job.model_dump(exclude={"id"}))
    job.id = str(result.inserted_id)

    background_tasks.add_task(process_misp_ingestion, job, events, db)
    return {"message": "MISP Sync Job Started", "job_id": job.id, "source": job_source, "events_fetched": len(events)}

async def process_misp_ingestion(job: IngestionJob, misp_events: list, db):
    job.status = JobStatus.processing
    job.total_records = len(misp_events)
    await db["ingestion_jobs"].update_one({"_id": ObjectId(job.id)}, {"$set": job.model_dump(exclude={"id"})})
    
    threat_events_raw, threat_indicators_raw = map_misp_events_to_canonical(misp_events)
    
    successful_events, successful_indicators = [], []
    
    for row in threat_events_raw:
        try:
            row["source_metadata"]["ingestion_job_id"] = job.id
            successful_events.append(ThreatEvent(**row).model_dump(exclude={"id"}))
            job.successful_records += 1
        except ValidationError as e:
            job.failed_records += 1
            if len(job.errors) < 20: job.errors.append(f"Event failed: {e.errors()[0]['msg']}")
            
    for row in threat_indicators_raw:
        try:
            row["source_metadata"]["ingestion_job_id"] = job.id
            successful_indicators.append(ThreatIndicator(**row).model_dump(exclude={"id"}))
        except ValidationError:
            pass

    if successful_events:
        await db["threat_events"].insert_many(successful_events)
    if successful_indicators:
        await db["threat_indicators"].insert_many(successful_indicators)

    job.status = JobStatus.completed if job.failed_records == 0 else JobStatus.partial_success
    await db["ingestion_jobs"].update_one({"_id": ObjectId(job.id)}, {"$set": job.model_dump(exclude={"id"})})
