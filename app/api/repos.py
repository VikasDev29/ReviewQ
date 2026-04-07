import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.repo import Repo

router = APIRouter(prefix="/repos", tags=["repos"])

@router.get("/{user_id}")
async def list_repos(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"Bearer {user.access_token}"},
            params={"sort": "updated", "per_page": 30},
        )
        github_repos = resp.json()

    synced = []
    for gr in github_repos:
        result = await db.execute(
            select(Repo).where(Repo.github_id == gr["id"])
        )
        repo = result.scalar_one_or_none()
        if not repo:
            repo = Repo(
                user_id=user_id,
                github_id=gr["id"],
                full_name=gr["full_name"],
                description=gr.get("description"),
                private=gr["private"],
            )
            db.add(repo)
        synced.append({
            "id": gr["id"],
            "full_name": gr["full_name"],
            "description": gr.get("description"),
            "private": gr["private"],
        })

    await db.commit()
    return synced