"""
Notion sync routes for Wizard Server.
"""

from typing import Callable, Awaitable, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.notion_sync_service import NotionSyncService

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_notion_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/notion", tags=["notion-sync"])
    notion_sync = NotionSyncService()

    class WebhookVerify(BaseModel):
        secret: Optional[str] = None

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        return {"status": "ok", "notion_sync": "ready"}

    @router.post("/webhook")
    async def notion_webhook(request: Request):
        """Receive Notion webhook events."""
        if auth_guard:
            await auth_guard(request)
        try:
            body = await request.json()
            return notion_sync.handle_webhook(body)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/sync/status")
    async def sync_status(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return notion_sync.get_sync_status()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/sync/pending")
    async def get_pending_items(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return notion_sync.get_pending_items()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/sync/manual")
    async def manual_sync(request: Request):
        if auth_guard:
            await auth_guard(request)
        try:
            return notion_sync.manual_sync()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/maps")
    async def get_mappings(request: Request, limit: int = 12):
        if auth_guard:
            await auth_guard(request)
        try:
            return notion_sync.get_local_notion_maps(limit=limit)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router
