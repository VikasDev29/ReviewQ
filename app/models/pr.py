from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id:           Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    repo_id:      Mapped[int]      = mapped_column(ForeignKey("repos.id"), nullable=False)
    github_pr_id: Mapped[int]      = mapped_column(BigInteger, nullable=False)
    number:       Mapped[int]      = mapped_column(Integer, nullable=False)
    title:        Mapped[str]      = mapped_column(String, nullable=False)
    body:         Mapped[str|None] = mapped_column(Text, nullable=True)
    state:        Mapped[str]      = mapped_column(String, default="open")
    author:       Mapped[str]      = mapped_column(String, nullable=False)
    diff:         Mapped[str|None] = mapped_column(Text, nullable=True)
    ai_review:    Mapped[str|None] = mapped_column(Text, nullable=True)
    review_job_id:Mapped[str|None] = mapped_column(String, nullable=True)
    created_at:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)