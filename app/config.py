from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost/reviewq"
    redis_url: str = "redis://localhost:6379"
    worker_concurrency: int = 4
    max_retries: int = 3
    retry_backoff_base: float = 2.0

    class Config:
        env_file = ".env"

settings = Settings()