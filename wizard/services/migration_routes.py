"""
Goblin-to-Wizard migration route stubs.

Adds placeholder routers for GitHub, AI, Workflow, and Notion endpoints using
Wizard auth scopes and secret store. These are scaffolds only; wire into
`wizard/server.py` when ready.
"""

from __future__ import annotations

import hmac
import hashlib
from typing import Optional, Dict, Any

from wizard.services.logging_manager import get_logger
from wizard.services.secret_store import get_secret_store, SecretStoreError

try:
    from fastapi import APIRouter, HTTPException, Header, Request, Body, Depends

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    APIRouter = None
    HTTPException = Exception
    Header = Request = Body = Depends = None
    FASTAPI_AVAILABLE = False

logger = get_logger("migration-routes")


class ScopeChecker:
    """Dependency to enforce auth scopes (placeholder)."""

    def __init__(self, scope: str):
        self.scope = scope

    async def __call__(self, x_wizard_scope: Optional[str] = Header(None)):
        if not x_wizard_scope or self.scope not in x_wizard_scope.split(","):
            raise HTTPException(status_code=403, detail=f"Missing scope: {self.scope}")


def _redact(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Redact obvious secret fields for logging."""
    redacted = {}
    for k, v in payload.items():
        if k.lower() in {"token", "secret", "authorization"}:
            redacted[k] = "[redacted]"
        else:
            redacted[k] = v
    return redacted


def _get_secret_value(key_id: str) -> Optional[str]:
    try:
        store = get_secret_store()
        store.unlock()
        entry = store.get(key_id)
        return entry.value if entry else None
    except SecretStoreError as exc:
        logger.warning("[WIZ] secret unavailable", extra={"key_id": key_id, "error": str(exc)})
        return None


def create_github_router() -> APIRouter:
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI required for router creation")

    router = APIRouter(prefix="/api/v1/github", tags=["github"])

    @router.get("/status", dependencies=[Depends(ScopeChecker("github:read"))])
    async def github_status():
        return {"status": "ok", "message": "GitHub service scaffold", "webhooks": "ready"}

    @router.post(
        "/webhook",
        dependencies=[Depends(ScopeChecker("github:webhook"))],
    )
    async def github_webhook(request: Request, x_hub_signature_256: Optional[str] = Header(None)):
        payload = await request.body()
        secret = _get_secret_value("github-webhook-secret")
        if not secret:
            raise HTTPException(status_code=503, detail="Webhook secret not configured")

        expected = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        if expected != (x_hub_signature_256 or ""):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        logger.info("[WIZ] github webhook received", extra={"sig": "ok"})
        return {"status": "accepted"}

    return router


def create_ai_router() -> APIRouter:
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI required for router creation")

    router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

    @router.post(
        "/route",
        dependencies=[Depends(ScopeChecker("ai:route"))],
    )
    async def ai_route(request: Dict[str, Any] = Body(...)):
        logger.info("[WIZ] ai route request", extra={"payload": _redact(request)})
        return {"status": "stub", "message": "Route via Wizard model router"}

    return router


def create_workflow_router() -> APIRouter:
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI required for router creation")

    router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

    @router.get("/", dependencies=[Depends(ScopeChecker("workflow:read"))])
    async def list_workflows():
        return {"items": [], "message": "Workflow service scaffold"}

    @router.post("/", dependencies=[Depends(ScopeChecker("workflow:write"))])
    async def create_workflow(body: Dict[str, Any] = Body(...)):
        logger.info("[WIZ] workflow create", extra={"payload": _redact(body)})
        return {"status": "stub", "received": True}

    return router


def create_notion_router() -> APIRouter:
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI required for router creation")

    router = APIRouter(prefix="/api/v1/notion", tags=["notion"], include_in_schema=False)

    @router.post(
        "/webhook",
        dependencies=[Depends(ScopeChecker("notion:sync"))],
    )
    async def notion_webhook(body: Dict[str, Any] = Body(...)):
        logger.info("[WIZ] notion webhook", extra={"payload": _redact(body)})
        return {"status": "stub", "feature_flag": "NOTION_SYNC_ENABLED"}

    return router
