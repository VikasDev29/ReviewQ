from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id:           Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    github_id:    Mapped[int]      = mapped_column(unique=True, nullable=False)
    username:     Mapped[str]      = mapped_column(String, nullable=False)
    email:        Mapped[str|None] = mapped_column(String, nullable=True)
    avatar_url:   Mapped[str|None] = mapped_column(String, nullable=True)
    access_token: Mapped[str]      = mapped_column(String, nullable=False)
    created_at:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)