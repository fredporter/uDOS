"""REPAIR command handler - Self-healing and system maintenance."""

from typing import List, Dict
from pathlib import Path
import subprocess
from core.commands.base import BaseCommandHandler


class RepairHandler(BaseCommandHandler):
    """Handler for REPAIR command - self-healing and system maintenance."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle REPAIR command - perform system maintenance.

        Args:
            command: Command name (REPAIR)
            params: [--pull|--install|--check|--upgrade] (default: --check)
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with repair status
        """
        if not params:
            params = ["--check"]

        action = params[0].lower()

        if action == "--pull":
            return self._git_pull()
        elif action == "--install":
            return self._install_dependencies()
        elif action == "--check":
            return self._check_system()
        elif action == "--upgrade":
            return self._upgrade_all()
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}",
                "available": ["--pull", "--install", "--check", "--upgrade"],
            }

    def _git_pull(self) -> Dict:
        """Pull latest changes from git repository."""
        try:
            repo_path = Path("/Users/fredbook/Code/uDOS")

            # Check if it's a git repo
            git_dir = repo_path / ".git"
            if not git_dir.exists():
                return {"status": "error", "message": "Not a git repository"}

            # Run git pull
            result = subprocess.run(
                ["git", "pull"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "✅ Repository synchronized",
                    "output": result.stdout or "Already up to date",
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Git pull failed",
                    "error": result.stderr,
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to pull repository: {str(e)}",
            }

    def _install_dependencies(self) -> Dict:
        """Install/verify Python dependencies."""
        try:
            repo_path = Path("/Users/fredbook/Code/uDOS")
            requirements = repo_path / "requirements.txt"

            if not requirements.exists():
                return {"status": "error", "message": "requirements.txt not found"}

            # Run pip install
            result = subprocess.run(
                ["pip", "install", "-r", str(requirements)],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "✅ Dependencies installed/verified",
                    "note": "Run this if you see import errors",
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Dependency installation failed",
                    "error": result.stderr[-200:],  # Last 200 chars
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Installation timed out (taking >2 minutes)",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to install dependencies: {str(e)}",
            }

    def _check_system(self) -> Dict:
        """Check system health status."""
        checks = {
            "python_version": None,
            "venv_active": None,
            "git_repo": None,
            "core_files": None,
        }

        # Check Python
        try:
            result = subprocess.run(
                ["python", "--version"], capture_output=True, text=True, timeout=5
            )
            checks["python_version"] = result.stdout.strip()
        except Exception as e:
            checks["python_version"] = f"Error: {str(e)}"

        # Check venv
        venv_path = Path("/Users/fredbook/Code/uDOS/.venv")
        checks["venv_active"] = "✅ Found" if venv_path.exists() else "❌ Not found"

        # Check git
        git_dir = Path("/Users/fredbook/Code/uDOS/.git")
        checks["git_repo"] = "✅ Git repo" if git_dir.exists() else "❌ Not a git repo"

        # Check core files
        core_dir = Path("/Users/fredbook/Code/uDOS/core")
        checks["core_files"] = (
            f"✅ {len(list(core_dir.glob('**/*.py')))} Python files"
            if core_dir.exists()
            else "❌ core/ not found"
        )

        return {
            "status": "success",
            "message": "System check complete",
            "checks": checks,
        }

    def _upgrade_all(self) -> Dict:
        """Upgrade all components (git pull + dependencies)."""
        results = {"status": "success", "steps": {}}

        # Step 1: Git pull
        pull_result = self._git_pull()
        results["steps"]["git_pull"] = pull_result

        # Step 2: Install dependencies
        install_result = self._install_dependencies()
        results["steps"]["install_dependencies"] = install_result

        # Overall status
        if pull_result["status"] != "success" or install_result["status"] != "success":
            results["status"] = "partial"
            results["message"] = "⚠️  Some steps had issues"
        else:
            results["message"] = "✅ System upgraded successfully"

        return results
