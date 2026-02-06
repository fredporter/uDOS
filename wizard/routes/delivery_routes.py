"""Delivery transport routes and dashboard."""

from typing import Awaitable, Callable, Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from library.delivery.delivery_daemon import get_delivery_daemon

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


def create_delivery_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/delivery", tags=["delivery"])
    daemon = get_delivery_daemon()

    @router.get("/status")
    async def status(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return daemon.status()

    @router.get("/manifest")
    async def manifest(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return daemon.get_manifest()

    @router.get("/sync/log")
    async def sync_log(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return daemon.get_sync_log()

    return router


def create_delivery_dashboard(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(tags=["delivery-dashboard"])
    daemon = get_delivery_daemon()

    @router.get("/delivery/dashboard", response_class=HTMLResponse)
    async def dashboard(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        status = daemon.status()
        manifest = daemon.get_manifest()
        packages = manifest.get("packages", [])

        rows = "".join(
            f"<tr><td>{p.get('name')}</td><td>{p.get('version')}</td><td>{p.get('sha256')[:10]}</td><td>{p.get('size_bytes')}</td></tr>"
            for p in packages
        )

        html = f"""
        <html>
        <head>
            <title>Delivery Sync Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #0e1117; color: #e6edf3; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
                th, td {{ border-bottom: 1px solid #2a2f3a; padding: 8px; text-align: left; }}
                th {{ color: #8b949e; }}
                .card {{ background: #161b22; border-radius: 8px; padding: 16px; }}
            </style>
        </head>
        <body>
            <h1>Delivery Sync Dashboard</h1>
            <div class="card">
                <p><strong>Packages:</strong> {status.get('packages')}</p>
                <p><strong>Signed:</strong> {status.get('signed')}</p>
                <p><strong>Last Signed:</strong> {status.get('last_signed')}</p>
            </div>
            <h2>Manifest Packages</h2>
            <table>
                <thead>
                    <tr><th>Name</th><th>Version</th><th>SHA</th><th>Size</th></tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    return router
