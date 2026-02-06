"""
Beacon Portal Pages

Serves captive portal HTML pages and offline/status messaging.
"""

from pathlib import Path
from datetime import datetime
import os

from typing import Awaitable, Callable, Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]

def _templates_root() -> Path:
    return Path(__file__).parent.parent.parent / "library" / "beacon" / "templates"


def _read_template(name: str) -> str:
    path = _templates_root() / name
    if not path.exists():
        return ""
    return path.read_text()


def _wizard_url() -> str:
    host = os.getenv("WIZARD_HOSTNAME", "wizard.local")
    return f"http://{host}"


def _wizard_ip() -> str:
    return os.getenv("WIZARD_IP", "192.168.1.10")


def _beacon_ssid() -> str:
    return os.getenv("BEACON_SSID", "uDOS-beacon")


def _beacon_mode() -> str:
    return os.getenv("BEACON_MODE", "portal")


def create_beacon_portal_pages(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(tags=["beacon-portal"])

    @router.get("/portal", response_class=HTMLResponse)
    async def portal_page(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        template = _read_template("portal.html")
        html = template.format(
            wizard_url=_wizard_url(),
            wizard_ip=_wizard_ip(),
            ssid=_beacon_ssid(),
            mode=_beacon_mode(),
            updated_at=datetime.utcnow().isoformat() + "Z",
        )
        return HTMLResponse(content=html)

    @router.get("/portal/status", response_class=HTMLResponse)
    async def portal_status_page(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        template = _read_template("status.html")
        html = template.format(
            wizard_url=_wizard_url(),
            wizard_ip=_wizard_ip(),
            ssid=_beacon_ssid(),
            mode=_beacon_mode(),
            updated_at=datetime.utcnow().isoformat() + "Z",
        )
        return HTMLResponse(content=html)

    @router.get("/portal/offline", response_class=HTMLResponse)
    async def portal_offline_page(request: Request = None):
        # Offline page remains public for captive portal fallback.
        template = _read_template("offline.html")
        html = template.format(
            wizard_url=_wizard_url(),
            wizard_ip=_wizard_ip(),
            ssid=_beacon_ssid(),
            mode=_beacon_mode(),
            updated_at=datetime.utcnow().isoformat() + "Z",
        )
        return HTMLResponse(content=html)

    return router
