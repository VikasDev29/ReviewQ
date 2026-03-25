import asyncio
from app.queue.registry import register_task

@register_task("add")
async def add(a: int, b: int) -> dict:
    await asyncio.sleep(0.1)
    return {"result": a + b}

@register_task("failing_task")
async def failing_task(**kwargs) -> dict:
    raise ValueError("Intentional failure — testing retry logic")