"""
uDOS v1.1.4.1 - Tauri Desktop App Test Suite

Tests cross-platform native desktop application built with Tauri framework.
Validates Rust backend bridge, Teletext GUI integration, OS features, and offline-first operation.

Test Coverage:
- Tauri Configuration (10 tests)
- Rust Backend Bridge (12 tests)
- Frontend Integration (8 tests)
- OS Native Features (10 tests)
- Auto-Update System (6 tests)
- Cross-Platform Compatibility (8 tests)
"""

import unittest
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# TAURI CONFIGURATION SYSTEM
# ============================================================================

class Platform(Enum):
    """Supported platforms"""
    MACOS = "macos"
    WINDOWS = "windows"
    LINUX = "linux"


@dataclass
class WindowConfig:
    """Tauri window configuration"""
    title: str = "uDOS - Offline Survival Handbook"
    width: int = 1200
    height: int = 800
    resizable: bool = True
    fullscreen: bool = False
    decorations: bool = True
    transparent: bool = False
    always_on_top: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "resizable": self.resizable,
            "fullscreen": self.fullscreen,
            "decorations": self.decorations,
            "transparent": self.transparent,
            "alwaysOnTop": self.always_on_top
        }


@dataclass
class SecurityConfig:
    """Tauri security configuration"""
    csp: str = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'"
    dangerous_allow_remote_urls: bool = False
    dangerous_disable_asset_csp_modification: bool = False
    freeze_prototype: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "csp": self.csp,
            "dangerousRemoteUrlIpcAccess": self.dangerous_allow_remote_urls,
            "dangerousDisableAssetCspModification": self.dangerous_disable_asset_csp_modification,
            "freezePrototype": self.freeze_prototype
        }


class TauriConfig:
    """Manages Tauri application configuration"""

    def __init__(self, app_name: str = "uDOS", version: str = "1.1.4"):
        self.app_name = app_name
        self.version = version
        self.identifier = "com.udos.app"
        self.window_config = WindowConfig()
        self.security_config = SecurityConfig()
        self.allowed_commands: List[str] = []
        self.file_associations: List[str] = [".uscript", ".md"]

    def add_command(self, command: str) -> None:
        """Add allowed Tauri command"""
        if command not in self.allowed_commands:
            self.allowed_commands.append(command)

    def generate_config(self) -> Dict[str, Any]:
        """Generate complete tauri.conf.json structure"""
        return {
            "package": {
                "productName": self.app_name,
                "version": self.version
            },
            "build": {
                "distDir": "../dist",
                "devPath": "http://localhost:5173",
                "beforeDevCommand": "npm run dev",
                "beforeBuildCommand": "npm run build"
            },
            "tauri": {
                "allowlist": {
                    "all": False,
                    "shell": {
                        "all": False,
                        "execute": True,
                        "sidecar": True,
                        "open": False
                    },
                    "fs": {
                        "all": False,
                        "readFile": True,
                        "writeFile": True,
                        "readDir": True,
                        "createDir": True,
                        "removeFile": True,
                        "exists": True,
                        "scope": ["$APPDATA/*", "$HOME/.udos/*"]
                    },
                    "protocol": {
                        "asset": True,
                        "assetScope": ["**"]
                    }
                },
                "bundle": {
                    "active": True,
                    "identifier": self.identifier,
                    "icon": [
                        "icons/32x32.png",
                        "icons/128x128.png",
                        "icons/icon.icns",
                        "icons/icon.ico"
                    ],
                    "resources": ["../memory/**/*", "../knowledge/**/*"],
                    "fileAssociations": [
                        {
                            "ext": ext.lstrip("."),
                            "name": f"uDOS {ext.upper()} File",
                            "role": "Editor"
                        }
                        for ext in self.file_associations
                    ],
                    "macOS": {
                        "minimumSystemVersion": "10.13"
                    },
                    "windows": {
                        "certificateThumbprint": None,
                        "digestAlgorithm": "sha256",
                        "timestampUrl": ""
                    }
                },
                "security": self.security_config.to_dict(),
                "windows": [self.window_config.to_dict()],
                "updater": {
                    "active": True,
                    "endpoints": ["https://releases.udos.app/{{target}}/{{current_version}}"],
                    "dialog": True,
                    "pubkey": "placeholder_public_key"
                }
            }
        }

    def validate(self) -> List[str]:
        """Validate configuration for common issues"""
        issues = []

        if not self.app_name:
            issues.append("App name is required")

        if not self.version:
            issues.append("Version is required")

        if self.security_config.dangerous_allow_remote_urls:
            issues.append("WARNING: Remote URL IPC access enabled (security risk)")

        if not self.security_config.csp:
            issues.append("CSP should be defined for security")

        if self.window_config.width < 800 or self.window_config.height < 600:
            issues.append("Window size may be too small for Teletext UI")

        return issues


# ============================================================================
# RUST BACKEND BRIDGE
# ============================================================================

@dataclass
class TauriCommand:
    """Represents a Tauri command callable from frontend"""
    name: str
    handler: str  # Rust function name
    allowed_roles: List[str] = field(default_factory=lambda: ["user", "power", "wizard", "root"])
    require_auth: bool = True

    def can_execute(self, user_role: str) -> bool:
        """Check if user role can execute this command"""
        return user_role in self.allowed_roles


class RustBridge:
    """Simulates Rust backend bridge for Python CLI integration"""

    def __init__(self):
        self.commands: Dict[str, TauriCommand] = {}
        self.active_processes: Dict[str, Dict[str, Any]] = {}
        self.ipc_log: List[Dict[str, Any]] = []

    def register_command(self, command: TauriCommand) -> None:
        """Register a Tauri command"""
        self.commands[command.name] = command

    def execute_cli_command(self, cmd: str, user_role: str = "user") -> Dict[str, Any]:
        """Execute uDOS CLI command through Rust bridge"""
        command_name = "execute_cli"

        if command_name not in self.commands:
            return {"success": False, "error": "Command not registered"}

        tauri_cmd = self.commands[command_name]
        if not tauri_cmd.can_execute(user_role):
            return {"success": False, "error": f"Insufficient permissions for role: {user_role}"}

        # Simulate command execution
        result = {
            "success": True,
            "command": cmd,
            "output": f"Executed: {cmd}",
            "exit_code": 0,
            "timestamp": datetime.now().isoformat()
        }

        self._log_ipc("execute_cli", {"cmd": cmd, "role": user_role}, result)
        return result

    def read_file(self, path: str, user_role: str = "user") -> Dict[str, Any]:
        """Read file through Rust FS API"""
        command_name = "read_file"

        if command_name not in self.commands:
            return {"success": False, "error": "Command not registered"}

        # Security check: ensure path is within allowed scope
        allowed_paths = ["/memory/", "/knowledge/", ".udos/"]
        if not any(allowed in path for allowed in allowed_paths):
            return {"success": False, "error": "Path outside allowed scope"}

        result = {
            "success": True,
            "path": path,
            "content": f"Mock file content from {path}",
            "size": 1024
        }

        self._log_ipc("read_file", {"path": path}, result)
        return result

    def write_file(self, path: str, content: str, user_role: str = "user") -> Dict[str, Any]:
        """Write file through Rust FS API"""
        command_name = "write_file"

        if command_name not in self.commands:
            return {"success": False, "error": "Command not registered"}

        tauri_cmd = self.commands[command_name]
        if not tauri_cmd.can_execute(user_role):
            return {"success": False, "error": "Insufficient permissions"}

        result = {
            "success": True,
            "path": path,
            "bytes_written": len(content)
        }

        self._log_ipc("write_file", {"path": path, "size": len(content)}, result)
        return result

    def spawn_process(self, executable: str, args: List[str]) -> str:
        """Spawn background process"""
        process_id = f"proc_{len(self.active_processes)}"
        self.active_processes[process_id] = {
            "executable": executable,
            "args": args,
            "started": datetime.now(),
            "status": "running"
        }
        return process_id

    def get_process_status(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get status of spawned process"""
        return self.active_processes.get(process_id)

    def _log_ipc(self, command: str, request: Dict, response: Dict) -> None:
        """Log IPC call for debugging"""
        self.ipc_log.append({
            "command": command,
            "request": request,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

    def get_ipc_stats(self) -> Dict[str, Any]:
        """Get IPC usage statistics"""
        return {
            "total_calls": len(self.ipc_log),
            "commands_registered": len(self.commands),
            "active_processes": len(self.active_processes),
            "call_breakdown": self._count_by_command()
        }

    def _count_by_command(self) -> Dict[str, int]:
        """Count IPC calls by command type"""
        counts = {}
        for log_entry in self.ipc_log:
            cmd = log_entry["command"]
            counts[cmd] = counts.get(cmd, 0) + 1
        return counts


# ============================================================================
# FRONTEND INTEGRATION
# ============================================================================

@dataclass
class TeletextAsset:
    """Represents a Teletext UI asset"""
    path: str
    asset_type: str  # "html", "css", "js", "font"
    size_bytes: int
    cached: bool = False


class FrontendIntegration:
    """Manages Teletext GUI integration in Tauri webview"""

    def __init__(self):
        self.assets: List[TeletextAsset] = []
        self.cached_assets: Dict[str, TeletextAsset] = {}
        self.webview_ready = False
        self.offline_mode = True

    def register_asset(self, path: str, asset_type: str, size_bytes: int) -> None:
        """Register Teletext UI asset"""
        asset = TeletextAsset(path, asset_type, size_bytes)
        self.assets.append(asset)

    def cache_asset(self, path: str) -> bool:
        """Cache asset for offline use"""
        asset = next((a for a in self.assets if a.path == path), None)
        if not asset:
            return False

        asset.cached = True
        self.cached_assets[path] = asset
        return True

    def get_asset_manifest(self) -> Dict[str, Any]:
        """Get manifest of all UI assets"""
        return {
            "total_assets": len(self.assets),
            "cached_assets": len(self.cached_assets),
            "total_size": sum(a.size_bytes for a in self.assets),
            "by_type": self._count_by_type(),
            "offline_ready": self.all_assets_cached()
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count assets by type"""
        counts = {}
        for asset in self.assets:
            counts[asset.asset_type] = counts.get(asset.asset_type, 0) + 1
        return counts

    def all_assets_cached(self) -> bool:
        """Check if all assets are cached for offline use"""
        return all(a.cached for a in self.assets)

    def initialize_webview(self) -> bool:
        """Initialize Tauri webview with Teletext UI"""
        if not self.all_assets_cached() and self.offline_mode:
            return False

        self.webview_ready = True
        return True

    def inject_api_bridge(self) -> Dict[str, str]:
        """Generate JavaScript bridge for Tauri API"""
        return {
            "executeCommand": "window.__TAURI__.invoke('execute_cli', { cmd })",
            "readFile": "window.__TAURI__.invoke('read_file', { path })",
            "writeFile": "window.__TAURI__.invoke('write_file', { path, content })",
            "showNotification": "window.__TAURI__.notification.sendNotification({ title, body })"
        }


# ============================================================================
# NATIVE OS FEATURES
# ============================================================================

@dataclass
class MenuItem:
    """Native menu item"""
    label: str
    action: str
    accelerator: Optional[str] = None  # Keyboard shortcut
    submenu: List['MenuItem'] = field(default_factory=list)
    enabled: bool = True


class SystemTrayManager:
    """Manages system tray icon and menu"""

    def __init__(self):
        self.icon_path = "icons/tray.png"
        self.menu_items: List[MenuItem] = []
        self.visible = True

    def add_menu_item(self, item: MenuItem) -> None:
        """Add item to tray menu"""
        self.menu_items.append(item)

    def set_tooltip(self, text: str) -> None:
        """Set tray icon tooltip"""
        self.tooltip = text

    def show_notification(self, title: str, body: str) -> None:
        """Show system notification"""
        # In real implementation, would use Tauri notification API
        pass


class NativeMenuManager:
    """Manages native application menus"""

    def __init__(self, platform: Platform):
        self.platform = platform
        self.menus: Dict[str, List[MenuItem]] = {}
        self._create_default_menus()

    def _create_default_menus(self) -> None:
        """Create platform-specific default menus"""
        # File menu
        self.menus["File"] = [
            MenuItem("New Mission", "new_mission", "Ctrl+N"),
            MenuItem("Open...", "open_file", "Ctrl+O"),
            MenuItem("Save", "save_file", "Ctrl+S"),
            MenuItem("Exit", "quit", "Ctrl+Q")
        ]

        # Edit menu
        self.menus["Edit"] = [
            MenuItem("Undo", "undo", "Ctrl+Z"),
            MenuItem("Redo", "redo", "Ctrl+Shift+Z"),
            MenuItem("Preferences", "preferences", "Ctrl+,")
        ]

        # View menu
        self.menus["View"] = [
            MenuItem("Toggle Fullscreen", "toggle_fullscreen", "F11"),
            MenuItem("Zoom In", "zoom_in", "Ctrl++"),
            MenuItem("Zoom Out", "zoom_out", "Ctrl+-"),
            MenuItem("Reset Zoom", "reset_zoom", "Ctrl+0")
        ]

        # Help menu
        self.menus["Help"] = [
            MenuItem("Documentation", "show_docs", "F1"),
            MenuItem("Check for Updates", "check_updates"),
            MenuItem("About uDOS", "show_about")
        ]

        # macOS-specific app menu
        if self.platform == Platform.MACOS:
            self.menus["uDOS"] = [
                MenuItem("About uDOS", "show_about"),
                MenuItem("Preferences", "preferences", "Cmd+,"),
                MenuItem("Hide uDOS", "hide", "Cmd+H"),
                MenuItem("Quit uDOS", "quit", "Cmd+Q")
            ]

    def get_menu_structure(self) -> Dict[str, List[MenuItem]]:
        """Get complete menu structure"""
        return self.menus

    def handle_menu_action(self, action: str) -> Dict[str, Any]:
        """Handle menu item action"""
        return {
            "action": action,
            "handled": True,
            "timestamp": datetime.now().isoformat()
        }


class FileAssociationManager:
    """Manages file type associations"""

    def __init__(self):
        self.associations: Dict[str, Dict[str, str]] = {}

    def register_extension(self, ext: str, name: str, icon: str) -> None:
        """Register file extension association"""
        self.associations[ext] = {
            "name": name,
            "icon": icon,
            "role": "Editor"
        }

    def can_open(self, file_path: str) -> bool:
        """Check if app can open file"""
        ext = os.path.splitext(file_path)[1]
        return ext in self.associations

    def get_registered_extensions(self) -> List[str]:
        """Get list of registered extensions"""
        return list(self.associations.keys())


# ============================================================================
# AUTO-UPDATE SYSTEM
# ============================================================================

@dataclass
class UpdateInfo:
    """Information about available update"""
    version: str
    release_date: datetime
    download_url: str
    signature: str
    size_bytes: int
    changelog: str
    critical: bool = False


class UpdateManager:
    """Manages application auto-updates"""

    def __init__(self, current_version: str):
        self.current_version = current_version
        self.update_endpoint = "https://releases.udos.app"
        self.public_key = "placeholder_public_key"
        self.auto_check = True
        self.download_progress = 0.0

    def check_for_updates(self, platform: Platform) -> Optional[UpdateInfo]:
        """Check if updates are available"""
        # Simulate update check
        # In real implementation, would query update endpoint
        latest_version = "1.1.5"

        if self._compare_versions(latest_version, self.current_version) > 0:
            return UpdateInfo(
                version=latest_version,
                release_date=datetime.now(),
                download_url=f"{self.update_endpoint}/{platform.value}/1.1.5",
                signature="mock_signature",
                size_bytes=52_428_800,  # 50 MB
                changelog="Bug fixes and performance improvements"
            )

        return None

    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare version strings (-1: v1<v2, 0: equal, 1: v1>v2)"""
        parts1 = [int(x) for x in v1.split('.')]
        parts2 = [int(x) for x in v2.split('.')]

        for p1, p2 in zip(parts1, parts2):
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1

        return 0

    def verify_signature(self, update: UpdateInfo) -> bool:
        """Verify update package signature"""
        # In real implementation, would verify cryptographic signature
        return update.signature == "mock_signature"

    def download_update(self, update: UpdateInfo) -> bool:
        """Download update package"""
        # Simulate download with progress
        self.download_progress = 0.0
        for i in range(10):
            self.download_progress = (i + 1) * 10.0

        return self.download_progress == 100.0

    def install_update(self) -> bool:
        """Install downloaded update"""
        # In real implementation, would trigger Tauri updater
        return True

    def get_update_status(self) -> Dict[str, Any]:
        """Get current update status"""
        return {
            "current_version": self.current_version,
            "auto_check_enabled": self.auto_check,
            "download_progress": self.download_progress
        }


# ============================================================================
# CROSS-PLATFORM COMPATIBILITY
# ============================================================================

class PlatformManager:
    """Manages platform-specific features and compatibility"""

    def __init__(self, platform: Platform):
        self.platform = platform
        self.features: Dict[str, bool] = {}
        self._detect_features()

    def _detect_features(self) -> None:
        """Detect platform-specific features"""
        # Common features
        self.features["notifications"] = True
        self.features["file_associations"] = True
        self.features["auto_updates"] = True

        # Platform-specific
        if self.platform == Platform.MACOS:
            self.features["touchbar"] = True
            self.features["app_menu"] = True
            self.features["dock_menu"] = True
        elif self.platform == Platform.WINDOWS:
            self.features["taskbar_integration"] = True
            self.features["jump_lists"] = True
        elif self.platform == Platform.LINUX:
            self.features["app_indicator"] = True
            self.features["desktop_file"] = True

    def is_feature_supported(self, feature: str) -> bool:
        """Check if feature is supported on current platform"""
        return self.features.get(feature, False)

    def get_data_directory(self) -> str:
        """Get platform-specific data directory"""
        if self.platform == Platform.MACOS:
            return "~/Library/Application Support/uDOS"
        elif self.platform == Platform.WINDOWS:
            return "%APPDATA%/uDOS"
        else:  # Linux
            return "~/.local/share/udos"

    def get_config_directory(self) -> str:
        """Get platform-specific config directory"""
        if self.platform == Platform.MACOS:
            return "~/Library/Preferences/uDOS"
        elif self.platform == Platform.WINDOWS:
            return "%APPDATA%/uDOS/config"
        else:  # Linux
            return "~/.config/udos"

    def get_shortcut_format(self, key: str) -> str:
        """Convert shortcut to platform-specific format"""
        if self.platform == Platform.MACOS:
            return key.replace("Ctrl", "Cmd")
        return key


# ============================================================================
# TEST SUITES
# ============================================================================

class TestTauriConfiguration(unittest.TestCase):
    """Test Tauri configuration generation and validation"""

    def setUp(self):
        self.config = TauriConfig()

    def test_default_config(self):
        """Test default configuration values"""
        self.assertEqual(self.config.app_name, "uDOS")
        self.assertEqual(self.config.version, "1.1.4")
        self.assertEqual(self.config.identifier, "com.udos.app")

    def test_window_config(self):
        """Test window configuration"""
        window = self.config.window_config
        self.assertEqual(window.title, "uDOS - Offline Survival Handbook")
        self.assertEqual(window.width, 1200)
        self.assertEqual(window.height, 800)
        self.assertTrue(window.resizable)

    def test_security_config(self):
        """Test security configuration"""
        security = self.config.security_config
        self.assertIn("default-src 'self'", security.csp)
        self.assertFalse(security.dangerous_allow_remote_urls)
        self.assertTrue(security.freeze_prototype)

    def test_add_commands(self):
        """Test adding allowed commands"""
        self.config.add_command("execute_cli")
        self.config.add_command("read_file")
        self.assertIn("execute_cli", self.config.allowed_commands)
        self.assertIn("read_file", self.config.allowed_commands)

    def test_file_associations(self):
        """Test file association configuration"""
        self.assertIn(".uscript", self.config.file_associations)
        self.assertIn(".md", self.config.file_associations)

    def test_generate_config_structure(self):
        """Test generated config has required structure"""
        config = self.config.generate_config()
        self.assertIn("package", config)
        self.assertIn("build", config)
        self.assertIn("tauri", config)
        self.assertIn("bundle", config["tauri"])
        self.assertIn("updater", config["tauri"])

    def test_bundle_resources(self):
        """Test bundle includes memory and knowledge"""
        config = self.config.generate_config()
        resources = config["tauri"]["bundle"]["resources"]
        self.assertTrue(any("memory" in r for r in resources))
        self.assertTrue(any("knowledge" in r for r in resources))

    def test_validation_success(self):
        """Test validation passes for valid config"""
        issues = self.config.validate()
        # Should only have warning about window size, no critical issues
        critical_issues = [i for i in issues if not i.startswith("WARNING")]
        self.assertEqual(len(critical_issues), 0)

    def test_validation_fails_no_name(self):
        """Test validation fails without app name"""
        self.config.app_name = ""
        issues = self.config.validate()
        self.assertTrue(any("name is required" in i for i in issues))

    def test_offline_first_config(self):
        """Test config supports offline-first operation"""
        config = self.config.generate_config()
        # Should not require network for basic operation
        allowlist = config["tauri"]["allowlist"]
        self.assertFalse(allowlist.get("all", True))  # Explicit permissions only


class TestRustBridge(unittest.TestCase):
    """Test Rust backend bridge functionality"""

    def setUp(self):
        self.bridge = RustBridge()
        self.bridge.register_command(TauriCommand("execute_cli", "execute_cli_handler"))
        self.bridge.register_command(TauriCommand("read_file", "read_file_handler"))
        self.bridge.register_command(TauriCommand("write_file", "write_file_handler", ["power", "wizard", "root"]))

    def test_register_command(self):
        """Test command registration"""
        cmd = TauriCommand("test_cmd", "test_handler")
        self.bridge.register_command(cmd)
        self.assertIn("test_cmd", self.bridge.commands)

    def test_execute_cli_command(self):
        """Test CLI command execution"""
        result = self.bridge.execute_cli_command("HELP", "user")
        self.assertTrue(result["success"])
        self.assertEqual(result["command"], "HELP")
        self.assertEqual(result["exit_code"], 0)

    def test_execute_unregistered_command(self):
        """Test executing unregistered command fails"""
        self.bridge.commands.clear()
        result = self.bridge.execute_cli_command("HELP", "user")
        self.assertFalse(result["success"])
        self.assertIn("not registered", result["error"])

    def test_rbac_enforcement(self):
        """Test RBAC enforcement in commands"""
        result = self.bridge.write_file("/memory/test.md", "content", "user")
        self.assertFalse(result["success"])
        self.assertIn("permissions", result["error"])

    def test_rbac_power_user(self):
        """Test power user can write files"""
        result = self.bridge.write_file("/memory/test.md", "content", "power")
        self.assertTrue(result["success"])

    def test_read_file_success(self):
        """Test file reading"""
        result = self.bridge.read_file("/memory/test.md", "user")
        self.assertTrue(result["success"])
        self.assertIn("content", result)

    def test_read_file_scope_check(self):
        """Test file scope security check"""
        result = self.bridge.read_file("/etc/passwd", "user")
        self.assertFalse(result["success"])
        self.assertIn("outside allowed scope", result["error"])

    def test_spawn_process(self):
        """Test process spawning"""
        proc_id = self.bridge.spawn_process("python", ["script.py"])
        self.assertIsNotNone(proc_id)
        self.assertIn(proc_id, self.bridge.active_processes)

    def test_get_process_status(self):
        """Test process status retrieval"""
        proc_id = self.bridge.spawn_process("python", ["script.py"])
        status = self.bridge.get_process_status(proc_id)
        self.assertIsNotNone(status)
        self.assertEqual(status["status"], "running")

    def test_ipc_logging(self):
        """Test IPC call logging"""
        self.bridge.execute_cli_command("HELP", "user")
        self.bridge.read_file("/memory/test.md", "user")

        stats = self.bridge.get_ipc_stats()
        self.assertEqual(stats["total_calls"], 2)

    def test_ipc_call_breakdown(self):
        """Test IPC call breakdown by command"""
        self.bridge.execute_cli_command("HELP", "user")
        self.bridge.execute_cli_command("STATUS", "user")
        self.bridge.read_file("/memory/test.md", "user")

        stats = self.bridge.get_ipc_stats()
        breakdown = stats["call_breakdown"]
        self.assertEqual(breakdown["execute_cli"], 2)
        self.assertEqual(breakdown["read_file"], 1)

    def test_write_file_success(self):
        """Test successful file write"""
        result = self.bridge.write_file("/memory/notes.md", "Test content", "wizard")
        self.assertTrue(result["success"])
        self.assertEqual(result["bytes_written"], len("Test content"))


class TestFrontendIntegration(unittest.TestCase):
    """Test Teletext GUI integration"""

    def setUp(self):
        self.frontend = FrontendIntegration()

    def test_register_assets(self):
        """Test asset registration"""
        self.frontend.register_asset("index.html", "html", 5000)
        self.frontend.register_asset("styles.css", "css", 3000)
        self.assertEqual(len(self.frontend.assets), 2)

    def test_cache_asset(self):
        """Test asset caching"""
        self.frontend.register_asset("index.html", "html", 5000)
        success = self.frontend.cache_asset("index.html")
        self.assertTrue(success)
        self.assertIn("index.html", self.frontend.cached_assets)

    def test_cache_nonexistent_asset(self):
        """Test caching nonexistent asset fails"""
        success = self.frontend.cache_asset("nonexistent.js")
        self.assertFalse(success)

    def test_asset_manifest(self):
        """Test asset manifest generation"""
        self.frontend.register_asset("index.html", "html", 5000)
        self.frontend.register_asset("styles.css", "css", 3000)
        self.frontend.cache_asset("index.html")

        manifest = self.frontend.get_asset_manifest()
        self.assertEqual(manifest["total_assets"], 2)
        self.assertEqual(manifest["cached_assets"], 1)
        self.assertEqual(manifest["total_size"], 8000)

    def test_offline_ready_check(self):
        """Test offline readiness check"""
        self.frontend.register_asset("index.html", "html", 5000)
        self.frontend.register_asset("styles.css", "css", 3000)

        # Not all cached yet
        self.assertFalse(self.frontend.all_assets_cached())

        # Cache all
        self.frontend.cache_asset("index.html")
        self.frontend.cache_asset("styles.css")

        self.assertTrue(self.frontend.all_assets_cached())

    def test_initialize_webview_offline(self):
        """Test webview initialization in offline mode"""
        self.frontend.offline_mode = True
        self.frontend.register_asset("index.html", "html", 5000)

        # Should fail without cached assets
        success = self.frontend.initialize_webview()
        self.assertFalse(success)

        # Cache and retry
        self.frontend.cache_asset("index.html")
        success = self.frontend.initialize_webview()
        self.assertTrue(success)

    def test_api_bridge_injection(self):
        """Test JavaScript API bridge injection"""
        bridge = self.frontend.inject_api_bridge()
        self.assertIn("executeCommand", bridge)
        self.assertIn("readFile", bridge)
        self.assertIn("writeFile", bridge)
        self.assertIn("window.__TAURI__", bridge["executeCommand"])

    def test_asset_count_by_type(self):
        """Test asset counting by type"""
        self.frontend.register_asset("index.html", "html", 5000)
        self.frontend.register_asset("about.html", "html", 3000)
        self.frontend.register_asset("styles.css", "css", 2000)
        self.frontend.register_asset("script.js", "js", 4000)

        manifest = self.frontend.get_asset_manifest()
        by_type = manifest["by_type"]
        self.assertEqual(by_type["html"], 2)
        self.assertEqual(by_type["css"], 1)
        self.assertEqual(by_type["js"], 1)


class TestNativeFeatures(unittest.TestCase):
    """Test native OS features"""

    def setUp(self):
        self.tray = SystemTrayManager()
        self.menu = NativeMenuManager(Platform.MACOS)
        self.file_assoc = FileAssociationManager()

    def test_system_tray_creation(self):
        """Test system tray creation"""
        self.assertTrue(self.tray.visible)
        self.assertEqual(self.tray.icon_path, "icons/tray.png")

    def test_tray_menu_items(self):
        """Test adding tray menu items"""
        item = MenuItem("Show uDOS", "show_window")
        self.tray.add_menu_item(item)
        self.assertEqual(len(self.tray.menu_items), 1)
        self.assertEqual(self.tray.menu_items[0].label, "Show uDOS")

    def test_native_menu_structure(self):
        """Test native menu structure"""
        menus = self.menu.get_menu_structure()
        self.assertIn("File", menus)
        self.assertIn("Edit", menus)
        self.assertIn("View", menus)
        self.assertIn("Help", menus)

    def test_macos_app_menu(self):
        """Test macOS-specific app menu"""
        menus = self.menu.get_menu_structure()
        self.assertIn("uDOS", menus)
        app_menu = menus["uDOS"]
        self.assertTrue(any(item.label == "About uDOS" for item in app_menu))

    def test_menu_accelerators(self):
        """Test keyboard shortcuts"""
        menus = self.menu.get_menu_structure()
        file_menu = menus["File"]
        new_item = next(item for item in file_menu if item.label == "New Mission")
        self.assertEqual(new_item.accelerator, "Ctrl+N")

    def test_file_association_registration(self):
        """Test file association registration"""
        self.file_assoc.register_extension(".uscript", "uDOS Script", "icons/uscript.png")
        extensions = self.file_assoc.get_registered_extensions()
        self.assertIn(".uscript", extensions)

    def test_can_open_file(self):
        """Test file opening capability check"""
        self.file_assoc.register_extension(".uscript", "uDOS Script", "icons/uscript.png")
        self.assertTrue(self.file_assoc.can_open("test.uscript"))
        self.assertFalse(self.file_assoc.can_open("test.exe"))

    def test_menu_action_handling(self):
        """Test menu action handling"""
        result = self.menu.handle_menu_action("show_docs")
        self.assertTrue(result["handled"])
        self.assertEqual(result["action"], "show_docs")

    def test_linux_menu_differences(self):
        """Test Linux menu doesn't have macOS app menu"""
        linux_menu = NativeMenuManager(Platform.LINUX)
        menus = linux_menu.get_menu_structure()
        self.assertNotIn("uDOS", menus)

    def test_disabled_menu_item(self):
        """Test disabled menu items"""
        item = MenuItem("Disabled Action", "disabled", enabled=False)
        self.assertFalse(item.enabled)


class TestAutoUpdate(unittest.TestCase):
    """Test auto-update system"""

    def setUp(self):
        self.updater = UpdateManager("1.1.4")

    def test_check_for_updates_available(self):
        """Test update check with newer version"""
        update = self.updater.check_for_updates(Platform.MACOS)
        self.assertIsNotNone(update)
        self.assertEqual(update.version, "1.1.5")

    def test_check_for_updates_current(self):
        """Test update check with current version"""
        self.updater.current_version = "1.1.5"
        update = self.updater.check_for_updates(Platform.MACOS)
        self.assertIsNone(update)

    def test_version_comparison(self):
        """Test version string comparison"""
        self.assertEqual(self.updater._compare_versions("1.1.5", "1.1.4"), 1)
        self.assertEqual(self.updater._compare_versions("1.1.4", "1.1.5"), -1)
        self.assertEqual(self.updater._compare_versions("1.1.4", "1.1.4"), 0)

    def test_signature_verification(self):
        """Test update signature verification"""
        update = UpdateInfo(
            version="1.1.5",
            release_date=datetime.now(),
            download_url="https://example.com/update",
            signature="mock_signature",
            size_bytes=1000000,
            changelog="Updates"
        )
        self.assertTrue(self.updater.verify_signature(update))

    def test_download_progress(self):
        """Test update download progress tracking"""
        update = UpdateInfo(
            version="1.1.5",
            release_date=datetime.now(),
            download_url="https://example.com/update",
            signature="mock_signature",
            size_bytes=50000000,
            changelog="Updates"
        )
        success = self.updater.download_update(update)
        self.assertTrue(success)
        self.assertEqual(self.updater.download_progress, 100.0)

    def test_update_status(self):
        """Test update status retrieval"""
        status = self.updater.get_update_status()
        self.assertEqual(status["current_version"], "1.1.4")
        self.assertTrue(status["auto_check_enabled"])


class TestCrossPlatform(unittest.TestCase):
    """Test cross-platform compatibility"""

    def test_macos_features(self):
        """Test macOS-specific features"""
        platform = PlatformManager(Platform.MACOS)
        self.assertTrue(platform.is_feature_supported("touchbar"))
        self.assertTrue(platform.is_feature_supported("app_menu"))
        self.assertTrue(platform.is_feature_supported("dock_menu"))

    def test_windows_features(self):
        """Test Windows-specific features"""
        platform = PlatformManager(Platform.WINDOWS)
        self.assertTrue(platform.is_feature_supported("taskbar_integration"))
        self.assertTrue(platform.is_feature_supported("jump_lists"))

    def test_linux_features(self):
        """Test Linux-specific features"""
        platform = PlatformManager(Platform.LINUX)
        self.assertTrue(platform.is_feature_supported("app_indicator"))
        self.assertTrue(platform.is_feature_supported("desktop_file"))

    def test_macos_data_directory(self):
        """Test macOS data directory"""
        platform = PlatformManager(Platform.MACOS)
        path = platform.get_data_directory()
        self.assertIn("Library/Application Support", path)

    def test_windows_data_directory(self):
        """Test Windows data directory"""
        platform = PlatformManager(Platform.WINDOWS)
        path = platform.get_data_directory()
        self.assertIn("APPDATA", path)

    def test_linux_data_directory(self):
        """Test Linux data directory"""
        platform = PlatformManager(Platform.LINUX)
        path = platform.get_data_directory()
        self.assertIn(".local/share", path)

    def test_macos_shortcut_format(self):
        """Test macOS keyboard shortcut format"""
        platform = PlatformManager(Platform.MACOS)
        shortcut = platform.get_shortcut_format("Ctrl+S")
        self.assertEqual(shortcut, "Cmd+S")

    def test_common_features_all_platforms(self):
        """Test features common to all platforms"""
        for plat in [Platform.MACOS, Platform.WINDOWS, Platform.LINUX]:
            platform = PlatformManager(plat)
            self.assertTrue(platform.is_feature_supported("notifications"))
            self.assertTrue(platform.is_feature_supported("file_associations"))
            self.assertTrue(platform.is_feature_supported("auto_updates"))


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
