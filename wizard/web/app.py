"""
Wizard Server Web GUI - FastAPI Application
============================================

Browser-based administration interface for Wizard Server.
Uses HTMX + Alpine.js for lightweight, no-build-step interactivity.

Features:
- Dashboard (system status, logs, health metrics)
- Webhook receiver (external integrations)
- Device monitor (paired mesh devices)
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
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

# Import Wizard Server components
from wizard.services.device_auth import get_device_auth, DeviceStatus
from wizard.services.mesh_sync import get_mesh_sync, SyncItemType
from wizard.services.rate_limiter import get_rate_limiter
from wizard.services.logging_api import get_logger
from wizard.services.secret_store import get_secret_store, SecretStoreError
from wizard.services.plugin_repository import get_repository
from wizard.services.plugin_validation import (
    compute_manifest_checksum,
    load_manifest,
    validate_manifest,
)
from core.services.hotkey_map import get_hotkey_payload
from core.services.config_sync_service import ConfigSyncManager
from wizard.services.oauth_manager import (
    get_oauth_manager,
    OAuthProvider,
    ConnectionStatus,
)

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

# CORS (localhost only by default; allow LAN via env)
allow_lan = os.environ.get("WIZARD_WEB_ALLOW_LAN", "false").lower() in ("1", "true")
origin_regex = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"
if allow_lan:
    origin_regex = r"^http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3})(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=origin_regex,
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

LOCALHOSTS = {"127.0.0.1", "::1", "localhost"}
LAN_PREFIXES = ("192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.")


def _is_allowed_host(host: Optional[str]) -> bool:
    if not host:
        return False
    if host in LOCALHOSTS:
        return True
    if allow_lan and host.startswith(LAN_PREFIXES):
        return True
    return False


async def _require_admin(request: Request) -> None:
    key_id = os.environ.get("WIZARD_WEB_ADMIN_KEY_ID", "wizard-admin-token")
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    token = auth_header[7:]
    try:
        store = get_secret_store()
        store.unlock()
        entry = store.get(key_id)
    except SecretStoreError:
        raise HTTPException(status_code=503, detail="admin secret store locked")
    if not entry or not entry.value:
        raise HTTPException(status_code=503, detail="admin token not configured")
    if not hmac.compare_digest(token, entry.value):
        raise HTTPException(status_code=403, detail="Invalid admin token")


@app.middleware("http")
async def local_only_middleware(request: Request, call_next):
    if not _is_allowed_host(request.client.host if request.client else ""):
        return JSONResponse(status_code=403, content={"detail": "Localhost only"})
    return await call_next(request)


# ============================================================================
# Dashboard Routes
# ============================================================================


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    # Get system stats
    stats = await get_system_stats()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"stats": stats, "page_title": "Wizard Server Dashboard"},
    )


@app.get("/config", response_class=HTMLResponse)
async def config_dashboard(request: Request):
    """All-in-one Wizard config page with venv, secrets, and installer actions."""
    repo_root = Path(__file__).parent.parent
    venv_path = repo_root / ".venv"
    venv_status = {
        "exists": venv_path.exists(),
        "python": None,
        "path": str(venv_path),
    }
    if (venv_path / "bin" / "python").exists():
        venv_status["python"] = str((venv_path / "bin" / "python").resolve())

    secret_state = {"unlocked": False, "entries": []}
    try:
        store = get_secret_store()
        store.unlock(os.environ.get("WIZARD_KEY", ""))
        secret_state["unlocked"] = True
        secret_state["entries"] = [
            {"key_id": entry.key_id, "provider": entry.provider}
            for entry in store.list()
        ]
    except Exception:
        secret_state["error"] = "Secret store locked or missing WIZARD_KEY"

    repository = get_repository()
    repository_stats = repository.get_stats()
    repo_entries = {entry.id: entry.to_dict() for entry in repository.list_plugins()}
    plugin_catalog = []
    plugin_dir = repository.repo_base
    if plugin_dir.exists():
        for plugin_path in sorted(plugin_dir.iterdir()):
            if not plugin_path.is_dir():
                continue
            manifest_path = plugin_path / "manifest.json"
            manifest = load_manifest(plugin_path)
            manifest_checksum = compute_manifest_checksum(manifest_path)
            repo_entry = repo_entries.get(plugin_path.name) or {}
            validation = validate_manifest(
                manifest, plugin_path.name, repo_entry
            )
            plugin_catalog.append(
                {
                    "name": plugin_path.name,
                    "manifest": manifest,
                    "manifest_checksum": manifest_checksum,
                    "validation": validation,
                    "repository_entry": repo_entry,
                }
            )

    # .env user variable configuration (identity boundary)
    config_sync = ConfigSyncManager()
    env_dict = config_sync.load_env_dict()
    identity_fields = []
    for env_key in sorted(config_sync.ENV_ONLY_FIELDS.keys()):
        if env_key == "WIZARD_KEY":
            continue
        identity_fields.append(
            {
                "key": env_key,
                "label": env_key.replace("_", " ").title(),
                "value": env_dict.get(env_key) or "Not set",
            }
        )

    wizard_key_value = (
        env_dict.get("WIZARD_KEY") or os.environ.get("WIZARD_KEY") or "Not set"
    )
    env_notice = (
        "Run command SETUP in the uCODE terminal to update these identity variables. "
        "Use DESTROY to start over (CLI only)."
    )

    # OAuth connection overview
    oauth_manager = get_oauth_manager()
    raw_connections = oauth_manager.get_all_connections()
    oauth_connections: List[Dict[str, Any]] = []
    status_notes = {
        ConnectionStatus.NOT_CONFIGURED: "Add client ID/secret in wizard/config/oauth_providers.json",
        ConnectionStatus.PENDING_AUTH: "Awaiting browser authorization",
        ConnectionStatus.EXPIRED: "Token expired — reconnect to refresh",
        ConnectionStatus.CONNECTED: "Connected",
    }

    for provider_key, connection in raw_connections.items():
        try:
            provider_enum = OAuthProvider(provider_key)
        except ValueError:
            continue

        note = status_notes.get(connection.status, "")
        oauth_connections.append(
            {
                "slug": provider_enum.value,
                "name": connection.display_name,
                "status": connection.status.value,
                "label": connection.status.name.replace("_", " ").title(),
                "note": note,
                "user": connection.user_display,
                "can_connect": connection.status != ConnectionStatus.NOT_CONFIGURED,
            }
        )

    return templates.TemplateResponse(
        request,
        "config.html",
        {
            "page_title": "Wizard Configuration",
            "venv_status": venv_status,
            "secret_state": secret_state,
            "plugin_catalog": plugin_catalog,
            "hotkey_link": "/hotkeys",
            "env_identity_fields": identity_fields,
            "wizard_key_value": wizard_key_value,
            "env_path": str(repo_root / ".env"),
            "env_notice": env_notice,
            "oauth_connections": oauth_connections,
            "oauth_note": "One-click OAuth connectors open the provider consent flows via the Wizard OAuth gateway.",
            "repository_stats": repository_stats,
        },
    )


@app.get("/api/v1/oauth/connect/{provider}")
async def oauth_connect(provider: str):
    """Redirect to the OAuth authorization URL for a provider."""
    try:
        provider_enum = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(status_code=404, detail="OAuth provider not supported")

    manager = get_oauth_manager()
    auth_url = manager.get_auth_url(provider_enum)

    if not auth_url:
        raise HTTPException(
            status_code=400,
            detail="Provider not configured. Add client_id/client_secret to wizard/config/oauth_providers.json",
        )

    return RedirectResponse(auth_url)


def _hotkey_map():
    return [
        {"key": "Tab", "action": "Command Selector", "notes": "Opens the TAB menu even in fallback mode (SmartPrompt handles <kbd>Tab</kbd>)."},
        {"key": "F1", "action": "Status / Help banner", "notes": "Bound by `core/tui/fkey_handler.py` to show self-heal stats."},
        {"key": "F2", "action": "Logs / Diagnostics", "notes": "Replays health logs pulled from `memory/logs/health-training.log`."},
        {"key": "F3", "action": "REPAIR shortcut", "notes": "Runs `SelfHealer` helpers via the CLI handler."},
        {"key": "F4", "action": "RESTART / HOT RELOAD", "notes": "Triggers watcher stats and automatic reloads via `core/services/hot_reload.py`."},
        {"key": "F5", "action": "Extension palette", "notes": "Opens the plugin menu in the CLI; uses `LibraryManagerService` metadata."},
        {"key": "F6", "action": "Pattern / Script runner", "notes": "Repeats the `PATTERN` banner logic defined in `memory/system/startup-script.md`."},
        {"key": "F7", "action": "Sonic Device DB", "notes": "Displays supported USB/media targets read from `memory/sonic/sonic-devices.db`."},
        {"key": "F8", "action": "Hotkey Center", "notes": "Proxies this same page from within the CLI and automation loops."},
        {"key": "↑ / ↓", "action": "Command history", "notes": "Shared with `SmartPrompt` history and predictor logging."},
        {"key": "Enter", "action": "Confirm input", "notes": "Approves the date/time/timezone block and records overrides when refused."},
    ]


@app.get("/hotkeys", response_class=HTMLResponse)
async def hotkey_center(request: Request):
    """Hotkey center page documenting CLI/automation keys."""
    payload = get_hotkey_payload(MEMORY_ROOT)
    return templates.TemplateResponse(
        request,
        "hotkeys.html",
        {
            "key_map": payload["key_map"],
            "page_title": "Hotkey Center",
            "health_log": str(LOGS_DIR / "health-training.log"),
            "hotkey_snapshot": payload["snapshot"],
        },
    )


@app.get("/hotkeys/data", response_class=JSONResponse)
async def hotkey_data():
    """Machine-readable key binding data + snapshot path."""
    payload = get_hotkey_payload(MEMORY_ROOT)
    return JSONResponse(payload)


@app.get("/api/stats")
async def get_stats():
    """API endpoint for system statistics."""
    stats = await get_system_stats()
    return JSONResponse(stats)


async def get_system_stats() -> Dict[str, Any]:
    """Gather system statistics."""
    # STUB: Implement stat gathering
    return {
        "status": "online",
        "uptime": "2h 34m",
        "devices": {"paired": 3, "active": 2, "total": 5},
        "api": {"requests_today": 1247, "avg_response_ms": 42},
        "costs": {"today": 0.47, "month": 12.34, "currency": "USD"},
        "logs": {"errors_today": 2, "warnings_today": 8},
    }


# ============================================================================
# Webhook Receiver
# ============================================================================


@app.get("/webhooks", response_class=HTMLResponse)
async def webhooks_dashboard(request: Request):
    """Webhook management page."""
    webhooks = await list_webhooks()

    return templates.TemplateResponse(
        request,
        "webhooks.html",
        {"webhooks": webhooks, "page_title": "Webhooks"},
    )


@app.post("/webhook/{webhook_id}")
async def receive_webhook(webhook_id: str, request: Request):
    """Receive webhook from external service."""
    await _require_admin(request)
    body = await request.json()

    logger.info(f"[WIZ] Webhook received: {webhook_id}")
    logger.debug(f"[WIZ] Webhook payload: {body}")

    # STUB: Process webhook based on type

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
        request,
        "devices.html",
        {"devices": devices, "page_title": "Mesh Devices"},
    )


@app.get("/api/devices")
async def get_devices(request: Request):
    """API endpoint for device list."""
    await _require_admin(request)
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
async def get_pairing_qr(request: Request):
    """Generate QR code for device pairing."""
    await _require_admin(request)
    auth = get_device_auth()
    wizard_address = request.url.netloc
    pairing = auth.create_pairing_request(wizard_address=wizard_address)

    return JSONResponse({"qr_data": pairing.qr_data, "code": pairing.code})


@app.get("/api/devices/pairing-code")
async def get_pairing_code(request: Request):
    """Generate manual pairing code."""
    await _require_admin(request)
    auth = get_device_auth()
    wizard_address = request.url.netloc
    pairing = auth.create_pairing_request(wizard_address=wizard_address)

    return JSONResponse({"code": pairing.code})


@app.post("/api/devices/pair")
async def pair_device(request: Request):
    """Complete device pairing."""
    await _require_admin(request)
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
    await _require_admin(request)
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
async def sync_all_devices(request: Request):
    """Trigger sync with all online devices."""
    await _require_admin(request)
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
async def ping_device(device_id: str, request: Request):
    """Ping a device to check connectivity."""
    await _require_admin(request)
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
    await _require_admin(request)
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
    await _require_admin(request)
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
async def sync_status(request: Request):
    """Get current sync status."""
    await _require_admin(request)
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
    return templates.TemplateResponse(request, "logs.html", {"page_title": "Server Logs"})


@app.get("/api/logs")
async def get_logs(request: Request, level: str = "all", limit: int = 100):
    """API endpoint for log entries."""
    await _require_admin(request)
    # Read recent logs
    log_entries = await read_recent_logs(level, limit)
    return JSONResponse({"logs": log_entries})


async def read_recent_logs(level: str, limit: int) -> List[Dict[str, Any]]:
    """Read recent log entries."""
    # STUB: Parse log files
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
    if not _is_allowed_host(websocket.client.host if websocket.client else ""):
        await websocket.close(code=1008)
        return
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
        request, "catalog.html", {"page_title": "Groovebox Catalog"}
    )


# Log streaming connections
log_connections: List[WebSocket] = []


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket for real-time log streaming."""
    if not _is_allowed_host(websocket.client.host if websocket.client else ""):
        await websocket.close(code=1008)
        return
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
        except Exception:
            pass  # Client disconnected


def _safe_join(base_dir: Path, rel_path: str) -> Optional[Path]:
    if not rel_path or rel_path.startswith(("/", "\\")):
        return None
    if ".." in rel_path.split("/"):
        return None
    base = base_dir.resolve()
    target = (base_dir / rel_path).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        return None
    return target


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



# ============================================================================
# Groovebox Catalog Routes
# ============================================================================

from groovebox.wizard.web.routes.catalog import router as catalog_router

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
