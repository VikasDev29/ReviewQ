import httpx
from sqlalchemy import select
from app.queue.registry import register_task
from app.database import AsyncSessionLocal
from app.models.pr import PullRequest
from app.models.user import User

@register_task("ai_review")
async def ai_review(pr_id: int, repo_full_name: str, pr_number: int, user_id: int) -> dict:
    async with AsyncSessionLocal() as db:
        pr = await db.get(PullRequest, pr_id)
        user = await db.get(User, user_id)
        if not pr or not user:
            raise ValueError("PR or user not found")

        # Fetch the actual diff from GitHub
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}",
                headers={
                    "Authorization": f"Bearer {user.access_token}",
                    "Accept": "application/vnd.github.diff",
                },
            )
            diff = resp.text

        pr.diff = diff[:10000]  # store first 10k chars

        # Simple placeholder review — Week 4 replaces this with real LLM call
        pr.ai_review = (
            f"Auto review for PR #{pr_number} in {repo_full_name}.\n"
            f"Diff size: {len(diff)} characters.\n"
            f"Full LLM review coming in Week 4."
        )

        await db.commit()

    return {"pr_id": pr_id, "diff_length": len(diff)}