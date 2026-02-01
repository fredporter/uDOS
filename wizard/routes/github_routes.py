"""
GitHub CLI routes for Wizard Server.
"""

from typing import Callable, Awaitable, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.github_integration import GitHubIntegration

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_github_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/github", tags=["github"])
    gh = GitHubIntegration()

    class IssueCreate(BaseModel):
        title: str
        body: str
        labels: Optional[list[str]] = None

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        if not gh.available:
            return {
                "status": "unavailable",
                "error": gh.error_message,
            }
        try:
            info = gh.get_repo_info()
            return {
                "status": "ok",
                "repo": info.get("name"),
                "owner": info.get("owner", {}).get("login"),
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    @router.post("/sync-cli")
    async def sync_repository(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return gh.sync_repo()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/issues")
    async def get_issues(request: Request, state: str = "open"):
        if auth_guard:
            await auth_guard(request)
        if not gh.available:
            raise HTTPException(status_code=503, detail=gh.error_message)
        try:
            issues = gh.get_issues(state)
            return {"issues": issues, "count": len(issues)}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/issues")
    async def create_issue(request: Request, issue: IssueCreate):
        if auth_guard:
            await auth_guard(request)
        if not gh.available:
            raise HTTPException(status_code=503, detail=gh.error_message)
        try:
            return gh.create_issue(
                title=issue.title, body=issue.body, labels=issue.labels
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/pulls")
    async def get_pull_requests(request: Request, state: str = "open"):
        if auth_guard:
            await auth_guard(request)
        if not gh.available:
            raise HTTPException(status_code=503, detail=gh.error_message)
        try:
            prs = gh.get_pull_requests(state)
            return {"pull_requests": prs, "count": len(prs)}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/context/devlog")
    async def get_devlog(request: Request, month: Optional[str] = None):
        if auth_guard:
            await auth_guard(request)
        return {"month": month, "content": gh.get_devlog(month)}

    @router.get("/context/roadmap")
    async def get_roadmap(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"content": gh.get_roadmap()}

    @router.get("/context/agents")
    async def get_agents_doc(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"content": gh.get_agents_doc()}

    @router.get("/context/copilot")
    async def get_copilot_instructions(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"content": gh.get_copilot_instructions()}

    @router.get("/logs/{log_type}")
    async def get_logs(log_type: str, request: Request, lines: int = 50):
        if auth_guard:
            await auth_guard(request)
        try:
            content = gh.search_logs(log_type, lines)
            return {"log_type": log_type, "lines": lines, "content": content}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
