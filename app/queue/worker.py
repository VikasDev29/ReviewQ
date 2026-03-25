import asyncio
import logging
from datetime import datetime
from app.database import AsyncSessionLocal
from app.queue.broker import broker
from app.queue.models import Job, JobStatus
from app.queue.registry import get_task
from app.config import settings

logger = logging.getLogger(__name__)

async def _run_job(job_id: str) -> None:
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            logger.warning(f"Job {job_id} not found in DB — skipping")
            return

        task_fn = get_task(job.task_name)
        if not task_fn:
            job.status = JobStatus.DEAD
            job.error = f"Unknown task: {job.task_name}"
            await db.commit()
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        await db.commit()

        try:
            result = await task_fn(**job.payload)
            job.status = JobStatus.SUCCESS
            job.result = result
            job.finished_at = datetime.utcnow()
            logger.info(f"Job {job_id} succeeded")

        except Exception as exc:
            job.retries += 1
            job.error = str(exc)
            logger.error(f"Job {job_id} failed (attempt {job.retries}): {exc}")

            if job.retries >= job.max_retries:
                job.status = JobStatus.DEAD
                job.finished_at = datetime.utcnow()
                logger.warning(f"Job {job_id} moved to dead letter queue")
            else:
                job.status = JobStatus.RETRYING
                delay = settings.retry_backoff_base ** job.retries
                await db.commit()
                await asyncio.sleep(delay)
                job.status = JobStatus.PENDING
                await broker.enqueue(job_id)

        await db.commit()


async def _worker_loop(worker_id: int) -> None:
    logger.info(f"Worker {worker_id} started")
    while True:
        job_id = await broker.dequeue(timeout=5)
        if job_id:
            logger.info(f"Worker {worker_id} picked up job {job_id}")
            await _run_job(job_id)


async def start_worker_pool() -> None:
    tasks = [
        asyncio.create_task(_worker_loop(i))
        for i in range(settings.worker_concurrency)
    ]
    await asyncio.gather(*tasks)