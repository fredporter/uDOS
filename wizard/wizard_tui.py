"""
Wizard Server TUI Interface
============================

Terminal UI for Wizard Server management and monitoring.

Features:
- Real-time status dashboard
- AI provider management
- Service control (start/stop/restart)
- Cost tracking and quota monitoring
- Log viewing with filtering
- Device session monitoring
- Rate limit management

Commands:
  STATUS          - Show status dashboard
  SERVICES        - List services and status
  AI              - AI provider management
  QUOTA           - View cost tracking and quotas
  LOGS            - View filtered logs
  DEVICES         - List connected devices
  RATES           - Rate limit management
  CONFIG          - Edit Wizard configuration
  START [service] - Start service
  STOP [service]  - Stop service
  RESTART         - Restart Wizard Server

Version: v1.0.1
Author: Fred Porter
Date: 2026-01-13
"""

import os
import sys
import json
import asyncio
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass
from time import time, sleep

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import HTML

from wizard.services.logging_manager import get_logger
from core.ui.grid_renderer import GridRenderer, ViewportTier, Symbols
from core.utils.viewport import ViewportDetector

# Import monitoring manager
from wizard.services.monitoring_manager import (
    MonitoringManager,
    HealthStatus,
    AlertSeverity,
    AlertType,
)


@dataclass
class WizardStatus:
    """Wizard Server status snapshot."""

    server_running: bool = False
    server_port: int = 8765
    server_host: str = "127.0.0.1"
    uptime_seconds: int = 0
    start_time: float = 0
    active_devices: int = 0
    total_requests: int = 0

    # Services
    web_proxy_enabled: bool = False
    gmail_relay_enabled: bool = False
    ai_gateway_enabled: bool = False
    plugin_repo_enabled: bool = False

    # AI Status
    ollama_connected: bool = False
    openrouter_enabled: bool = False
    current_model: str = "devstral-small-2"
    ollama_endpoint: str = "http://127.0.0.1:11434"

    # Cost tracking
    ai_cost_today: float = 0.0
    ai_cost_month: float = 0.0
    ai_budget_daily: float = 10.0
    ai_budget_monthly: float = 100.0

    # Rate limits
    requests_per_minute: int = 60
    requests_per_hour: int = 1000

    # Last health check
    last_health_check: float = 0
    health_check_error: Optional[str] = None


class WizardTUI:
    """
    Wizard Server TUI Controller.

    Manages terminal interface for Wizard Server operations.
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        host: str = "127.0.0.1",
        port: int = 8765,
    ):
        """Initialize Wizard TUI."""
        self.config_path = (
            config_path or Path(__file__).parent / "config" / "wizard.json"
        )
        self.logger = get_logger("wizard-tui")
        self.host = host
        self.port = port

        # Initialize components
        self.viewport = ViewportDetector()
        terminal_size = self.viewport.detect_terminal_size()
        self.grid_renderer = GridRenderer(terminal_size[0])
        self.history = InMemoryHistory()
        self.session = None

        # Server status
        self.status = WizardStatus(server_host=host, server_port=port)
        self.server_instance = None

        # Initialize monitoring manager
        self.monitoring = MonitoringManager()

        # Track server process
        self.server_pid: Optional[int] = None
        self.server_process: Optional[subprocess.Popen] = None

        # Command handlers
        self.commands = {
            "STATUS": self._cmd_status,
            "SERVICES": self._cmd_services,
            "AI": self._cmd_ai,
            "QUOTA": self._cmd_quota,
            "LOGS": self._cmd_logs,
            "DEVICES": self._cmd_devices,
            "RATES": self._cmd_rates,
            "CONFIG": self._cmd_config,
            "START": self._cmd_start,
            "STOP": self._cmd_stop,
            "RESTART": self._cmd_restart,
            "BUILD": self._cmd_build,
            "TEST": self._cmd_test,
            "RELEASE": self._cmd_release,
            "ARTIFACTS": self._cmd_artifacts,
            "GITHUB": self._cmd_github,
            "HEALTH": self._cmd_health,
            "ALERTS": self._cmd_alerts,
            "RATELIMIT": self._cmd_ratelimit,
            "COSTS": self._cmd_costs,
            "AUDIT": self._cmd_audit,
            "HELP": self._cmd_help,
            "EXIT": self._cmd_exit,
            "QUIT": self._cmd_exit,
        }

        self.logger.info(f"[WIZ] Wizard TUI initialized (host={host}, port={port}")

    def _check_server_health(self) -> bool:
        """Check if Wizard Server is running via health endpoint."""
        try:
            url = f"http://{self.host}:{self.port}/health"
            response = requests.get(url, timeout=2)
            self.status.last_health_check = time()
            self.status.health_check_error = None
            return response.status_code == 200
        except requests.RequestException as e:
            self.status.last_health_check = time()
            self.status.health_check_error = str(e)
            return False
        except Exception as e:
            self.logger.error(f"[WIZ] Health check error: {e}")
            self.status.health_check_error = str(e)
            return False

    def _check_ollama_connection(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(
                f"{self.status.ollama_endpoint}/api/tags", timeout=2
            )
            return response.status_code == 200
        except Exception:
            return False

    def _load_status(self) -> WizardStatus:
        """Load current Wizard Server status."""
        status = self.status

        try:
            # Load configuration
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                    status.web_proxy_enabled = config.get("web_proxy_enabled", False)
                    status.gmail_relay_enabled = config.get(
                        "gmail_relay_enabled", False
                    )
                    status.ai_gateway_enabled = config.get("ai_gateway_enabled", False)
                    status.plugin_repo_enabled = config.get("plugin_repo_enabled", True)
                    status.ai_budget_daily = config.get("ai_budget_daily", 10.0)
                    status.ai_budget_monthly = config.get("ai_budget_monthly", 100.0)
                    status.requests_per_minute = config.get("requests_per_minute", 60)
                    status.requests_per_hour = config.get("requests_per_hour", 1000)

            # Check if server is running
            status.server_running = self._check_server_health()

            # Update uptime
            if status.server_running and status.start_time > 0:
                status.uptime_seconds = int(time() - status.start_time)

            # Check Ollama connection
            status.ollama_connected = self._check_ollama_connection()

        except Exception as e:
            self.logger.error(f"[WIZ] Error loading status: {e}")

        return status

    def _render_header(self) -> str:
        """Render TUI header."""
        terminal_size = self.viewport.detect_terminal_size()
        width = terminal_size[0]

        header = []
        header.append("═" * width)
        header.append("🧙 WIZARD SERVER TUI".center(width))
        header.append("Always-On Service Layer for uDOS".center(width))
        header.append("═" * width)

        return "\n".join(header)

    def _render_status_dashboard(self) -> str:
        """Render status dashboard."""
        status = self._load_status()
        terminal_size = self.viewport.detect_terminal_size()
        width = terminal_size[0]

        lines = []
        lines.append("\n📊 STATUS DASHBOARD\n")

        # Server Status
        server_status = (
            f"{Symbols.ONLINE} RUNNING"
            if status.server_running
            else f"{Symbols.OFFLINE} STOPPED"
        )
        lines.append(f"  Server:         {server_status}")
        if status.server_running:
            lines.append(
                f"  Endpoint:       http://{status.server_host}:{status.server_port}"
            )
            lines.append(
                f"  Uptime:         {self._format_uptime(status.uptime_seconds)}"
            )
        lines.append(f"  Active Devices: {status.active_devices}")
        lines.append(f"  Total Requests: {status.total_requests}\n")

        # Services
        lines.append("🔧 SERVICES\n")
        lines.append(
            f"  Web Proxy:     {self._format_enabled(status.web_proxy_enabled)}"
        )
        lines.append(
            f"  Gmail Relay:   {self._format_enabled(status.gmail_relay_enabled)}"
        )
        lines.append(
            f"  AI Gateway:    {self._format_enabled(status.ai_gateway_enabled)}"
        )
        lines.append(
            f"  Plugin Repo:   {self._format_enabled(status.plugin_repo_enabled)}\n"
        )

        # AI Status
        lines.append("🤖 AI PROVIDERS\n")
        ollama_status = (
            f"{Symbols.ONLINE} Connected"
            if status.ollama_connected
            else f"{Symbols.OFFLINE} Disconnected"
        )
        lines.append(f"  Ollama:        {ollama_status}")
        if status.ollama_connected:
            lines.append(f"    Endpoint:    {status.ollama_endpoint}")
        lines.append(
            f"  OpenRouter:    {self._format_enabled(status.openrouter_enabled)}"
        )
        lines.append(f"  Current Model: {status.current_model}\n")

        # Cost Tracking
        lines.append("💰 COST TRACKING\n")
        lines.append(
            f"  Today:         ${status.ai_cost_today:.2f} / ${status.ai_budget_daily:.2f}"
        )
        lines.append(
            f"  This Month:    ${status.ai_cost_month:.2f} / ${status.ai_budget_monthly:.2f}"
        )
        daily_pct = (
            (status.ai_cost_today / status.ai_budget_daily * 100)
            if status.ai_budget_daily > 0
            else 0
        )
        lines.append(f"  Daily Usage:   {self._render_progress_bar(daily_pct, 30)}\n")

        # Rate Limits
        lines.append("⚡ RATE LIMITS\n")
        lines.append(f"  Per Minute:    {status.requests_per_minute}")
        lines.append(f"  Per Hour:      {status.requests_per_hour}\n")

        return "\n".join(lines)

    def _format_enabled(self, enabled: bool) -> str:
        """Format enabled/disabled status."""
        return f"{Symbols.ONLINE} Enabled" if enabled else f"{Symbols.OFFLINE} Disabled"

    def _format_uptime(self, seconds: int) -> str:
        """Format uptime in human-readable form."""
        if seconds == 0:
            return "0s"

        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if mins > 0:
            parts.append(f"{mins}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)

    def _render_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Render progress bar."""
        filled = int(percentage / 100 * width)
        bar = Symbols.SIGNAL_100 * filled + Symbols.SIGNAL_00 * (width - filled)
        return f"[{bar}] {percentage:.1f}%"

    # Command Handlers

    def _cmd_status(self, args: List[str]) -> str:
        """Show status dashboard."""
        return self._render_status_dashboard()

    def _cmd_services(self, args: List[str]) -> str:
        """List services and status."""
        lines = []
        lines.append("\n🔧 WIZARD SERVICES\n")
        lines.append("Service          Status      Port")
        lines.append("───────────────  ──────────  ────")

        services = [
            ("Web Proxy", self.status.web_proxy_enabled, 8765),
            ("Gmail Relay", self.status.gmail_relay_enabled, None),
            ("AI Gateway", self.status.ai_gateway_enabled, None),
            ("Plugin Repo", self.status.plugin_repo_enabled, None),
        ]

        for name, enabled, port in services:
            status_str = (
                f"{Symbols.ONLINE} Running" if enabled else f"{Symbols.OFFLINE} Stopped"
            )
            port_str = str(port) if port else "N/A"
            lines.append(f"{name:16} {status_str:12} {port_str}")

        lines.append("")
        return "\n".join(lines)

    def _cmd_ai(self, args: List[str]) -> str:
        """AI provider management."""
        if not args:
            return self._cmd_ai_status()

        subcommand = args[0].upper()

        if subcommand == "STATUS":
            return self._cmd_ai_status()
        elif subcommand == "MODELS":
            return self._cmd_ai_models()
        elif subcommand == "SWITCH":
            if len(args) < 2:
                return "❌ Usage: AI SWITCH <model_name>"
            return self._cmd_ai_switch(args[1])
        else:
            return f"❌ Unknown AI subcommand: {subcommand}\nTry: AI STATUS, AI MODELS, AI SWITCH"

    def _cmd_ai_status(self) -> str:
        """Show AI provider status."""
        lines = []
        lines.append("\n🤖 AI PROVIDER STATUS\n")

        # Ollama
        ollama_status = (
            f"{Symbols.ONLINE} Connected"
            if self.status.ollama_connected
            else f"{Symbols.OFFLINE} Disconnected"
        )
        lines.append(f"Ollama (Local):    {ollama_status}")
        lines.append(f"  Endpoint:        http://127.0.0.1:11434")
        lines.append(f"  Default Model:   {self.status.current_model}\n")

        # OpenRouter
        or_status = (
            f"{Symbols.ONLINE} Enabled"
            if self.status.openrouter_enabled
            else f"{Symbols.OFFLINE} Disabled"
        )
        lines.append(f"OpenRouter (Cloud): {or_status}")
        lines.append(f"  Endpoint:        https://openrouter.ai/api/v1")
        lines.append(f"  Status:          {or_status}\n")

        lines.append("💰 Usage Today:      $" + f"{self.status.ai_cost_today:.4f}")
        lines.append("💰 Usage This Month: $" + f"{self.status.ai_cost_month:.2f}\n")

        return "\n".join(lines)

    def _cmd_ai_models(self) -> str:
        """List available AI models."""
        lines = []
        lines.append("\n🤖 AVAILABLE MODELS\n")
        lines.append("Local (Ollama):")
        lines.append("  • devstral-small-2 (default)")
        lines.append("  • llama3.2")
        lines.append("  • codellama\n")

        lines.append("Cloud (OpenRouter):")
        lines.append("  • anthropic/claude-sonnet-4")
        lines.append("  • google/gemini-pro")
        lines.append("  • mistral/mistral-large\n")

        return "\n".join(lines)

    def _cmd_ai_switch(self, model: str) -> str:
        """Switch AI model."""
        self.logger.info(f"[WIZ] Switching to model: {model}")

        try:
            # Try to switch model via API
            url = f"http://{self.host}:{self.port}/api/v1/models/switch"
            payload = {"model": model}
            response = requests.post(url, json=payload, timeout=3)

            if response.status_code == 200:
                self.status.current_model = model
                self.logger.info(f"[WIZ] Successfully switched to model: {model}")
                return f"✅ Switched to model: {model}"
            elif response.status_code == 400:
                return (
                    f"❌ Invalid model: {model}\nUse: AI MODELS to see available models"
                )
            else:
                return f"⚠️ Server error: {response.status_code}"

        except requests.RequestException as e:
            self.logger.error(f"[WIZ] Failed to switch model: {e}")
            return f"⚠️ Could not connect to API: {e}\nTry: START SERVER first"
        except Exception as e:
            self.logger.error(f"[WIZ] Error switching model: {e}")
            return f"❌ Error: {e}"

    def _cmd_quota(self, args: List[str]) -> str:
        """View cost tracking and quotas."""
        lines = []
        lines.append("\n💰 COST TRACKING & QUOTAS\n")

        # Daily
        lines.append("Daily Budget:")
        lines.append(f"  Limit:     ${self.status.ai_budget_daily:.2f}")
        lines.append(f"  Used:      ${self.status.ai_cost_today:.2f}")
        lines.append(
            f"  Remaining: ${self.status.ai_budget_daily - self.status.ai_cost_today:.2f}"
        )
        daily_pct = (
            (self.status.ai_cost_today / self.status.ai_budget_daily * 100)
            if self.status.ai_budget_daily > 0
            else 0
        )
        lines.append(f"  Progress:  {self._render_progress_bar(daily_pct, 30)}\n")

        # Monthly
        lines.append("Monthly Budget:")
        lines.append(f"  Limit:     ${self.status.ai_budget_monthly:.2f}")
        lines.append(f"  Used:      ${self.status.ai_cost_month:.2f}")
        lines.append(
            f"  Remaining: ${self.status.ai_budget_monthly - self.status.ai_cost_month:.2f}"
        )
        monthly_pct = (
            (self.status.ai_cost_month / self.status.ai_budget_monthly * 100)
            if self.status.ai_budget_monthly > 0
            else 0
        )
        lines.append(f"  Progress:  {self._render_progress_bar(monthly_pct, 30)}\n")

        return "\n".join(lines)

    def _cmd_logs(self, args: List[str]) -> str:
        """View filtered logs."""
        lines = []
        lines.append("\n📝 LOG VIEWER\n")

        # Parse filter arguments
        filter_type = "all"
        lines_count = 20
        if args:
            if args[0].upper() in ["API", "AI", "PLUGIN", "WEB", "ERROR", "WARN"]:
                filter_type = args[0].upper()
            if len(args) > 1 and args[1].isdigit():
                lines_count = int(args[1])

        try:
            # Try to get logs from API
            url = f"http://{self.host}:{self.port}/api/v1/logs"
            params = {"filter": filter_type, "limit": lines_count}
            response = requests.get(url, params=params, timeout=3)

            if response.status_code == 200:
                log_data = response.json()
                lines.append(f"Filter: {filter_type} | Lines: {lines_count}\n")
                for entry in log_data.get("logs", []):
                    timestamp = entry.get("timestamp", "")
                    level = entry.get("level", "INFO")
                    message = entry.get("message", "")
                    level_icon = {
                        "ERROR": "❌",
                        "WARN": "⚠️",
                        "INFO": "ℹ️",
                        "DEBUG": "🔍",
                    }.get(level, "•")
                    lines.append(f"{timestamp} {level_icon} {message}")
                lines.append("")
            else:
                lines.append("⚠️ Could not fetch logs from API")
                lines.append(
                    "Available filters: ALL, API, AI, PLUGIN, WEB, ERROR, WARN"
                )
                lines.append("Usage: LOGS [filter] [count]\n")

        except requests.RequestException as e:
            lines.append(f"⚠️ Could not connect to API: {e}")
            lines.append("Try: START SERVER first\n")

        return "\n".join(lines)

    def _cmd_devices(self, args: List[str]) -> str:
        """List connected devices."""
        lines = []
        lines.append("\n📱 CONNECTED DEVICES\n")
        lines.append(
            "Device ID             Name                Last Request         Requests"
        )
        lines.append(
            "────────────────────  ──────────────────  ───────────────────  ────────"
        )

        try:
            # Try to get devices from API
            url = f"http://{self.host}:{self.port}/api/v1/devices"
            response = requests.get(url, timeout=3)

            if response.status_code == 200:
                devices = response.json().get("devices", [])
                if not devices:
                    lines.append("\nNo devices currently connected.\n")
                else:
                    for device in devices:
                        device_id = device.get("id", "unknown")[:20]
                        name = device.get("name", "unnamed")[:18]
                        last_request = device.get("last_request", "never")
                        request_count = device.get("requests", 0)
                        lines.append(
                            f"{device_id:20}  {name:18}  {last_request:19}  {request_count}"
                        )
                    lines.append("")
            else:
                lines.append("\nNo devices currently connected.\n")

        except requests.RequestException as e:
            lines.append(f"\n⚠️ Could not connect to API: {e}")
            lines.append("Try: START SERVER first\n")
        except Exception as e:
            self.logger.error(f"[WIZ] Error loading devices: {e}")
            lines.append(f"\n⚠️ Error loading devices: {e}\n")

        return "\n".join(lines)

    def _cmd_rates(self, args: List[str]) -> str:
        """Rate limit management."""
        lines = []
        lines.append("\n⚡ RATE LIMIT CONFIGURATION\n")
        lines.append(f"Requests per Minute: {self.status.requests_per_minute}")
        lines.append(f"Requests per Hour:   {self.status.requests_per_hour}\n")
        lines.append("Tiers:")
        lines.append("  • FREE:      10/min,  100/hour")
        lines.append("  • STANDARD:  60/min, 1000/hour")
        lines.append("  • PREMIUM:  120/min, 5000/hour")
        lines.append("  • UNLIMITED: No limits\n")

        return "\n".join(lines)

    def _cmd_config(self, args: List[str]) -> str:
        """Edit Wizard configuration."""
        lines = []
        lines.append("\n⚙️ WIZARD CONFIGURATION\n")
        lines.append(f"Config file: {self.config_path}\n")

        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)

            lines.append(json.dumps(config, indent=2))
        else:
            lines.append("⚠️ Configuration file not found.\n")

        lines.append(
            "\nTo edit: Use your text editor to modify wizard/config/wizard.json"
        )
        lines.append("Then run: RESTART\n")

        return "\n".join(lines)

    def _cmd_start(self, args: List[str]) -> str:
        """Start service."""
        if not args:
            service = "server"
        else:
            service = args[0].lower()

        self.logger.info(f"[WIZ] Starting service: {service}")

        if service == "server":
            if self.status.server_running:
                return "⚠️ Wizard Server already running"

            return self._start_server()
        else:
            # Try to start service via API
            return self._control_service(service, "start")

    def _control_service(self, service: str, action: str) -> str:
        """Control service via API (start/stop)."""
        try:
            url = f"http://{self.host}:{self.port}/api/v1/services/{service}/{action}"
            response = requests.post(url, timeout=3)

            if response.status_code == 200:
                return f"✅ {action.capitalize()}ed service: {service}"
            elif response.status_code == 404:
                return f"❌ Unknown service: {service}\nUse: SERVICES to see available services"
            else:
                error_msg = response.json().get("error", "Unknown error")
                return f"⚠️ Error: {error_msg}"

        except requests.RequestException as e:
            self.logger.error(f"[WIZ] Failed to control service: {e}")
            return f"⚠️ Could not connect to API: {e}\nTry: START SERVER first"
        except Exception as e:
            self.logger.error(f"[WIZ] Error controlling service: {e}")
            return f"❌ Error: {e}"

    def _start_server(self) -> str:
        """Start Wizard Server process."""
        try:
            log_dir = Path(__file__).parent.parent / "memory" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = (
                log_dir / f"wizard-server-{datetime.now().strftime('%Y-%m-%d')}.log"
            )

            with open(log_file, "a") as f:
                self.server_process = subprocess.Popen(
                    [sys.executable, str(Path(__file__).parent / "server.py")],
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=str(Path(__file__).parent.parent),
                )
                self.server_pid = self.server_process.pid
                self.status.start_time = time()

            # Wait for server to start
            sleep(2)

            if self._check_server_health():
                self.status.server_running = True
                self.logger.info(
                    f"[WIZ] Server started successfully (PID: {self.server_pid})"
                )
                return f"✅ Wizard Server started (PID: {self.server_pid})\n   Endpoint: http://{self.host}:{self.port}"
            else:
                return f"⚠️ Server process started (PID: {self.server_pid}) but not responding yet\n   Check logs: {log_file}"

        except Exception as e:
            self.logger.error(f"[WIZ] Failed to start server: {e}")
            return f"❌ Failed to start server: {e}"

    def _cmd_stop(self, args: List[str]) -> str:
        """Stop service."""
        if not args:
            service = "server"
        else:
            service = args[0].lower()

        self.logger.info(f"[WIZ] Stopping service: {service}")

        if service == "server":
            return self._stop_server()
        else:
            # Try to stop service via API
            return self._control_service(service, "stop")

    def _stop_server(self) -> str:
        """Stop Wizard Server process."""
        try:
            if not self.status.server_running and self.server_pid is None:
                return "⚠️ Wizard Server not running"

            if self.server_process and self.server_pid:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()

                self.server_pid = None
                self.server_process = None
                self.status.server_running = False
                self.logger.info("[WIZ] Server stopped")
                return "✅ Wizard Server stopped"
            else:
                # Server not managed by this TUI instance
                self.status.server_running = False
                return "✅ Wizard Server status cleared"

        except Exception as e:
            self.logger.error(f"[WIZ] Error stopping server: {e}")
            return f"❌ Error stopping server: {e}"

    def _cmd_restart(self, args: List[str]) -> str:
        """Restart Wizard Server."""
        self.logger.info("[WIZ] Restarting Wizard Server")

        # Stop
        stop_result = self._stop_server()
        if "Error" in stop_result:
            return f"❌ Failed to stop server: {stop_result}"

        # Wait a bit
        sleep(1)

        # Start
        start_result = self._start_server()
        return f"{stop_result}\n{start_result}"

    # -------------------------------------------------------------------------
    # Monitoring Commands
    # -------------------------------------------------------------------------

    def _cmd_health(self, args: List[str]) -> str:
        """Check system health status."""
        lines = []
        lines.append("\n🏥 SYSTEM HEALTH CHECK\n")

        # Run health checks
        wizard_health = self.monitoring.check_wizard_server()
        ollama_health = self.monitoring.check_ollama()
        github_health = self.monitoring.check_github_api(
            token=os.getenv("GITHUB_TOKEN")
        )

        summary = self.monitoring.get_health_summary()

        # Overall status
        status_icon = (
            "✅"
            if summary["status"] == "healthy"
            else ("⚠️" if summary["status"] == "degraded" else "❌")
        )
        lines.append(f"{status_icon} Overall Status: {summary['status'].upper()}\n")

        # Details
        lines.append("Service Health Details:\n")
        lines.append("Service          Status       Response Time  Message")
        lines.append(
            "─────────────────  ───────────  ──────────────  ───────────────────"
        )

        for name, check in summary.get("checks", {}).items():
            status_str = (
                "✅ Healthy"
                if check["status"] == "healthy"
                else ("⚠️ Degraded" if check["status"] == "degraded" else "❌ Unhealthy")
            )
            response_time = f"{check['response_time_ms']:.1f}ms"
            message = check.get("message", "")[:30]
            lines.append(f"{name:17} {status_str:12} {response_time:14} {message}")

        lines.append(f"\nTotal Services:  {summary['services']}")
        lines.append(f"Healthy:         {summary['healthy']}")
        lines.append(f"Degraded:        {summary['degraded']}")
        lines.append(f"Unhealthy:       {summary['unhealthy']}\n")

        return "\n".join(lines)

    def _cmd_alerts(self, args: List[str]) -> str:
        """View and manage alerts."""
        if not args:
            return self._cmd_alerts_list()

        subcommand = args[0].upper()

        if subcommand == "LIST":
            return self._cmd_alerts_list()
        elif subcommand == "ACK":
            if len(args) < 2:
                return "❌ Usage: ALERTS ACK <alert_id>"
            return self._cmd_alerts_ack(args[1])
        elif subcommand == "RESOLVE":
            if len(args) < 2:
                return "❌ Usage: ALERTS RESOLVE <alert_id>"
            return self._cmd_alerts_resolve(args[1])
        else:
            return f"❌ Unknown alerts command: {subcommand}\nTry: LIST, ACK, RESOLVE"

    def _cmd_alerts_list(self) -> str:
        """List all alerts."""
        alerts = self.monitoring.get_alerts(unacknowledged_only=False, limit=20)

        if not alerts:
            return "\n✅ No alerts\n"

        lines = []
        lines.append("\n⚠️  ALERTS\n")
        lines.append("ID               Type           Severity   Service      Message")
        lines.append(
            "─────────────────  ──────────────  ─────────  ────────────  ───────────────────"
        )

        for alert in alerts:
            severity_icon = {
                "info": "ℹ️",
                "warning": "⚠️",
                "error": "❌",
                "critical": "🔴",
            }.get(alert.severity, "❓")

            alert_type = alert.type[:12]
            severity = alert.severity[:9]
            service = (alert.service or "system")[:12]
            message = alert.message[:21]

            ack_icon = "✓" if alert.acknowledged else " "

            lines.append(
                f"{alert.id:17} {alert_type:14} {severity:10} {service:13} {message}"
            )

        lines.append(f"\nTotal: {len(alerts)} alert(s)")
        unacked = len([a for a in alerts if not a.acknowledged])
        lines.append(f"Unacknowledged: {unacked}\n")

        return "\n".join(lines)

    def _cmd_alerts_ack(self, alert_id: str) -> str:
        """Acknowledge alert."""
        if self.monitoring.acknowledge_alert(alert_id):
            return f"✅ Alert {alert_id} acknowledged"
        else:
            return f"❌ Alert not found: {alert_id}"

    def _cmd_alerts_resolve(self, alert_id: str) -> str:
        """Resolve alert."""
        if self.monitoring.resolve_alert(alert_id):
            return f"✅ Alert {alert_id} resolved"
        else:
            return f"❌ Alert not found: {alert_id}"

    def _cmd_ratelimit(self, args: List[str]) -> str:
        """Show API rate limit status."""
        rate_limits = self.monitoring.get_rate_limit_status()

        if not rate_limits:
            return "\n📊 No rate limit data tracked yet.\n"

        lines = []
        lines.append("\n⚡ RATE LIMIT STATUS\n")
        lines.append("Service          Limit    Remaining  Usage %  Resets At")
        lines.append(
            "─────────────────  ────────  ─────────  ────────  ──────────────────"
        )

        for service, status in rate_limits.items():
            usage = status.usage_percent
            reset_dt = datetime.fromisoformat(status.reset_at)
            reset_str = reset_dt.strftime("%Y-%m-%d %H:%M")

            # Warn if approaching limit
            if usage > 80:
                warn_icon = "🔴"
            elif usage > 50:
                warn_icon = "🟡"
            else:
                warn_icon = "🟢"

            lines.append(
                f"{service:17} {status.limit:8}  {status.remaining:9}  {usage:6.1f}%  {reset_str}"
            )

        lines.append("")
        return "\n".join(lines)

    def _cmd_costs(self, args: List[str]) -> str:
        """Monitor service costs."""
        costs = self.monitoring.get_cost_summary()

        if not costs:
            return "\n💰 No cost tracking data yet.\n"

        lines = []
        lines.append("\n💰 COST MONITORING\n")
        lines.append(
            "Service         Daily Cost      Daily Budget  Usage %  Monthly Cost      Monthly Budget  Usage %"
        )
        lines.append(
            "─────────────────  ──────────────  ──────────────  ───────  ──────────────────  ────────────────  ───────"
        )

        for service, metrics in costs.items():
            daily_cost = f"${metrics.cost_today:.2f}"
            daily_budget = f"${metrics.budget_daily:.2f}"
            monthly_cost = f"${metrics.cost_month:.2f}"
            monthly_budget = f"${metrics.budget_monthly:.2f}"

            lines.append(
                f"{service:17} {daily_cost:14} {daily_budget:14} {metrics.usage_percent_daily:6.1f}%  "
                f"{monthly_cost:18} {monthly_budget:16} {metrics.usage_percent_monthly:6.1f}%"
            )

        lines.append("")
        return "\n".join(lines)

    def _cmd_audit(self, args: List[str]) -> str:
        """View audit log."""
        operation = args[0] if args and args[0].upper() != "SERVICE" else None
        service = args[1] if len(args) > 1 else None

        # Get audit log
        audit_log = self.monitoring.get_audit_log(
            operation=operation, service=service, limit=20
        )

        if not audit_log:
            return "\n📝 No audit log entries found.\n"

        lines = []
        lines.append("\n📝 AUDIT LOG\n")
        lines.append(
            "Timestamp                 Operation         Service       User     Status   Duration"
        )
        lines.append(
            "─────────────────────────  ─────────────────  ─────────────  ─────────  ───────  ────────────"
        )

        for entry in audit_log:
            timestamp = datetime.fromisoformat(entry.timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            operation = entry.operation[:17]
            service = (entry.service or "N/A")[:13]
            user = entry.user[:9]
            status = "✅ OK" if entry.success else "❌ FAIL"
            duration = f"{entry.duration_ms:.0f}ms" if entry.duration_ms else "N/A"

            lines.append(
                f"{timestamp}  {operation:17}  {service:13}  {user:9}  {status:7}  {duration}"
            )

        lines.append(f"\nTotal: {len(audit_log)} entries\n")

        return "\n".join(lines)

    def _cmd_help(self, args: List[str]) -> str:
        """Show help."""
        lines = []
        lines.append("\n📚 WIZARD TUI COMMANDS\n")
        lines.append("Command            Description")
        lines.append("─────────────────  ────────────────────────────────────")
        lines.append("STATUS             Show status dashboard")
        lines.append("SERVICES           List services and status")
        lines.append("AI                 AI provider management")
        lines.append("QUOTA              View cost tracking and quotas")
        lines.append("LOGS               View filtered logs")
        lines.append("DEVICES            List connected devices")
        lines.append("RATES              Rate limit management")
        lines.append("CONFIG             Edit Wizard configuration")
        lines.append("START <service>    Start service")
        lines.append("STOP <service>     Stop service")
        lines.append("RESTART            Restart Wizard Server")
        lines.append("")
        lines.append("Monitoring Commands:")
        lines.append("HEALTH             Check system health status")
        lines.append("ALERTS             View and manage alerts")
        lines.append("RATELIMIT          Show API rate limit status")
        lines.append("COSTS              Monitor service costs")
        lines.append("AUDIT              View audit log")
        lines.append("")
        lines.append("CI/CD Commands:")
        lines.append("BUILD <target>     Trigger build (core, app, wizard, api, all)")
        lines.append("TEST <target>      Run test suite (core, app, wizard, api, all)")
        lines.append("RELEASE <ver>      Create release from build")
        lines.append("ARTIFACTS          List/manage build artifacts")
        lines.append("GITHUB             GitHub integration status")
        lines.append("")
        lines.append("HELP               Show this help")
        lines.append("EXIT               Exit Wizard TUI\n")

        return "\n".join(lines)

    def _cmd_exit(self, args: List[str]) -> str:
        """Exit Wizard TUI."""
        self.logger.info("[WIZ] Exiting Wizard TUI")
        return "exit"

    def _process_command(self, user_input: str) -> str:
        """Process user command."""
        if not user_input.strip():
            return ""

        parts = user_input.strip().split()
        command = parts[0].upper()
        args = parts[1:] if len(parts) > 1 else []

        if command in self.commands:
            try:
                result = self.commands[command](args)
                return result
            except Exception as e:
                self.logger.error(f"[WIZ] Error executing command '{command}': {e}")
                return f"❌ Error: {e}"
        else:
            return f"❌ Unknown command: {command}\nType HELP for available commands."

    def _get_prompt(self) -> HTML:
        """Get command prompt."""
        server_status = "●" if self.status.server_running else "○"
        return HTML(
            f"<ansigreen>wizard@udos</ansigreen> <ansired>{server_status}</ansired> > "
        )

    async def run_async(self):
        """Run TUI (async version)."""
        print("\033[2J\033[H")  # Clear screen
        print(self._render_header())
        print(self._render_status_dashboard())
        print("\nType HELP for commands, EXIT to quit.\n")

        # Create prompt session
        self.session = PromptSession(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
        )

        while True:
            try:
                # Update status
                self.status = self._load_status()

                # Get user input
                user_input = await self.session.prompt_async(self._get_prompt())

                # Process command
                result = self._process_command(user_input)

                if result == "exit":
                    print("\n👋 Goodbye!\n")
                    break

                if result:
                    print(result)

            except KeyboardInterrupt:
                print("\n\n⚠️ Use EXIT command to quit.\n")
                continue
            except EOFError:
                break
            except Exception as e:
                self.logger.error(f"[WIZ] Error in main loop: {e}")
                print(f"\n❌ Error: {e}\n")

    # -------------------------------------------------------------------------
    # CI/CD Commands
    # -------------------------------------------------------------------------

    def _cmd_build(self, args: List[str]) -> str:
        """Trigger build via CI/CD pipeline."""
        from wizard.github_integration.cicd_manager import CICDManager, BuildTarget
        from wizard.github_integration.client import GitHubClient

        if not args:
            return (
                "❌ Usage: BUILD <target> [branch]\n"
                "Targets: core, app, wizard, api, transport, all"
            )

        target_name = args[0].lower()
        branch = args[1] if len(args) > 1 else "main"

        try:
            # Map target name to enum
            target_map = {
                "core": BuildTarget.CORE,
                "app": BuildTarget.APP,
                "wizard": BuildTarget.WIZARD,
                "api": BuildTarget.API,
                "transport": BuildTarget.TRANSPORT,
                "all": BuildTarget.ALL,
            }

            if target_name not in target_map:
                return f"❌ Unknown target: {target_name}"

            target = target_map[target_name]

            # Initialize CI/CD manager
            client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
            cicd = CICDManager(
                client, "fredpook", "uDOS"
            )  # Replace with actual owner/repo

            # Trigger build
            print(f"\n🏗️ Building {target_name} from {branch}...\n")
            result = cicd.build(target, branch=branch, wait=False)

            lines = [f"\n✅ Build triggered: {result['build_id']}"]
            lines.append(f"Target: {result['target']}")
            lines.append(f"Branch: {result['branch']}")
            lines.append(f"Workflow Run ID: {result['workflow_run_id']}")
            lines.append(f"Status: {result['status']}")
            lines.append("\nCheck status with: ARTIFACTS LIST")

            return "\n".join(lines)

        except Exception as e:
            self.logger.error(f"[WIZ] Build failed: {e}")
            return f"❌ Build failed: {e}"

    def _cmd_test(self, args: List[str]) -> str:
        """Run test suite via CI/CD pipeline."""
        from wizard.github_integration.cicd_manager import CICDManager, BuildTarget
        from wizard.github_integration.client import GitHubClient

        target_name = args[0].lower() if args else "all"
        branch = args[1] if len(args) > 1 else "main"

        try:
            target_map = {
                "core": BuildTarget.CORE,
                "app": BuildTarget.APP,
                "wizard": BuildTarget.WIZARD,
                "api": BuildTarget.API,
                "all": BuildTarget.ALL,
            }

            target = target_map.get(target_name, BuildTarget.ALL)

            client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
            cicd = CICDManager(client, "fredpook", "uDOS")

            print(f"\n🧪 Running tests for {target_name}...\n")
            result = cicd.run_tests(target, branch=branch, wait=False)

            lines = [f"\n✅ Tests started: {result['test_id']}"]
            lines.append(f"Target: {result['target']}")
            lines.append(f"Branch: {result['branch']}")
            lines.append(f"Workflow Run ID: {result['workflow_run_id']}")
            lines.append(f"Status: {result['status']}")

            return "\n".join(lines)

        except Exception as e:
            self.logger.error(f"[WIZ] Test failed: {e}")
            return f"❌ Test failed: {e}"

    def _cmd_release(self, args: List[str]) -> str:
        """Create release from build artifacts."""
        from wizard.github_integration.cicd_manager import CICDManager
        from wizard.github_integration.client import GitHubClient

        if not args:
            return "❌ Usage: RELEASE <version> [build_id]"

        version = args[0]
        build_id = args[1] if len(args) > 1 else None

        try:
            client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
            cicd = CICDManager(client, "fredpook", "uDOS")

            print(f"\n📦 Creating release {version}...\n")
            result = cicd.create_release(version, build_id=build_id, draft=True)

            lines = [f"\n✅ Release created: {version}"]
            lines.append(f"Release ID: {result['id']}")
            lines.append(f"Tag: {result['tag']}")
            lines.append(f"URL: {result['url']}")
            lines.append(f"Status: Draft (publish when ready)")

            return "\n".join(lines)

        except Exception as e:
            self.logger.error(f"[WIZ] Release failed: {e}")
            return f"❌ Release failed: {e}"

    def _cmd_artifacts(self, args: List[str]) -> str:
        """List or manage build artifacts."""
        from wizard.github_integration.cicd_manager import CICDManager
        from wizard.github_integration.client import GitHubClient

        if not args:
            return "❌ Usage: ARTIFACTS <command>\n" "Commands: LIST, INFO <build_id>"

        subcommand = args[0].upper()

        try:
            client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
            cicd = CICDManager(client, "fredpook", "uDOS")

            if subcommand == "LIST":
                artifacts = cicd.list_artifacts()
                if not artifacts:
                    return "\nNo artifacts found."

                lines = ["\n📦 BUILD ARTIFACTS\n"]
                lines.append(
                    "Build ID         Artifact                  Size       Created"
                )
                lines.append(
                    "───────────────  ────────────────────────  ─────────  ──────────"
                )

                for artifact in artifacts[:20]:  # Show latest 20
                    size_mb = artifact["size"] / (1024 * 1024)
                    created = datetime.fromisoformat(artifact["created_at"]).strftime(
                        "%Y-%m-%d"
                    )
                    lines.append(
                        f"{artifact['build_id']:16} {artifact['name']:24} "
                        f"{size_mb:6.2f} MB  {created}"
                    )

                return "\n".join(lines)

            elif subcommand == "INFO":
                if len(args) < 2:
                    return "❌ Usage: ARTIFACTS INFO <build_id>"

                build_id = args[1]
                build = cicd.get_build_status(build_id)

                if not build:
                    return f"❌ Build not found: {build_id}"

                lines = [f"\n🏗️  BUILD INFO: {build_id}\n"]
                lines.append(f"Target: {build['target']}")
                lines.append(f"Branch: {build['branch']}")
                lines.append(f"Status: {build['status']}")
                lines.append(f"Started: {build['started_at']}")
                if "completed_at" in build:
                    lines.append(f"Completed: {build['completed_at']}")
                if build["artifacts"]:
                    lines.append(f"\nArtifacts:")
                    for artifact in build["artifacts"]:
                        lines.append(f"  - {artifact}")

                return "\n".join(lines)

            else:
                return f"❌ Unknown artifacts command: {subcommand}"

        except Exception as e:
            self.logger.error(f"[WIZ] Artifacts command failed: {e}")
            return f"❌ Artifacts command failed: {e}"

    def _cmd_github(self, args: List[str]) -> str:
        """GitHub integration management."""
        from wizard.github_integration.client import GitHubClient

        if not args:
            return (
                "❌ Usage: GITHUB <command>\n"
                "Commands: STATUS, REPOS, WORKFLOWS, RUNS"
            )

        subcommand = args[0].upper()

        try:
            client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))

            if subcommand == "STATUS":
                try:
                    user = client.get_user()
                    lines = ["\n🐙 GITHUB STATUS\n"]
                    lines.append(f"User: {user['login']}")
                    lines.append(f"Name: {user['name']}")
                    lines.append(f"Token: ✅ Valid")
                    lines.append(f"Rate Limit: {client.get_rate_limit()}/5000")
                    return "\n".join(lines)
                except Exception as e:
                    return f"❌ GitHub connection failed: {e}"

            else:
                return f"❌ Unknown GitHub command: {subcommand}"

        except Exception as e:
            self.logger.error(f"[WIZ] GitHub command failed: {e}")
            return f"❌ GitHub command failed: {e}"

    # -------------------------------------------------------------------------
    # End CI/CD Commands
    # -------------------------------------------------------------------------

    def run(self):
        """Run TUI (main entry point)."""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
        except Exception as e:
            self.logger.error(f"[WIZ] Fatal error: {e}")
            print(f"\n❌ Fatal error: {e}\n")
            sys.exit(1)


def main():
    """Main entry point."""
    tui = WizardTUI()
    tui.run()


if __name__ == "__main__":
    main()
