from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.queue.models import Job, JobStatus
from app.queue.broker import broker

router = APIRouter(prefix="/jobs", tags=["jobs"])

class EnqueueRequest(BaseModel):
    task_name: str
    payload: dict = {}
    max_retries: int = 3

@router.post("/", status_code=201)
async def enqueue_job(req: EnqueueRequest, db: AsyncSession = Depends(get_db)):
    job = Job(task_name=req.task_name, payload=req.payload, max_retries=req.max_retries)
    db.add(job)
    await db.commit()
    await broker.enqueue(job.id)
    return {"job_id": job.id, "status": job.status}

@router.get("/stats/queue")
async def queue_stats():
    depth = await broker.queue_depth()
    return {"queue_depth": depth}

@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).order_by(Job.run_at.desc()).limit(50))
    return result.scalars().all()

@router.delete("/{job_id}/cancel")
async def cancel_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job or job.status != JobStatus.PENDING:
        raise HTTPException(status_code=400, detail="Can only cancel pending jobs")
    job.status = JobStatus.DEAD
    job.error = "Cancelled by user"
    await db.commit()
    return {"cancelled": True}