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
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from wizard.services.ok_gateway import OKRequest, OKGateway
from wizard.services.logging_api import get_log_stats
from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root
from wizard.services.device_auth import get_device_auth, DeviceStatus
from wizard.services.mesh_sync import get_mesh_sync
from core.services.dependency_warning_monitor import (
    install_dependency_warning_monitor,
)
from wizard.services.env_loader import load_dotenv
from wizard.services.dashboard_fallback import get_fallback_dashboard_html
from wizard.services.log_reader import LogReader
from wizard.services.wizard_auth import WizardAuthService
from wizard.services.web_proxy_service import WebProxyService
from wizard.services.plugin_repo_service import PluginRepoService
from wizard.services.system_stats_service import SystemStatsService
from wizard.services.task_scheduler_runner import TaskSchedulerRunner
from wizard.services.webhook_utils import (
    get_base_url,
    resolve_github_webhook_secret,
    verify_signature,
)
from wizard.services.wizard_config import WizardConfig

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


load_dotenv(REPO_ROOT / ".env")
install_dependency_warning_monitor(component="wizard")


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
        self.config = config or WizardConfig.load(CONFIG_PATH / "wizard.json")
        self.app: Optional[FastAPI] = None
        self.logger = get_logger("wizard", category="server", name="wizard-server")
        self.rate_limiter = get_rate_limiter()
        self.ok_gateway = OKGateway()
        self._started = False
        self.logging_manager = None
        self.auth = WizardAuthService(self.config, self.logger)
        self.log_reader = LogReader()
        self.web_proxy = WebProxyService(logger=self.logger)
        self.plugin_repo = PluginRepoService(PLUGIN_REPO_PATH)
        self.system_stats = SystemStatsService(REPO_ROOT)
        self.scheduler_runner = TaskSchedulerRunner()
        self.task_scheduler = self.scheduler_runner.scheduler

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

        webhook_router = create_webhook_routes(
            auth_guard=self._authenticate_admin,
            base_url_provider=lambda: get_base_url(
                self.config.host, self.config.port
            ),
            github_secret_provider=lambda: resolve_github_webhook_secret(
                self.config.github_webhook_secret_key_id
            ),
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
                return HTMLResponse(get_fallback_dashboard_html())

            @app.get("/dashboard")
            async def serve_dashboard_fallback_alt():
                """Fallback dashboard at /dashboard for compatibility."""
                return HTMLResponse(get_fallback_dashboard_html())

        self.app = app
        self.scheduler_runner.start(
            days=self.config.compost_cleanup_days,
            dry_run=self.config.compost_cleanup_dry_run,
        )
        return app

    def _register_routes(self, app: FastAPI):
        """Register API routes."""

        def _get_webhook_secret() -> Optional[str]:
            return resolve_github_webhook_secret(
                self.config.github_webhook_secret_key_id
            )

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
            system_stats = self.system_stats.get_system_stats()
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
            return self.system_stats.get_system_stats()

        @app.get("/api/status")
        async def server_status(request: Request):
            """Get server status (authenticated)."""
            device_id = await self._authenticate(request)
            session = self.auth.sessions.get(device_id)

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
            return self.plugin_repo.list_plugins()

        @app.get("/api/plugin/{plugin_id}")
        async def get_plugin_info(plugin_id: str, request: Request):
            """Get plugin information."""
            await self._authenticate(request)
            return self.plugin_repo.get_plugin_info(plugin_id)

        @app.get("/api/plugin/{plugin_id}/download")
        async def download_plugin(plugin_id: str, request: Request):
            """Download plugin package."""
            await self._authenticate(request)
            return self.plugin_repo.get_download_info(plugin_id)

        # Web proxy routes
        @app.post("/api/web/fetch")
        async def fetch_url(request: Request):
            """Fetch web content (proxy)."""
            if not self.config.web_proxy_enabled:
                raise HTTPException(status_code=503, detail="Web proxy disabled")
            await self._authenticate(request)
            body = await request.json()
            return await self.web_proxy.fetch_url(
                body.get("url"), body.get("options", {})
            )

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
            if not verify_signature(raw_body, signature, secret):
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
            for device_id, session in self.auth.sessions.items():
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
            return self.log_reader.read_logs(
                selected_category, limit=limit, level=level
            )

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

    async def _authenticate(self, request: "FastAPIRequest") -> str:
        """Authenticate device request (delegated to auth service)."""
        return await self.auth.authenticate_device(request)

    async def _authenticate_admin(self, request: Request) -> None:
        """Authenticate admin request (delegated to auth service)."""
        return await self.auth.authenticate_admin(request)


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

    config = WizardConfig.load(CONFIG_PATH / "wizard.json")
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
