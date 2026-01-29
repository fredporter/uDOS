"""
uCODE - Unified Terminal TUI
=============================

The pivotal single-entry-point Terminal TUI for uDOS.

Features:
- Auto-detects available components (core, wizard, extensions)
- Graceful fallback to core-only mode if components are missing
- Integrated Wizard server control (start/stop/status)
- Extension/plugin packaging, installation, and distribution
- Core command dispatch with context-aware pages
- Dynamic capability loading based on available folders

Architecture:
  1. On startup, detect available components
  2. Build capability registry dynamically
  3. Expose only commands/pages for what's present
  4. If wizard exists, allow server control + Wizard pages
  5. If extensions exist, allow plugin management
  6. Fallback gracefully to core-only mode

Commands:
  STATUS          - System status and component detection
  HELP            - Show available commands
  WIZARD [cmd]    - Wizard server control (if available)
  PLUGIN [cmd]    - Extension/plugin management (if available)
  EXT [cmd]       - Extension management (alias for PLUGIN)
  + Core commands (routed to dispatcher)

Version: v1.0.0 (uCODE Unified)
Status: Production
Date: 2026-01-28
"""

import sys
import os
import json
import logging
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.tui.dispatcher import CommandDispatcher
from core.tui.renderer import GridRenderer
from core.tui.state import GameState
from core.input import SmartPrompt
from core.services.logging_manager import get_logger


def get_repo_root() -> Path:
    """Get uDOS repository root."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "core" / "tui").exists() and (current / "wizard").exists():
            return current
        current = current.parent
    # Fallback: current working directory
    return Path.cwd()


class ComponentState(Enum):
    """Component availability state."""
    AVAILABLE = "available"
    MISSING = "missing"
    ERROR = "error"


@dataclass
class Component:
    """Component registration."""
    name: str
    path: Path
    state: ComponentState
    version: Optional[str] = None
    description: str = ""


class ComponentDetector:
    """Detect and validate available components."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.logger = get_logger("ucode-detector")
        self.components: Dict[str, Component] = {}

    def detect_all(self) -> Dict[str, Component]:
        """Detect all available components."""
        self.components = {
            "core": self._detect_core(),
            "wizard": self._detect_wizard(),
            "extensions": self._detect_extensions(),
            "app": self._detect_app(),
        }
        return self.components

    def _detect_core(self) -> Component:
        """Detect core component."""
        path = self.repo_root / "core"
        if path.exists() and (path / "__init__.py").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="core",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Core TUI runtime"
            )
        return Component(
            name="core",
            path=path,
            state=ComponentState.MISSING,
            description="Core TUI runtime (missing)"
        )

    def _detect_wizard(self) -> Component:
        """Detect Wizard server component."""
        path = self.repo_root / "wizard"
        if path.exists() and (path / "server.py").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="wizard",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Wizard server & services"
            )
        return Component(
            name="wizard",
            path=path,
            state=ComponentState.MISSING,
            description="Wizard server (not installed)"
        )

    def _detect_extensions(self) -> Component:
        """Detect extensions component."""
        path = self.repo_root / "extensions"
        # Extensions folder exists and has subdirectories like api, transport
        if path.exists() and ((path / "api").exists() or (path / "transport").exists()):
            version = self._get_version(path / "version.json")
            return Component(
                name="extensions",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Extensible plugin system"
            )
        return Component(
            name="extensions",
            path=path,
            state=ComponentState.MISSING,
            description="Extensions system (not installed)"
        )

    def _detect_app(self) -> Component:
        """Detect app component."""
        path = self.repo_root / "app"
        if path.exists() and (path / "package.json").exists():
            version = self._get_version(path / "version.json")
            return Component(
                name="app",
                path=path,
                state=ComponentState.AVAILABLE,
                version=version,
                description="Desktop GUI application"
            )
        return Component(
            name="app",
            path=path,
            state=ComponentState.MISSING,
            description="Desktop app (not installed)"
        )

    def _get_version(self, version_file: Path) -> Optional[str]:
        """Read version from component's version.json."""
        try:
            if version_file.exists():
                with open(version_file) as f:
                    data = json.load(f)
                    return data.get("display") or data.get("version")
        except Exception as e:
            self.logger.debug(f"Failed to read version from {version_file}: {e}")
        return None

    def is_available(self, component_name: str) -> bool:
        """Check if component is available."""
        comp = self.components.get(component_name)
        return comp and comp.state == ComponentState.AVAILABLE


class uCODETUI:
    """Unified Terminal TUI for uDOS."""

    def __init__(self):
        """Initialize uCODE TUI."""
        self.repo_root = get_repo_root()
        self.logger = get_logger("ucode-tui")
        self.running = False

        # Component detection
        self.detector = ComponentDetector(self.repo_root)
        self.components = self.detector.detect_all()

        # Core components (always available)
        self.dispatcher = CommandDispatcher()
        self.renderer = GridRenderer()
        self.state = GameState()
        self.prompt = SmartPrompt()

        # Command registry
        self.commands: Dict[str, Callable] = {
            "STATUS": self._cmd_status,
            "HELP": self._cmd_help,
            "EXIT": self._cmd_exit,
            "QUIT": self._cmd_exit,
        }

        # Conditional commands
        if self.detector.is_available("wizard"):
            self.commands["WIZARD"] = self._cmd_wizard
            self.commands["WIZ"] = self._cmd_wizard

        if self.detector.is_available("extensions"):
            self.commands["PLUGIN"] = self._cmd_plugin
            self.commands["EXT"] = self._cmd_plugin
            self.commands["EXTENSION"] = self._cmd_plugin

        if self.prompt.use_fallback:
            self.logger.info(f"[SmartPrompt] Using fallback mode: {self.prompt.fallback_reason}")
        else:
            self.logger.info("[SmartPrompt] Initialized with prompt_toolkit")

    def run(self) -> None:
        """Start uCODE TUI."""
        self.running = True
        self._show_banner()
        self._show_component_status()

        try:
            while self.running:
                try:
                    plain_prompt = "[uCODE] > "
                    
                    # Ensure terminal is in good state before asking for input
                    sys.stdout.flush()
                    sys.stderr.flush()
                    
                    user_input = self.prompt.ask(plain_prompt)

                    if not user_input:
                        continue

                    # Parse command
                    parts = user_input.split(None, 1)
                    cmd = parts[0].upper()
                    args = parts[1] if len(parts) > 1 else ""

                    # Check for uCODE commands
                    if cmd in self.commands:
                        self.commands[cmd](args)
                        continue

                    # Route to core dispatcher (fallback)
                    result = self.dispatcher.dispatch(user_input)
                    self.state.update_from_handler(result)
                    self.logger.info(f"[COMMAND] {user_input} -> {result.get('status')}")
                    self.state.add_to_history(user_input)

                    output = self.renderer.render(result)
                    print(output)

                except KeyboardInterrupt:
                    print()
                    continue
                except Exception as e:
                    self.logger.error(f"[ERROR] {e}", exc_info=True)
                    print(f"ERROR: {e}")

        except KeyboardInterrupt:
            print("\nInterrupt. Type EXIT to quit.")
        except EOFError:
            self.running = False
        finally:
            self._cleanup()

    def _show_banner(self) -> None:
        """Show startup banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                        uCODE v1.0.1                           ║
║                 Unified Terminal TUI for uDOS                 ║
║                    Type HELP for commands                     ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(banner)

    def _show_component_status(self) -> None:
        """Show detected components."""
        print("\n📦 Component Detection:\n")
        for comp_name, comp in self.components.items():
            status = "✅" if comp.state == ComponentState.AVAILABLE else "❌"
            version_str = f" ({comp.version})" if comp.version else ""
            print(f"  {status} {comp.name.upper():12} {comp.description}{version_str}")
        print()

    def _cmd_status(self, args: str) -> None:
        """Show system status."""
        print("\n═══ uCODE STATUS ═══\n")
        self._show_component_status()

        if self.detector.is_available("wizard"):
            print("🧙 Wizard Server control available: Use WIZARD [start|stop|status]")
        if self.detector.is_available("extensions"):
            print("🔌 Extension management available: Use PLUGIN [list|install|remove]")
        print()

    def _cmd_help(self, args: str) -> None:
        """Show help."""
        help_text = """
═══ uCODE HELP ═══

Core Commands:
  STATUS              - Show system status
  HELP                - This help message
  EXIT, QUIT          - Exit uCODE

System Management:
  SETUP               - View your setup profile from Wizard Server
  CONFIG              - Manage configuration variables
  DESTROY             - System cleanup (wipe user, compost, reset)
  SHAKEDOWN           - Validate system health
  REPAIR              - Fix issues and self-heal
  RESTART             - Restart/reload system
  USER                - User profile and permission management
  LOGS                - View unified system logs

Data & Stories:
  BINDER              - Multi-chapter project management
  STORY [name]        - Run story files (.md with questions/flow)
  RUN [file]          - Execute uPy scripts or USCRIPT files
  DATASET             - Manage data imports and datasets

Navigation & Info:
  MAP                 - Show spatial map
  GOTO [location]     - Travel to location
  FIND [query]        - Search for locations
  TELL [query]        - Get information
  BAG                 - Inventory management

"""
        if self.detector.is_available("wizard"):
            help_text += """Wizard Server:
  WIZARD start        - Start Wizard server
  WIZARD stop         - Stop Wizard server
  WIZARD status       - Check Wizard status
  WIZARD console      - Enter Wizard interactive console
  WIZARD [page]       - Show Wizard page (status, ai, devices, quota, logs)

"""
        if self.detector.is_available("extensions"):
            help_text += """Extensions:
  PLUGIN list         - List installed plugins
  PLUGIN install      - Install new plugin
  PLUGIN remove       - Remove plugin
  PLUGIN pack         - Package plugin for distribution
  EXT [cmd]           - Alias for PLUGIN

"""
        help_text += """
Examples:
  SETUP                      - View your setup profile
  STORY wizard-setup         - Run setup story
  DESTROY --wipe-user        - Wipe user data
  WIZARD start               - Start Wizard Server
  BINDER open my-project     - Open a project
  MAP                        - Show spatial map

For detailed help on any command, type the command name followed by --help
(e.g., CONFIG --help, DESTROY --help)

"""
        print(help_text)

    def _cmd_wizard(self, args: str) -> None:
        """Wizard server control."""
        if not self.detector.is_available("wizard"):
            print("❌ Wizard component not available.")
            return

        parts = args.split(None, 1)
        action = parts[0].lower() if parts else "status"
        subargs = parts[1] if len(parts) > 1 else ""

        if action == "start":
            print("\n🧙 Starting Wizard Server...")
            self._wizard_start()
        elif action == "stop":
            print("\n🧙 Stopping Wizard Server...")
            self._wizard_stop()
        elif action == "status":
            print("\n🧙 Wizard Server Status:")
            self._wizard_status()
        elif action == "console":
            print("\n🧙 Entering Wizard interactive console...")
            self._wizard_console()
        elif action in ("pages", "help"):
            print("\nWizard pages: status, ai, services, quota, devices, logs, config")
        else:
            print(f"\n🧙 Wizard [{action}]:")
            self._wizard_page(action)

    def _wizard_start(self) -> None:
        """Start Wizard server."""
        try:
            # Check if already running
            try:
                resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                if resp.status_code == 200:
                    print("  ✅ Wizard already running")
                    return
            except requests.exceptions.ConnectionError:
                pass  # Not running, proceed

            print("  Starting Wizard Server...")
            venv_activate = self.repo_root / ".venv" / "bin" / "activate"
            
            # Build command
            if venv_activate.exists():
                cmd = f"source {venv_activate} && python wizard/server.py"
            else:
                cmd = "python wizard/server.py"

            # Start in background with proper I/O isolation
            try:
                with open(os.devnull, 'w') as devnull:
                    with open(os.devnull, 'r') as devnull_in:
                        proc = subprocess.Popen(
                            cmd,
                            shell=True,
                            cwd=str(self.repo_root),
                            stdin=devnull_in,
                            stdout=devnull,
                            stderr=devnull,
                            preexec_fn=os.setsid if sys.platform != 'win32' else None
                        )
            except Exception as start_err:
                raise Exception(f"Failed to spawn wizard process: {start_err}")
            
            # Wait for server to be ready
            max_wait = 10
            start = time.time()
            while time.time() - start < max_wait:
                try:
                    resp = requests.get("http://127.0.0.1:8765/health", timeout=1)
                    if resp.status_code == 200:
                        print(f"  ✅ Wizard Server started (PID: {proc.pid})")
                        sys.stdout.flush()  # Ensure output is flushed
                        return
                except requests.exceptions.ConnectionError:
                    time.sleep(0.5)

            print("  ⚠️  Wizard Server started but not responding (timeout)")
            sys.stdout.flush()

        except Exception as e:
            self.logger.error(f"Failed to start Wizard: {e}")
            print(f"  ❌ Error: {e}")
            sys.stdout.flush()

    def _wizard_stop(self) -> None:
        """Stop Wizard server."""
        try:
            # Kill all python processes running wizard/server.py
            if sys.platform == 'win32':
                cmd = "taskkill /F /IM python.exe"
            else:
                cmd = "pkill -f 'wizard/server.py' || pkill -f 'wizard.server' || true"
            
            subprocess.run(cmd, shell=True, timeout=5)
            print("  ✅ Wizard Server stopped")
            sys.stdout.flush()  # Ensure output is flushed
            time.sleep(0.5)

        except Exception as e:
            self.logger.error(f"Failed to stop Wizard: {e}")
            print(f"  ❌ Error: {e}")
            sys.stdout.flush()

    def _wizard_status(self) -> None:
        """Check Wizard status."""
        try:
            resp = requests.get("http://127.0.0.1:8765/health", timeout=2)
            if resp.status_code == 200:
                print("  ✅ Wizard running on http://127.0.0.1:8765")
                data = resp.json()
                if "status" in data:
                    print(f"     Status: {data['status']}")
            else:
                print("  ❌ Wizard not responding")
        except requests.exceptions.ConnectionError:
            print("  ❌ Wizard not running")
        except Exception as e:
            print(f"  ⚠️  Error checking status: {e}")

    def _wizard_console(self) -> None:
        """Enter Wizard interactive console."""
        try:
            print("  Launching Wizard interactive console...")
            venv_activate = self.repo_root / ".venv" / "bin" / "activate"
            
            if venv_activate.exists():
                cmd = f"source {venv_activate} && python wizard/wizard_tui.py"
            else:
                cmd = "python wizard/wizard_tui.py"

            subprocess.run(cmd, shell=True, cwd=str(self.repo_root))

        except Exception as e:
            self.logger.error(f"Failed to launch Wizard console: {e}")
            print(f"  ❌ Error: {e}")

    def _wizard_page(self, page: str) -> None:
        """Show Wizard page via API."""
        try:
            # Map page names to API endpoints
            page_map = {
                "status": "/health",
                "ai": "/api/v1/ai/status",
                "services": "/api/v1/status",
                "devices": "/api/v1/devices",
                "quota": "/api/v1/ai/quota",
                "logs": "/api/v1/logs",
            }

            endpoint = page_map.get(page.lower())
            if not endpoint:
                print(f"  ❌ Unknown page: {page}")
                print(f"     Available: {', '.join(page_map.keys())}")
                return

            resp = requests.get(f"http://127.0.0.1:8765{endpoint}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                print(json.dumps(data, indent=2))
            else:
                print(f"  ❌ Request failed: {resp.status_code}")

        except requests.exceptions.ConnectionError:
            print("  ❌ Wizard not running. Start with: WIZARD start")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _cmd_plugin(self, args: str) -> None:
        """Plugin/extension management."""
        if not self.detector.is_available("extensions"):
            print("❌ Extensions component not available.")
            return

        parts = args.split(None, 1)
        action = parts[0].lower() if parts else "list"
        subargs = parts[1] if len(parts) > 1 else ""

        if action == "list":
            print("\n🔌 Installed Plugins:\n")
            self._plugin_list()
        elif action == "install":
            print(f"\n🔌 Installing plugin: {subargs}")
            self._plugin_install(subargs)
        elif action == "remove":
            print(f"\n🔌 Removing plugin: {subargs}")
            self._plugin_remove(subargs)
        elif action == "pack":
            print(f"\n🔌 Packaging plugin: {subargs}")
            self._plugin_pack(subargs)
        elif action in ("help", "info"):
            print("\nPlugin commands: list, install <name>, remove <name>, pack <name>")
        else:
            print(f"\n🔌 Unknown plugin action: {action}")

    def _plugin_list(self) -> None:
        """List installed plugins."""
        try:
            ext_path = self.repo_root / "extensions"
            if not ext_path.exists():
                print("  ❌ Extensions folder not found")
                return

            # Scan for extensions
            extensions = []
            for item in ext_path.iterdir():
                if item.is_dir() and (item / "version.json").exists():
                    try:
                        with open(item / "version.json") as f:
                            data = json.load(f)
                            version = data.get("display") or data.get("version", "unknown")
                            extensions.append((item.name, version))
                    except Exception:
                        extensions.append((item.name, "error reading version"))

            if extensions:
                print("  Installed Extensions:")
                for name, version in sorted(extensions):
                    print(f"    ✅ {name:15} {version}")
            else:
                print("  No extensions installed")

        except Exception as e:
            print(f"  ❌ Error listing extensions: {e}")

    def _plugin_install(self, name: str) -> None:
        """Install a plugin."""
        try:
            print(f"  🔌 Installing plugin: {name}")
            print("  [TODO] Implement plugin install from registry")
            print("         Use PLUGIN list to see available plugins")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _plugin_remove(self, name: str) -> None:
        """Remove a plugin."""
        try:
            ext_path = self.repo_root / "extensions" / name
            if not ext_path.exists():
                print(f"  ❌ Plugin not found: {name}")
                return

            # Safety confirmation
            print(f"  ⚠️  Remove plugin: {name}?")
            response = input("  Type 'yes' to confirm: ").strip().lower()
            if response == 'yes':
                import shutil
                shutil.rmtree(ext_path)
                print(f"  ✅ Plugin removed: {name}")
            else:
                print("  Cancelled")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _plugin_pack(self, name: str) -> None:
        """Package a plugin for distribution."""
        try:
            ext_path = self.repo_root / "extensions" / name
            if not ext_path.exists():
                print(f"  ❌ Extension not found: {name}")
                return

            # Create distribution package
            dist_path = self.repo_root / "distribution" / "plugins" / name
            print(f"  📦 Packaging {name}...")
            
            # TODO: Real packaging logic (copy to distribution, create manifest, etc)
            print(f"  [TODO] Package {name} for distribution")
            print(f"         Output: {dist_path}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _cmd_exit(self, args: str) -> None:
        """Exit uCODE."""
        self.running = False
        print("\n👋 Goodbye!")

    def _cleanup(self) -> None:
        """Cleanup on exit."""
        self.logger.info("uCODE TUI shutting down")


def main():
    """Main entry point for uCODE."""
    tui = uCODETUI()
    tui.run()


if __name__ == "__main__":
    main()
