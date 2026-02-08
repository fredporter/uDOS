"""
Wizard Server Interactive Console
==================================

Interactive command prompt for Wizard Server that runs while servers are active.
Allows real-time monitoring, configuration, and system procedures.

Commands:
  status     - Show server status and capabilities
  services   - List all services and their versions
  config     - Show current configuration
  setup      - Show user and installation profile (from TUI story)
  health     - Run health checks
  reload     - Reload configuration
  github     - Show GitHub Actions status
  workflows  - Alias for 'github' command
  dev        - DEV MODE on/off/status/clear
  ai         - Vibe/Ollama/Mistral helpers
  git        - Git shortcuts (status/pull/push)
    workflow   - Workflow/todo helper
    logs       - Tail logs from memory/logs
    tree       - Generate structure.txt snapshots (2 levels)
  peek       - Convert URL to Markdown (PEEK <url> [filename])
  extract    - Extract PDF to Markdown (EXTRACT [file.pdf] or bulk)
  backup     - Create .backup snapshot (scope-aware)
  restore    - Restore latest backup (use --force)
  tidy       - Move junk into .archive
  clean      - Reset scope into .archive
  compost    - Move .archive/.backup/.tmp into /.compost
  destroy    - Dev TUI only (reinstall)
  help       - Show this help message
  exit/quit  - Shutdown server gracefully
"""

import asyncio
import sys
import json
import threading
import time
import urllib.request
import urllib.error
import urllib.parse
import subprocess
import shutil
from wizard.services.path_utils import get_repo_root
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import os
from wizard.services.dev_mode_service import get_dev_mode_service
from wizard.services.vibe_service import VibeService
from wizard.services.mistral_api import MistralAPI
from wizard.services.workflow_manager import WorkflowManager
from wizard.services.ai_context_store import write_context_bundle
from wizard.services.editor_utils import (
    resolve_workspace_path,
    open_in_editor,
    ensure_micro_repo,
)
from core.services.maintenance_utils import (
    create_backup,
    restore_backup,
    tidy,
    clean,
    compost,
    list_backups,
    default_repo_allowlist,
    default_memory_allowlist,
    get_memory_root,
)
from wizard.services.url_to_markdown_service import get_url_to_markdown_service
from wizard.services.pdf_ocr_service import get_pdf_ocr_service
from wizard.services.tree_service import TreeStructureService
from wizard.services.secret_store import get_secret_store, SecretStoreError


class WizardConsole:
    """Interactive console for Wizard Server."""

    def __init__(self, server_instance, config):
        """Initialize console with server reference."""
        self.server = server_instance
        self.config = config
        self.running = False
        self.start_time = time.time()
        self.repo_root = get_repo_root()
        self.commands: Dict[str, Callable] = {
            "status": self.cmd_status,
            "services": self.cmd_services,
            "config": self.cmd_config,
            "setup": self.cmd_setup,
            "health": self.cmd_health,
            "reload": self.cmd_reload,
            "reboot": self.cmd_reboot,
            "github": self.cmd_github,
            "workflows": self.cmd_workflows,
            "workflow": self.cmd_workflow,
            "dev": self.cmd_dev,
            "ai": self.cmd_ai,
            "git": self.cmd_git,
            "logs": self.cmd_logs,
            "tree": self.cmd_tree,
            "peek": self.cmd_peek,
            "extract": self.cmd_extract,
            "new": self.cmd_new,
            "edit": self.cmd_edit,
            "load": self.cmd_load,
            "save": self.cmd_save,
            "backup": self.cmd_backup,
            "restore": self.cmd_restore,
            "tidy": self.cmd_tidy,
            "clean": self.cmd_clean,
            "compost": self.cmd_compost,
            "destroy": self.cmd_destroy,
            "help": self.cmd_help,
            "providers": self.cmd_providers,
            "provider": self.cmd_provider,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
        }
        self._current_file: Optional[Path] = None
        self._dashboard_ready: Optional[bool] = None
        self.tree_service = TreeStructureService(self.repo_root)

    def _run_with_spinner(self, message: str, func: Callable[[], Any]) -> Any:
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        done = False
        error: Optional[BaseException] = None
        result: Any = None

        def runner():
            nonlocal done, error, result
            try:
                result = func()
            except BaseException as exc:
                error = exc
            finally:
                done = True

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

        idx = 0
        while not done:
            sys.stdout.write(f"\r{spinner[idx % len(spinner)]} {message}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.08)

        sys.stdout.write("\r")
        sys.stdout.flush()

        if error:
            print(f"⚠️  {message} (failed: {error})")
            return None

        print(f"✅ {message}")
        return result

    def _check_dashboard_build(self) -> bool:
        dashboard_index = Path(__file__).parent.parent / "dashboard" / "dist" / "index.html"
        return dashboard_index.exists()

    def _assistant_keys_path(self) -> Path:
        return Path(__file__).parent.parent / "config" / "assistant_keys.json"

    def _load_assistant_keys(self) -> Dict[str, Any]:
        path = self._assistant_keys_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}

    def _resolve_secret_store(self):
        try:
            store = get_secret_store()
            store.unlock()
            return store, None
        except SecretStoreError as exc:
            return None, str(exc)

    def _secret_has_value(self, store, key_id: str) -> bool:
        if not store or not key_id:
            return False
        entry = store.get_entry(key_id)
        return entry is not None and bool(entry.value)

    def _ollama_host(self) -> str:
        host = (os.getenv("OLLAMA_HOST") or "http://127.0.0.1:11434").strip()
        return host.rstrip("/")

    def _check_ollama_status(self) -> Dict[str, Any]:
        """Return ollama reachability + available models."""
        endpoint = self._ollama_host()
        try:
            with urllib.request.urlopen(f"{endpoint}/api/tags", timeout=4) as resp:
                if resp.status != 200:
                    return {"reachable": False, "models": [], "error": f"HTTP {resp.status}"}
                payload = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in payload.get("models", [])]
                return {"reachable": True, "models": models, "error": None}
        except Exception as exc:
            return {"reachable": False, "models": [], "error": str(exc)}

    def _check_openrouter_key(self) -> Dict[str, Any]:
        """Check if OpenRouter key is configured via assistant_keys or secret store."""
        assistant_keys = self._load_assistant_keys()
        providers_map = assistant_keys.get("providers", {})
        entry = providers_map.get("openrouter")
        key_id = None
        direct_key = None

        if isinstance(entry, dict):
            direct_key = entry.get("api_key") or entry.get("key")
            key_id = entry.get("key_id")
        elif isinstance(entry, str):
            direct_key = entry

        if direct_key:
            return {"configured": True, "source": "assistant_keys.json"}

        store, err = self._resolve_secret_store()
        if key_id and self._secret_has_value(store, key_id):
            return {"configured": True, "source": f"secret_store:{key_id}"}

        for candidate in ("openrouter_api_key", "ai-openrouter"):
            if self._secret_has_value(store, candidate):
                return {"configured": True, "source": f"secret_store:{candidate}"}

        if err:
            return {"configured": False, "locked": True, "error": err}

        return {"configured": False, "locked": False, "error": "Missing OpenRouter key"}

    def _check_default_ai_setup(self) -> Dict[str, Any]:
        """Check default AI providers (OF/OL/PR) readiness."""
        ollama = self._check_ollama_status()
        models = [m.split(":")[0] for m in ollama.get("models", [])]
        devstral_ready = "devstral-small-2" in models

        openrouter = self._check_openrouter_key()

        return {
            "ollama": ollama,
            "devstral": {"ready": devstral_ready, "model": "devstral-small-2"},
            "openrouter": openrouter,
        }

    def _print_default_ai_startup_checks(self) -> None:
        checks = self._check_default_ai_setup()
        base_host = "localhost" if self.config.host == "0.0.0.0" else self.config.host
        config_url = f"http://{base_host}:{self.config.port}/#config"

        print("\n🤖 DEFAULT AI STARTUP CHECKS (OF / OL / PR):")

        # OL: Ollama service
        if checks["ollama"]["reachable"]:
            print("  • OL (Ollama service): ✅ Reachable")
        else:
            print("  • OL (Ollama service): ⚠️  Not reachable")
            print(f"    - Start Ollama or set OLLAMA_HOST (currently {self._ollama_host()})")
            print(f"    - Visit Wizard Config to complete setup: {config_url}")

        # OF: Offline Devstral model
        if checks["devstral"]["ready"]:
            print("  • OF (Offline Devstral): ✅ Model ready")
        else:
            print("  • OF (Offline Devstral): ⚠️  Model missing")
            print("    - Install: ollama pull devstral-small-2")
            print(f"    - Or use Wizard Config: {config_url}")

        # PR: OpenRouter key
        if checks["openrouter"].get("configured"):
            print("  • PR (OpenRouter): ✅ Key configured")
        else:
            if checks["openrouter"].get("locked"):
                print("  • PR (OpenRouter): ⚠️  Secret store locked")
            else:
                print("  • PR (OpenRouter): ⚠️  Key missing")
            print("    - Add OpenRouter API key in Wizard Config → Quick Keys")
            print(f"    - Open: {config_url}")
        print()

    def _startup_checks(self) -> None:
        self._run_with_spinner("Preparing editor (micro)", ensure_micro_repo)
        self._dashboard_ready = self._run_with_spinner(
            "Checking dashboard build", self._check_dashboard_build
        )
        self._print_default_ai_startup_checks()

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
            print(
                f"  {status} {service_name:<20} {version_str:<12} {service_info.get('description', '')}"
            )

        print(f"\n⚙️  CONFIGURATION:")
        print(
            f"  • Rate Limit: {self.config.requests_per_minute}/min, {self.config.requests_per_hour}/hour"
        )
        print(
            f"  • AI Budget: ${self.config.ai_budget_daily}/day, ${self.config.ai_budget_monthly}/month"
        )
        print(f"  • Debug Mode: {'Enabled' if self.config.debug else 'Disabled'}")

        print(f"\n🌐 ENDPOINTS:")
        print(
            f"  • Health:         http://{self.config.host}:{self.config.port}/health"
        )
        print(
            f"  • API:            http://{self.config.host}:{self.config.port}/api/"
        )
        print(f"  • WebSocket:      ws://{self.config.host}:{self.config.port}/ws")
        print(f"  • Documentation:  http://{self.config.host}:{self.config.port}/docs")

        if self._dashboard_ready is False:
            print("\n⚠️  Dashboard build missing. Run: cd wizard/dashboard && npm run build")

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
                "description": "Plugin distribution and updates",
            },
            "OK Gateway": {
                "enabled": self.config.ok_gateway_enabled,
                "version": "1.1.0",
                "description": "AI model routing (Ollama/OpenRouter)",
            },
            "Web Proxy": {
                "enabled": self.config.web_proxy_enabled,
                "version": "1.0.0",
                "description": "Web content fetching",
            },
            "GitHub Monitor": {
                "enabled": True,
                "version": "1.0.0",
                "description": "CI/CD self-healing (Actions webhooks)",
            },
            "Rate Limiter": {
                "enabled": True,
                "version": "1.1.0",
                "description": "Request rate limiting",
            },
            "Cost Tracker": {
                "enabled": True,
                "version": "1.0.0",
                "description": "API cost monitoring",
            },
            "Device Auth": {
                "enabled": True,
                "version": "1.0.0",
                "description": "Device authentication",
            },
            "WebSocket": {
                "enabled": True,
                "version": "1.0.0",
                "description": "Real-time updates",
            },
        }

    def _parse_scope(self, args: list) -> tuple[str, list]:
        if not args:
            return "workspace", []
        scope = args[0].lower()
        if scope in {"current", "+subfolders", "workspace", "all"}:
            return scope, args[1:]
        return "workspace", args

    def _resolve_scope(self, scope: str) -> tuple[Path, bool]:
        if scope == "current":
            return Path.cwd(), False
        if scope == "+subfolders":
            return Path.cwd(), True
        if scope == "all":
            return get_repo_root(), True
        return get_memory_root(), True

    async def cmd_status(self, args: list) -> None:
        """Show server status."""
        print("\n📊 SERVER STATUS:")
        print(f"  • Uptime: {self._get_uptime()}")
        print(f"  • Port: {self.config.port}")
        print(f"  • Debug: {'Yes' if self.config.debug else 'No'}")
        print(
            f"  • Active Services: {sum(1 for s in self._get_service_status().values() if s['enabled'])}/8"
        )
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
        print(f"    • OK Gateway: {self.config.ok_gateway_enabled}")
        print()

    async def cmd_setup(self, args: list) -> None:
        """Show setup profile information (from TUI story)."""
        from wizard.services.setup_profiles import load_user_profile, load_install_profile, load_install_metrics
        import os

        print("\n🧙 SETUP PROFILE:")

        # Quick diagnostic
        wizard_key = os.getenv("WIZARD_KEY")
        if not wizard_key:
            print("  ⚠️  WIZARD_KEY environment variable not set!")
            print()
            print("  💡 Fix this by:")
            print("     1. Ensure .env file exists in repo root with WIZARD_KEY=...")
            print("     2. Restart Wizard Server: ./bin/start_wizard.sh")
            print("     3. Or set manually: export WIZARD_KEY=<your-key>")
            print()
            return

        # Load user profile
        user_result = load_user_profile()
        if user_result.locked:
            print(f"  ⚠️  Secret store locked: {user_result.error}")
            print()
            print("  💡 This means:")
            print("     • WIZARD_KEY is set but doesn't match the encryption key")
            print("     • The secrets.tomb file may have been encrypted with a different key")
            print()
            print("  💡 To fix:")
            print("     1. Check .env file: cat .env | grep WIZARD_KEY")
            print("     2. If you changed the key, you may need to re-run the setup story")
            print("     3. Or delete wizard/secrets.tomb and re-submit the story")
            print()
            return

        if user_result.data:
            print("\n  User Identity:")
            print(f"    • Username: {user_result.data.get('username', 'N/A')}")
            print(f"    • Role: {user_result.data.get('role', 'N/A')}")
            print(f"    • Timezone: {user_result.data.get('timezone', 'N/A')}")
            print(f"    • Location: {user_result.data.get('location_name', 'N/A')} ({user_result.data.get('location_id', 'N/A')})")
        else:
            print("  ⚠️  No user profile found. Complete the setup story first.")

        # Load installation profile
        install_result = load_install_profile()
        if install_result.locked:
            print(f"  ⚠️  Secret store locked: {install_result.error}")
            print()
            return

        if install_result.data:
            print("\n  Installation:")
            print(f"    • ID: {install_result.data.get('installation_id', 'N/A')}")
            print(f"    • OS Type: {install_result.data.get('os_type', 'N/A')}")
            print(f"    • Lifespan Mode: {install_result.data.get('lifespan_mode', 'infinite')}")

            moves_limit = install_result.data.get('moves_limit')
            if moves_limit:
                print(f"    • Moves Limit: {moves_limit}")

            # Show capabilities
            capabilities = install_result.data.get('capabilities', {})
            if capabilities:
                print("\n  Capabilities:")
                for cap, enabled in capabilities.items():
                    status = "✅" if enabled else "❌"
                    print(f"    {status} {cap.replace('_', ' ').title()}")
        else:
            print("  ⚠️  No installation profile found. Complete the setup story first.")

        # Load metrics
        metrics = load_install_metrics()
        if metrics and metrics.get('moves_used') is not None:
            print("\n  Metrics:")
            print(f"    • Moves Used: {metrics.get('moves_used', 0)}")
            if metrics.get('moves_limit'):
                remaining = metrics['moves_limit'] - metrics.get('moves_used', 0)
                print(f"    • Remaining: {remaining}/{metrics['moves_limit']}")
            last_move = metrics.get('last_move_at')
            if last_move:
                print(f"    • Last Move: {last_move}")

        print()

    async def cmd_health(self, args: list) -> None:
        """Run health checks."""
        print("\n🏥 HEALTH CHECKS:")

        # Check data directories
        data_path = Path(__file__).parent.parent.parent / "memory" / "wizard"
        plugin_path = Path(__file__).parent.parent.parent / "distribution" / "plugins"

        print(f"  • Data Directory: {'✅ OK' if data_path.exists() else '❌ MISSING'}")
        print(
            f"  • Plugin Directory: {'✅ OK' if plugin_path.exists() else '❌ MISSING'}"
        )

        # Check configuration
        config_path = Path(__file__).parent.parent / "config" / "wizard.json"
        print(f"  • Configuration: {'✅ OK' if config_path.exists() else '⚠️  DEFAULT'}")

        # Check service status
        services = self._get_service_status()
        active_count = sum(1 for s in services.values() if s["enabled"])
        print(f"  • Active Services: ✅ {active_count}/8")

        print(
            f"\n  Overall Status: {'✅ HEALTHY' if active_count > 0 else '⚠️  DEGRADED'}"
        )
        print()

    async def cmd_dev(self, args: list) -> None:
        """Dev Mode controls (on/off/status/clear)."""
        if not args:
            print("\nUsage: dev on|off|status|clear\n")
            return
        action = args[0].lower()
        dev_mode = get_dev_mode_service()
        if action == "on":
            result = dev_mode.activate()
            print(f"\n{result.get('message','Dev mode activated')}")
            if result.get("status") == "activated":
                # Check Ollama availability
                try:
                    import requests
                    requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
                    print("✅ Ollama is reachable")
                except Exception:
                    print("⚠️  Ollama not reachable. Install/start with: brew install ollama && ollama serve")
                    print("    Optional: run bin/setup_wizard.sh --auto --no-browser")

                print("\n🔍 Suggested next steps (Vibe/Ollama):")
                suggestion = dev_mode.suggest_next_steps()
                if "Failed" in suggestion:
                    client = MistralAPI()
                    if client.available():
                        suggestion = client.chat(
                            "Suggest next development steps for uDOS based on context."
                        )
                print(suggestion)
            print()
        elif action == "off":
            result = dev_mode.deactivate()
            print(f"\n{result.get('message','Dev mode deactivated')}\n")
        elif action == "status":
            result = dev_mode.get_status()
            print("\nDEV MODE STATUS:")
            print(f"  active: {result.get('active')}")
            print(f"  endpoint: {result.get('goblin_endpoint')}")
            print(f"  uptime: {result.get('uptime_seconds')}s")
            print()
        elif action == "clear":
            result = dev_mode.clear()
            print("\nDEV MODE CLEAR:")
            print(json.dumps(result, indent=2))
            print()
        else:
            print("\nUsage: dev on|off|status|clear\n")

    async def cmd_ai(self, args: list) -> None:
        """AI commands: vibe|mistral|ollama|context."""
        dev_mode = get_dev_mode_service()
        if not dev_mode.active:
            print("\n⚠️  DEV MODE is inactive. Use: dev on\n")
            return
        if not args:
            print("\nUsage: ai vibe|mistral|mistral2|ollama|context\n")
            return
        action = args[0].lower()
        if action == "context":
            write_context_bundle()
            print("\n✅ AI context bundle refreshed (memory/ai/context.*)\n")
            return
        if action == "vibe":
            if len(args) < 2:
                print("\nUsage: ai vibe <prompt>\n")
                return
            prompt = " ".join(args[1:])
            vibe = VibeService()
            context = vibe.load_default_context()
            result = vibe.generate(prompt=prompt, system=context)
            print(f"\n{result}\n")
            return
        if action in ("mistral", "mistral2"):
            if len(args) < 2:
                print("\nUsage: ai mistral|mistral2 <prompt>\n")
                return
            prompt = " ".join(args[1:])
            client = MistralAPI()
            if not client.available():
                print("\n⚠️  MISTRAL_API_KEY not configured\n")
                return
            result = client.chat(prompt=prompt)
            print(f"\n{result}\n")
            return
        if action == "ollama":
            if len(args) < 2:
                print("\nUsage: ai ollama status|pull <model>\n")
                return
            sub = args[1].lower()
            if sub == "status":
                try:
                    import requests
                    resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
                    print("\nOllama status:")
                    print(resp.json())
                    print()
                except Exception as exc:
                    print(f"\n⚠️  Ollama not reachable: {exc}\n")
            elif sub == "pull":
                model = args[2] if len(args) > 2 else "devstral-small-2"
                cmd = ["ollama", "pull", model]
                if not shutil.which("ollama"):
                    print("\n⚠️  Ollama CLI not installed. Run: brew install ollama\n")
                    return
                subprocess.run(cmd, check=False)
            else:
                print("\nUsage: ai ollama status|pull <model>\n")
            return

    async def cmd_git(self, args: list) -> None:
        """Git shortcuts: status|pull|push|log."""
        dev_mode = get_dev_mode_service()
        if not dev_mode.active:
            print("\n⚠️  DEV MODE is inactive. Use: dev on\n")
            return
        if not args:
            print("\nUsage: git status|pull|push|log\n")
            return
        action = args[0].lower()
        if action == "status":
            subprocess.run(["git", "status", "-sb"], cwd=self.repo_root, check=False)
        elif action == "pull":
            subprocess.run(["git", "pull"], cwd=self.repo_root, check=False)
        elif action == "push":
            subprocess.run(["git", "push"], cwd=self.repo_root, check=False)
        elif action == "log":
            subprocess.run(["git", "log", "--oneline", "-5"], cwd=self.repo_root, check=False)
        else:
            print("\nUsage: git status|pull|push|log\n")

    async def cmd_logs(self, args: list) -> None:
        """Tail logs from memory/logs."""
        log_type = args[0] if args else "debug"
        lines = int(args[1]) if len(args) > 1 else 50
        log_dir = self.repo_root / "memory" / "logs"
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = log_dir / f"{log_type}-{today}.log"
        if not log_path.exists():
            print(f"\nNo log found: {log_path}\n")
            return
        try:
            result = subprocess.run(
                ["tail", "-n", str(lines), str(log_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"\n{result.stdout}\n")
        except Exception as exc:
            print(f"\nFailed to read log: {exc}\n")

    async def cmd_peek(self, args: list) -> None:
        """Convert URL to Markdown and save to outbox.

        Usage: peek <url> [filename]

        Examples:
            peek https://example.com
            peek https://github.com/fredporter/uDOS my-readme
        """
        if not args:
            print("\n❌ PEEK requires a URL")
            print("   Usage: peek <url> [optional-filename]\n")
            return

        url = args[0]
        filename = args[1] if len(args) > 1 else None

        service = get_url_to_markdown_service()

        print(f"\n⏳ Converting {url}...")
        success, output_path, message = await service.convert(url, filename)

        if success:
            print(f"   {message}")
            print(f"   📄 File: {output_path.relative_to(self.repo_root)}")
        else:
            print(f"   ❌ {message}")

        print()

    async def cmd_extract(self, args: list) -> None:
        """Extract PDF to Markdown and save to outbox.

        Usage: extract [pdf-filename]
               extract                    (bulk process inbox)

        Examples:
            extract invoice.pdf
            extract /path/to/document.pdf
            extract                      (process all PDFs in inbox)
        """
        service = get_pdf_ocr_service()

        if args:
            # Single file extraction
            pdf_path = args[0]
            print(f"\n⏳ Extracting {pdf_path}...")
            success, output_path, message = await service.extract(pdf_path)

            if success:
                print(f"   {message}")
                print(f"   📄 File: {output_path.relative_to(self.repo_root)}")
            else:
                print(f"   ❌ {message}")
        else:
            # Bulk extraction from inbox
            print("\n⏳ Processing PDFs from inbox...")
            success, results, message = await service.extract_batch()

            if success:
                print(f"   {message}")
                if results:
                    for result in results:
                        print(f"   ✅ {result['filename']}")
                        print(f"      📄 {result['output_path']}")
                        print(f"      🖼️  {result['images']} images, {result['pages']} pages")
                else:
                    print("   (no PDFs found in inbox)")
            else:
                print(f"   ❌ {message}")

        print()

    async def cmd_workflow(self, args: list) -> None:
        """Workflow manager commands."""
        manager = WorkflowManager()
        if not args or args[0] == "list":
            projects = manager.list_projects()
            print("\nProjects:")
            for proj in projects:
                print(f"  [{proj['id']}] {proj['name']} ({proj['status']})")
            print()
            return
        if args[0] == "export":
            md = manager.export_to_markdown()
            print(f"\n{md}\n")
            return
        if args[0] == "add" and len(args) >= 3:
            project_id = int(args[1])
            title = " ".join(args[2:])
            manager.create_task(project_id=project_id, title=title)
            print("\n✅ Task added\n")
            return
        print("\nUsage: workflow list|export|add <project_id> <title>\n")

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

    async def cmd_reboot(self, args: list) -> None:
        """Hot-reload the console state (config + dashboard checks)."""
        print("\n🔁 HOT RELOAD REQUESTED - refreshing configuration + console")
        await self.cmd_reload([])
        self._startup_checks()
        self.print_banner()
        print("✅ Hot reload complete. Console state reset.\n")

    async def cmd_github(self, args: list) -> None:
        """Show GitHub Actions status and recent runs."""
        print("\n📊 GITHUB ACTIONS STATUS:")

        try:
            from wizard.services.github_monitor import get_github_monitor

            monitor = get_github_monitor()

            # Get recent runs
            runs = await monitor.get_recent_runs(limit=5)

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
                    print(
                        f"    {emoji} {run.name:<30} {run.head_branch:<15} {run.conclusion or run.status}"
                    )

            # Show failure patterns
            if monitor.failure_patterns:
                print(f"\n  Failure Patterns:")
                for pattern, count in sorted(
                    monitor.failure_patterns.items(), key=lambda x: x[1], reverse=True
                ):
                    print(f"    • {pattern}: {count}x")

            print(
                f"\n  Webhook URL: http://{self.config.host}:{self.config.port}/api/github/webhook"
            )
            print("  Configure at: https://github.com/[owner]/[repo]/settings/hooks")
        except Exception as e:
            print(f"  ⚠️  GitHub Monitor unavailable: {e}")
        print()

    async def cmd_workflows(self, args: list) -> None:
        """Alias for github command."""
        await self.cmd_github(args)

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
        print("  dev        - DEV MODE on/off/status/clear")
        print("  ai         - Vibe/Ollama/Mistral helpers")
        print("  git        - Git shortcuts (status/pull/push/log)")
        print("  workflow   - Workflow/todo helper")
        print("  logs       - Tail logs from memory/logs")
        print("  tree       - Generate structure.txt snapshots (2 levels)")
        print("  peek       - Convert URL to Markdown (peek <url> [filename])")
        print("  extract    - Extract PDF to Markdown (extract [file.pdf] or extract for bulk)")
        print("  new/edit/load/save - Open files in editor (/memory)")
        print("  backup     - Create .backup snapshot (workspace default)")
        print("  restore    - Restore latest backup (use --force to overwrite)")
        print("  tidy       - Move junk into .archive")
        print("  clean      - Reset scope into .archive")
        print("  compost    - Move .archive/.backup/.tmp to /.compost")
        print("  destroy    - Dev TUI only (reinstall)")
        print("  providers  - List provider status (Ollama, OpenRouter, etc.)")
        print("  provider   - Provider actions: status|flag|unflag|setup <id>")
        print("  help       - Show this help message")
        print("  exit/quit  - Shutdown server gracefully")
        print()

    async def cmd_tree(self, _args: list) -> None:
        """Generate structure.txt files for root, memory, knowledge, and submodules."""
        try:
            result = self.tree_service.generate_all_structure_files()
        except Exception as exc:  # pragma: no cover - defensive
            print(f"\n❌ Failed to generate trees: {exc}\n")
            return

        summary = result.get("results", {})
        submodules = summary.get("submodules", {}) if isinstance(summary.get("submodules"), dict) else {}

        print("\n📁 DIRECTORY TREES (2 levels deep):\n")
        print(f"  Root:      {summary.get('root', '❌ Not updated')}")
        print(f"  Memory:    {summary.get('memory', '❌ Not updated')}")
        print(f"  Knowledge: {summary.get('knowledge', '❌ Not updated')}")

        if submodules:
            print("\n  Submodules:")
            for rel_path, status in submodules.items():
                print(f"    • {rel_path}: {status}")

        root_tree = result.get("root_tree", "")
        if root_tree:
            print("\n" + root_tree + "\n")

    async def cmd_new(self, args: list) -> None:
        """Create a new markdown file in /memory."""
        name = " ".join(args).strip() if args else "untitled"
        await self._open_editor(name)

    async def cmd_edit(self, args: list) -> None:
        """Edit a file in /memory."""
        target = " ".join(args).strip() if args else ""
        if not target and self._current_file:
            target = str(self._current_file)
        if not target:
            print("EDIT requires a filename")
            return
        await self._open_editor(target)

    async def cmd_load(self, args: list) -> None:
        """Load a file in /memory (opens editor)."""
        await self.cmd_edit(args)

    async def cmd_save(self, args: list) -> None:
        """Save a file in /memory (opens editor)."""
        await self.cmd_edit(args)

    async def cmd_backup(self, args: list) -> None:
        scope, remaining = self._parse_scope(args)
        label = "backup" if not remaining else " ".join(remaining)
        target_root, _recursive = self._resolve_scope(scope)
        archive_path, manifest_path = create_backup(target_root, label)
        print(
            "\n".join(
                [
                    "\n=== BACKUP ===",
                    f"Scope: {scope}",
                    f"Target: {target_root}",
                    f"Archive: {archive_path}",
                    f"Manifest: {manifest_path}\n",
                ]
            )
        )

    async def cmd_restore(self, args: list) -> None:
        scope, remaining = self._parse_scope(args)
        target_root, _recursive = self._resolve_scope(scope)
        force = False
        if "--force" in remaining:
            force = True
            remaining = [p for p in remaining if p != "--force"]

        archive = None
        if remaining:
            candidate = Path(remaining[0])
            if candidate.exists():
                archive = candidate
        if archive is None:
            backups = list_backups(target_root)
            if not backups:
                print(f"No backups found in {target_root / '.backup'}")
                return
            archive = backups[0]

        try:
            message = restore_backup(archive, target_root, force=force)
        except FileExistsError as exc:
            print(f"{exc}\nUse RESTORE --force to overwrite existing files.")
            return

        print(
            "\n".join(
                [
                    "\n=== RESTORE ===",
                    message,
                    f"Scope: {scope}",
                    f"Archive: {archive}",
                    f"Target: {target_root}\n",
                ]
            )
        )

    async def cmd_tidy(self, args: list) -> None:
        scope, _remaining = self._parse_scope(args)
        target_root, recursive = self._resolve_scope(scope)
        moved, archive_root = tidy(target_root, recursive=recursive)
        print(
            "\n".join(
                [
                    "\n=== TIDY ===",
                    f"Scope: {scope}",
                    f"Target: {target_root}",
                    f"Moved: {moved}",
                    f"Archive: {archive_root}\n",
                ]
            )
        )

    async def cmd_clean(self, args: list) -> None:
        scope, _remaining = self._parse_scope(args)
        target_root, recursive = self._resolve_scope(scope)
        if target_root == get_repo_root():
            allowlist = default_repo_allowlist()
        elif target_root == get_memory_root():
            allowlist = default_memory_allowlist()
        else:
            allowlist = []
        moved, archive_root = clean(
            target_root,
            allowed_entries=allowlist,
            recursive=recursive,
        )
        print(
            "\n".join(
                [
                    "\n=== CLEAN ===",
                    f"Scope: {scope}",
                    f"Target: {target_root}",
                    f"Moved: {moved}",
                    f"Archive: {archive_root}\n",
                ]
            )
        )

    async def cmd_compost(self, args: list) -> None:
        scope, _remaining = self._parse_scope(args)
        target_root, recursive = self._resolve_scope(scope)
        moved, compost_root = compost(target_root, recursive=recursive)
        print(
            "\n".join(
                [
                    "\n=== COMPOST ===",
                    f"Scope: {scope}",
                    f"Target: {target_root}",
                    f"Moved: {moved}",
                    f"Compost: {compost_root}\n",
                ]
            )
        )

    async def cmd_destroy(self, _args: list) -> None:
        print("DESTROY is only available from the Dev TUI.")

    async def _open_editor(self, target: str) -> None:
        try:
            path = resolve_workspace_path(target)
        except Exception as exc:
            print(f"Error: {exc}")
            return

        ok, editor_name = open_in_editor(path)
        if not ok:
            print(f"Error: {editor_name}")
            return

        self._current_file = path
        print(f"Opened {path} in {editor_name}")

    def _api_request(self, method: str, path: str, data: Optional[dict] = None):
        """Call Wizard API from the console."""
        base_host = "localhost" if self.config.host == "0.0.0.0" else self.config.host
        url = f"http://{base_host}:{self.config.port}{path}"
        headers = {"Content-Type": "application/json"}

        request_data = None
        if data is not None:
            request_data = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(
            url, data=request_data, headers=headers, method=method.upper()
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}

    async def cmd_providers(self, args: list) -> None:
        """List providers and their status."""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None, lambda: self._api_request("GET", "/api/providers/list")
            )
        except Exception as e:
            print(f"\n❌ Provider list failed: {e}\n")
            return

        providers = result.get("providers", [])
        if not providers:
            print("\n⚠️  No providers found\n")
            return

        print("\n🤖 PROVIDERS:")
        for p in providers:
            status = p.get("status", {})
            configured = "✅" if status.get("configured") else "⚠️"
            available = "✅" if status.get("available") else "❌"
            print(
                f"  {p['id']:<10} {p['name']:<18} configured {configured}  available {available}  type {p.get('type','')}"
            )
        print()

    async def cmd_provider(self, args: list) -> None:
        """Provider actions: status|flag|unflag|setup <id>."""
        if not args or len(args) < 2:
            print("\nUsage: provider status|flag|unflag|setup <provider_id>\n")
            return

        action, provider_id = args[0].lower(), args[1]
        loop = asyncio.get_event_loop()

        try:
            if action == "status":
                result = await loop.run_in_executor(
                    None,
                    lambda: self._api_request(
                        "GET", f"/api/providers/{provider_id}/status"
                    ),
                )
                status = result.get("status", {})
                print(
                    f"\n{result.get('name','')} ({provider_id})\n  configured: {status.get('configured')}\n  available:  {status.get('available')}\n  cli_installed: {status.get('cli_installed')}\n  needs_restart: {status.get('needs_restart')}\n"
                )

            elif action == "flag":
                result = await loop.run_in_executor(
                    None,
                    lambda: self._api_request(
                        "POST", f"/api/providers/{provider_id}/flag"
                    ),
                )
                print(f"\n{result.get('message','Flagged')}\n")

            elif action == "unflag":
                result = await loop.run_in_executor(
                    None,
                    lambda: self._api_request(
                        "POST", f"/api/providers/{provider_id}/unflag"
                    ),
                )
                print(f"\n{result.get('message','Unflagged')}\n")

            elif action == "setup":
                # POST with query param
                query = urllib.parse.urlencode({"provider_id": provider_id})
                path = f"/api/providers/setup/run?{query}"
                result = await loop.run_in_executor(
                    None, lambda: self._api_request("POST", path)
                )
                if not result.get("success"):
                    print(f"\n⚠️  {result.get('message','Setup not available')}\n")
                    return

                commands = result.get("commands", [])
                if not commands:
                    print(f"\n⚠️  No automation available for {provider_id}\n")
                    return

                print(f"\n{provider_id} setup running...")
                for cmd in commands:
                    raw_cmd = cmd.get("cmd", "")
                    if not raw_cmd:
                        continue

                    cmd_str = raw_cmd

                    # Apply simple platform-aware substitutions
                    if provider_id == "github":
                        if (
                            "brew install gh" in raw_cmd
                            and shutil.which("brew") is None
                        ):
                            if shutil.which("apt-get"):
                                cmd_str = (
                                    "sudo apt-get update && sudo apt-get install -y gh"
                                )
                            else:
                                print(
                                    "  • install: gh CLI required (install via package manager)"
                                )
                                continue
                        if (
                            raw_cmd.startswith("gh ") or " gh " in raw_cmd
                        ) and shutil.which("gh") is None:
                            print("  • setup: gh CLI missing (install gh first)")
                            continue

                    # Handle repo-local setup script for ollama
                    if "setup_wizard.sh" in raw_cmd:
                        script_path = self.repo_root / "bin" / "setup_wizard.sh"
                        if script_path.exists():
                            cmd_str = f"bash {script_path} --auto --no-browser"
                        else:
                            print("  • setup: setup_wizard.sh not found")
                            continue

                    print(f"  • {cmd.get('type','cmd')}: {cmd_str}")
                    try:
                        completed = await loop.run_in_executor(
                            None,
                            lambda: subprocess.run(
                                cmd_str,
                                shell=True,
                                cwd=self.repo_root,
                                check=False,
                            ),
                        )
                        if completed.returncode != 0:
                            print(f"    ⚠️  exited {completed.returncode}")
                        else:
                            print("    ✅ done")
                    except Exception as run_err:
                        print(f"    ❌ {run_err}")
                print()

            else:
                print("\nUsage: provider status|flag|unflag|setup <provider_id>\n")
        except urllib.error.HTTPError as e:
            print(
                f"\n❌ Provider API error: {e.read().decode('utf-8') if e.fp else e}\n"
            )
        except Exception as e:
            print(f"\n❌ Provider command failed: {e}\n")

    async def cmd_exit(self, args: list) -> None:
        """Shutdown server."""
        print("\n🛑 Shutting down Wizard Server...")
        self.running = False

    def _get_uptime(self) -> str:
        """Get server uptime."""
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    async def run(self):
        """Run interactive console loop."""
        self.running = True
        self._startup_checks()
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
