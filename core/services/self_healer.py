"""
Self-Healing System for uDOS
=============================

Detects and automatically repairs common issues:
- Missing dependencies
- Deprecated code patterns
- Configuration errors
- Port conflicts
- Version mismatches

Usage:
    from core.services.self_healer import SelfHealer

    healer = SelfHealer(component="wizard")
    result = healer.diagnose_and_repair()
    if result.success:
        logger.info("System healthy!")
"""

import sys
import subprocess
import warnings
import importlib
import ssl
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from core.services.logging_service import get_logger

logger = get_logger("self-healer")


class Spinner:
    """Simple spinner with elapsed time display."""

    def __init__(self, message: str = "Working"):
        self.message = message
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.start_time: float = 0.0

    def start(self):
        self.start_time = time.time()

        def _run():
            glyphs = "|/-\\"
            idx = 0
            while not self._stop.is_set():
                elapsed = time.time() - self.start_time
                sys.stdout.write(
                    f"\r{glyphs[idx % len(glyphs)]} {self.message}... (elapsed: {elapsed:0.1f}s) "
                )
                sys.stdout.flush()
                idx += 1
                time.sleep(0.12)
            # clear line and print final
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self, final_message: Optional[str] = None):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
        if final_message:
            elapsed = time.time() - self.start_time
            sys.stdout.write(f"{final_message} (elapsed: {elapsed:0.1f}s)\n")
            sys.stdout.flush()


class IssueType(Enum):
    """Types of issues that can be detected and repaired."""
    MISSING_DEPENDENCY = "missing_dependency"
    DEPRECATED_CODE = "deprecated_code"
    CONFIG_ERROR = "config_error"
    PORT_CONFLICT = "port_conflict"
    VERSION_MISMATCH = "version_mismatch"
    FILE_PERMISSION = "file_permission"


class IssueSeverity(Enum):
    """Severity levels for detected issues."""
    CRITICAL = "critical"  # Blocks startup
    WARNING = "warning"    # Works but needs attention
    INFO = "info"          # Optional improvement


@dataclass
class Issue:
    """Represents a detected issue."""
    type: IssueType
    severity: IssueSeverity
    description: str
    component: str
    repairable: bool = False
    auto_repairable: bool = False  # Can be fixed without user confirmation
    repair_action: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RepairResult:
    """Result of a repair operation."""
    success: bool
    issues_found: List[Issue] = field(default_factory=list)
    issues_repaired: List[Issue] = field(default_factory=list)
    issues_remaining: List[Issue] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)


class SelfHealer:
    """Self-healing system for uDOS components."""

    def __init__(self, component: str = "core", auto_repair: bool = True):
        """
        Initialize self-healer.

        Args:
            component: Component name (core, wizard, goblin, app)
            auto_repair: Whether to automatically repair issues
        """
        self.component = component
        self.auto_repair = auto_repair
        self.repo_root = self._find_repo_root()
        self.issues: List[Issue] = []

    def _find_repo_root(self) -> Path:
        """Find uDOS repository root."""
        current = Path(__file__).resolve()
        while current.parent != current:
            if (current / "AGENTS.md").exists():
                return current
            current = current.parent
        return Path.cwd()

    def diagnose_and_repair(self) -> RepairResult:
        """
        Run full diagnostic and repair cycle.

        Returns:
            RepairResult with details of issues found and repaired
        """
        logger.info(f"[HEAL] Running diagnostics for {self.component}...")

        # Run all diagnostic checks
        self._check_dependencies()
        self._check_ssl_backend()
        self._check_deprecations()
        self._check_configuration()
        self._check_ports()
        self._check_permissions()
        self._check_ts_runtime()  # Add TS runtime check

        # Attempt repairs if auto_repair is enabled
        repaired = []
        remaining = []

        if self.auto_repair:
            for issue in self.issues:
                if issue.repairable:
                    if self._attempt_repair(issue):
                        repaired.append(issue)
                        logger.info(f"[HEAL] ✅ Repaired: {issue.description}")
                    else:
                        remaining.append(issue)
                        logger.warning(f"[HEAL] ❌ Failed to repair: {issue.description}")
                else:
                    remaining.append(issue)
        else:
            remaining = self.issues

        success = len(remaining) == 0 or all(
            i.severity != IssueSeverity.CRITICAL for i in remaining
        )

        return RepairResult(
            success=success,
            issues_found=self.issues,
            issues_repaired=repaired,
            issues_remaining=remaining,
            messages=self._generate_summary(repaired, remaining)
        )

    def _check_dependencies(self):
        """Check for missing Python dependencies."""
        required_deps = self._get_required_dependencies()

        for dep, version in required_deps.items():
            try:
                mod = importlib.import_module(dep)
                # Check version if specified
                if version and hasattr(mod, "__version__"):
                    installed = mod.__version__
                    if not self._version_matches(installed, version):
                        self.issues.append(Issue(
                            type=IssueType.VERSION_MISMATCH,
                            severity=IssueSeverity.WARNING,
                            description=f"Dependency {dep} version mismatch: {installed} vs {version}",
                            component=self.component,
                            repairable=True,
                            repair_action=f"pip install {dep}=={version}",
                            details={"dependency": dep, "installed": installed, "required": version}
                        ))
            except ImportError:
                self.issues.append(Issue(
                    type=IssueType.MISSING_DEPENDENCY,
                    severity=IssueSeverity.CRITICAL,
                    description=f"Missing required dependency: {dep}",
                    component=self.component,
                    repairable=True,
                    repair_action=f"pip install {dep}{f'=={version}' if version else ''}",
                    details={"dependency": dep, "version": version}
                ))

    def _check_deprecations(self):
        """Check for deprecated code patterns."""
        deprecation_patterns = {
            "wizard": [
                {
                    "file": "wizard/server.py",
                    "pattern": "@app.on_event",
                    "description": "FastAPI on_event is deprecated, use lifespan instead",
                    "severity": IssueSeverity.WARNING,
                }
            ],
            "goblin": [
                {
                    "file": "dev/goblin/goblin_server.py",
                    "pattern": "@app.on_event",
                    "description": "FastAPI on_event is deprecated, use lifespan instead",
                    "severity": IssueSeverity.WARNING,
                }
            ]
        }

        patterns = deprecation_patterns.get(self.component, [])
        for pattern in patterns:
            file_path = self.repo_root / pattern["file"]
            if file_path.exists():
                content = file_path.read_text()
                if pattern["pattern"] in content:
                    self.issues.append(Issue(
                        type=IssueType.DEPRECATED_CODE,
                        severity=pattern["severity"],
                        description=pattern["description"],
                        component=self.component,
                        repairable=True,
                        repair_action="migrate_to_lifespan",
                        details={"file": str(file_path), "pattern": pattern["pattern"]}
                    ))

    def _check_configuration(self):
        """Check configuration files."""
        config_files = {
            "wizard": ["wizard/config/wizard.json"],
            "goblin": ["dev/goblin/config/goblin.json"],
            "core": ["core/config/core.json"]
        }

        files = config_files.get(self.component, [])
        for config_file in files:
            config_path = self.repo_root / config_file
            if not config_path.exists():
                # Config missing is usually OK (defaults used)
                logger.debug(f"[HEAL] Config file not found (using defaults): {config_file}")

    def _check_ssl_backend(self):
        """Detect incompatible SSL backend (e.g., macOS LibreSSL with urllib3 v2)."""
        try:
            import urllib3

            ssl_version = ssl.OPENSSL_VERSION
            urllib3_version = getattr(urllib3, "__version__", "0")

            # urllib3 v2 requires OpenSSL >= 1.1.1; macOS system Python links LibreSSL 2.8.x
            if "LibreSSL" in ssl_version and urllib3_version.startswith("2"):
                self.issues.append(Issue(
                    type=IssueType.CONFIG_ERROR,
                    severity=IssueSeverity.WARNING,
                    description="urllib3 v2 requires OpenSSL >=1.1.1; current backend is LibreSSL",
                    component=self.component,
                    repairable=True,
                    auto_repairable=True,  # Safe to auto-repair on macOS LibreSSL
                    repair_action="pip install 'urllib3<2.0.0'",
                    details={
                        "openssl_version": ssl_version,
                        "urllib3_version": urllib3_version,
                        "recommendation": "Downgrading urllib3 to <2.0 for LibreSSL compatibility"
                    }
                ))
        except Exception as e:
            logger.debug(f"[HEAL] SSL backend check skipped: {e}")

    def _check_ports(self):
        """Check for port conflicts."""
        try:
            import socket

            port_map = {
                "wizard": 8765,
                "goblin": 8767,
                "api": 8766
            }

            port = port_map.get(self.component)
            if port:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(("127.0.0.1", port))
                sock.close()

                if result == 0:
                    self.issues.append(Issue(
                        type=IssueType.PORT_CONFLICT,
                        severity=IssueSeverity.CRITICAL,
                        description=f"Port {port} is already in use",
                        component=self.component,
                        repairable=True,
                        repair_action=f"kill_port_{port}",
                        details={"port": port}
                    ))
        except Exception as e:
            logger.debug(f"[HEAL] Port check failed: {e}")

    def _check_permissions(self):
        """Check file permissions."""
        script_dirs = [
            self.repo_root / "bin",
            self.repo_root / "dev" / "bin",
            self.repo_root / "dev" / "goblin" / "bin"
        ]

        for script_dir in script_dirs:
            if not script_dir.exists():
                continue

            for script in script_dir.glob("*.sh"):
                if not script.stat().st_mode & 0o111:  # Not executable
                    self.issues.append(Issue(
                        type=IssueType.FILE_PERMISSION,
                        severity=IssueSeverity.WARNING,
                        description=f"Script not executable: {script.name}",
                        component=self.component,
                        repairable=True,
                        repair_action=f"chmod +x {script}",
                        details={"file": str(script)}
                    ))

    def _check_ts_runtime(self):
        """Check if TypeScript runtime is built."""
        runtime_dist = self.repo_root / "core" / "grid-runtime" / "dist" / "index.js"

        if not runtime_dist.exists():
            # Check if Node.js/npm are available
            try:
                node_check = subprocess.run(
                    ["node", "--version"],
                    capture_output=True,
                    timeout=5
                )
                npm_check = subprocess.run(
                    ["npm", "--version"],
                    capture_output=True,
                    timeout=5
                )

                if node_check.returncode == 0 and npm_check.returncode == 0:
                    self.issues.append(Issue(
                        type=IssueType.CONFIG_ERROR,
                        severity=IssueSeverity.WARNING,
                        description="TypeScript runtime not built (Node.js available)",
                        component=self.component,
                        repairable=True,
                        repair_action="build_ts_runtime",
                        details={"runtime_dist": str(runtime_dist)}
                    ))
                else:
                    self.issues.append(Issue(
                        type=IssueType.MISSING_DEPENDENCY,
                        severity=IssueSeverity.WARNING,
                        description="TypeScript runtime not built (Node.js/npm not available)",
                        component=self.component,
                        repairable=False,
                        repair_action="install Node.js/npm and run: bash core/tools/build_ts_runtime.sh",
                        details={"runtime_dist": str(runtime_dist)}
                    ))
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.issues.append(Issue(
                    type=IssueType.MISSING_DEPENDENCY,
                    severity=IssueSeverity.WARNING,
                    description="TypeScript runtime not built (Node.js/npm check failed)",
                    component=self.component,
                    repairable=False,
                    repair_action="install Node.js/npm and run: bash core/tools/build_ts_runtime.sh",
                    details={"runtime_dist": str(runtime_dist)}
                ))

    def _attempt_repair(self, issue: Issue) -> bool:
        """
        Attempt to repair an issue.

        Args:
            issue: Issue to repair

        Returns:
            True if repair succeeded
        """
        try:
            if issue.type == IssueType.MISSING_DEPENDENCY:
                return self._repair_dependency(issue)
            elif issue.type == IssueType.PORT_CONFLICT:
                return self._repair_port_conflict(issue)
            elif issue.type == IssueType.FILE_PERMISSION:
                return self._repair_permission(issue)
            elif issue.type == IssueType.CONFIG_ERROR and issue.repair_action == "build_ts_runtime":
                return self._repair_ts_runtime(issue)
            elif issue.type == IssueType.CONFIG_ERROR and issue.repair_action:
                # Ask user before applying config-related fixes
                if self._confirm_repair(issue):
                    return self._repair_command(issue.repair_action)
                logger.info("[HEAL] Skipped repair at user request")
                return False
            elif issue.type == IssueType.DEPRECATED_CODE:
                # Don't auto-repair code changes (require manual review)
                logger.info(f"[HEAL] Code changes require manual review: {issue.description}")
                return False
            else:
                return False
        except Exception as e:
            logger.error(f"[HEAL] Repair failed: {e}")
            return False

    def _repair_dependency(self, issue: Issue) -> bool:
        """Install missing dependency."""
        dep = issue.details.get("dependency")
        version = issue.details.get("version")

        if not dep:
            return False

        package = f"{dep}{f'=={version}' if version else ''}"
        logger.info(f"[HEAL] Installing {package}...")

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", package],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[HEAL] Failed to install {package}: {e}")
            return False

    def _repair_port_conflict(self, issue: Issue) -> bool:
        """Kill process using conflicting port."""
        port = issue.details.get("port")
        if not port:
            return False

        try:
            # Try using port manager
            subprocess.run(
                [sys.executable, "-m", "wizard.cli_port_manager", "kill", f":{port}"],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            logger.warning(f"[HEAL] Could not kill port {port} - may require manual intervention")
            return False

    def _repair_permission(self, issue: Issue) -> bool:
        """Fix file permissions."""
        file_path = Path(issue.details.get("file", ""))
        if not file_path.exists():
            return False

        try:
            file_path.chmod(0o755)
            return True
        except Exception as e:
            logger.error(f"[HEAL] Failed to chmod {file_path}: {e}")
            return False

    def _repair_ts_runtime(self, issue: Issue) -> bool:
        """Build TypeScript runtime."""
        build_script = self.repo_root / "core" / "tools" / "build_ts_runtime.sh"

        if not build_script.exists():
            logger.error(f"[HEAL] Build script not found: {build_script}")
            return False

        spinner = Spinner("Building TypeScript runtime")
        spinner.start()

        try:
            result = subprocess.run(
                ["bash", str(build_script)],
                cwd=str(self.repo_root),
                capture_output=True,
                timeout=300,  # 5 minute timeout
                text=True
            )

            if result.returncode == 0:
                spinner.stop("✓ TypeScript runtime built successfully")
                return True
            else:
                spinner.stop(f"✗ Build failed: {result.stderr[:200]}")
                logger.error(f"[HEAL] TS runtime build failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            spinner.stop("✗ Build timeout (5 minutes)")
            logger.error("[HEAL] TS runtime build timed out")
            return False
        except Exception as e:
            spinner.stop(f"✗ Build error: {e}")
            logger.error(f"[HEAL] TS runtime build error: {e}")
            return False

    def _repair_command(self, command: str) -> bool:
        """Run a shell command for repair (e.g., pip install)."""
        spinner = Spinner("Applying fix")
        spinner.start()

        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            spinner.stop("✓ Fix applied")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[HEAL] Repair command failed: {e}")
            spinner.stop("✗ Fix failed")
            return False

    def _confirm_repair(self, issue: Issue) -> bool:
        """Prompt user before applying a repair that may change environments."""
        # Auto-repair if marked safe or if stdin is unavailable
        if issue.auto_repairable:
            logger.info(f"[HEAL] Auto-repairing safe issue: {issue.description}")
            return True

        try:
            # Check if stdin is available
            if not sys.stdin.isatty():
                logger.warning(f"[HEAL] stdin unavailable; auto-repairing: {issue.description}")
                return True

            print("\n" + "-" * 60)
            print("Self-Heal: Action Available")
            print(f"Issue: {issue.description}")
            if issue.details:
                for k, v in issue.details.items():
                    print(f"  {k}: {v}")
            print(f"Proposed fix: {issue.repair_action}")
            print("(Press 'y' to apply, 'n' to skip)")
            sys.stdout.flush()

            choice = input("Apply this fix now? [y/N]: ").strip().lower()
            decision = choice in ("y", "yes")
            logger.info(f"[HEAL] User decision: {'apply' if decision else 'skip'} repair")
            return decision
        except (EOFError, OSError, ValueError):
            # stdin not available or other I/O error; auto-repair if safe
            logger.warning(f"[HEAL] stdin error; auto-repairing if safe: {issue.description}")
            return issue.auto_repairable

    def _get_required_dependencies(self) -> Dict[str, Optional[str]]:
        """Get required dependencies for component."""
        deps = {
            "core": {
                # Core has minimal dependencies, uses standard library & pip packages
                # FastAPI/uvicorn are only needed for wizard/web components
            },
            "wizard": {
                # Wizard server requirements
                "fastapi": None,
                "uvicorn": None,
                "aiohttp": None,
            },
            "goblin": {
                # Goblin mode requirements (minimal)
            }
        }
        return deps.get(self.component, {})

    def _version_matches(self, installed: str, required: str) -> bool:
        """Check if installed version matches requirement."""
        # Simple version check (can be enhanced)
        return installed.startswith(required.split(".")[0])

    def _generate_summary(
        self, repaired: List[Issue], remaining: List[Issue]
    ) -> List[str]:
        """Generate human-readable summary."""
        messages = []

        if repaired:
            messages.append(f"✅ Repaired {len(repaired)} issue(s)")
            for issue in repaired:
                messages.append(f"  - {issue.description}")

        if remaining:
            critical = [i for i in remaining if i.severity == IssueSeverity.CRITICAL]
            warnings = [i for i in remaining if i.severity == IssueSeverity.WARNING]

            if critical:
                messages.append(f"❌ {len(critical)} critical issue(s) remaining:")
                for issue in critical:
                    messages.append(f"  - {issue.description}")

            if warnings:
                messages.append(f"⚠️  {len(warnings)} warning(s):")
                for issue in warnings:
                    messages.append(f"  - {issue.description}")

        if not repaired and not remaining:
            messages.append("✅ No issues detected - system healthy!")

        return messages


def run_self_heal(component: str, auto_repair: bool = True) -> RepairResult:
    """
    Convenience function to run self-healing check.

    Args:
        component: Component name (core, wizard, goblin, app)
        auto_repair: Whether to automatically repair issues

    Returns:
        RepairResult
    """
    healer = SelfHealer(component=component, auto_repair=auto_repair)
    return healer.diagnose_and_repair()


def summarize_self_heal_result(result: RepairResult) -> Dict[str, Any]:
    """Return a serializable summary of a RepairResult."""
    return {
        "success": result.success,
        "issues": len(result.issues_found),
        "repaired": len(result.issues_repaired),
        "remaining": len(result.issues_remaining),
        "messages": result.messages,
        "issues_found": [issue.description for issue in result.issues_found],
    }


def collect_self_heal_summary(component: str = "core", auto_repair: bool = False) -> Dict[str, Any]:
    """Run SelfHealer and return both the result and the summary."""
    result = run_self_heal(component=component, auto_repair=auto_repair)
    summary = summarize_self_heal_result(result)
    summary["component"] = component
    return summary


if __name__ == "__main__":
    import sys

    component = sys.argv[1] if len(sys.argv) > 1 else "core"
    result = run_self_heal(component)

    print("\n" + "=" * 60)
    print(f"Self-Healing Report: {component}")
    print("=" * 60)
    for msg in result.messages:
        print(msg)
    print("=" * 60)

    sys.exit(0 if result.success else 1)
