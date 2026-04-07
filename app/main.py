import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.jobs import router as jobs_router
from app.api.auth import router as auth_router
from app.api.repos import router as repos_router
from app.api.prs import router as prs_router
from app.queue.worker import start_worker_pool
import app.tasks.sample
import app.tasks.review

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(start_worker_pool())
    yield
    worker_task.cancel()

app = FastAPI(title="ReviewQ", lifespan=lifespan)
app.include_router(jobs_router)
app.include_router(auth_router)
app.include_router(repos_router)
app.include_router(prs_router)

@app.get("/health")
async def health():
    return {"status": "ok"}