"""
uDOS Startup Health Check and Self-Healing System

This module provides comprehensive health checks and auto-repair capabilities
for the uDOS system. It validates critical files, modules, configurations,
and dependencies at startup, with the ability to automatically fix common issues.

Functions:
    - check_system_health(): Run all health checks
    - repair_system(): Auto-repair detected issues
    - get_health_report(): Generate detailed diagnostic report
"""

import os
import sys
import json
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Any


class HealthCheckResult:
    """Result of a health check operation."""

    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.issues = []
        self.warnings = []
        self.recommendations = []

    def add_issue(self, issue: str, recommendation: str = ""):
        """Add a critical issue (fails health check)."""
        self.passed = False
        self.issues.append(issue)
        if recommendation:
            self.recommendations.append(recommendation)

    def add_warning(self, warning: str, recommendation: str = ""):
        """Add a non-critical warning."""
        self.warnings.append(warning)
        if recommendation:
            self.recommendations.append(recommendation)

    def is_healthy(self) -> bool:
        """Check if this component is healthy."""
        return self.passed and len(self.issues) == 0


class SystemHealth:
    """Overall system health status."""

    def __init__(self):
        self.checks: List[HealthCheckResult] = []
        self.repaired_issues = []

    def add_check(self, check: HealthCheckResult):
        """Add a health check result."""
        self.checks.append(check)

    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        return all(check.is_healthy() for check in self.checks)

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return any(len(check.warnings) > 0 for check in self.checks)

    def get_issues_count(self) -> int:
        """Count total critical issues."""
        return sum(len(check.issues) for check in self.checks)

    def get_warnings_count(self) -> int:
        """Count total warnings."""
        return sum(len(check.warnings) for check in self.checks)


def get_udos_root() -> Path:
    """Get the root directory of the uDOS installation."""
    # Assume this module is in core/ subdirectory
    return Path(__file__).parent.parent


def check_critical_files() -> HealthCheckResult:
    """
    Check for existence of critical uDOS files and directories.

    Returns:
        HealthCheckResult with status of critical files
    """
    result = HealthCheckResult("Critical Files")
    root = get_udos_root()

    # Critical files that must exist
    critical_files = [
        "uDOS.py",
        "core/uDOS_main.py",
        "core/uDOS_parser.py",
        "core/uDOS_grid.py",
        "core/uDOS_commands.py",
        "data/system/commands.json",
        "data/themes/dungeon.json",
    ]

    # Critical directories
    critical_dirs = [
        "core",
        "data",
        "data/system",
        "data/themes",
        "sandbox",
        "memory",
    ]

    # Check files
    for file_path in critical_files:
        full_path = root / file_path
        if not full_path.exists():
            result.add_issue(
                f"Missing critical file: {file_path}",
                f"Restore {file_path} from repository or backup"
            )
        elif not full_path.is_file():
            result.add_issue(
                f"Path is not a file: {file_path}",
                f"Remove conflicting directory and restore file"
            )

    # Check directories
    for dir_path in critical_dirs:
        full_path = root / dir_path
        if not full_path.exists():
            result.add_warning(
                f"Missing directory: {dir_path}",
                f"Directory will be auto-created: {dir_path}"
            )
        elif not full_path.is_dir():
            result.add_issue(
                f"Path is not a directory: {dir_path}",
                f"Remove conflicting file and create directory"
            )

    return result


def check_module_imports() -> HealthCheckResult:
    """
    Check that all core uDOS modules can be imported.

    Returns:
        HealthCheckResult with status of module imports
    """
    result = HealthCheckResult("Module Imports")

    # Add the uDOS root to sys.path temporarily for imports
    root = get_udos_root()
    sys_path_backup = sys.path.copy()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Core modules that should be importable
    core_modules = [
        "core.uDOS_main",
        "core.uDOS_parser",
        "core.uDOS_grid",
        "core.uDOS_commands",
        "core.uDOS_splash",
        "core.uDOS_graphics",
        "core.uDOS_viewport",
    ]

    for module_name in core_modules:
        try:
            # Remove from cache if already imported to get fresh import
            if module_name in sys.modules:
                del sys.modules[module_name]
            importlib.import_module(module_name)
        except ImportError as e:
            result.add_issue(
                f"Cannot import module: {module_name}",
                f"Check for syntax errors or missing dependencies: {str(e)}"
            )
        except Exception as e:
            result.add_warning(
                f"Error importing module: {module_name} - {str(e)}",
                "Check module for runtime errors during import"
            )

    # Restore sys.path
    sys.path = sys_path_backup

    return result
def check_json_configs() -> HealthCheckResult:
    """
    Check that JSON configuration files are valid.

    Returns:
        HealthCheckResult with status of JSON configs
    """
    result = HealthCheckResult("JSON Configurations")
    root = get_udos_root()

    # JSON files to validate
    json_files = [
        "data/system/commands.json",
        "data/themes/dungeon.json",
        "data/templates/story.template.json",
    ]

    for json_path in json_files:
        full_path = root / json_path

        if not full_path.exists():
            # Not an error if story template doesn't exist
            if "story.template" in json_path:
                continue
            result.add_warning(
                f"Missing JSON file: {json_path}",
                f"File will be created with defaults"
            )
            continue

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Basic structure validation
                if "commands.json" in json_path:
                    if not isinstance(data, dict) or "COMMANDS" not in data:
                        result.add_issue(
                            f"Invalid structure in {json_path}",
                            "Restore from backup or repository"
                        )
                elif "dungeon.json" in json_path or "theme" in json_path:
                    # Theme files should have TERMINOLOGY
                    if not isinstance(data, dict) or "TERMINOLOGY" not in data:
                        result.add_issue(
                            f"Invalid structure in {json_path}",
                            "Restore from backup or repository"
                        )

        except json.JSONDecodeError as e:
            result.add_issue(
                f"Invalid JSON in {json_path}: {str(e)}",
                "Fix JSON syntax or restore from backup"
            )
        except Exception as e:
            result.add_warning(
                f"Error reading {json_path}: {str(e)}",
                "Check file permissions and encoding"
            )

    return result


def check_permissions() -> HealthCheckResult:
    """
    Check file and directory permissions.

    Returns:
        HealthCheckResult with status of permissions
    """
    result = HealthCheckResult("Permissions")
    root = get_udos_root()

    # Directories that need write permission
    writable_dirs = [
        "sandbox",
        "memory",
        "data",
        "output",
    ]

    for dir_path in writable_dirs:
        full_path = root / dir_path

        if not full_path.exists():
            continue  # Will be caught by critical files check

        if not os.access(full_path, os.W_OK):
            result.add_issue(
                f"No write permission for directory: {dir_path}",
                f"Grant write permissions: chmod u+w {full_path}"
            )

        if not os.access(full_path, os.R_OK):
            result.add_issue(
                f"No read permission for directory: {dir_path}",
                f"Grant read permissions: chmod u+r {full_path}"
            )

    return result


def check_python_version() -> HealthCheckResult:
    """
    Check Python version compatibility.

    Returns:
        HealthCheckResult with Python version status
    """
    result = HealthCheckResult("Python Version")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    # Require Python 3.7+
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        result.add_issue(
            f"Python version {version_str} is too old (requires 3.7+)",
            "Upgrade to Python 3.7 or later"
        )
    elif version.minor < 9:
        result.add_warning(
            f"Python {version_str} detected (recommended 3.9+)",
            "Consider upgrading for best compatibility"
        )

    return result


def check_virtual_environment() -> HealthCheckResult:
    """
    Check if running in a virtual environment and if it's properly configured.

    Returns:
        HealthCheckResult with virtual environment status
    """
    result = HealthCheckResult("Virtual Environment")

    # Check if running in venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if not in_venv:
        result.add_warning(
            "Not running in a virtual environment",
            "Create and activate venv: python3 -m venv .venv && source .venv/bin/activate"
        )

    # Check if venv directory exists
    root = get_udos_root()
    venv_path = root / '.venv'

    if venv_path.exists() and not in_venv:
        result.add_warning(
            "Virtual environment exists but not activated",
            "Activate with: source .venv/bin/activate"
        )
    elif not venv_path.exists():
        result.add_warning(
            "No virtual environment found",
            "Create with: python3 -m venv .venv"
        )

    return result


def check_pip_version() -> HealthCheckResult:
    """
    Check pip version and recommend upgrade if outdated.

    Returns:
        HealthCheckResult with pip version status
    """
    import subprocess
    result = HealthCheckResult("pip Version")

    try:
        # Get current pip version
        pip_version_output = subprocess.check_output(
            [sys.executable, '-m', 'pip', '--version'],
            stderr=subprocess.STDOUT,
            text=True
        )

        # Parse version (format: "pip X.Y.Z from ...")
        current_version = None
        for part in pip_version_output.split():
            if part[0].isdigit() and '.' in part:
                current_version = part
                break

        if current_version:
            # Check if there's a newer version available
            try:
                check_output = subprocess.check_output(
                    [sys.executable, '-m', 'pip', 'list', '--outdated'],
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=5  # Don't wait too long
                )

                if 'pip' in check_output:
                    # Extract available version
                    for line in check_output.split('\n'):
                        if line.startswith('pip '):
                            parts = line.split()
                            if len(parts) >= 3:
                                available_version = parts[2]
                                result.add_warning(
                                    f"pip {current_version} is outdated (latest: {available_version})",
                                    f"Upgrade with: {sys.executable} -m pip install --upgrade pip"
                                )
                                break
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                # Network issue or pip list failed, skip upgrade check
                pass

    except Exception as e:
        result.add_warning(
            f"Could not check pip version: {str(e)}",
            "Ensure pip is installed and accessible"
        )

    return result


def check_dependencies() -> HealthCheckResult:
    """
    Check for required and optional Python packages.

    Returns:
        HealthCheckResult with dependency status
    """
    result = HealthCheckResult("Python Dependencies")

    # Check for optional web extension dependencies
    optional_packages = {
        "flask": "Web extensions (dashboard, font-editor, markdown-viewer)",
        "requests": "Network connectivity checks and API features",
    }

    for package, purpose in optional_packages.items():
        try:
            importlib.import_module(package)
        except ImportError:
            result.add_warning(
                f"Optional package not installed: {package}",
                f"Install for {purpose}: pip install {package}"
            )

    return result


def check_git_repository() -> HealthCheckResult:
    """
    Check if this is a git repository and if it's up to date.

    Returns:
        HealthCheckResult with git repository status
    """
    import subprocess
    result = HealthCheckResult("Git Repository")
    root = get_udos_root()

    # Check if .git directory exists
    git_dir = root / '.git'
    if not git_dir.exists():
        result.add_warning(
            "Not a git repository",
            "Clone from GitHub: git clone https://github.com/fredporter/uDOS.git"
        )
        return result

    try:
        # Check if git is installed
        subprocess.run(
            ['git', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            cwd=str(root)
        )

        # Check current branch
        branch_output = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(root)
        ).strip()

        # Check if there are uncommitted changes
        status_output = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(root)
        ).strip()

        if status_output:
            result.add_warning(
                f"Uncommitted changes detected on branch '{branch_output}'",
                "Commit or stash changes before pulling updates"
            )

        # Check if remote exists
        try:
            remote_output = subprocess.check_output(
                ['git', 'remote', '-v'],
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(root)
            ).strip()

            if 'origin' not in remote_output:
                result.add_warning(
                    "No 'origin' remote configured",
                    "Add remote: git remote add origin https://github.com/fredporter/uDOS.git"
                )
            else:
                # Check if we can fetch from remote (requires network)
                try:
                    subprocess.run(
                        ['git', 'fetch', '--dry-run'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5,
                        cwd=str(root)
                    )

                    # Check if behind remote
                    behind_output = subprocess.check_output(
                        ['git', 'rev-list', '--count', 'HEAD..@{u}'],
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=str(root)
                    ).strip()

                    if behind_output and int(behind_output) > 0:
                        result.add_warning(
                            f"Repository is {behind_output} commit(s) behind origin/{branch_output}",
                            f"Update with: REPAIR --pull or git pull origin {branch_output}"
                        )

                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    # Network issue, can't check remote status
                    pass

        except subprocess.CalledProcessError:
            # No remote or can't access it
            pass

    except subprocess.CalledProcessError as e:
        result.add_warning(
            f"Git error: {str(e)}",
            "Check git installation and repository integrity"
        )
    except FileNotFoundError:
        result.add_warning(
            "Git not installed",
            "Install git to enable version control features"
        )

    return result


def repair_git_pull(verbose: bool = False) -> Tuple[bool, str]:
    """
    Pull latest changes from GitHub repository.

    Args:
        verbose: If True, print detailed progress

    Returns:
        Tuple of (success, message)
    """
    import subprocess
    root = get_udos_root()

    if verbose:
        print("📥 Pulling latest changes from GitHub...")
        print()

    # Check if git repo
    git_dir = root / '.git'
    if not git_dir.exists():
        return False, "Not a git repository"

    try:
        # Get current branch
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(root)
        ).strip()

        # Check for uncommitted changes
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(root)
        ).strip()

        if status:
            if verbose:
                print("  ⚠️  Uncommitted changes detected")
                print("  📦 Stashing local changes...")

            # Stash changes
            subprocess.run(
                ['git', 'stash', 'push', '-m', 'Auto-stash before REPAIR --pull'],
                stdout=subprocess.PIPE if not verbose else None,
                stderr=subprocess.PIPE if not verbose else None,
                cwd=str(root)
            )

        if verbose:
            print(f"  🔄 Pulling from origin/{branch}...")

        # Pull changes
        pull_result = subprocess.run(
            ['git', 'pull', 'origin', branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(root)
        )

        if pull_result.returncode != 0:
            return False, f"Git pull failed: {pull_result.stdout}"

        if verbose:
            if "Already up to date" in pull_result.stdout:
                print("  ✅ Already up to date")
            else:
                print("  ✅ Successfully pulled changes")

            # Restore stashed changes if any
            if status:
                print("  📦 Restoring stashed changes...")
                subprocess.run(
                    ['git', 'stash', 'pop'],
                    stdout=subprocess.PIPE if not verbose else None,
                    stderr=subprocess.PIPE if not verbose else None,
                    cwd=str(root)
                )

        return True, "Successfully updated from GitHub"

    except subprocess.CalledProcessError as e:
        return False, f"Git error: {str(e)}"
    except FileNotFoundError:
        return False, "Git not installed"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def repair_pip_upgrade(verbose: bool = False) -> Tuple[bool, str]:
    """
    Upgrade pip to the latest version.

    Args:
        verbose: If True, print detailed progress

    Returns:
        Tuple of (success, message)
    """
    import subprocess

    if verbose:
        print("📦 Upgrading pip to latest version...")
        print()

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        if result.returncode == 0:
            if verbose:
                print("  ✅ pip upgraded successfully")
            return True, "pip upgraded successfully"
        else:
            return False, f"pip upgrade failed: {result.stdout}"

    except Exception as e:
        return False, f"Error upgrading pip: {str(e)}"


def repair_missing_directories() -> List[str]:
    """
    Create any missing critical directories.

    Returns:
        List of directories that were created
    """
    created = []
    root = get_udos_root()

    critical_dirs = ["core", "data", "sandbox", "memory", "output"]

    for dir_path in critical_dirs:
        full_path = root / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            created.append(dir_path)

    return created


def check_web_servers() -> HealthCheckResult:
    """
    Check if required web servers are running and start them if needed.

    Returns:
        HealthCheckResult with web server status
    """
    import subprocess
    import socket

    result = HealthCheckResult("Web Servers")
    root = get_udos_root()

    # Define required servers
    servers = {
        'markdown-viewer': {
            'port': 9000,
            'path': 'extensions/web/markdown-viewer',
            'script': 'server.py',
            'name': 'Markdown Viewer'
        },
        'dashboard': {
            'port': 8887,
            'path': 'extensions/web/dashboard',
            'script': 'server.py',
            'name': 'Dashboard'
        }
    }

    def is_port_in_use(port: int) -> bool:
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    for server_id, config in servers.items():
        server_path = root / config['path']
        server_script = server_path / config['script']

        # Check if server directory exists
        if not server_path.exists():
            result.add_warning(
                f"{config['name']} directory not found: {config['path']}",
                f"Server will not be auto-started"
            )
            continue

        # Check if server script exists
        if not server_script.exists():
            result.add_warning(
                f"{config['name']} script not found: {server_script}",
                f"Create {config['script']} or check installation"
            )
            continue

        # Check if server is running
        if is_port_in_use(config['port']):
            # Server already running - good!
            continue
        else:
            # Server not running - try to start it
            try:
                # Start server in background
                subprocess.Popen(
                    [sys.executable, config['script'], '--port', str(config['port'])],
                    cwd=str(server_path),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True  # Detach from parent process
                )

                # Wait a moment and check if it started
                import time
                time.sleep(0.5)

                if is_port_in_use(config['port']):
                    result.add_warning(
                        f"Started {config['name']} on port {config['port']}",
                        f"Server auto-started successfully"
                    )
                else:
                    result.add_warning(
                        f"{config['name']} failed to start on port {config['port']}",
                        f"Try manually: cd {config['path']} && python3 {config['script']}"
                    )

            except Exception as e:
                result.add_warning(
                    f"Could not auto-start {config['name']}: {e}",
                    f"Start manually: cd {config['path']} && python3 {config['script']}"
                )

    return result


def check_web_extensions() -> HealthCheckResult:
    """
    Check if web extensions are installed and install if missing.

    Returns:
        HealthCheckResult with extension status
    """
    result = HealthCheckResult("Web Extensions")

    try:
        # Import extension manager
        from core.uDOS_extensions import ExtensionManager

        manager = ExtensionManager()

        # Get extension status
        status = manager.get_extension_status()

        # Check each extension
        missing = []
        installed = []

        for ext_name, is_installed in status.items():
            if is_installed:
                installed.append(ext_name)
            else:
                missing.append(ext_name)

        # Report installed extensions
        if installed:
            result.add_warning(
                f"Extensions installed: {', '.join(installed)}",
                ""
            )

        # Try to install missing extensions
        if missing:
            result.add_warning(
                f"Missing extensions: {', '.join(missing)}",
                "Attempting auto-install..."
            )

            # Install missing extensions
            for ext_name in missing:
                if ext_name == 'cmd':  # Skip built-in
                    continue

                success, message = manager.install_extension(ext_name, quiet=True)

                if success:
                    result.add_warning(
                        f"✓ {ext_name} installed successfully",
                        ""
                    )
                else:
                    result.add_warning(
                        f"✗ {ext_name} installation failed: {message}",
                        f"Try: cd extensions && bash setup_{ext_name}.sh"
                    )

        # All extensions installed
        if not missing:
            result.add_warning(
                "All extensions ready",
                ""
            )

    except Exception as e:
        result.add_warning(
            f"Extension check failed: {str(e)}",
            "Extensions may need manual installation"
        )

    return result


def check_viewport() -> HealthCheckResult:
    """
    Check viewport detection and screen size tier identification.

    Returns:
        HealthCheckResult with viewport status
    """
    result = HealthCheckResult("Viewport System")

    try:
        # Import viewport manager
        from core.services.viewport_manager import ViewportManager

        # Initialize viewport manager
        viewport = ViewportManager()
        viewport_info = viewport.get_viewport_info()

        # Check terminal detection
        char_width, char_height = viewport.get_terminal_size()
        if char_width < 40 or char_height < 10:
            result.add_warning(
                f"Small terminal detected: {char_width}×{char_height} chars",
                "Consider using a larger terminal for optimal experience"
            )

        # Check screen tier detection
        tier = viewport_info["screen_tier"]
        cell_width = tier["actual_width_cells"]
        cell_height = tier["actual_height_cells"]

        if cell_width < 20 or cell_height < 10:
            result.add_warning(
                f"Very small viewport: {cell_width}×{cell_height} cells (Tier {tier['tier']})",
                "Some features may be limited on small screens"
            )
        elif tier["tier"] >= 8:  # HD Display or larger
            result.add_warning(
                f"Large viewport detected: {tier['label']} (Tier {tier['tier']})",
                "Excellent display capabilities available"
            )

        # Validate screen tier data
        if "label" not in tier or "tier" not in tier:
            result.add_issue(
                "Invalid screen tier data detected",
                "Run REBOOT to refresh viewport detection"
            )
        else:
            result.add_warning(
                f"Viewport: {tier['label']} ({cell_width}×{cell_height} cells)",
                f"Detection method: {viewport_info.get('detection_method', 'unknown')}"
            )

        # Check viewport settings file
        if viewport.settings_file.exists():
            result.add_warning(
                "Viewport settings saved",
                "Use CONFIG VIEWPORT to modify"
            )
        else:
            result.add_warning(
                "Using auto-detected viewport",
                "Settings will be saved on first manual configuration"
            )

    except ImportError as e:
        result.add_issue(
            "Viewport manager not available",
            "Check core/services/viewport_manager.py exists"
        )
    except Exception as e:
        result.add_warning(
            f"Viewport check error: {str(e)}",
            "Viewport detection may not be optimal"
        )

    return result


def repair_permissions() -> List[str]:
    """
    Fix permissions on critical directories.

    Returns:
        List of directories that were repaired
    """
    repaired = []
    root = get_udos_root()

    writable_dirs = ["sandbox", "memory", "data", "output"]

    for dir_path in writable_dirs:
        full_path = root / dir_path
        if full_path.exists() and not os.access(full_path, os.W_OK):
            try:
                os.chmod(full_path, 0o755)
                repaired.append(dir_path)
            except Exception as e:
                print(f"  ⚠️  Failed to repair {dir_path}: {e}")

    return repaired


def check_system_health(verbose: bool = False) -> SystemHealth:
    """
    Run all health checks on the uDOS system.

    Args:
        verbose: If True, print detailed progress

    Returns:
        SystemHealth object with all check results
    """
    health = SystemHealth()

    if verbose:
        print("🔍 Running system health checks...")
        print()

    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("pip Version", check_pip_version),
        ("Git Repository", check_git_repository),
        ("Critical Files", check_critical_files),
        ("Module Imports", check_module_imports),
        ("JSON Configs", check_json_configs),
        ("Permissions", check_permissions),
        ("Dependencies", check_dependencies),
        ("Viewport System", check_viewport),
        ("Web Extensions", check_web_extensions),
        ("Web Servers", check_web_servers),
    ]

    for name, check_func in checks:
        if verbose:
            print(f"  Checking {name}...", end=" ", flush=True)

        result = check_func()
        health.add_check(result)

        if verbose:
            if result.is_healthy():
                print("✅")
            elif result.passed:
                print(f"⚠️  ({len(result.warnings)} warnings)")
            else:
                print(f"❌ ({len(result.issues)} issues)")

    if verbose:
        print()

    return health


def repair_system(health: SystemHealth, verbose: bool = False) -> SystemHealth:
    """
    Attempt to automatically repair issues found in health checks.

    Args:
        health: SystemHealth object from check_system_health()
        verbose: If True, print repair progress

    Returns:
        Updated SystemHealth object after repairs
    """
    if verbose:
        print("🔧 Attempting auto-repair...")
        print()

    # Repair missing directories
    created_dirs = repair_missing_directories()
    if created_dirs:
        health.repaired_issues.extend([f"Created directory: {d}" for d in created_dirs])
        if verbose:
            for d in created_dirs:
                print(f"  ✅ Created directory: {d}")

    # Repair permissions
    repaired_perms = repair_permissions()
    if repaired_perms:
        health.repaired_issues.extend([f"Fixed permissions: {d}" for d in repaired_perms])
        if verbose:
            for d in repaired_perms:
                print(f"  ✅ Fixed permissions: {d}")

    if verbose and (created_dirs or repaired_perms):
        print()

    # Re-run health checks to see if repairs worked
    return check_system_health(verbose=False)


def get_health_report(health: SystemHealth, include_warnings: bool = True) -> str:
    """
    Generate a detailed health report.

    Args:
        health: SystemHealth object
        include_warnings: Include warnings in report

    Returns:
        Formatted health report string
    """
    lines = []
    lines.append("╔════════════════════════════════════════════════════════════╗")
    lines.append("║            🏥 uDOS SYSTEM HEALTH REPORT                    ║")
    lines.append("╠════════════════════════════════════════════════════════════╣")
    lines.append("")

    # Overall status
    if health.is_healthy():
        status = "✅ HEALTHY - All systems operational"
    elif health.get_issues_count() == 0:
        status = f"⚠️  CAUTION - {health.get_warnings_count()} warnings detected"
    else:
        status = f"❌ CRITICAL - {health.get_issues_count()} issues require attention"

    lines.append(f"  Status: {status}")
    lines.append("")

    # Repaired issues
    if health.repaired_issues:
        lines.append("  🔧 Auto-Repairs Applied:")
        for repair in health.repaired_issues:
            lines.append(f"     • {repair}")
        lines.append("")

    # Detailed check results
    for check in health.checks:
        status_icon = "✅" if check.is_healthy() else ("⚠️ " if check.passed else "❌")
        lines.append(f"  {status_icon} {check.name}")

        if check.issues:
            for issue in check.issues:
                lines.append(f"     ❌ {issue}")

        if include_warnings and check.warnings:
            for warning in check.warnings:
                lines.append(f"     ⚠️  {warning}")

        if check.recommendations:
            lines.append(f"     💡 Recommendations:")
            for rec in check.recommendations:
                lines.append(f"        • {rec}")

        lines.append("")

    lines.append("╚════════════════════════════════════════════════════════════╝")

    return "\n".join(lines)


def quick_health_check() -> Tuple[bool, str]:
    """
    Quick startup health check - only shows if there are issues.

    Returns:
        Tuple of (is_healthy, message)
    """
    health = check_system_health(verbose=False)

    if health.is_healthy():
        return True, "✅ System healthy"

    issues = health.get_issues_count()
    warnings = health.get_warnings_count()

    if issues > 0:
        return False, f"❌ {issues} critical issue(s) detected - run REPAIR for details"
    else:
        return True, f"⚠️  {warnings} warning(s) - run REPAIR --check for details"


if __name__ == "__main__":
    # Test the health check system
    print("Testing uDOS Health Check System")
    print("=" * 60)
    print()

    health = check_system_health(verbose=True)

    print()
    print(get_health_report(health))

    if not health.is_healthy():
        print("\nAttempting repairs...\n")
        health = repair_system(health, verbose=True)
        print()
        print(get_health_report(health))
