import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.jobs import router as jobs_router
from app.queue.worker import start_worker_pool
import app.tasks.sample

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(start_worker_pool())
    yield
    worker_task.cancel()

app = FastAPI(title="ReviewQ", lifespan=lifespan)
app.include_router(jobs_router)

@app.get("/health")
async def health():
    return {"status": "ok"}