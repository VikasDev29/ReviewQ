import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.repo import Repo
from app.models.pr import PullRequest
from app.queue.broker import broker
from app.queue.models import Job, JobStatus

router = APIRouter(prefix="/prs", tags=["pull requests"])

@router.get("/{user_id}/{repo_full_name:path}")
async def list_prs(user_id: int, repo_full_name: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.github.com/repos/{repo_full_name}/pulls",
            headers={"Authorization": f"Bearer {user.access_token}"},
            params={"state": "open", "per_page": 20},
        )
        github_prs = resp.json()

    result = await db.execute(
        select(Repo).where(Repo.full_name == repo_full_name)
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found — sync repos first")

    prs = []
    for gpr in github_prs:
        result = await db.execute(
            select(PullRequest).where(PullRequest.github_pr_id == gpr["id"])
        )
        pr = result.scalar_one_or_none()
        if not pr:
            pr = PullRequest(
                repo_id=repo.id,
                github_pr_id=gpr["id"],
                number=gpr["number"],
                title=gpr["title"],
                body=gpr.get("body"),
                state=gpr["state"],
                author=gpr["user"]["login"],
            )
            db.add(pr)
            await db.commit()
            await db.refresh(pr)

            # Enqueue AI review job via your task queue
            job = Job(
                task_name="ai_review",
                payload={
                    "pr_id": pr.id,
                    "repo_full_name": repo_full_name,
                    "pr_number": pr.number,
                    "user_id": user_id,
                },
            )
            db.add(job)
            await db.commit()
            await broker.enqueue(job.id)
            pr.review_job_id = job.id
            await db.commit()

        prs.append({
            "id": pr.id,
            "number": pr.number,
            "title": pr.title,
            "author": pr.author,
            "state": pr.state,
            "review_job_id": pr.review_job_id,
        })

    return prs

@router.get("/detail/{pr_id}")
async def get_pr(pr_id: int, db: AsyncSession = Depends(get_db)):
    pr = await db.get(PullRequest, pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    return {
        "id": pr.id,
        "title": pr.title,
        "author": pr.author,
        "state": pr.state,
        "body": pr.body,
        "diff": pr.diff,
        "ai_review": pr.ai_review,
        "review_job_id": pr.review_job_id,
    }