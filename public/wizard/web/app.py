"""
Wizard Server Web GUI - FastAPI Application
============================================

Browser-based administration interface for Wizard Server.
Uses HTMX + Alpine.js for lightweight, no-build-step interactivity.

Features:
- Dashboard (system status, logs, health metrics)
- POKE server (host files/pages)
- Webhook receiver (external integrations)
- Device monitor (paired mesh devices)
- BizIntel dashboard (contact tools)
- Plugin manager (browse/install/update)

Stack:
- FastAPI (async backend)
- Jinja2 (server-side templates)
- HTMX (reactive updates without JS frameworks)
- Alpine.js (minimal client-side state)
- Tailwind CSS (utility-first styling)

Version: v1.0.0.0
Date: 2026-01-05
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

# Import Wizard Server components
from wizard.services.device_auth import get_device_auth, DeviceStatus
from wizard.services.mesh_sync import get_mesh_sync, SyncItemType
from wizard.services.rate_limiter import get_rate_limiter
from wizard.services.logging_manager import get_logger

# Gmail OAuth (Flask blueprint - convert to FastAPI)
try:
    from wizard.services.gmail_auth import get_gmail_auth
except ImportError:
    get_gmail_auth = None

# Setup
WIZARD_ROOT = Path(__file__).parent.parent
MEMORY_ROOT = WIZARD_ROOT.parent / "memory"
LOGS_DIR = MEMORY_ROOT / "logs"

logger = get_logger("wizard-web")

# FastAPI app
app = FastAPI(
    title="uDOS Wizard Server",
    description="Browser-based administration for Wizard Server",
    version="v1.0.0.0",
)

# CORS (localhost + local network only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*", "http://192.168.*.*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware (for OAuth state)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get(
        "SESSION_SECRET_KEY", "udos-wizard-dev-secret-change-in-production"
    ),
)

# Static files + templates
app.mount(
    "/static", StaticFiles(directory=str(WIZARD_ROOT / "web" / "static")), name="static"
)
templates = Jinja2Templates(directory=str(WIZARD_ROOT / "web" / "templates"))

# WebSocket connections
active_connections: List[WebSocket] = []


# ============================================================================
# Dashboard Routes
# ============================================================================


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    # Get system stats
    stats = await get_system_stats()

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "stats": stats, "page_title": "Wizard Server Dashboard"},
    )


@app.get("/api/stats")
async def get_stats():
    """API endpoint for system statistics."""
    stats = await get_system_stats()
    return JSONResponse(stats)


async def get_system_stats() -> Dict[str, Any]:
    """Gather system statistics."""
    # TODO: Implement actual stat gathering
    return {
        "status": "online",
        "uptime": "2h 34m",
        "devices": {"paired": 3, "active": 2, "total": 5},
        "api": {"requests_today": 1247, "avg_response_ms": 42},
        "costs": {"today": 0.47, "month": 12.34, "currency": "USD"},
        "logs": {"errors_today": 2, "warnings_today": 8},
    }


# ============================================================================
# POKE Server Routes (File/Page Hosting)
# ============================================================================


@app.get("/poke", response_class=HTMLResponse)
async def poke_dashboard(request: Request):
    """POKE server management page."""
    # List hosted files/pages
    poke_items = await list_poke_items()

    return templates.TemplateResponse(
        "poke.html",
        {"request": request, "items": poke_items, "page_title": "POKE Server"},
    )


@app.post("/api/poke/upload")
async def upload_poke_file(request: Request):
    """Upload file for POKE hosting."""
    # TODO: Implement file upload
    return {"status": "success", "url": "/p/example.html"}


@app.get("/p/{path:path}")
async def serve_poke_file(path: str):
    """Serve hosted POKE file."""
    poke_dir = MEMORY_ROOT / "wizard" / "poke"
    file_path = poke_dir / path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


async def list_poke_items() -> List[Dict[str, Any]]:
    """List all POKE-hosted items."""
    # TODO: Implement
    return [
        {
            "name": "example.html",
            "size": "2.3 KB",
            "views": 42,
            "created": "2026-01-04",
        },
        {"name": "status.json", "size": "512 B", "views": 127, "created": "2026-01-03"},
    ]


# ============================================================================
# Webhook Receiver
# ============================================================================


@app.get("/webhooks", response_class=HTMLResponse)
async def webhooks_dashboard(request: Request):
    """Webhook management page."""
    webhooks = await list_webhooks()

    return templates.TemplateResponse(
        "webhooks.html",
        {"request": request, "webhooks": webhooks, "page_title": "Webhooks"},
    )


@app.post("/webhook/{webhook_id}")
async def receive_webhook(webhook_id: str, request: Request):
    """Receive webhook from external service."""
    body = await request.json()

    logger.info(f"[WIZ] Webhook received: {webhook_id}")
    logger.debug(f"[WIZ] Webhook payload: {body}")

    # TODO: Process webhook based on type

    return {"status": "received", "webhook_id": webhook_id}


async def list_webhooks() -> List[Dict[str, Any]]:
    """List configured webhooks."""
    return [
        {
            "id": "github-deploy",
            "service": "GitHub",
            "events": 12,
            "last": "2 hours ago",
        },
        {"id": "stripe-payment", "service": "Stripe", "events": 3, "last": "1 day ago"},
    ]


# ============================================================================
# Device Monitor
# ============================================================================


@app.get("/devices", response_class=HTMLResponse)
async def devices_dashboard(request: Request):
    """Device monitoring page."""
    devices = await list_devices()

    return templates.TemplateResponse(
        "devices.html",
        {"request": request, "devices": devices, "page_title": "Mesh Devices"},
    )


@app.get("/api/devices")
async def get_devices():
    """API endpoint for device list."""
    devices = await list_devices()
    return JSONResponse({"devices": devices})


async def list_devices() -> List[Dict[str, Any]]:
    """List all paired mesh devices."""
    # Get actual devices from auth service
    auth = get_device_auth()
    devices = auth.list_devices()

    return [
        {
            "id": d.id,
            "name": d.name,
            "type": d.device_type,
            "status": d.status.value,
            "transport": d.transport,
            "trust_level": d.trust_level.value,
            "last_seen": d.last_seen or "Never",
            "sync_status": f"v{d.sync_version}" if d.sync_version else "Never synced",
        }
        for d in devices
    ] or [
        # Placeholder data if no devices
        {
            "id": "node-alpha",
            "name": "Desktop Node",
            "type": "desktop",
            "status": "online",
            "last_seen": "2 min ago",
        },
    ]


# ============================================================================
# Device Pairing API
# ============================================================================


@app.get("/api/devices/pairing-qr")
async def get_pairing_qr():
    """Generate QR code for device pairing."""
    auth = get_device_auth()
    request = auth.create_pairing_request()

    # Return QR code as HTML (or could return SVG/image)
    # For now, return the data that would be encoded
    return HTMLResponse(
        f"""
        <div class="text-center">
            <div class="bg-white p-4 rounded inline-block">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={request.qr_data}" 
                     alt="Pairing QR Code" class="mx-auto">
            </div>
            <p class="text-xs text-gray-500 mt-2">Scan with uDOS device</p>
        </div>
    """
    )


@app.get("/api/devices/pairing-code")
async def get_pairing_code():
    """Generate manual pairing code."""
    auth = get_device_auth()
    request = auth.create_pairing_request()

    return HTMLResponse(
        f"""
        <code class="text-2xl font-mono text-blue-400 bg-gray-900 px-4 py-2 rounded">
            {request.code}
        </code>
    """
    )


@app.post("/api/devices/pair")
async def pair_device(request: Request):
    """Complete device pairing."""
    body = await request.json()

    auth = get_device_auth()
    device = auth.complete_pairing(
        code=body.get("code"),
        device_id=body.get("device_id"),
        device_name=body.get("device_name"),
        device_type=body.get("device_type", "desktop"),
        public_key=body.get("public_key", ""),
    )

    if device:
        # Broadcast pairing success to WebSocket clients
        await broadcast_event("device_paired", device.to_dict())
        return JSONResponse({"status": "success", "device": device.to_dict()})
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired pairing code")


@app.post("/api/devices/{device_id}/sync")
async def sync_device(device_id: str, request: Request):
    """Trigger sync with a specific device."""
    auth = get_device_auth()
    sync = get_mesh_sync()

    device = auth.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Get delta since device's last sync
    delta = sync.get_delta(device.sync_version)

    # In a real implementation, this would push to the device
    # For now, return the delta
    logger.info(f"[MESH] Sync requested for {device_id}: {len(delta.items)} items")

    return JSONResponse(
        {
            "status": "sync_initiated",
            "device_id": device_id,
            "items_to_sync": len(delta.items),
            "from_version": delta.from_version,
            "to_version": delta.to_version,
        }
    )


@app.post("/api/devices/sync-all")
async def sync_all_devices():
    """Trigger sync with all online devices."""
    auth = get_device_auth()
    online_devices = [d for d in auth.list_devices() if d.status == DeviceStatus.ONLINE]

    results = []
    for device in online_devices:
        results.append(
            {
                "device_id": device.id,
                "device_name": device.name,
                "status": "sync_initiated",
            }
        )

    logger.info(f"[MESH] Sync-all triggered for {len(results)} devices")

    return JSONResponse(
        {"status": "success", "devices_synced": len(results), "results": results}
    )


@app.post("/api/devices/{device_id}/ping")
async def ping_device(device_id: str):
    """Ping a device to check connectivity."""
    auth = get_device_auth()
    device = auth.get_device(device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # In a real implementation, this would send a ping via transport
    # For now, simulate response
    return JSONResponse(
        {
            "status": "pong",
            "device_id": device_id,
            "latency_ms": 42,
            "transport": device.transport,
        }
    )


# ============================================================================
# Mesh Sync API
# ============================================================================


@app.post("/api/sync/push")
async def sync_push(request: Request):
    """
    Receive sync data from a device.

    Device pushes its changes to Wizard Server.
    """
    body = await request.json()
    device_id = body.get("device_id")
    items = body.get("items", [])

    auth = get_device_auth()
    sync = get_mesh_sync()

    # Verify device
    device = auth.get_device(device_id)
    if not device:
        raise HTTPException(status_code=401, detail="Unknown device")

    # Apply changes
    new_version = sync.apply_from_device(device_id, items)

    # Update device sync version
    auth.update_device_sync(device_id, new_version)

    return JSONResponse(
        {"status": "success", "applied": len(items), "new_version": new_version}
    )


@app.get("/api/sync/pull")
async def sync_pull(request: Request, device_id: str, since_version: int = 0):
    """
    Send sync data to a device.

    Device pulls changes from Wizard Server.
    """
    auth = get_device_auth()
    sync = get_mesh_sync()

    # Verify device
    device = auth.get_device(device_id)
    if not device:
        raise HTTPException(status_code=401, detail="Unknown device")

    # Get delta
    delta = sync.get_delta(since_version)

    return JSONResponse(delta.to_dict())


@app.get("/api/sync/status")
async def sync_status():
    """Get current sync status."""
    sync = get_mesh_sync()
    auth = get_device_auth()

    devices = auth.list_devices()

    return JSONResponse(
        {
            "global_version": sync.global_version,
            "item_count": len(sync.item_versions),
            "devices": [
                {
                    "id": d.id,
                    "name": d.name,
                    "sync_version": d.sync_version,
                    "behind": sync.global_version - d.sync_version,
                }
                for d in devices
            ],
        }
    )


# ============================================================================
# Logs Viewer
# ============================================================================


@app.get("/logs", response_class=HTMLResponse)
async def logs_dashboard(request: Request):
    """Log viewer page."""
    return templates.TemplateResponse(
        "logs.html", {"request": request, "page_title": "Server Logs"}
    )


@app.get("/api/logs")
async def get_logs(level: str = "all", limit: int = 100):
    """API endpoint for log entries."""
    # Read recent logs
    log_entries = await read_recent_logs(level, limit)
    return JSONResponse({"logs": log_entries})


async def read_recent_logs(level: str, limit: int) -> List[Dict[str, Any]]:
    """Read recent log entries."""
    # TODO: Parse actual log files
    return [
        {
            "timestamp": "2026-01-05 14:32:10",
            "level": "INFO",
            "message": "Device node-alpha connected",
        },
        {
            "timestamp": "2026-01-05 14:31:05",
            "level": "ERROR",
            "message": "Rate limit exceeded for device node-beta",
        },
        {
            "timestamp": "2026-01-05 14:30:22",
            "level": "INFO",
            "message": "Webhook received: github-deploy",
        },
    ]


# ============================================================================
# WebSocket - Real-time Updates
# ============================================================================


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time dashboard updates."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Send periodic updates
            stats = await get_system_stats()
            await websocket.send_json(
                {
                    "type": "stats_update",
                    "data": stats,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            await asyncio.sleep(5)  # Update every 5 seconds

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("[WIZ] WebSocket client disconnected")


# ============================================================================
# Groovebox Catalog Page
# ============================================================================


@app.get("/catalog", response_class=HTMLResponse)
async def catalog_page(request: Request):
    """Groovebox sound pack catalog page."""
    return templates.TemplateResponse(
        "catalog.html", {"request": request, "page_title": "Groovebox Catalog"}
    )


# Log streaming connections
log_connections: List[WebSocket] = []


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket for real-time log streaming."""
    await websocket.accept()
    log_connections.append(websocket)

    try:
        # Stream logs
        log_id = 0
        while True:
            # In production, this would tail actual log files
            # For now, simulate log entries
            await asyncio.sleep(2)

            log_id += 1
            log_entry = {
                "id": f"log-{log_id}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "level": ["INFO", "DEBUG", "WARNING", "ERROR"][log_id % 4],
                "source": ["wizard", "mesh", "api", "transport"][log_id % 4],
                "message": f"Sample log message #{log_id}",
            }

            await websocket.send_json(log_entry)

    except WebSocketDisconnect:
        log_connections.remove(websocket)


async def broadcast_event(event_type: str, data: Any):
    """Broadcast event to all connected WebSocket clients."""
    message = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }

    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass  # Client disconnected


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "v1.0.0.0",
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# Gmail OAuth Routes
# ============================================================================

from wizard.web.gmail_fastapi_routes import gmail_router

app.include_router(gmail_router)


# ============================================================================
# Groovebox Catalog Routes
# ============================================================================

from wizard.web.routes.catalog import router as catalog_router

app.include_router(catalog_router)


# ============================================================================
# Server Entry Point
# ============================================================================


def start_web_server(host: str = "127.0.0.1", port: int = 8080):
    """
    Start the Wizard Server web interface.

    Args:
        host: Host to bind to (default: localhost only)
        port: Port to bind to (default: 8080)
    """
    logger.info(f"[WIZ] Starting Wizard Server web interface on {host}:{port}")
    logger.info(f"[WIZ] Dashboard: http://{host}:{port}/")

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_web_server()
