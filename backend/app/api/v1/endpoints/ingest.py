from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from app.api.v1.dependencies import get_current_user
from app.models.user import UserResponse
from app.models.ingest import IngestionJob
from app.services.ingest_service import process_ingestion, ENTITY_REGISTRY
from app.db.mongodb import get_database
import os

router = APIRouter()

@router.post("/files", response_model=IngestionJob)
async def upload_ingestion_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    entity_type: str = Form(...),
    current_user: UserResponse = Depends(require_role([RoleEnum.admin])),
    db = Depends(get_database)

):
    if entity_type not in ENTITY_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unsupported entity_type. Choose from {list(ENTITY_REGISTRY.keys())}")
        
    ext = file.filename.split('.')[-1].lower()
    if ext not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Only .json and .csv files are supported for MVP.")

    raw_data = await file.read()
    
    if len(raw_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum 10MB limit.")

    job = IngestionJob(
        user_id=current_user.id,
        filename=file.filename,
        file_type=ext,
        entity_type=entity_type
    )
    
    result = await db["ingestion_jobs"].insert_one(job.model_dump(exclude={"id"}))
    job.id = str(result.inserted_id)
    
    background_tasks.add_task(process_ingestion, job, raw_data, db)
    
    return job

@router.post("/load-seed-data")
async def load_seed_data(
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Loads default seed data out of the project folder."""
    seed_files = [
        {"file": "example_assets.csv", "type": "asset"},
        {"file": "example_threats.json", "type": "threat_event"},
        {"file": "example_policies.json", "type": "policy"},
        {"file": "example_vulnerabilities.json", "type": "vulnerability"}
    ]


    
    jobs_triggered = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../seed_data"))
    
    for s in seed_files:
        path = os.path.join(base_dir, s["file"])
        if not os.path.exists(path):
            continue
            
        with open(path, "rb") as f:
            raw_data = f.read()
            
        ext = s["file"].split('.')[-1]
        job = IngestionJob(
            user_id=current_user.id,
            filename=s["file"],
            file_type=ext,
            entity_type=s["type"]
        )
        result = await db["ingestion_jobs"].insert_one(job.model_dump(exclude={"id"}))
        job.id = str(result.inserted_id)
        jobs_triggered.append(job)
        
        background_tasks.add_task(process_ingestion, job, raw_data, db)
        
    return {"message": f"Triggered {len(jobs_triggered)} seed ingestion jobs", "jobs": jobs_triggered}

from app.services.graph_service import drop_and_rebuild_graph

@router.post("/rebuild-graph")
async def rebuild_graph(
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Triggers a synchronous rebuild of the security knowledge graph."""
    edges_count = await drop_and_rebuild_graph(db)
    return {"message": "Graph rebuilt successfully", "edges_created": edges_count}
