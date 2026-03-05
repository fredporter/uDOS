"""Wizard proxy helpers for core command shims.

Core command handlers can call local Wizard APIs through this service.
All proxy traffic is restricted to loopback hosts.
"""

from __future__ import annotations

from urllib.parse import urlparse

from core.services.background_service_manager import get_wizard_process_manager
from core.services.error_contract import CommandError
from core.services.stdlib_http import HTTPError, http_get, http_post
from core.services.unified_config_loader import get_config
from core.services.wizard_runtime_config import get_loopback_wizard_base_url

_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})


def _wizard_base_url() -> str:
    return get_loopback_wizard_base_url(get_config("WIZARD_BASE_URL", ""))


def _admin_headers() -> dict[str, str]:
    if not (token := get_config("WIZARD_ADMIN_TOKEN", "").strip()):
        return {}
    return {"X-Admin-Token": token}


def _assert_loopback_base_url(base_url: str) -> None:
    parsed = urlparse(base_url)
    host = (parsed.hostname or "").strip().lower()
    if host in _LOOPBACK_HOSTS:
        return
    raise CommandError(
        code="ERR_BOUNDARY_POLICY",
        message=f"Core command proxy blocked non-loopback Wizard target: {base_url}",
        recovery_hint="Set WIZARD_BASE_URL to localhost/127.0.0.1 or run the command in Wizard directly",
        level="ERROR",
    )


def wizard_proxy_status() -> dict[str, object]:
    """Return local Wizard proxy status."""
    base_url = _wizard_base_url()
    _assert_loopback_base_url(base_url)
    manager = get_wizard_process_manager()
    status = manager.status(base_url=base_url)
    try:
        response = http_get(f"{base_url}/health", timeout=3)
        payload = response.get("json") if isinstance(response, dict) else None
        return {
            "status": "success",
            "wizard_base_url": base_url,
            "loopback_only": True,
            "connected": True,
            "running": status.running,
            "pid": status.pid,
            "wizard_health": payload if isinstance(payload, dict) else {},
        }
    except HTTPError as exc:
        return {
            "status": "warning",
            "wizard_base_url": base_url,
            "loopback_only": True,
            "connected": False,
            "running": status.running,
            "pid": status.pid,
            "message": str(exc),
        }


def dispatch_via_wizard(command: str, *, timeout: int = 30) -> dict[str, object]:
    """Dispatch a uCODE command through local Wizard API."""
    base_url = _wizard_base_url()
    _assert_loopback_base_url(base_url)
    manager = get_wizard_process_manager()
    status = manager.ensure_running(base_url=base_url)
    if not status.connected:
        raise CommandError(
            code="ERR_RUNTIME_DEPENDENCY_MISSING",
            message=f"Wizard service unavailable ({status.message}).",
            recovery_hint="Run WIZARD START and inspect memory/logs/wizard-daemon.log",
            level="ERROR",
        )

    try:
        response = http_post(
            f"{base_url}/api/ucode/dispatch",
            json_data={"command": command},
            headers=_admin_headers() or None,
            timeout=timeout,
        )
        payload = response.get("json") if isinstance(response, dict) else None
    except HTTPError as exc:
        message = exc.response_text or exc.message
        if exc.code in {401, 403}:
            raise CommandError(
                code="ERR_AUTH_REQUIRED",
                message=f"Wizard proxy authentication failed ({exc.code}).",
                recovery_hint="Set WIZARD_ADMIN_TOKEN or run this command inside Wizard",
                level="ERROR",
            ) from exc
        raise CommandError(
            code="ERR_RUNTIME_UNEXPECTED",
            message=f"Wizard proxy request failed: {message}",
            recovery_hint="Check local Wizard server status with WIZARD STATUS",
            level="ERROR",
            cause=exc,
        ) from exc

    if not isinstance(payload, dict):
        raise CommandError(
            code="ERR_RUNTIME_UNEXPECTED",
            message="Wizard proxy returned non-JSON response.",
            recovery_hint="Check local Wizard server logs",
            level="ERROR",
        )

    if (result := payload.get("result")) and isinstance(result, dict):
        return result

    if payload.get("status") == "ok":
        return {"status": "success", "message": "Wizard proxy command completed"}

    raise CommandError(
        code="ERR_RUNTIME_UNEXPECTED",
        message=f"Wizard proxy returned unexpected payload for command: {command}",
        recovery_hint="Check local Wizard server logs",
        level="ERROR",
    )
