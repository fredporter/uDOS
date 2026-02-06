"""MeshCore Integration routes."""

from typing import Awaitable, Callable, Optional

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from extensions.transport.meshcore.coverage_planner import plan_coverage
from extensions.transport.meshcore.relay_daemon import MeshRelayDaemon
from extensions.transport.meshcore.topology_sync import TopologySyncService

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


class RelayCreateRequest(BaseModel):
    name: str
    location: str
    lat: Optional[float] = None
    lon: Optional[float] = None


def create_meshcore_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/meshcore", tags=["meshcore"])
    relay_daemon = MeshRelayDaemon()
    topology_service = TopologySyncService()

    @router.get("/relays")
    async def list_relays(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return [relay.__dict__ for relay in relay_daemon.list_relays()]

    @router.post("/relays")
    async def register_relay(payload: RelayCreateRequest, request: Request = None):
        if auth_guard:
            await auth_guard(request)
        relay = relay_daemon.register_relay(
            name=payload.name,
            location=payload.location,
            lat=payload.lat,
            lon=payload.lon,
        )
        return {"status": "success", "relay": relay.__dict__}

    @router.post("/relays/{relay_id}/heartbeat")
    async def relay_heartbeat(relay_id: str, request: Request = None):
        if auth_guard:
            await auth_guard(request)
        relay = relay_daemon.heartbeat(relay_id)
        if not relay:
            raise HTTPException(status_code=404, detail="Relay not found")
        return {"status": "success", "relay": relay.__dict__}

    @router.get("/relays/{relay_id}/status")
    async def relay_status(relay_id: str, request: Request = None):
        if auth_guard:
            await auth_guard(request)
        relay = relay_daemon.evaluate_status(relay_id)
        if not relay:
            raise HTTPException(status_code=404, detail="Relay not found")
        return relay.__dict__

    @router.get("/topology")
    async def topology_snapshot(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        snapshot = topology_service.build_snapshot()
        return snapshot.__dict__

    @router.post("/coverage/plan")
    async def coverage_plan(
        area_km2: float = Body(...),
        relay_radius_km: float = Body(...),
        redundancy: int = Body(default=1),
        request: Request = None,
    ):
        if auth_guard:
            await auth_guard(request)
        plan = plan_coverage(area_km2, relay_radius_km, redundancy)
        return plan.__dict__

    return router


def create_meshcore_dashboard(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(tags=["meshcore-dashboard"])
    relay_daemon = MeshRelayDaemon()
    topology_service = TopologySyncService()

    @router.get("/meshcore/dashboard", response_class=HTMLResponse)
    async def dashboard(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        relays = relay_daemon.list_relays()
        topology = topology_service.get_snapshot()

        relay_rows = "".join(
            f"<tr><td>{r.relay_id}</td><td>{r.name}</td><td>{r.location}</td><td>{r.status}</td><td>{r.last_seen or ''}</td></tr>"
            for r in relays
        )

        html = f"""
        <html>
        <head>
            <title>MeshCore Relay Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #0e1117; color: #e6edf3; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
                th, td {{ border-bottom: 1px solid #2a2f3a; padding: 8px; text-align: left; }}
                th {{ color: #8b949e; }}
                .card {{ background: #161b22; border-radius: 8px; padding: 16px; }}
            </style>
        </head>
        <body>
            <h1>MeshCore Relay Dashboard</h1>
            <div class="card">
                <p><strong>Relays:</strong> {len(relays)}</p>
                <p><strong>Nodes:</strong> {len(topology.nodes)}</p>
                <p><strong>Edges:</strong> {len(topology.edges)}</p>
                <p><strong>Updated:</strong> {topology.updated_at}</p>
            </div>
            <h2>Relay Status</h2>
            <table>
                <thead>
                    <tr><th>ID</th><th>Name</th><th>Location</th><th>Status</th><th>Last Seen</th></tr>
                </thead>
                <tbody>
                    {relay_rows}
                </tbody>
            </table>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    return router
