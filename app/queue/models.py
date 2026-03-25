import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class JobStatus(str, enum.Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    SUCCESS  = "success"
    RETRYING = "retrying"
    DEAD     = "dead"

class Job(Base):
    __tablename__ = "jobs"

    id:          Mapped[str]            = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_name:   Mapped[str]            = mapped_column(String, nullable=False)
    payload:     Mapped[dict]           = mapped_column(JSON, default=dict)
    status:      Mapped[JobStatus]      = mapped_column(SAEnum(JobStatus), default=JobStatus.PENDING)
    retries:     Mapped[int]            = mapped_column(Integer, default=0)
    max_retries: Mapped[int]            = mapped_column(Integer, default=3)
    result:      Mapped[dict | None]    = mapped_column(JSON, nullable=True)
    error:       Mapped[str | None]     = mapped_column(String, nullable=True)
    run_at:      Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)
    started_at:  Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)