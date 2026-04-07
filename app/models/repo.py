from sqlalchemy import String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base

class Repo(Base):
    __tablename__ = "repos"

    id:          Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    user_id:     Mapped[int]      = mapped_column(ForeignKey("users.id"), nullable=False)
    github_id:   Mapped[int]      = mapped_column(BigInteger, nullable=False)
    full_name:   Mapped[str]      = mapped_column(String, nullable=False)
    description: Mapped[str|None] = mapped_column(String, nullable=True)
    private:     Mapped[bool]     = mapped_column(default=False)
    synced_at:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)