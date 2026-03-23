from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from app.api.v1.dependencies import get_current_user, require_role
from app.models.user import UserResponse, RoleEnum
from app.models.ingest import IngestionJob, JobStatus
from app.integrations.ciso_assistant.connector import CISOConnector, CISOConnectorError
from app.integrations.ciso_assistant.mapper import map_ciso_to_canonical
from app.models.domain import Policy, Control, Framework
from app.db.mongodb import get_database
from pydantic import ValidationError
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

connector = CISOConnector()

@router.get("/health")
async def ciso_health_check(current_user: UserResponse = Depends(require_role([RoleEnum.admin]))):
    is_healthy = await connector.check_health()
    return {"status": "ok" if is_healthy else "unavailable", "enabled": connector.enabled}

@router.post("/sync")
async def sync_ciso(
    background_tasks: BackgroundTasks,
    offline_file: UploadFile = File(None),
    current_user: UserResponse = Depends(require_role([RoleEnum.admin, RoleEnum.executive])),
    db = Depends(get_database)
):
    if offline_file:
        raw_data = await offline_file.read()
        if len(raw_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Offline file too large (>10MB)")
        try:
            grc_data = connector.parse_offline_export(raw_data)
        except CISOConnectorError as e:
            raise HTTPException(status_code=400, detail=str(e))
        job_source = f"offline_file:{offline_file.filename}"
    else:
        if not connector.enabled:
            raise HTTPException(status_code=400, detail="CISO Assistant Connector is disabled in configuration.")
        try:
            grc_data = await connector.fetch_compliance_data()
            job_source = "live_ciso_api"
        except CISOConnectorError as e:
            raise HTTPException(status_code=502, detail=str(e))

    job = IngestionJob(
        user_id=current_user.id,
        filename=job_source,
        file_type="json",
        entity_type="ciso_assistant_composite"
    )
    result = await db["ingestion_jobs"].insert_one(job.model_dump(exclude={"id"}))
    job.id = str(result.inserted_id)

    background_tasks.add_task(process_ciso_ingestion, job, grc_data, db)
    return {"message": "CISO Assistant Sync Started", "job_id": job.id, "source": job_source}

async def process_ciso_ingestion(job: IngestionJob, grc_data: dict, db):
    job.status = JobStatus.processing
    policies, controls, frameworks = map_ciso_to_canonical(grc_data)
    
    job.total_records = len(policies) + len(controls) + len(frameworks)
    await db["ingestion_jobs"].update_one({"_id": ObjectId(job.id)}, {"$set": job.model_dump(exclude={"id"})})
    
    succ_pol, succ_ctrl, succ_fw = [], [], []
    
    for row in policies:
        try:
            row["source_metadata"]["ingestion_job_id"] = job.id
            succ_pol.append(Policy(**row).model_dump(exclude={"id"}))
            job.successful_records += 1
        except ValidationError as e:
            job.failed_records += 1
            if len(job.errors) < 20: job.errors.append(f"Policy validation failed: {str(e)}")

    for row in controls:
        try:
            row["source_metadata"]["ingestion_job_id"] = job.id
            succ_ctrl.append(Control(**row).model_dump(exclude={"id"}))
            job.successful_records += 1
        except ValidationError as e:
            job.failed_records += 1
            if len(job.errors) < 20: job.errors.append(f"Control validation failed: {str(e)}")

    for row in frameworks:
        try:
            row["source_metadata"]["ingestion_job_id"] = job.id
            succ_fw.append(Framework(**row).model_dump(exclude={"id"}))
            job.successful_records += 1
        except ValidationError as e:
            job.failed_records += 1
            if len(job.errors) < 20: job.errors.append(f"Framework validation failed: {str(e)}")

    if succ_pol: await db["policies"].insert_many(succ_pol)
    if succ_ctrl: await db["controls"].insert_many(succ_ctrl)
    if succ_fw: await db["frameworks"].insert_many(succ_fw)

    job.status = JobStatus.completed if job.failed_records == 0 else JobStatus.partial_success
    await db["ingestion_jobs"].update_one({"_id": ObjectId(job.id)}, {"$set": job.model_dump(exclude={"id"})})
