import redis.asyncio as aioredis
from app.config import settings

QUEUE_KEY = "reviewq:jobs"

class RedisBroker:
    def __init__(self):
        self.redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    async def enqueue(self, job_id: str) -> None:
        await self.redis.rpush(QUEUE_KEY, job_id)

    async def dequeue(self, timeout: int = 5) -> str | None:
        result = await self.redis.blpop(QUEUE_KEY, timeout=timeout)
        if result:
            _, job_id = result
            return job_id
        return None

    async def queue_depth(self) -> int:
        return await self.redis.llen(QUEUE_KEY)

broker = RedisBroker()