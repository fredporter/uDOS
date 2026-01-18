"""
Wizard Server Interactive Console
==================================

Interactive command prompt for Wizard Server that runs while servers are active.
Allows real-time monitoring, configuration, and system procedures.

Commands:
  status     - Show server status and capabilities
  services   - List all services and their versions
  config     - Show current configuration
  health     - Run health checks
  reload     - Reload configuration
  github     - Show GitHub Actions status
  workflows  - Alias for 'github' command
  help       - Show this help message
  exit/quit  - Shutdown server gracefully
"""

import asyncio
import sys
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import json


class WizardConsole:
    """Interactive console for Wizard Server."""

    def __init__(self, server_instance, config):
        """Initialize console with server reference."""
        self.server = server_instance
        self.config = config
        self.running = False
        self.commands: Dict[str, Callable] = {
            "status": self.cmd_status,
            "services": self.cmd_services,
            "config": self.cmd_config,
            "health": self.cmd_health,
            "reload": self.cmd_reload,
            "github": self.cmd_github,
            "workflows": self.cmd_workflows,            "poke": self.cmd_poke,            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
        }

    def print_banner(self):
        """Display startup banner with capabilities."""
        version = self._get_version()
        
        banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🧙  uDOS WIZARD SERVER  v{version}                        ║
║                                                                  ║
║   Production Server - Port {self.config.port}                                      ║
║   {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}                                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

📊 CAPABILITIES:
"""
        print(banner)
        
        # List enabled services
        services = self._get_service_status()
        for service_name, service_info in services.items():
            status = "✅" if service_info["enabled"] else "⏸️ "
            version_str = f"v{service_info.get('version', 'unknown')}"
            print(f"  {status} {service_name:<20} {version_str:<12} {service_info.get('description', '')}")
        
        print(f"\n⚙️  CONFIGURATION:")
        print(f"  • Rate Limit: {self.config.requests_per_minute}/min, {self.config.requests_per_hour}/hour")
        print(f"  • AI Budget: ${self.config.ai_budget_daily}/day, ${self.config.ai_budget_monthly}/month")
        print(f"  • Debug Mode: {'Enabled' if self.config.debug else 'Disabled'}")
        
        print(f"\n🌐 ENDPOINTS:")
        print(f"  • Health:         http://{self.config.host}:{self.config.port}/health")
        print(f"  • API:            http://{self.config.host}:{self.config.port}/api/v1/")
        print(f"  • WebSocket:      ws://{self.config.host}:{self.config.port}/ws")
        print(f"  • Documentation:  http://{self.config.host}:{self.config.port}/docs")
        
        print("\n💬 INTERACTIVE MODE: Type 'help' for commands, 'exit' to shutdown")
        print("=" * 68)
        print()

    def _get_version(self) -> str:
        """Get wizard server version."""
        try:
            version_file = Path(__file__).parent.parent / "version.json"
            if version_file.exists():
                with open(version_file) as f:
                    data = json.load(f)
                    v = data["version"]
                    return f"{v['major']}.{v['minor']}.{v['patch']}.{v['build']}"
        except Exception:
            pass
        return "1.1.0.0"

    def _get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all services."""
        return {
            "Plugin Repository": {
                "enabled": self.config.plugin_repo_enabled,
                "version": "1.1.0",
                "description": "Plugin distribution and updates"
            },
            "AI Gateway": {
                "enabled": self.config.ai_gateway_enabled,
                "version": "1.1.0",
                "description": "AI model routing (Ollama/OpenRouter)"
            },
            "Web Proxy": {
                "enabled": self.config.web_proxy_enabled,
                "version": "1.0.0",
                "description": "Web content fetching"
            },
            "Gmail Relay": {
                "enabled": self.config.gmail_relay_enabled,
                "version": "1.0.0",
                "description": "Email relay service"
            },
            "GitHub Monitor": {
                "enabled": True,
                "version": "1.0.0",
                "description": "CI/CD self-healing (Actions webhooks)"
            },
            "Rate Limiter": {
                "enabled": True,
                "version": "1.1.0",
                "description": "Request rate limiting"
            },
            "Cost Tracker": {
                "enabled": True,
                "version": "1.0.0",
                "description": "API cost monitoring"
            },
            "Device Auth": {
                "enabled": True,
                "version": "1.0.0",
                "description": "Device authentication"
            },
            "WebSocket": {
                "enabled": True,
                "version": "1.0.0",
                "description": "Real-time updates"
            }
        }

    async def cmd_status(self, args: list) -> None:
        """Show server status."""
        print("\n📊 SERVER STATUS:")
        print(f"  • Uptime: {self._get_uptime()}")
        print(f"  • Port: {self.config.port}")
        print(f"  • Debug: {'Yes' if self.config.debug else 'No'}")
        print(f"  • Active Services: {sum(1 for s in self._get_service_status().values() if s['enabled'])}/8")
        print()

    async def cmd_services(self, args: list) -> None:
        """List all services with versions."""
        print("\n🔧 SERVICES:")
        services = self._get_service_status()
        for name, info in services.items():
            status = "✅ ACTIVE" if info["enabled"] else "⏸️  INACTIVE"
            print(f"  {name:<20} v{info['version']:<8} {status}")
            print(f"    └─ {info['description']}")
        print()

    async def cmd_config(self, args: list) -> None:
        """Show current configuration."""
        print("\n⚙️  CONFIGURATION:")
        print(f"  Host: {self.config.host}")
        print(f"  Port: {self.config.port}")
        print(f"  Debug: {self.config.debug}")
        print(f"\n  Rate Limiting:")
        print(f"    • Per Minute: {self.config.requests_per_minute}")
        print(f"    • Per Hour: {self.config.requests_per_hour}")
        print(f"\n  AI Budgets:")
        print(f"    • Daily: ${self.config.ai_budget_daily}")
        print(f"    • Monthly: ${self.config.ai_budget_monthly}")
        print(f"\n  Service Toggles:")
        print(f"    • Plugin Repo: {self.config.plugin_repo_enabled}")
        print(f"    • Web Proxy: {self.config.web_proxy_enabled}")
        print(f"    • Gmail Relay: {self.config.gmail_relay_enabled}")
        print(f"    • AI Gateway: {self.config.ai_gateway_enabled}")
        print()

    async def cmd_health(self, args: list) -> None:
        """Run health checks."""
        print("\n🏥 HEALTH CHECKS:")
        
        # Check data directories
        data_path = Path(__file__).parent.parent.parent / "memory" / "wizard"
        plugin_path = Path(__file__).parent.parent.parent / "distribution" / "plugins"
        
        print(f"  • Data Directory: {'✅ OK' if data_path.exists() else '❌ MISSING'}")
        print(f"  • Plugin Directory: {'✅ OK' if plugin_path.exists() else '❌ MISSING'}")
        
        # Check configuration
        config_path = Path(__file__).parent.parent / "config" / "wizard.json"
        print(f"  • Configuration: {'✅ OK' if config_path.exists() else '⚠️  DEFAULT'}")
        
        # Check service status
        services = self._get_service_status()
        active_count = sum(1 for s in services.values() if s["enabled"])
        print(f"  • Active Services: ✅ {active_count}/8")
        
        print(f"\n  Overall Status: {'✅ HEALTHY' if active_count > 0 else '⚠️  DEGRADED'}")
        print()

    async def cmd_reload(self, args: list) -> None:
        """Reload configuration."""
        print("\n🔄 RELOADING CONFIGURATION...")
        try:
            from wizard.server import WizardConfig
            config_path = Path(__file__).parent.parent / "config" / "wizard.json"
            if config_path.exists():
                self.config = WizardConfig.load(config_path)
                print("  ✅ Configuration reloaded successfully")
            else:
                print("  ⚠️  No config file found, using defaults")
        except Exception as e:
            print(f"  ❌ Error reloading configuration: {e}")
        print()

    async def cmd_github(self, args: list) -> None:
        """Show GitHub Actions status and recent runs."""
        print("\n📊 GITHUB ACTIONS STATUS:")
        
        try:
            from wizard.services.github_monitor import get_github_monitor
            monitor = get_github_monitor()
            
            # Get recent runs
            runs = monitor.get_recent_runs(limit=5)
            
            if not runs:
                print("  ⚠️  No recent runs found (GitHub CLI may not be configured)")
                print("  Install: brew install gh")
                print("  Authenticate: gh auth login")
            else:
                print(f"\n  Recent Runs ({len(runs)}):")
                for run in runs:
                    # Status emoji
                    if run.conclusion == "success":
                        emoji = "✅"
                    elif run.conclusion == "failure":
                        emoji = "❌"
                    elif run.conclusion == "cancelled":
                        emoji = "🚫"
                    elif run.status == "in_progress":
                        emoji = "⏳"
                    else:
                        emoji = "⏸️ "
                    
                    # Format output
                    print(f"    {emoji} {run.name:<30} {run.head_branch:<15} {run.conclusion or run.status}")
            
            # Show failure patterns
            if monitor.failure_patterns:
                print(f"\n  Failure Patterns:")
                for pattern, count in sorted(monitor.failure_patterns.items(), key=lambda x: x[1], reverse=True):
                    print(f"    • {pattern}: {count}x")
            
            print(f"\n  Webhook URL: http://{self.config.host}:{self.config.port}/api/v1/github/webhook")
            print("  Configure at: https://github.com/[owner]/[repo]/settings/hooks")
        except Exception as e:
            print(f"  ⚠️  GitHub Monitor unavailable: {e}")
        print()

    async def cmd_workflows(self, args: list) -> None:
        """Alias for github command."""
        await self.cmd_github(args)

    async def cmd_poke(self, args: list) -> None:
        """Open a URL in the default browser."""
        import webbrowser
        
        if not args:
            print("\n❌ ERROR: No URL provided")
            print("   Usage: poke <url>")
            print("   Example: poke http://localhost:8765/docs")
            print()
            return
        
        url = args[0]
        
        # Validate URL format
        if not url.startswith(("http://", "https://", "file://")):
            print(f"\n⚠️  WARNING: URL should start with http://, https://, or file://")
            print(f"   Attempting to open: {url}")
        
        try:
            print(f"\n🌐 Opening URL in browser...")
            print(f"   {url}")
            webbrowser.open(url)
            print("   ✅ Browser opened successfully\n")
        except Exception as e:
            print(f"\n❌ ERROR: Could not open browser")
            print(f"   {str(e)}")
            print(f"   Copy URL manually: {url}\n")

    async def cmd_help(self, args: list) -> None:
        """Show help message."""
        print("\n💬 AVAILABLE COMMANDS:")
        print("  status     - Show server status and uptime")
        print("  services   - List all services with versions")
        print("  config     - Display current configuration")
        print("  health     - Run health checks on all systems")
        print("  reload     - Reload configuration from disk")
        print("  github     - Show GitHub Actions status and recent runs")
        print("  workflows  - Alias for 'github' command")
        print("  poke       - Open a URL in the default browser")
        print("  help       - Show this help message")
        print("  exit/quit  - Shutdown server gracefully")
        print()

    async def cmd_exit(self, args: list) -> None:
        """Shutdown server."""
        print("\n🛑 Shutting down Wizard Server...")
        self.running = False

    def _get_uptime(self) -> str:
        """Get server uptime (placeholder)."""
        # TODO: Track actual start time
        return "< 1 hour"

    async def run(self):
        """Run interactive console loop."""
        self.running = True
        self.print_banner()
        
        while self.running:
            try:
                # Use asyncio-compatible input
                print("wizard> ", end="", flush=True)
                
                # Run input in executor to not block event loop
                loop = asyncio.get_event_loop()
                command_line = await loop.run_in_executor(None, sys.stdin.readline)
                command_line = command_line.strip()
                
                if not command_line:
                    continue
                
                # Parse command
                parts = command_line.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute command
                if cmd in self.commands:
                    await self.commands[cmd](args)
                else:
                    print(f"❌ Unknown command: {cmd}")
                    print("   Type 'help' for available commands\n")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Keyboard interrupt received")
                await self.cmd_exit([])
                break
            except EOFError:
                print("\n")
                await self.cmd_exit([])
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
        
        print("✅ Wizard Server shutdown complete\n")
