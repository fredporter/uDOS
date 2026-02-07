from __future__ import annotations

"""
Wizard Server - Main Server
===========================

FastAPI server providing web access and services for uDOS user devices.
Runs on dedicated always-on machine with internet access.

Endpoints:
  /health          - Health check
  /api/plugin/* - Plugin repository API
  /api/web/*    - Web proxy API
  /api/ai/*     - OK gateway API
  /ws              - WebSocket for real-time updates

Security:
  - All endpoints require device authentication
  - Granular rate limiting per device/endpoint tier
  - Cost tracking for AI/cloud APIs
"""

import os
import re
import json
import asyncio
import threading
import shutil
import webbrowser
import hmac
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from collections import deque

from wizard.services.ok_gateway import OKRequest, OKGateway
from wizard.services.logging_api import get_log_stats, get_logs_root
from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root
from wizard.services.secret_store import get_secret_store, SecretStoreError
from wizard.services.device_auth import get_device_auth, DeviceStatus
from wizard.services.mesh_sync import get_mesh_sync
from core.services.dependency_warning_monitor import (
    install_dependency_warning_monitor,
)

from typing import TYPE_CHECKING

# Optional FastAPI (only on Wizard Server)
try:
    from fastapi import FastAPI, HTTPException, Depends, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    HTTPException = None
    Request = None

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Request as FastAPIRequest

# Rate limiter
from wizard.services.rate_limiter import (
    RateLimiter,
    get_rate_limiter,
    create_rate_limit_middleware,
    RateLimitTier,
)

# Configuration
# Use shared path utility to find repo root reliably
REPO_ROOT = get_repo_root()
WIZARD_DATA_PATH = REPO_ROOT / "memory" / "wizard"
PLUGIN_REPO_PATH = REPO_ROOT / "distribution" / "plugins"
CONFIG_PATH = Path(__file__).parent / "config"


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv(REPO_ROOT / ".env")
install_dependency_warning_monitor(component="wizard")


@dataclass
class WizardConfig:
    """Wizard Server configuration."""

    host: str = "0.0.0.0"
    port: int = 8765
    debug: bool = False

    # Rate limiting
    requests_per_minute: int = 60
    requests_per_hour: int = 1000

    # Cost tracking
    ai_budget_daily: float = 10.0  # USD
    ai_budget_monthly: float = 100.0

    # Plugin repository
    plugin_repo_enabled: bool = True
    plugin_auto_update: bool = False

    # Services
    web_proxy_enabled: bool = True
    ok_gateway_enabled: bool = False

    # GitHub integration
    github_webhook_secret: Optional[str] = None
    github_webhook_secret_key_id: Optional[str] = None
    github_allowed_repo: str = "fredporter/uDOS-dev"
    github_default_branch: str = "main"
    github_push_enabled: bool = False
    admin_api_key_id: Optional[str] = None
    icloud_enabled: bool = False
    oauth_enabled: bool = False
    compost_cleanup_days: int = 30
    compost_cleanup_dry_run: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WizardConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def load(cls, path: Path = None) -> "WizardConfig":
        """Load config from file with validation."""
        config_file = path or (CONFIG_PATH / "wizard.json")
        if config_file.exists():
            try:
                with open(config_file) as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        return cls()
                    if "ok_gateway_enabled" not in data and "ai_gateway_enabled" in data:
                        data["ok_gateway_enabled"] = data.get("ai_gateway_enabled")
                    return cls.from_dict(data)
            except (json.JSONDecodeError, IOError, ValueError):
                # Return defaults if config is invalid
                return cls()
        return cls()

    def save(self, path: Path = None):
        """Save config to file."""
        config_file = path or (CONFIG_PATH / "wizard.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class DeviceSession:
    """Authenticated device session."""

    device_id: str
    device_name: str
    authenticated_at: str
    last_request: str
    request_count: int = 0
    ai_cost_today: float = 0.0


class WizardServer:
    """
    Main Wizard Server class.

    Provides:
    - Device authentication
    - Request routing
    - Granular rate limiting (4 tiers)
    - Cost tracking
    """

    LOG_LINE_PATTERN = re.compile(
        r"^\[(?P<timestamp>[^\]]+)\]\s+\[(?P<level>[^\]]+)\]\s+\[(?P<category>[^\]]+)\](?:\s+\[(?P<source>[^\]]+)\])?\s+(?P<message>.*)$"
    )

    def __init__(self, config: WizardConfig = None):
        """Initialize Wizard Server."""
        self.config = config or WizardConfig.load()
        self.sessions: Dict[str, DeviceSession] = {}
        self.app: Optional[FastAPI] = None
        self.logger = get_logger("wizard", category="server", name="wizard-server")
        self.rate_limiter = get_rate_limiter()
        self.ok_gateway = OKGateway()
        self._started = False
        self.logging_manager = None
        self.task_scheduler = None
        self._scheduler_thread = None
        self._scheduler_stop = threading.Event()

        # Ensure directories exist
        WIZARD_DATA_PATH.mkdir(parents=True, exist_ok=True)
        PLUGIN_REPO_PATH.mkdir(parents=True, exist_ok=True)

    def create_app(self) -> "FastAPI":
        """Create FastAPI application."""
        if not FASTAPI_AVAILABLE:
            raise RuntimeError(
                "FastAPI not available. Install: pip install fastapi uvicorn"
            )

        app = FastAPI(
            title="uDOS Wizard Server",
            description="Always-on server for uDOS user devices",
            version="1.0.0",
            docs_url="/docs" if self.config.debug else None,
            redoc_url="/redoc" if self.config.debug else None,
        )
        self.logger.info(
            "Wizard app created",
            ctx={
                "host": self.config.host,
                "port": self.config.port,
                "debug": self.config.debug,
            },
        )

        # Ensure micro editor is available in /library
        try:
            from wizard.services.editor_utils import ensure_micro_repo
            ensure_micro_repo()
        except Exception as exc:
            self.logger.warn("[WIZ] Failed to ensure micro editor: %s", exc)

        # CORS (restricted to known origins in production)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"] if self.config.debug else [],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Rate limiting middleware
        app.middleware("http")(create_rate_limit_middleware(self.rate_limiter))

        # Register routes
        self._register_routes(app)

        # Register VSCode extension API bridge
        from wizard.services.vscode_bridge import create_vscode_bridge_router

        vscode_router = create_vscode_bridge_router()
        app.include_router(vscode_router)

        # Register Port Manager routes
        from wizard.services.port_manager import create_port_manager_router

        port_router = create_port_manager_router(auth_guard=self._authenticate_admin)
        app.include_router(port_router)

        # Register Notification History routes
        from wizard.services.notification_history_service import (
            NotificationHistoryService,
        )
        from wizard.routes.notification_history_routes import (
            create_notification_history_routes,
        )

        history_service = NotificationHistoryService()
        history_router = create_notification_history_routes(history_service)
        app.include_router(history_router)

        # Register Dev Mode routes
        from wizard.routes.dev_routes import create_dev_routes

        dev_router = create_dev_routes(auth_guard=self._authenticate_admin)
        app.include_router(dev_router)

        # Register Unified Settings (v1.1.0)
        from wizard.routes.settings_unified import create_settings_unified_router

        settings_router = create_settings_unified_router(auth_guard=self._authenticate_admin)
        app.include_router(settings_router)

        # Register Task scheduler routes
        from wizard.routes.task_routes import create_task_routes

        task_router = create_task_routes(auth_guard=self._authenticate_admin)
        app.include_router(task_router)
        from wizard.routes.dataset_routes import router as dataset_router
        app.include_router(dataset_router)
        from wizard.routes.teletext_routes import router as teletext_router
        app.include_router(teletext_router)
        from wizard.routes.groovebox_routes import router as groovebox_router
        app.include_router(groovebox_router)
        from wizard.routes.songscribe_routes import router as songscribe_router
        app.include_router(songscribe_router)
        from wizard.routes.songscribe_export_routes import router as songscribe_export_router
        app.include_router(songscribe_export_router)

        # Register Setup wizard routes

        # Register Workflow manager routes
        from wizard.routes.workflow_routes import create_workflow_routes

        workflow_router = create_workflow_routes(auth_guard=self._authenticate_admin)
        app.include_router(workflow_router)

        # Register Sync executor routes
        from wizard.routes.sync_executor_routes import create_sync_executor_routes

        sync_executor_router = create_sync_executor_routes(
            auth_guard=self._authenticate_admin
        )
        app.include_router(sync_executor_router)

        # Register Binder compiler routes
        from wizard.routes.binder_routes import create_binder_routes

        binder_router = create_binder_routes(auth_guard=self._authenticate_admin)
        app.include_router(binder_router)

        from wizard.routes.beacon_routes import create_beacon_routes

        beacon_public = os.getenv("WIZARD_BEACON_PUBLIC", "1").strip().lower()
        beacon_auth_guard = None
        if beacon_public in {"0", "false", "no"}:
            beacon_auth_guard = self._authenticate_admin
        beacon_router = create_beacon_routes(auth_guard=beacon_auth_guard)
        app.include_router(beacon_router)

        from wizard.routes.renderer_routes import create_renderer_routes

        renderer_public = os.getenv("WIZARD_RENDERER_PUBLIC", "1").strip().lower()
        renderer_auth_guard = None
        if renderer_public in {"0", "false", "no"}:
            renderer_auth_guard = self._authenticate_admin
        renderer_router = create_renderer_routes(auth_guard=renderer_auth_guard)
        app.include_router(renderer_router)

        from wizard.routes.anchor_routes import create_anchor_routes

        anchor_router = create_anchor_routes(auth_guard=self._authenticate_admin)
        app.include_router(anchor_router)

        # Register GitHub integration routes (optional)
        try:
            from wizard.routes.github_routes import create_github_routes

            github_router = create_github_routes(auth_guard=self._authenticate_admin)
            app.include_router(github_router)
        except ImportError as exc:
            self.logger.warn("[WIZ] GitHub routes disabled: %s", exc)

        # Register AI routes (Mistral/Vibe)
        from wizard.routes.ai_routes import create_ai_routes

        ai_router = create_ai_routes(auth_guard=self._authenticate)
        app.include_router(ai_router)

        # Register Configuration routes
        from wizard.routes.config_routes import (
            create_config_routes,
            create_admin_token_routes,
            create_public_export_routes,
        )

        config_router = create_config_routes(auth_guard=self._authenticate_admin)
        app.include_router(config_router)

        admin_token_router = create_admin_token_routes()
        app.include_router(admin_token_router)

        public_export_router = create_public_export_routes()
        app.include_router(public_export_router)

        # Register uCODE bridge routes (MCP/Vibe exploration)
        from wizard.routes.ucode_routes import create_ucode_routes

        ucode_router = create_ucode_routes(auth_guard=self._authenticate_admin)
        app.include_router(ucode_router)

        # Register Plugin CLI stub routes (migration placeholder)
        from wizard.routes.plugin_stub_routes import create_plugin_stub_routes

        plugin_stub_router = create_plugin_stub_routes(auth_guard=self._authenticate_admin)
        app.include_router(plugin_stub_router)

        # Register public Ollama routes FIRST (no auth required for local operations)
        # Must be registered before protected provider routes due to route matching
        from wizard.routes.provider_routes import create_public_ollama_routes

        public_ollama_router = create_public_ollama_routes()
        app.include_router(public_ollama_router)

        # Register Provider management routes
        from wizard.routes.provider_routes import create_provider_routes

        provider_router = create_provider_routes(auth_guard=self._authenticate_admin)
        app.include_router(provider_router)

        # Register System Info routes (OS detection, library status)
        from wizard.routes.system_info_routes import create_system_info_routes

        system_info_router_v1 = create_system_info_routes(
            auth_guard=self._authenticate, prefix="/api/system"
        )
        app.include_router(system_info_router_v1)
        system_info_router = create_system_info_routes(
            auth_guard=self._authenticate, prefix="/api/system"
        )
        app.include_router(system_info_router)

        # Register Wiki provisioning routes
        from wizard.routes.wiki_routes import create_wiki_routes

        wiki_router = create_wiki_routes(auth_guard=self._authenticate)
        app.include_router(wiki_router)

        # Register Library management routes
        from wizard.routes.library_routes import get_library_router

        library_router = get_library_router(auth_guard=self._authenticate_admin)
        app.include_router(library_router)

        # Register Container Launcher routes (home-assistant, songscribe, etc)
        from wizard.routes.container_launcher_routes import router as container_launcher_router

        app.include_router(container_launcher_router)

        # Register Container Proxy routes for browser UI access
        from wizard.routes.container_proxy_routes import router as container_proxy_router

        app.include_router(container_proxy_router)

        # Register Workspace routes
        from wizard.routes.workspace_routes import create_workspace_routes

        workspace_router_v1 = create_workspace_routes(
            auth_guard=self._authenticate_admin, prefix="/api/workspace"
        )
        app.include_router(workspace_router_v1)
        workspace_router = create_workspace_routes(
            auth_guard=self._authenticate_admin, prefix="/api/workspace"
        )
        app.include_router(workspace_router)

        # Register Font routes
        from wizard.routes.font_routes import create_font_routes

        # Fonts are read-only assets; keep public for dashboard tools.
        font_router = create_font_routes()
        app.include_router(font_router)

        # Register Layer editor routes
        from wizard.routes.layer_editor_routes import create_layer_editor_routes

        layer_editor_router = create_layer_editor_routes(
            auth_guard=self._authenticate_admin
        )
        app.include_router(layer_editor_router)

        # Register Log routes
        from wizard.routes.log_routes import create_log_routes

        log_router = create_log_routes()
        app.include_router(log_router)

        # Register Monitoring routes
        from wizard.routes.monitoring_routes import create_monitoring_routes

        monitoring_router = create_monitoring_routes(auth_guard=self._authenticate_admin)
        app.include_router(monitoring_router)

        # Register Catalog routes
        from wizard.routes.catalog_routes import create_catalog_routes

        catalog_router = create_catalog_routes(auth_guard=self._authenticate_admin)
        app.include_router(catalog_router)

        # Register Enhanced Plugin routes (discovery, git, installation)
        from wizard.routes.enhanced_plugin_routes import create_enhanced_plugin_routes

        enhanced_plugin_router = create_enhanced_plugin_routes(auth_guard=self._authenticate_admin)
        app.include_router(enhanced_plugin_router)

        # Register Plugin Manifest Registry routes
        from wizard.routes.plugin_registry_routes import create_plugin_registry_routes

        plugin_registry_router = create_plugin_registry_routes(auth_guard=self._authenticate_admin)
        app.include_router(plugin_registry_router)

        # Register Webhook status routes
        from wizard.routes.webhook_routes import create_webhook_routes

        def _get_base_url() -> str:
            host = self.config.host
            port = self.config.port
            if host == "0.0.0.0":
                host = "localhost"
            return f"http://{host}:{port}"

        def _get_webhook_secret() -> Optional[str]:
            # Prefer secret store via key-id
            key_id = self.config.github_webhook_secret_key_id
            if not key_id:
                return None
            try:
                store = get_secret_store()
                store.unlock()
                entry = store.get(key_id)
                return entry.value if entry and entry.value else None
            except SecretStoreError:
                return None

        webhook_router = create_webhook_routes(
            auth_guard=self._authenticate_admin,
            base_url_provider=_get_base_url,
            github_secret_provider=_get_webhook_secret,
        )
        app.include_router(webhook_router)

        # Register Artifact store routes
        from wizard.routes.artifact_routes import create_artifact_routes

        artifact_router = create_artifact_routes(auth_guard=self._authenticate_admin)
        app.include_router(artifact_router)

        # Register Repair routes
        from wizard.routes.repair_routes import create_repair_routes

        repair_router = create_repair_routes(auth_guard=self._authenticate_admin)
        app.include_router(repair_router)

        # Register Sonic Screwdriver device database routes (modular plugin system)
        from wizard.routes.sonic_plugin_routes import create_sonic_plugin_routes

        sonic_router = create_sonic_plugin_routes(auth_guard=self._authenticate_admin)
        app.include_router(sonic_router)

        # Mount dashboard static files
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse, HTMLResponse

        dashboard_path = Path(__file__).parent / "dashboard" / "dist"
        site_root = REPO_ROOT / "vault" / "_site"
        if site_root.exists():
            app.mount(
                "/_site",
                StaticFiles(directory=str(site_root)),
                name="vault-site",
            )
        if dashboard_path.exists():
            app.mount(
                "/assets",
                StaticFiles(directory=str(dashboard_path / "assets")),
                name="assets",
            )

            @app.get("/")
            async def serve_dashboard():
                return FileResponse(str(dashboard_path / "index.html"))

            @app.get("/dashboard")
            async def serve_dashboard_alt():
                """Serve dashboard at /dashboard for compatibility."""
                return FileResponse(str(dashboard_path / "index.html"))

        else:
            # Fallback: serve basic dashboard when build isn't available
            @app.get("/")
            async def serve_dashboard_fallback():
                return HTMLResponse(self._get_fallback_dashboard_html())

            @app.get("/dashboard")
            async def serve_dashboard_fallback_alt():
                """Fallback dashboard at /dashboard for compatibility."""
                return HTMLResponse(self._get_fallback_dashboard_html())

        self.app = app
        self._start_scheduler()
        return app

    def _start_scheduler(self) -> None:
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        from wizard.services.task_scheduler import TaskScheduler

        self.task_scheduler = TaskScheduler()
        try:
            self.task_scheduler.ensure_daily_compost_cleanup(
                days=self.config.compost_cleanup_days,
                dry_run=self.config.compost_cleanup_dry_run,
            )
        except Exception:
            pass

        # Get logger for the scheduler loop
        logger = get_logger("wizard", category="scheduler", name="wizard-scheduler")

        def loop():
            while not self._scheduler_stop.is_set():
                try:
                    settings = self.task_scheduler.get_settings()
                    max_tasks = int(settings.get("max_tasks_per_tick", 2))
                    tick_seconds = int(settings.get("tick_seconds", 60))
                    result = self.task_scheduler.run_pending(max_tasks=max_tasks)
                    if result.get("executed", 0):
                        logger.info(f"[WIZ] Scheduler executed {result.get('executed')} task(s)")
                except Exception as exc:
                    logger.warn("[WIZ] Scheduler loop error: %s", exc)
                self._scheduler_stop.wait(tick_seconds)

        self._scheduler_thread = threading.Thread(target=loop, daemon=True)
        self._scheduler_thread.start()

    def _get_fallback_dashboard_html(self) -> str:
        """Return basic HTML dashboard when Svelte build isn't available."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>uDOS Wizard Server</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 60px; }
        h1 { font-size: 2.5em; margin-bottom: 10px; color: #60a5fa; }
        .subtitle { font-size: 1.1em; color: #cbd5e1; margin-bottom: 30px; }
        .note { background: #1e293b; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b; margin-bottom: 40px; }
        .endpoints { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .endpoint { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; }
        .endpoint h3 { color: #60a5fa; margin-bottom: 10px; font-size: 1.1em; }
        .endpoint p { color: #94a3b8; font-size: 0.9em; line-height: 1.6; }
        .code { background: #0f172a; padding: 8px 12px; border-radius: 4px; font-family: monospace; font-size: 0.85em; margin-top: 10px; color: #86efac; word-break: break-all; }
        .status { display: flex; align-items: center; gap: 10px; margin-top: 20px; }
        .status-dot { width: 12px; height: 12px; border-radius: 50%; background: #10b981; }
        footer { text-align: center; margin-top: 60px; color: #64748b; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧙 uDOS Wizard Server</h1>
            <p class="subtitle">Always-on backend service</p>
        </header>

        <div class="note">
            <strong>ℹ️ Note:</strong> This is a basic fallback dashboard. The full Svelte dashboard hasn't been built yet.
            <br><br>
            <strong>To build the Svelte dashboard:</strong>
            <div class="code">cd wizard/dashboard && npm install && npm run build</div>
        </div>

        <div class="endpoints">
            <div class="endpoint">
                <h3>✅ Health Check</h3>
                <p>Server status and enabled services</p>
                <div class="code">/health</div>
            </div>

            <div class="endpoint">
                <h3>📊 Dashboard Index</h3>
                <p>Features and configuration overview</p>
                <div class="code">/api/index</div>
            </div>

            <div class="endpoint">
                <h3>📡 Server Status</h3>
                <p>Rate limits, sessions, and costs</p>
                <div class="code">/api/status</div>
            </div>

            <div class="endpoint">
                <h3>🤖 AI Models</h3>
                <p>Available AI models for routing</p>
                <div class="code">/api/ai/models</div>
            </div>

            <div class="endpoint">
                <h3>🔌 Port Manager</h3>
                <p>Manage connected devices and ports</p>
                <div class="code">/api/ports/status</div>
            </div>

            <div class="endpoint">
                <h3>🔗 VS Code Bridge</h3>
                <p>Integration with VS Code extension</p>
                <div class="code">/api/vscode/status</div>
            </div>
        </div>

        <div class="status">
            <div class="status-dot"></div>
            <span>Server is running and healthy</span>
        </div>

        <footer>
            <p>uDOS Wizard Server • v1.1.0 • <a href="https://github.com/fredporter/uDOS" style="color: #60a5fa; text-decoration: none;">GitHub</a></p>
        </footer>
    </div>
</body>
</html>"""

    def _register_routes(self, app: FastAPI):
        """Register API routes."""

        def _get_webhook_secret() -> Optional[str]:
            """Resolve GitHub webhook secret from secret store or config."""
            # Prefer secret store via key-id
            key_id = self.config.github_webhook_secret_key_id
            if key_id:
                try:
                    store = get_secret_store()
                    store.unlock()  # uses WIZARD_KEY env or peer
                    entry = store.get(key_id)
                    if entry and entry.value:
                        return entry.value
                except SecretStoreError:
                    return None
            # Strict: no fallback to plaintext config; require secret store
            return None

        def _get_base_url() -> str:
            host = self.config.host
            port = self.config.port
            if host == "0.0.0.0":
                host = "localhost"
            return f"http://{host}:{port}"

        def _verify_signature(
            body: bytes, signature_header: Optional[str], secret: Optional[str]
        ) -> bool:
            """Verify GitHub HMAC-SHA256 signature ('sha256=...'). Requires secret."""
            if not secret:
                return False
            if not signature_header or not signature_header.startswith("sha256="):
                return False
            digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
            expected = f"sha256={digest}"
            return hmac.compare_digest(expected, signature_header)

        @app.get("/health")
        async def health_check():
            """Health check endpoint."""
            self.logger.debug("Health check requested")
            return {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "services": {
                    "plugin_repo": self.config.plugin_repo_enabled,
                    "web_proxy": self.config.web_proxy_enabled,
                    "ok_gateway": self.config.ok_gateway_enabled,
                },
            }

        @app.get("/api/index")
        async def dashboard_index():
            """Dashboard index data."""
            from wizard.services.system_info_service import get_system_info_service

            system_service = get_system_info_service()
            system_stats = self._get_system_stats()
            os_info = system_service.get_os_info()
            library_status = system_service.get_library_status()
            log_stats = get_log_stats()

            # Derive library counts from available status fields
            available_count = len(
                [
                    i
                    for i in library_status.integrations
                    if i.can_install and not i.installed
                ]
            )
            installed_count = library_status.installed_count
            enabled_count = library_status.enabled_count

            return {
                "dashboard": {
                    "name": "uDOS Wizard Server",
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                "features": [
                    {
                        "name": "Plugin Repository",
                        "enabled": self.config.plugin_repo_enabled,
                        "description": "Distribute and install plugins",
                    },
                    {
                        "name": "Web Proxy",
                        "enabled": self.config.web_proxy_enabled,
                        "description": "Fetch web content for devices",
                    },
                    {
                        "name": "OK Gateway",
                        "enabled": self.config.ok_gateway_enabled,
                        "description": "OK model access with cost tracking",
                    },
                ],
                "system": system_stats,
                "os": os_info.to_dict(),
                "library": {
                    "total": library_status.total_integrations,
                    "available": available_count,
                    "installed": installed_count,
                    "enabled": enabled_count,
                },
                "log_stats": log_stats,
            }

        @app.get("/api/github/health")
        async def github_health():
            """GitHub integration health: CLI, webhook secret, repo settings."""
            try:
                from wizard.services.github_integration import GitHubIntegration

                gh = GitHubIntegration()
                secret_present = bool(_get_webhook_secret())
                return {
                    "status": "ok" if gh.available else "unavailable",
                    "cli": {
                        "available": gh.available,
                        "error": gh.error_message,
                    },
                    "webhook": {
                        "secret_configured": secret_present,
                    },
                    "repo": {
                        "allowed": self.config.github_allowed_repo,
                        "default_branch": self.config.github_default_branch,
                        "push_enabled": self.config.github_push_enabled,
                    },
                }
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

        @app.get("/api/system/stats")
        async def system_stats():
            """Return current system resource stats."""
            return self._get_system_stats()

        @app.get("/api/status")
        async def server_status(request: Request):
            """Get server status (authenticated)."""
            device_id = await self._authenticate(request)
            session = self.sessions.get(device_id)

            # Get rate limit stats for this device
            rate_stats = self.rate_limiter.get_device_stats(device_id)

            return {
                "server": "wizard",
                "device_id": device_id,
                "session": {
                    "request_count": session.request_count if session else 0,
                    "ai_cost_today": session.ai_cost_today if session else 0,
                },
                "rate_limits": rate_stats["tiers"],
                "limits_config": {
                    "tiers": ["light", "standard", "heavy", "expensive"],
                    "ai_budget_daily": self.config.ai_budget_daily,
                },
            }

        @app.get("/api/rate-limits")
        async def get_rate_limits(request: Request):
            """Get current rate limit status."""
            device_id = await self._authenticate(request)
            return self.rate_limiter.get_device_stats(device_id)

        # OK gateway routes
        @app.get("/api/ai/status")
        async def ai_status(request: Request):
            """Return OK gateway + routing status."""
            device_id = await self._authenticate(request)
            return {
                "device_id": device_id,
                "gateway": self.ok_gateway.get_status(),
            }

        @app.get("/api/ai/models")
        async def ai_models(request: Request):
            """List available AI models (local-first)."""
            await self._authenticate(request)
            return {"models": self.ok_gateway.list_models()}

        @app.post("/api/ai/complete")
        async def ai_complete(request: Request):
            """Run OK completion through the routed gateway."""
            device_id = await self._authenticate(request)
            body = await request.json()

            ai_request = OKRequest(
                prompt=body.get("prompt", ""),
                model=body.get("model", ""),
                system_prompt=body.get("system") or body.get("system_prompt", ""),
                max_tokens=body.get("max_tokens", 1024),
                temperature=body.get("temperature"),
                stream=body.get("stream", False),
                mode=body.get("mode"),
                task_id=body.get("task_id"),
                workspace=body.get("workspace", "core"),
                privacy=body.get("privacy", "internal"),
                urgency=body.get("urgency", "normal"),
                tags=body.get("tags") or [],
                actor=body.get("actor"),
                conversation_id=body.get("conversation_id"),
            )

            response = await self.ok_gateway.complete(ai_request, device_id=device_id)
            status_code = 200 if response.success else 400
            return JSONResponse(status_code=status_code, content=response.to_dict())

        # Plugin repository routes
        @app.get("/api/plugin/list")
        async def list_plugins(request: Request):
            """List available plugins."""
            await self._authenticate(request)
            return await self._list_plugins()

        @app.get("/api/plugin/{plugin_id}")
        async def get_plugin_info(plugin_id: str, request: Request):
            """Get plugin information."""
            await self._authenticate(request)
            return await self._get_plugin_info(plugin_id)

        @app.get("/api/plugin/{plugin_id}/download")
        async def download_plugin(plugin_id: str, request: Request):
            """Download plugin package."""
            await self._authenticate(request)
            return await self._download_plugin(plugin_id)

        # Web proxy routes
        @app.post("/api/web/fetch")
        async def fetch_url(request: Request):
            """Fetch web content (proxy)."""
            if not self.config.web_proxy_enabled:
                raise HTTPException(status_code=503, detail="Web proxy disabled")
            await self._authenticate(request)
            body = await request.json()
            return await self._fetch_url(body.get("url"), body.get("options", {}))

        # GitHub webhook (actions + repo sync)
        @app.post("/api/github/webhook")
        async def github_webhook(request: Request):
            """
            Receive GitHub webhooks for CI self-healing and safe repo sync.
            Signature validation is enforced when `github_webhook_secret` is set.

            Events to subscribe:
              - workflow_run (completed, requested)
              - check_run (completed)
              - push (main branch)
            """
            from wizard.services.github_monitor import get_github_monitor
            from wizard.services.github_sync import get_github_sync_service

            event_type = request.headers.get("X-GitHub-Event", "unknown")
            delivery_id = request.headers.get("X-GitHub-Delivery", "unknown")
            signature = request.headers.get("X-Hub-Signature-256")

            raw_body = await request.body()
            secret = _get_webhook_secret()
            if not secret:
                raise HTTPException(
                    status_code=503, detail="webhook secret not configured"
                )
            if not _verify_signature(raw_body, signature, secret):
                raise HTTPException(status_code=401, detail="invalid signature")

            try:
                payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            except json.JSONDecodeError:
                payload = {}

            print(f"\n🔔 GitHub Webhook Received:")
            print(f"   Event: {event_type}")
            print(f"   Delivery: {delivery_id}")

            sync_result = None
            if event_type == "push":
                sync_service = get_github_sync_service(
                    allowed_repo=self.config.github_allowed_repo,
                    default_branch=self.config.github_default_branch,
                    push_enabled=self.config.github_push_enabled,
                )
                sync_result = sync_service.handle_webhook(event_type, payload)
                if sync_result.success:
                    print("   🔄 Repo sync (pull) applied")
                elif sync_result.action != "ignored":
                    print(f"   ⚠️  Repo sync skipped: {sync_result.detail}")

            monitor = get_github_monitor()
            result = await monitor.handle_webhook(event_type, payload)

            return {
                "status": "received",
                "event": event_type,
                "delivery_id": delivery_id,
                "sync": sync_result.__dict__ if sync_result else None,
                "result": result,
            }

        # Manual GitHub sync endpoint
        @app.post("/api/github/sync")
        async def github_sync(request: Request):
            """
            Manually trigger a safe sync (pull by default) for the allowed repo.
            """
            from wizard.services.github_sync import get_github_sync_service

            await self._authenticate(request)  # reuse auth guard
            body = await request.json()
            action = body.get("action", "pull")
            sync_service = get_github_sync_service(
                allowed_repo=self.config.github_allowed_repo,
                default_branch=self.config.github_default_branch,
                push_enabled=self.config.github_push_enabled,
            )
            if action == "push":
                result = sync_service.sync_push()
            else:
                result = sync_service.sync_pull()
            return result.__dict__

        # Mesh device management (dashboard)
        @app.get("/api/mesh/devices")
        async def list_mesh_devices(request: Request):
            """List paired mesh devices."""
            await self._authenticate_admin(request)
            auth = get_device_auth()
            devices = auth.list_devices()
            return {
                "devices": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "type": d.device_type,
                        "status": d.status.value,
                        "transport": d.transport,
                        "trust_level": d.trust_level.value,
                        "last_seen": d.last_seen or "Never",
                        "sync_status": f"v{d.sync_version}"
                        if d.sync_version
                        else "Never synced",
                    }
                    for d in devices
                ],
                "count": len(devices),
            }

        @app.post("/api/mesh/pairing-code")
        async def mesh_pairing_code(request: Request):
            """Generate pairing code for mesh device."""
            await self._authenticate_admin(request)
            auth = get_device_auth()
            wizard_address = request.url.netloc
            pairing = auth.create_pairing_request(wizard_address=wizard_address)
            return {"code": pairing.code, "qr_data": pairing.qr_data}

        @app.get("/api/mesh/pairing-qr")
        async def mesh_pairing_qr(request: Request, data: str):
            """Generate QR SVG for pairing payload."""
            await self._authenticate_admin(request)
            try:
                import qrcode
                from qrcode.image.svg import SvgImage
            except Exception:
                raise HTTPException(status_code=503, detail="qrcode not installed")

            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(image_factory=SvgImage)
            svg = img.to_string().decode("utf-8")
            return JSONResponse(content={"svg": svg})

        @app.post("/api/mesh/pair")
        async def mesh_pair(request: Request):
            """Complete device pairing."""
            await self._authenticate_admin(request)
            body = await request.json()
            auth = get_device_auth()
            device = auth.complete_pairing(
                code=body.get("code"),
                device_id=body.get("device_id"),
                device_name=body.get("device_name"),
                device_type=body.get("device_type", "desktop"),
                public_key=body.get("public_key", ""),
            )
            if not device:
                raise HTTPException(status_code=400, detail="Invalid or expired code")
            return {"status": "success", "device": device.to_dict()}

        @app.post("/api/mesh/devices/{device_id}/sync")
        async def mesh_sync_device(device_id: str, request: Request):
            """Trigger sync for a specific device."""
            await self._authenticate_admin(request)
            auth = get_device_auth()
            sync = get_mesh_sync()
            device = auth.get_device(device_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            delta = sync.get_delta(device.sync_version)
            return {
                "status": "sync_initiated",
                "device_id": device_id,
                "items_to_sync": len(delta.items),
                "from_version": delta.from_version,
                "to_version": delta.to_version,
            }

        @app.post("/api/mesh/devices/sync-all")
        async def mesh_sync_all(request: Request):
            """Trigger sync for all online devices."""
            await self._authenticate_admin(request)
            auth = get_device_auth()
            online_devices = [
                d for d in auth.list_devices() if d.status == DeviceStatus.ONLINE
            ]
            results = [
                {
                    "device_id": d.id,
                    "device_name": d.name,
                    "status": "sync_initiated",
                }
                for d in online_devices
            ]
            return {
                "status": "success",
                "devices_synced": len(results),
                "results": results,
            }

        @app.post("/api/mesh/devices/{device_id}/ping")
        async def mesh_ping(device_id: str, request: Request):
            """Ping a device (placeholder)."""
            await self._authenticate_admin(request)
            auth = get_device_auth()
            device = auth.get_device(device_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            return {
                "status": "pong",
                "device_id": device_id,
                "latency_ms": 42,
                "transport": device.transport,
            }

        # TUI Control Routes (for Wizard TUI interface)
        @app.get("/api/devices")
        async def list_devices(request: Request):
            """List connected devices (TUI endpoint)."""
            await self._authenticate_admin(request)
            devices = []
            for device_id, session in self.sessions.items():
                devices.append(
                    {
                        "id": device_id,
                        "name": session.device_name,
                        "last_request": session.last_request,
                        "requests": session.request_count,
                        "cost_today": session.ai_cost_today,
                    }
                )
            return {"devices": devices, "count": len(devices)}

        @app.get("/api/logs")
        async def get_logs(
            request: Request,
            category: str = "all",
            filter: Optional[str] = None,
            limit: int = 200,
            level: Optional[str] = None,
        ):
            """Return recent Wizard logs (latest first)."""
            await self._authenticate_admin(request)
            selected_category = filter or category or "all"
            return self._read_logs(selected_category, limit=limit, level=level)

        @app.post("/api/models/switch")
        async def switch_model(request: Request):
            """Switch AI model (TUI endpoint)."""
            await self._authenticate_admin(request)
            body = await request.json()
            model = body.get("model")
            if not model:
                raise HTTPException(status_code=400, detail="Model required")

            # TODO: Implement actual model switching in OK gateway
            return {"success": True, "model": model, "message": f"Switched to {model}"}

        @app.post("/api/services/{service}/{action}")
        async def control_service(service: str, action: str, request: Request):
            """Control service start/stop (TUI endpoint)."""
            await self._authenticate_admin(request)
            valid_services = ["web-proxy", "ok-gateway", "plugin-repo"]
            valid_actions = ["start", "stop", "restart"]

            if service not in valid_services:
                raise HTTPException(
                    status_code=404, detail=f"Unknown service: {service}"
                )

            if action not in valid_actions:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

            # TODO: Implement actual service control
            return {
                "success": True,
                "service": service,
                "action": action,
                "message": f"Service {service} {action}ed successfully",
            }

    def _get_system_stats(self) -> Dict[str, Any]:
        """Collect lightweight system resource metrics."""
        cpu_count = os.cpu_count() or 1
        try:
            load1, load5, load15 = os.getloadavg()
        except OSError:
            load1 = load5 = load15 = 0.0

        load_per_cpu = round(load1 / cpu_count, 2) if cpu_count else 0.0
        memory = self._read_memory_stats()
        swap = self._read_swap_stats()
        disk = self._read_disk_stats()
        uptime_seconds = self._get_uptime_seconds()
        process_count = self._get_process_count()

        overload_reasons: List[str] = []
        if load_per_cpu > 1.25:
            overload_reasons.append("cpu_load_high")
        if memory["used_percent"] > 95:  # Higher threshold since swap is active
            overload_reasons.append("memory_high")
        if disk["used_percent"] > 90:
            overload_reasons.append("disk_high")

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "cpu": {
                "count": cpu_count,
                "load1": round(load1, 2),
                "load5": round(load5, 2),
                "load15": round(load15, 2),
                "load_per_cpu": load_per_cpu,
            },
            "memory": memory,
            "swap": swap,
            "disk": disk,
            "uptime_seconds": uptime_seconds,
            "process_count": process_count,
            "overload": bool(overload_reasons),
            "overload_reasons": overload_reasons,
        }

    def _read_memory_stats(self) -> Dict[str, Any]:
        """Read memory stats from /proc/meminfo (Linux)."""
        meminfo_path = Path("/proc/meminfo")
        total_kb = available_kb = None
        if meminfo_path.exists():
            try:
                for line in meminfo_path.read_text().splitlines():
                    if line.startswith("MemTotal:"):
                        total_kb = int(line.split()[1])
                    elif line.startswith("MemAvailable:"):
                        available_kb = int(line.split()[1])
            except (OSError, ValueError):
                total_kb = available_kb = None

        total_bytes = (total_kb or 0) * 1024
        available_bytes = (available_kb or 0) * 1024
        used_bytes = max(total_bytes - available_bytes, 0)

        to_mb = lambda b: round(b / (1024 * 1024), 1)
        used_percent = (
            round((used_bytes / total_bytes) * 100, 1) if total_bytes else 0.0
        )

        return {
            "total_mb": to_mb(total_bytes),
            "available_mb": to_mb(available_bytes),
            "used_mb": to_mb(used_bytes),
            "used_percent": used_percent,
        }

    def _read_swap_stats(self) -> Dict[str, Any]:
        """Read swap memory statistics from /proc/meminfo or /proc/swaps."""
        meminfo_path = Path("/proc/meminfo")
        swap_total_kb = swap_free_kb = None

        if meminfo_path.exists():
            try:
                for line in meminfo_path.read_text().splitlines():
                    if line.startswith("SwapTotal:"):
                        swap_total_kb = int(line.split()[1])
                    elif line.startswith("SwapFree:"):
                        swap_free_kb = int(line.split()[1])
            except (OSError, ValueError):
                swap_total_kb = swap_free_kb = None

        total_bytes = (swap_total_kb or 0) * 1024
        free_bytes = (swap_free_kb or 0) * 1024
        used_bytes = max(total_bytes - free_bytes, 0)

        to_gb = lambda b: round(b / (1024 * 1024 * 1024), 2)
        used_percent = (
            round((used_bytes / total_bytes) * 100, 1) if total_bytes else 0.0
        )

        return {
            "total_gb": to_gb(total_bytes),
            "used_gb": to_gb(used_bytes),
            "free_gb": to_gb(free_bytes),
            "used_percent": used_percent,
            "active": total_bytes > 0,
        }

    def _read_disk_stats(self) -> Dict[str, Any]:
        """Read disk usage for the repo root volume."""
        try:
            usage = shutil.disk_usage(str(REPO_ROOT))
        except OSError:
            return {
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "used_percent": 0.0,
            }

        total_bytes = usage.total
        used_bytes = usage.total - usage.free
        free_bytes = usage.free
        used_percent = (
            round((used_bytes / total_bytes) * 100, 1) if total_bytes else 0.0
        )

        to_gb = lambda b: round(b / (1024 * 1024 * 1024), 2)
        return {
            "total_gb": to_gb(total_bytes),
            "used_gb": to_gb(used_bytes),
            "free_gb": to_gb(free_bytes),
            "used_percent": used_percent,
        }

    def _get_uptime_seconds(self) -> Optional[float]:
        """Read system uptime in seconds if available."""
        uptime_path = Path("/proc/uptime")
        if uptime_path.exists():
            try:
                return float(uptime_path.read_text().split()[0])
            except (OSError, ValueError):
                return None
        return None

    def _get_process_count(self) -> Optional[int]:
        """Count active processes on Linux."""
        proc_path = Path("/proc")
        if not proc_path.exists():
            return None
        try:
            return len(
                [p for p in proc_path.iterdir() if p.is_dir() and p.name.isdigit()]
            )
        except OSError:
            return None

    def _read_logs(
        self, category: str = "all", limit: int = 200, level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Tail recent log lines for dashboard/TUI usage."""
        log_dir = get_logs_root()
        if not log_dir.exists():
            return {
                "logs": [],
                "category": category,
                "limit": limit,
                "categories": [],
                "stats": {},
            }

        files = sorted(log_dir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        categories = sorted({p.parent.name for p in files})

        selected = (category or "all").lower()
        entries: List[Dict[str, Any]] = []

        for log_file in files:
            if selected not in ("all", ""):
                if log_file.parent.name != selected and log_file.stem.split("-")[0] != selected:
                    continue

            for line in self._tail_file(log_file, max(limit * 3, 200)):
                parsed = self._parse_log_json(line, log_file.name)
                if not parsed:
                    continue
                if level and parsed["level"].lower() != level.lower():
                    continue
                entries.append(parsed)

        entries.sort(key=lambda e: e["timestamp_sort"], reverse=True)
        trimmed = entries[:limit]
        for entry in trimmed:
            entry.pop("timestamp_sort", None)

        return {
            "logs": trimmed,
            "category": selected,
            "limit": limit,
            "categories": categories,
            "stats": get_log_stats(),
        }

    def _tail_file(self, path: Path, max_lines: int) -> List[str]:
        """Return up to max_lines from end of file."""
        buf: deque = deque(maxlen=max_lines)
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    buf.append(line.rstrip("\n"))
        except OSError:
            return []
        return list(buf)

    def _parse_log_json(self, line: str, filename: str) -> Optional[Dict[str, Any]]:
        """Parse a JSONL log line from v1.3 logging API."""
        try:
            payload = json.loads(line)
        except Exception:
            return None

        ts_raw = payload.get("ts") or payload.get("timestamp")
        try:
            ts_dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            ts_iso = ts_dt.isoformat()
        except Exception:
            ts_dt = datetime.min
            ts_iso = ts_raw or ""

        return {
            "timestamp": ts_iso,
            "timestamp_sort": ts_dt,
            "level": payload.get("level", ""),
            "category": payload.get("category", ""),
            "component": payload.get("component", ""),
            "event": payload.get("event", ""),
            "message": payload.get("msg", ""),
            "file": filename,
        }

    async def _authenticate(self, request: "FastAPIRequest") -> str:
        """Authenticate device request."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")

        token = auth_header[7:]
        # TODO: Validate token against paired devices
        # For now, extract device_id from token format
        device_id = token.split(":")[0] if ":" in token else token[:16]
        auth = get_device_auth()
        if not auth.get_device(device_id):
            raise HTTPException(status_code=401, detail="Unknown device")

        # Update session
        now = datetime.utcnow().isoformat() + "Z"
        if device_id not in self.sessions:
            self.sessions[device_id] = DeviceSession(
                device_id=device_id,
                device_name="Unknown",
                authenticated_at=now,
                last_request=now,
            )

        session = self.sessions[device_id]
        session.last_request = now
        session.request_count += 1
        return device_id

    async def _authenticate_admin(self, request: Request) -> None:
        """Authenticate admin request using secret store key or WIZARD_ADMIN_TOKEN."""
        key_id = self.config.admin_api_key_id
        auth_header = request.headers.get("Authorization", "").strip()

        # Validate header format
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        token = auth_header[7:].strip()
        if not token or len(token) < 8:
            raise HTTPException(status_code=401, detail="Invalid token format")

        # Try environment token first (faster path)
        env_token = os.getenv("WIZARD_ADMIN_TOKEN", "").strip()
        if env_token and hmac.compare_digest(token, env_token):
            return

        # Try secret store if key_id configured
        if not key_id:
            raise HTTPException(status_code=503, detail="Admin authentication not configured")

        try:
            store = get_secret_store()
            store.unlock()
            entry = store.get(key_id)
            if entry and entry.value and hmac.compare_digest(token, entry.value):
                return
        except SecretStoreError as exc:
            self.logger.warn("[WIZ] Secret store error during auth: %s", exc)
            if not env_token:
                raise HTTPException(status_code=503, detail="Admin secret store locked")

        # Token validation failed
        raise HTTPException(status_code=403, detail="Invalid admin token")

    async def _list_plugins(self) -> Dict[str, Any]:
        """List available plugins in repository."""
        plugins = []

        if PLUGIN_REPO_PATH.exists():
            for item in PLUGIN_REPO_PATH.iterdir():
                if item.is_dir():
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                        plugins.append(
                            {
                                "id": item.name,
                                "name": manifest.get("name", item.name),
                                "version": manifest.get("version", "0.0.0"),
                                "description": manifest.get("description", ""),
                            }
                        )

        return {"plugins": plugins, "count": len(plugins)}

    async def _get_plugin_info(self, plugin_id: str) -> Dict[str, Any]:
        """Get detailed plugin information."""
        # Validate plugin ID to prevent path traversal
        if not plugin_id or "/" in plugin_id or ".." in plugin_id:
            raise HTTPException(status_code=400, detail="Invalid plugin ID")

        plugin_path = PLUGIN_REPO_PATH / plugin_id

        if not plugin_path.exists():
            raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            raise HTTPException(status_code=404, detail=f"No manifest for plugin: {plugin_id}")

        with open(manifest_path) as f:
            manifest = json.load(f)

        # Find package file
        packages = list(plugin_path.glob("*.tar.gz")) + list(plugin_path.glob("*.tcz"))
        package_info = None
        if packages:
            pkg = packages[0]
            package_info = {
                "filename": pkg.name,
                "size": pkg.stat().st_size,
            }

        return {
            "id": plugin_id,
            "manifest": manifest,
            "package": package_info,
        }

    async def _download_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Get download URL/data for plugin."""
        # Validate plugin ID
        if not plugin_id or "/" in plugin_id or ".." in plugin_id:
            raise HTTPException(status_code=400, detail="Invalid plugin ID")

        plugin_path = PLUGIN_REPO_PATH / plugin_id

        if not plugin_path.exists():
            raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

        packages = list(plugin_path.glob("*.tar.gz")) + list(plugin_path.glob("*.tcz"))
        if not packages:
            raise HTTPException(status_code=404, detail=f"No downloadable package for: {plugin_id}")

        pkg = packages[0]

        # For now, return path info. In production, return presigned URL or stream
        return {
            "plugin_id": plugin_id,
            "filename": pkg.name,
            "size": pkg.stat().st_size,
            "download_method": "qr_relay",  # Recommend QR relay for large files
            "message": "Use QR RECEIVE on device to download",
        }

    async def _fetch_url(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch URL content for user device."""
        if not url or not isinstance(url, str):
            raise HTTPException(status_code=400, detail="URL required and must be a string")

        # Validate URL format
        url = url.strip()
        if len(url) > 2048:
            raise HTTPException(status_code=400, detail="URL too long (max 2048 chars)")

        # Security checks
        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Only HTTP/HTTPS URLs allowed")

        # TODO: Implement actual fetching with httpx/aiohttp
        # For now, return placeholder
        return {
            "url": url,
            "status": "not_implemented",
            "message": "Web proxy fetch not yet implemented",
        }

    def run(self, host: str = None, port: int = None, interactive: bool = True):
        """Run the Wizard Server with optional interactive console."""
        import uvicorn
        from wizard.services.interactive_console import WizardConsole

        app = self.create_app()
        self.logger.info(
            "Wizard server starting",
            ctx={
                "host": host or self.config.host,
                "port": port or self.config.port,
                "interactive": interactive,
            },
        )

        if interactive:
            # Run server in background with interactive console in foreground
            config = uvicorn.Config(
                app,
                host=host or self.config.host,
                port=port or self.config.port,
                log_level="info" if self.config.debug else "warning",
            )
            server = uvicorn.Server(config)

            # Create console
            console = WizardConsole(self, self.config)

            # Run both concurrently
            async def run_with_console():
                # Start server in background
                server_task = asyncio.create_task(server.serve())

                # Wait a moment for server to start
                await asyncio.sleep(1)
                self.logger.info("Wizard server ready")

                # Open dashboard in browser
                dashboard_url = (
                    f"http://{host or self.config.host}:{port or self.config.port}"
                )
                if self.config.host == "0.0.0.0":
                    dashboard_url = f"http://localhost:{port or self.config.port}"
                webbrowser.open(dashboard_url)
                # Run interactive console in foreground
                console_task = asyncio.create_task(console.run())

                # Wait for console to exit (user types 'exit')
                await console_task

                # Shutdown server gracefully
                server.should_exit = True
                await server_task

            # Run the async main function
            asyncio.run(run_with_console())
        else:
            # Run server without interactive console (daemon mode)
            # Use uvicorn.run() which properly initializes and starts the server
            uvicorn.run(
                app,
                host=host or self.config.host,
                port=port or self.config.port,
                log_level="info" if self.config.debug else "warning",
            )


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="uDOS Wizard Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Run in daemon mode without interactive console",
    )

    args = parser.parse_args()

    config = WizardConfig.load()
    config.host = args.host or config.host
    config.port = args.port or config.port
    config.debug = args.debug or config.debug

    server = WizardServer(config)

    if not args.no_interactive:
        # Interactive mode with console (default)
        server.run(interactive=True)
    else:
        # Daemon mode without console
        print(f"🧙 Starting uDOS Wizard Server on {args.host}:{args.port}")
        server.run(interactive=False)
