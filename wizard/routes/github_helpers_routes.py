"""
GitHub helper routes for issue/PR automation workflows.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field


class IssueDraftRequest(BaseModel):
    repo: str
    title: str
    body: str
    labels: List[str] = Field(default_factory=list)
    dry_run: bool = True


class PRDraftRequest(BaseModel):
    repo: str
    title: str
    body: str
    base: str = "main"
    head: Optional[str] = None
    draft: bool = True
    dry_run: bool = True


def _gh_available() -> bool:
    return shutil.which("gh") is not None


def _gh_auth_status() -> Dict[str, Any]:
    if not _gh_available():
        return {"available": False, "authenticated": False, "detail": "gh CLI not found"}
    proc = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return {
        "available": True,
        "authenticated": proc.returncode == 0,
        "detail": (proc.stderr or proc.stdout or "").strip()[:1000],
    }


def create_github_helpers_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/github/helpers", tags=["github-helpers"], dependencies=dependencies)

    @router.get("/status")
    async def github_helpers_status():
        return {"success": True, "gh": _gh_auth_status()}

    @router.post("/issue/draft")
    async def draft_issue(payload: IssueDraftRequest):
        if not payload.repo.strip():
            raise HTTPException(status_code=400, detail="repo is required")
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="title is required")
        if not payload.body.strip():
            raise HTTPException(status_code=400, detail="body is required")

        cmd = ["gh", "issue", "create", "--repo", payload.repo, "--title", payload.title, "--body", payload.body]
        for label in payload.labels:
            if label:
                cmd.extend(["--label", label])

        if payload.dry_run:
            return {"success": True, "dry_run": True, "command": cmd}

        if not _gh_available():
            raise HTTPException(status_code=503, detail="gh CLI not found")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail=(proc.stderr or proc.stdout or "issue draft failed").strip())
        return {"success": True, "dry_run": False, "url": (proc.stdout or "").strip()}

    @router.post("/pr/draft")
    async def draft_pr(payload: PRDraftRequest):
        if not payload.repo.strip():
            raise HTTPException(status_code=400, detail="repo is required")
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="title is required")
        if not payload.body.strip():
            raise HTTPException(status_code=400, detail="body is required")

        cmd = ["gh", "pr", "create", "--repo", payload.repo, "--base", payload.base, "--title", payload.title, "--body", payload.body]
        if payload.head:
            cmd.extend(["--head", payload.head])
        if payload.draft:
            cmd.append("--draft")

        if payload.dry_run:
            return {"success": True, "dry_run": True, "command": cmd}

        if not _gh_available():
            raise HTTPException(status_code=503, detail="gh CLI not found")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail=(proc.stderr or proc.stdout or "pr draft failed").strip())
        return {"success": True, "dry_run": False, "url": (proc.stdout or "").strip()}

    return router
