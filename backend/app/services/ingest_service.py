import json
import csv
import io
import logging
from typing import Dict, Any
from pydantic import ValidationError
from app.models.domain import Asset, ThreatEvent, ThreatIndicator, Alert
from app.models.ingest import JobStatus, IngestionJob
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)

# Registry mapping explicit entity types to their Pydantic classes and target collections
ENTITY_REGISTRY: Dict[str, Dict[str, Any]] = {
    "asset": {"model": Asset, "collection": "assets"},
    "threat_event": {"model": ThreatEvent, "collection": "threat_events"},
    "threat_indicator": {"model": ThreatIndicator, "collection": "threat_indicators"},
    "alert": {"model": Alert, "collection": "alerts"}
}

async def process_ingestion(job: IngestionJob, raw_data: bytes, db):
    """
    Normalizes and ingests bulk data from CSV or JSON into explicit domain collections.
    Does not use a background queue for the MVP; relies on asyncio tasks.
    """
    registry_entry = ENTITY_REGISTRY.get(job.entity_type)
    if not registry_entry:
        await _fail_job(job, f"Unsupported entity type: {job.entity_type}", db)
        return

    model_class = registry_entry["model"]
    collection_name = registry_entry["collection"]
    collection = db[collection_name]

    try:
        if job.file_type == "json":
            records = json.loads(raw_data)
            if not isinstance(records, list):
                records = [records] # Handle single objects gracefully
        elif job.file_type == "csv":
            text_data = raw_data.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(text_data))
            records = [row for row in csv_reader]
        else:
            await _fail_job(job, f"Unsupported file type: {job.file_type}", db)
            return
    except Exception as e:
        await _fail_job(job, f"Failed to parse {job.file_type}: {str(e)}", db)
        return

    job.total_records = len(records)
    await _update_job(job, db, status=JobStatus.processing)

    successful_docs = []
    
    for idx, record in enumerate(records):
        try:
            # Map canonical metadata into the record
            record["source_metadata"] = {
                "ingestion_job_id": job.id,
                "original_filename": job.filename
            }
            # Normalize with strict pydantic model check
            parsed_record = model_class(**record)
            doc_to_save = parsed_record.model_dump(exclude={"id"}, exclude_unset=True)
            successful_docs.append(doc_to_save)
            job.successful_records += 1
        except ValidationError as v_err:
            job.failed_records += 1
            if len(job.errors) < 50:
                job.errors.append(f"Row {idx+1} Validation Error: {v_err.errors()[0]['msg']}")
    
    if successful_docs:
        await collection.insert_many(successful_docs)

    final_status = JobStatus.completed
    if job.failed_records > 0:
        final_status = JobStatus.partial_success if job.successful_records > 0 else JobStatus.failed

    await _update_job(job, db, status=final_status)

async def _fail_job(job: IngestionJob, error_msg: str, db):
    logger.error(f"Ingestion Job {job.id} failed: {error_msg}")
    job.errors.append(error_msg)
    await _update_job(job, db, status=JobStatus.failed)

async def _update_job(job: IngestionJob, db, status: JobStatus = None):
    from bson import ObjectId
    if status:
        job.status = status
    await db["ingestion_jobs"].update_one(
        {"_id": ObjectId(job.id)},
        {"$set": job.model_dump(exclude={"id"})}
    )
