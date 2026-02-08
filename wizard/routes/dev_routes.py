"""
Dev Mode routes for Wizard Server.
"""

import secrets
from typing import Callable, Awaitable, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from wizard.services.dev_mode_service import get_dev_mode_service
from wizard.services.logging_api import get_logger, new_corr_id

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


class GitHubPATRequest(BaseModel):
    token: str


class WebhookSecretResponse(BaseModel):
    secret: str
    length: int


def create_dev_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/dev", tags=["dev-mode"])
    dev_mode = get_dev_mode_service()
    logger = get_logger("wizard", category="dev-mode", name="dev")

    def _ensure_admin_dev_access():
        try:
            from core.services.user_service import get_user_manager, Permission

            user_mgr = get_user_manager()
            if not user_mgr.has_permission(Permission.ADMIN):
                raise HTTPException(status_code=403, detail="Admin role required for dev mode")
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    def _ensure_dev_submodule():
        message = dev_mode.ensure_requirements()
        if message:
            raise HTTPException(status_code=412, detail=message)

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        logger.debug("Dev health check requested")
        return dev_mode.get_health()

    @router.get("/status")
    async def get_status(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        logger.debug("Dev status requested")
        return dev_mode.get_status()

    @router.post("/activate")
    async def activate_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        corr_id = new_corr_id("C")
        logger.info("Dev mode activate requested", ctx={"corr_id": corr_id})
        return dev_mode.activate()

    @router.post("/deactivate")
    async def deactivate_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        corr_id = new_corr_id("C")
        logger.info("Dev mode deactivate requested", ctx={"corr_id": corr_id})
        return dev_mode.deactivate()

    @router.post("/restart")
    async def restart_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        corr_id = new_corr_id("C")
        logger.info("Dev mode restart requested", ctx={"corr_id": corr_id})
        return dev_mode.restart()

    @router.post("/clear")
    async def clear_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        corr_id = new_corr_id("C")
        logger.info("Dev mode clear requested", ctx={"corr_id": corr_id})
        return dev_mode.clear()

    @router.get("/logs")
    async def get_dev_logs(request: Request, lines: int = 50):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        try:
            return dev_mode.get_logs(lines)
        except Exception as exc:
            logger.error("Dev logs fetch failed", err=exc)
            raise HTTPException(status_code=500, detail=str(exc))

    # --- GitHub PAT Management ---

    @router.get("/github/pat-status")
    async def github_pat_status(request: Request):
        """Check if GitHub PAT is configured."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        try:
            from wizard.services.secret_store import get_secret
            token = get_secret("github_token")
            configured = bool(token and len(token) > 10)
            masked = f"{token[:4]}...{token[-4:]}" if configured and len(token) > 8 else None
            return {"configured": configured, "masked": masked}
        except Exception as exc:
            logger.error("GitHub PAT status check failed", err=exc)
            return {"configured": False, "masked": None, "error": str(exc)}

    @router.post("/github/pat")
    async def set_github_pat(request: Request, body: GitHubPATRequest):
        """Set GitHub Personal Access Token."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        corr_id = new_corr_id("C")
        try:
            from wizard.services.secret_store import set_secret
            set_secret("github_token", body.token)
            logger.info("GitHub PAT updated", ctx={"corr_id": corr_id})
            return {"success": True, "message": "GitHub PAT saved"}
        except Exception as exc:
            logger.error("GitHub PAT update failed", err=exc, ctx={"corr_id": corr_id})
            raise HTTPException(status_code=500, detail=str(exc))

    @router.delete("/github/pat")
    async def clear_github_pat(request: Request):
        """Clear GitHub Personal Access Token."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        corr_id = new_corr_id("C")
        try:
            from wizard.services.secret_store import set_secret
            set_secret("github_token", "")
            logger.info("GitHub PAT cleared", ctx={"corr_id": corr_id})
            return {"success": True, "message": "GitHub PAT cleared"}
        except Exception as exc:
            logger.error("GitHub PAT clear failed", err=exc, ctx={"corr_id": corr_id})
            raise HTTPException(status_code=500, detail=str(exc))

    # --- Webhook Secret Generator ---

    @router.post("/webhook/generate-secret")
    async def generate_webhook_secret(request: Request, length: int = 32):
        """Generate a cryptographically secure webhook secret."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        if length < 16 or length > 64:
            raise HTTPException(status_code=400, detail="Length must be 16-64")
        secret = secrets.token_hex(length)
        return WebhookSecretResponse(secret=secret, length=len(secret))

    @router.get("/webhook/github-secret-status")
    async def github_webhook_secret_status(request: Request):
        """Check if GitHub webhook secret is configured."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        try:
            from wizard.services.secret_store import get_secret
            secret = get_secret("github_webhook_secret")
            configured = bool(secret and len(secret) > 8)
            return {"configured": configured}
        except Exception as exc:
            logger.error("GitHub webhook secret status check failed", err=exc)
            return {"configured": False, "error": str(exc)}

    @router.post("/webhook/github-secret")
    async def set_github_webhook_secret(request: Request):
        """Generate and save a new GitHub webhook secret."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        corr_id = new_corr_id("C")
        try:
            from wizard.services.secret_store import set_secret
            new_secret = secrets.token_hex(32)
            set_secret("github_webhook_secret", new_secret)
            logger.info("GitHub webhook secret generated", ctx={"corr_id": corr_id})
            return {"success": True, "secret": new_secret, "message": "Webhook secret generated and saved"}
        except Exception as exc:
            logger.error("GitHub webhook secret generation failed", err=exc, ctx={"corr_id": corr_id})
            raise HTTPException(status_code=500, detail=str(exc))

    return router
