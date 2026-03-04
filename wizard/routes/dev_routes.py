"""
Dev Mode routes for Wizard Server.
"""

import secrets
from typing import Callable, Awaitable, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from core.services.path_service import get_repo_root
from core.services.permission_handler import Permission
from core.services.user_service import get_user_manager
from wizard.services.dev_extension_service import get_dev_extension_service
from wizard.services.dev_mode_service import get_dev_mode_service
from wizard.services.logging_api import get_logger, new_corr_id

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


class GitHubPATRequest(BaseModel):
    token: str


class WebhookSecretResponse(BaseModel):
    secret: str
    length: int


class ScriptRunRequest(BaseModel):
    path: str
    args: list[str] = []
    timeout: int = 300


class TestRunRequest(BaseModel):
    path: Optional[str] = None
    args: list[str] = []
    timeout: int = 600


def create_dev_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/dev", tags=["dev-mode"])
    repo_root = get_repo_root()
    dev_mode = get_dev_mode_service(repo_root=repo_root)
    dev_extension = get_dev_extension_service(repo_root=repo_root)
    logger = get_logger("wizard", category="dev-mode", name="dev")

    def _ensure_admin_dev_access():
        try:
            user_mgr = get_user_manager()
            if not user_mgr.has_permission(Permission.ADMIN) or not user_mgr.has_permission(Permission.DEV_MODE):
                raise HTTPException(status_code=403, detail="Admin + Dev Mode permissions required")
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    def _ensure_dev_submodule():
        message = dev_extension.ensure_framework()
        if message:
            raise HTTPException(status_code=412, detail=message)

    def _ensure_dev_active():
        message = dev_mode.ensure_active()
        if message:
            raise HTTPException(status_code=409, detail=message)

    @router.get("/health")
    async def health_check(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        _ensure_dev_active()
        logger.debug("Dev health check requested")
        return dev_mode.get_health()

    @router.get("/status")
    async def get_status(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        logger.debug("Dev status requested")
        status = dev_mode.get_status()
        status["extension"] = dev_extension.status()
        return status

    @router.get("/ops")
    async def get_ops_status(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        logger.debug("Dev ops status requested")
        return dev_mode.get_ops_summary()

    @router.get("/ops/files")
    async def list_ops_files(request: Request, area: str = "ops", path: str = ""):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        result = dev_mode.list_browser_entries(area=area, rel_path=path)
        if result.get("status") == "error":
            detail = result.get("message", "Unable to list files")
            if "Unknown area" in detail or "not allowed" in detail:
                raise HTTPException(status_code=400, detail=detail)
            if "not found" in detail:
                raise HTTPException(status_code=404, detail=detail)
            raise HTTPException(status_code=400, detail=detail)
        return result

    @router.get("/ops/read")
    async def read_ops_file(request: Request, area: str = "ops", path: str = ""):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        result = dev_mode.read_browser_file(area=area, rel_path=path)
        if result.get("status") == "error":
            detail = result.get("message", "Unable to read file")
            if "Unknown area" in detail or "not allowed" in detail:
                raise HTTPException(status_code=400, detail=detail)
            if "not found" in detail:
                raise HTTPException(status_code=404, detail=detail)
            raise HTTPException(status_code=400, detail=detail)
        return result

    @router.post("/activate")
    async def activate_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        corr_id = new_corr_id("C")
        logger.info("Dev mode activate requested", ctx={"corr_id": corr_id})
        result = dev_mode.activate()
        result["extension"] = dev_extension.status()
        return result

    @router.post("/deactivate")
    async def deactivate_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        corr_id = new_corr_id("C")
        logger.info("Dev mode deactivate requested", ctx={"corr_id": corr_id})
        result = dev_mode.deactivate()
        result["extension"] = dev_extension.status()
        return result

    @router.post("/restart")
    async def restart_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        corr_id = new_corr_id("C")
        logger.info("Dev mode restart requested", ctx={"corr_id": corr_id})
        result = dev_mode.restart()
        result["extension"] = dev_extension.status()
        return result

    @router.post("/clear")
    async def clear_dev_mode(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        _ensure_dev_active()
        corr_id = new_corr_id("C")
        logger.info("Dev mode clear requested", ctx={"corr_id": corr_id})
        return dev_mode.clear()

    @router.get("/logs")
    async def get_dev_logs(request: Request, lines: int = 50):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        _ensure_dev_active()
        try:
            return dev_mode.get_logs(lines)
        except Exception as exc:
            logger.error("Dev logs fetch failed", err=exc)
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/scripts")
    async def list_dev_scripts(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        _ensure_dev_active()
        return {"scripts": dev_mode.list_scripts()}

    @router.post("/scripts/run")
    async def run_dev_script(request: Request, body: ScriptRunRequest):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        _ensure_dev_active()
        return dev_mode.run_script(body.path, args=body.args, timeout=body.timeout)

    @router.get("/tests")
    async def list_dev_tests(request: Request):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        _ensure_dev_active()
        return {"tests": dev_mode.list_tests()}

    @router.post("/tests/run")
    async def run_dev_tests(request: Request, body: TestRunRequest):
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        _ensure_dev_submodule()
        _ensure_dev_active()
        return dev_mode.run_tests(rel_path=body.path, args=body.args, timeout=body.timeout)

    # --- GitHub PAT Management ---

    @router.get("/github/pat-status")
    async def github_pat_status(request: Request):
        """Check if GitHub PAT is configured."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        try:
            return dev_extension.get_pat_status()
        except Exception as exc:
            logger.error("GitHub PAT status check failed", err=exc)
            return {"configured": False, "masked": None, "error": str(exc)}

    @router.get("/github/status")
    async def github_status(request: Request):
        """Return consolidated GitHub/Dev extension status."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        return dev_extension.github_status()

    @router.post("/github/pat")
    async def set_github_pat(request: Request, body: GitHubPATRequest):
        """Set GitHub Personal Access Token."""
        if auth_guard:
            await auth_guard(request)
        _ensure_admin_dev_access()
        corr_id = new_corr_id("C")
        try:
            result = dev_extension.set_pat(body.token)
            logger.info("GitHub PAT updated", ctx={"corr_id": corr_id})
            return result
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
            result = dev_extension.clear_pat()
            logger.info("GitHub PAT cleared", ctx={"corr_id": corr_id})
            return result
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
            return dev_extension.get_webhook_secret_status()
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
            result = dev_extension.set_webhook_secret()
            logger.info("GitHub webhook secret generated", ctx={"corr_id": corr_id})
            return result
        except Exception as exc:
            logger.error("GitHub webhook secret generation failed", err=exc, ctx={"corr_id": corr_id})
            raise HTTPException(status_code=500, detail=str(exc))

    return router
