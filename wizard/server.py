"""
Wizard Server - Main Server
===========================

FastAPI server providing web access and services for uDOS user devices.
Runs on dedicated always-on machine with internet access.

Endpoints:
  /health          - Health check
  /api/v1/plugin/* - Plugin repository API
  /api/v1/web/*    - Web proxy API
  /api/v1/ai/*     - AI gateway API
  /api/v1/gmail/*  - Gmail relay API
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
import shutil
import webbrowser
import hmac
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from collections import deque

from wizard.services.ai_gateway import AIRequest, AIGateway
from wizard.services.logging_manager import get_logging_manager
from wizard.services.path_utils import get_repo_root
from wizard.services.secret_store import get_secret_store, SecretStoreError

# Optional FastAPI (only on Wizard Server)
try:
    from fastapi import FastAPI, HTTPException, Depends, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None

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
    gmail_relay_enabled: bool = False
    ai_gateway_enabled: bool = False

    # GitHub integration
    github_webhook_secret: Optional[str] = None
    github_webhook_secret_key_id: Optional[str] = None
    github_allowed_repo: str = "fredporter/uDOS-dev"
    github_default_branch: str = "main"
    github_push_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WizardConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def load(cls, path: Path = None) -> "WizardConfig":
        """Load config from file."""
        config_file = path or (CONFIG_PATH / "wizard.json")
        if config_file.exists():
            with open(config_file) as f:
                return cls.from_dict(json.load(f))
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
        self.rate_limiter = get_rate_limiter()
        self.ai_gateway = AIGateway()
        self._started = False
        self.logging_manager = get_logging_manager()

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
        from wizard.services.port_manager_service import create_port_manager_router

        port_router = create_port_manager_router()
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

        dev_router = create_dev_routes(auth_guard=self._authenticate)
        app.include_router(dev_router)

        # Register Notion sync routes
        from wizard.routes.notion_routes import create_notion_routes

        notion_router = create_notion_routes(auth_guard=self._authenticate)
        app.include_router(notion_router)

        # Register Task scheduler routes
        from wizard.routes.task_routes import create_task_routes

        task_router = create_task_routes(auth_guard=self._authenticate)
        app.include_router(task_router)

        # Register Workflow manager routes
        from wizard.routes.workflow_routes import create_workflow_routes

        workflow_router = create_workflow_routes(auth_guard=self._authenticate)
        app.include_router(workflow_router)

        # Register Sync executor routes
        from wizard.routes.sync_executor_routes import create_sync_executor_routes

        sync_executor_router = create_sync_executor_routes(
            auth_guard=self._authenticate
        )
        app.include_router(sync_executor_router)

        # Register Binder compiler routes
        from wizard.routes.binder_routes import create_binder_routes

        binder_router = create_binder_routes(auth_guard=self._authenticate)
        app.include_router(binder_router)

        # Register GitHub integration routes
        from wizard.routes.github_routes import create_github_routes

        github_router = create_github_routes(auth_guard=self._authenticate)
        app.include_router(github_router)

        # Register AI routes (Mistral/Vibe)
        from wizard.routes.ai_routes import create_ai_routes

        ai_router = create_ai_routes(auth_guard=self._authenticate)
        app.include_router(ai_router)

        # Register Configuration routes
        from wizard.routes.config_routes import create_config_routes

        config_router = create_config_routes(auth_guard=self._authenticate)
        app.include_router(config_router)
        # Register Provider management routes
        from wizard.routes.provider_routes import create_provider_routes

        provider_router = create_provider_routes(auth_guard=self._authenticate)
        app.include_router(provider_router)

        # Register System Info routes (OS detection, library status)
        from wizard.routes.system_info_routes import create_system_info_routes

        system_info_router = create_system_info_routes(auth_guard=self._authenticate)
        app.include_router(system_info_router)

        # Register Wiki provisioning routes
        from wizard.routes.wiki_routes import create_wiki_routes

        wiki_router = create_wiki_routes(auth_guard=self._authenticate)
        app.include_router(wiki_router)

        # Register Library management routes
        from wizard.routes.library_routes import get_library_router

        library_router = get_library_router()
        app.include_router(library_router)

        # Mount dashboard static files
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse, HTMLResponse

        dashboard_path = Path(__file__).parent / "dashboard" / "dist"
        if dashboard_path.exists():
            app.mount(
                "/assets",
                StaticFiles(directory=str(dashboard_path / "assets")),
                name="assets",
            )

            @app.get("/")
            async def serve_dashboard():
                return FileResponse(str(dashboard_path / "index.html"))

        else:
            # Fallback: serve basic dashboard when build isn't available
            @app.get("/")
            async def serve_dashboard_fallback():
                return HTMLResponse(self._get_fallback_dashboard_html())

        self.app = app
        return app

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
                <div class="code">/api/v1/index</div>
            </div>

            <div class="endpoint">
                <h3>📡 Server Status</h3>
                <p>Rate limits, sessions, and costs</p>
                <div class="code">/api/v1/status</div>
            </div>

            <div class="endpoint">
                <h3>🤖 AI Models</h3>
                <p>Available AI models for routing</p>
                <div class="code">/api/v1/ai/models</div>
            </div>

            <div class="endpoint">
                <h3>🔌 Port Manager</h3>
                <p>Manage connected devices and ports</p>
                <div class="code">/api/v1/ports/status</div>
            </div>

            <div class="endpoint">
                <h3>🔗 VS Code Bridge</h3>
                <p>Integration with VS Code extension</p>
                <div class="code">/api/v1/vscode/status</div>
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
            return {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "services": {
                    "plugin_repo": self.config.plugin_repo_enabled,
                    "web_proxy": self.config.web_proxy_enabled,
                    "gmail_relay": self.config.gmail_relay_enabled,
                    "ai_gateway": self.config.ai_gateway_enabled,
                },
            }

        @app.get("/api/v1/index")
        async def dashboard_index():
            """Dashboard index data."""
            from wizard.services.system_info_service import get_system_info_service

            system_service = get_system_info_service()
            system_stats = self._get_system_stats()
            os_info = system_service.get_os_info()
            library_status = system_service.get_library_status()
            log_stats = self.logging_manager.get_log_stats()

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
                        "name": "Gmail Relay",
                        "enabled": self.config.gmail_relay_enabled,
                        "description": "Send emails via Gmail API",
                    },
                    {
                        "name": "AI Gateway",
                        "enabled": self.config.ai_gateway_enabled,
                        "description": "AI model access with cost tracking",
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

        @app.get("/api/v1/github/health")
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

        @app.get("/api/v1/system/stats")
        async def system_stats():
            """Return current system resource stats."""
            return self._get_system_stats()

        @app.get("/api/v1/status")
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

        @app.get("/api/v1/rate-limits")
        async def get_rate_limits(request: Request):
            """Get current rate limit status."""
            device_id = await self._authenticate(request)
            return self.rate_limiter.get_device_stats(device_id)

        # AI gateway routes
        @app.get("/api/v1/ai/status")
        async def ai_status(request: Request):
            """Return AI gateway + routing status."""
            device_id = await self._authenticate(request)
            return {
                "device_id": device_id,
                "gateway": self.ai_gateway.get_status(),
            }

        @app.get("/api/v1/ai/models")
        async def ai_models(request: Request):
            """List available AI models (local-first)."""
            await self._authenticate(request)
            return {"models": self.ai_gateway.list_models()}

        @app.post("/api/v1/ai/complete")
        async def ai_complete(request: Request):
            """Run AI completion through the routed gateway."""
            device_id = await self._authenticate(request)
            body = await request.json()

            ai_request = AIRequest(
                prompt=body.get("prompt", ""),
                model=body.get("model", ""),
                system_prompt=body.get("system") or body.get("system_prompt", ""),
                max_tokens=body.get("max_tokens", 1024),
                temperature=body.get("temperature", 0.7),
                stream=body.get("stream", False),
                task_id=body.get("task_id"),
                workspace=body.get("workspace", "core"),
                privacy=body.get("privacy", "internal"),
                urgency=body.get("urgency", "normal"),
                tags=body.get("tags") or [],
                actor=body.get("actor"),
                conversation_id=body.get("conversation_id"),
            )

            response = await self.ai_gateway.complete(ai_request, device_id=device_id)
            status_code = 200 if response.success else 400
            return JSONResponse(status_code=status_code, content=response.to_dict())

        # Plugin repository routes
        @app.get("/api/v1/plugin/list")
        async def list_plugins(request: Request):
            """List available plugins."""
            await self._authenticate(request)
            return await self._list_plugins()

        @app.get("/api/v1/plugin/{plugin_id}")
        async def get_plugin_info(plugin_id: str, request: Request):
            """Get plugin information."""
            await self._authenticate(request)
            return await self._get_plugin_info(plugin_id)

        @app.get("/api/v1/plugin/{plugin_id}/download")
        async def download_plugin(plugin_id: str, request: Request):
            """Download plugin package."""
            await self._authenticate(request)
            return await self._download_plugin(plugin_id)

        # Web proxy routes
        @app.post("/api/v1/web/fetch")
        async def fetch_url(request: Request):
            """Fetch web content (proxy)."""
            if not self.config.web_proxy_enabled:
                raise HTTPException(status_code=503, detail="Web proxy disabled")
            await self._authenticate(request)
            body = await request.json()
            return await self._fetch_url(body.get("url"), body.get("options", {}))

        # GitHub webhook (actions + repo sync)
        @app.post("/api/v1/github/webhook")
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
        @app.post("/api/v1/github/sync")
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

        # TUI Control Routes (for Wizard TUI interface)
        @app.get("/api/v1/devices")
        async def list_devices():
            """List connected devices (TUI endpoint)."""
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

        @app.get("/api/v1/logs")
        async def get_logs(
            request: Request,
            category: str = "all",
            filter: Optional[str] = None,
            limit: int = 200,
            level: Optional[str] = None,
        ):
            """Return recent Wizard logs (latest first)."""
            _ = request  # placeholder for future auth guard
            selected_category = filter or category or "all"
            return self._read_logs(selected_category, limit=limit, level=level)

        @app.post("/api/v1/models/switch")
        async def switch_model(request: Request):
            """Switch AI model (TUI endpoint)."""
            body = await request.json()
            model = body.get("model")
            if not model:
                raise HTTPException(status_code=400, detail="Model required")

            # TODO: Implement actual model switching in AI gateway
            return {"success": True, "model": model, "message": f"Switched to {model}"}

        @app.post("/api/v1/services/{service}/{action}")
        async def control_service(service: str, action: str):
            """Control service start/stop (TUI endpoint)."""
            valid_services = ["web-proxy", "gmail-relay", "ai-gateway", "plugin-repo"]
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
        log_dir = self.logging_manager.log_dir
        if not log_dir.exists():
            return {
                "logs": [],
                "category": category,
                "limit": limit,
                "categories": [],
                "stats": {},
            }

        files = sorted(
            log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        categories = sorted({p.stem.split("-")[0] for p in files})

        selected = (category or "all").lower()
        entries: List[Dict[str, Any]] = []

        for log_file in files:
            if selected not in ("all", "") and not log_file.stem.startswith(
                f"{selected}-"
            ):
                continue

            for line in self._tail_file(log_file, max(limit * 3, 200)):
                parsed = self._parse_log_line(line, log_file.name)
                if not parsed:
                    continue
                if level and parsed["level"].lower() != level.lower():
                    continue
                entries.append(parsed)

        entries.sort(
            key=lambda e: e.get("timestamp_sort") or e.get("timestamp"),
            reverse=True,
        )
        trimmed = entries[:limit]
        for entry in trimmed:
            entry.pop("timestamp_sort", None)

        return {
            "logs": trimmed,
            "category": selected,
            "limit": limit,
            "categories": categories,
            "stats": self.logging_manager.get_log_stats(),
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

    def _parse_log_line(self, line: str, filename: str) -> Optional[Dict[str, Any]]:
        """Parse a log line emitted by LoggingManager format."""
        match = self.LOG_LINE_PATTERN.match(line)
        if not match:
            return None

        ts_raw = match.group("timestamp")
        try:
            ts_dt = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S")
            ts_iso = ts_dt.isoformat()
        except ValueError:
            ts_dt = None
            ts_iso = ts_raw

        return {
            "timestamp": ts_iso,
            "timestamp_sort": ts_dt,
            "level": match.group("level"),
            "category": match.group("category"),
            "source": match.group("source") or "wizard",
            "message": match.group("message"),
            "file": filename,
        }

    async def _authenticate(self, request: Request) -> str:
        """Authenticate device request."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")

        token = auth_header[7:]
        # TODO: Validate token against paired devices
        # For now, extract device_id from token format
        device_id = token.split(":")[0] if ":" in token else token[:16]

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

    @staticmethod
    def _verify_signature(
        raw_body: bytes, signature: Optional[str], secret: str
    ) -> bool:
        """Validate GitHub webhook signature (sha256)."""
        if not signature or not signature.startswith("sha256="):
            return False
        expected = hmac.new(
            secret.encode("utf-8"), raw_body, hashlib.sha256
        ).hexdigest()
        provided = signature.split("sha256=", 1)[1]
        return hmac.compare_digest(expected, provided)

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
        plugin_path = PLUGIN_REPO_PATH / plugin_id

        if not plugin_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Plugin not found: {plugin_id}"
            )

        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Plugin manifest not found: {plugin_id}"
            )

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
        plugin_path = PLUGIN_REPO_PATH / plugin_id

        if not plugin_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Plugin not found: {plugin_id}"
            )

        packages = list(plugin_path.glob("*.tar.gz")) + list(plugin_path.glob("*.tcz"))
        if not packages:
            raise HTTPException(
                status_code=404, detail=f"No package found for: {plugin_id}"
            )

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
        if not url:
            raise HTTPException(status_code=400, detail="URL required")

        # Security checks
        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL scheme")

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

    config = WizardConfig(
        host=args.host,
        port=args.port,
        debug=args.debug,
    )

    server = WizardServer(config)

    if not args.no_interactive:
        # Interactive mode with console (default)
        server.run(interactive=True)
    else:
        # Daemon mode without console
        print(f"🧙 Starting uDOS Wizard Server on {args.host}:{args.port}")
        server.run(interactive=False)
