from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:password@localhost/reviewq"
    redis_url: str = "redis://localhost:6379"
    worker_concurrency: int = 4
    max_retries: int = 3
    retry_backoff_base: float = 2.0
    github_client_id: str = ""
    github_client_secret: str = ""
    secret_key: str = "supersecretkey123"

settings = Settings()