"""
Repair Service
==============

Self-heal and recovery helpers for Wizard-managed components.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tarfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from wizard.services.path_utils import get_repo_root
from wizard.services.logging_api import get_logger
from wizard.services.library_manager_service import get_library_manager
from wizard.services.system_info_service import get_system_info_service
from wizard.services.artifact_store import get_artifact_store, ArtifactEntry
from core.services.maintenance_utils import compost_stats

logger = get_logger("wizard-repair")


@dataclass
class RepairResult:
    success: bool
    action: str
    message: str = ""
    output: str = ""
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "output": self.output,
            "error": self.error,
        }


class RepairService:
    """Self-heal, backup, and restore helpers."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.artifact_store = get_artifact_store()
        self.allowed_backup_targets = {
            "wizard-config": repo_root / "wizard" / "config",
            "wizard-memory": repo_root / "memory" / "wizard",
            "memory-private": repo_root / "memory" / "private",
            "memory-binders": repo_root / "memory" / "binders",
            "library": repo_root / "library",
        }

    def _wizard_venv_path(self) -> Path:
        return self.repo_root / "wizard" / ".venv"

    def _wizard_requirements_path(self) -> Path:
        primary = self.repo_root / "wizard" / "requirements.txt"
        if primary.exists():
            return primary
        return self.repo_root / "requirements.txt"

    def status(self) -> Dict[str, Any]:
        """Return status checks for tooling and paths."""
        os_info = get_system_info_service(self.repo_root).get_os_info()

        def tool_info(name: str) -> Dict[str, Any]:
            path = shutil.which(name)
            return {"name": name, "path": path, "available": path is not None}

        def path_info(path: Path) -> Dict[str, Any]:
            return {"path": str(path), "exists": path.exists()}

        return {
            "os": {
                "platform": os_info.platform_system,
                "detected_os": os_info.detected_os,
                "is_alpine": os_info.is_alpine,
            },
            "tools": {
                "python3": tool_info("python3"),
                "pip3": tool_info("pip3"),
                "node": tool_info("node"),
                "npm": tool_info("npm"),
                "git": tool_info("git"),
                "apk": tool_info("apk"),
                "abuild": tool_info("abuild"),
            },
            "paths": {
                "repo_root": path_info(self.repo_root),
                "venv": path_info(self._wizard_venv_path()),
                "requirements": path_info(self._wizard_requirements_path()),
                "wizard_dashboard": path_info(
                    self.repo_root / "wizard" / "dashboard"
                ),
                "wizard_dashboard_node_modules": path_info(
                    self.repo_root / "wizard" / "dashboard" / "node_modules"
                ),
                "wizard_dashboard_dist": path_info(
                    self.repo_root / "wizard" / "dashboard" / "dist"
                ),
            },
            "backup_targets": {
                key: str(path) for key, path in self.allowed_backup_targets.items()
            },
            "compost": compost_stats(),
        }

    def update_alpine_toolchain(
        self, packages: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """Update Alpine toolchain via library manager."""
        return get_library_manager().update_alpine_toolchain(packages)

    def bootstrap_venv(self) -> RepairResult:
        """Create venv and install requirements if present."""
        venv_path = self._wizard_venv_path()
        requirements_path = self._wizard_requirements_path()
        python_path = shutil.which("python3")
        if not python_path:
            return RepairResult(
                success=False,
                action="bootstrap-venv",
                error="python3 not found",
            )

        outputs = []
        try:
            if not venv_path.exists():
                result = self._run_command(
                    [python_path, "-m", "venv", str(venv_path)],
                    cwd=self.repo_root,
                )
                if not result.success:
                    return result
                outputs.append(result.output)

            pip_path = venv_path / "bin" / "pip"
            if pip_path.exists():
                result = self._run_command(
                    [str(pip_path), "install", "--upgrade", "pip"],
                    cwd=self.repo_root,
                )
                if not result.success:
                    return result
                outputs.append(result.output)
                if requirements_path.exists():
                    result = self._run_command(
                        [str(pip_path), "install", "-r", str(requirements_path)],
                        cwd=self.repo_root,
                    )
                    if not result.success:
                        return result
                    outputs.append(result.output)

            return RepairResult(
                success=True,
                action="bootstrap-venv",
                message="Venv bootstrapped",
                output="\n".join(outputs).strip(),
            )
        except Exception as exc:
            return RepairResult(
                success=False,
                action="bootstrap-venv",
                error=str(exc),
            )

    def install_python_deps(self) -> RepairResult:
        """Install Python dependencies via venv if present."""
        requirements = self._wizard_requirements_path()
        if not requirements.exists():
            return RepairResult(
                success=False,
                action="install-python-deps",
                error=f"{requirements.name} not found",
            )

        pip_path = self._wizard_venv_path() / "bin" / "pip"
        pip_cmd = str(pip_path) if pip_path.exists() else shutil.which("pip3")
        if not pip_cmd:
            return RepairResult(
                success=False,
                action="install-python-deps",
                error="pip3 not found",
            )

        return self._run_command(
            [pip_cmd, "install", "-r", str(requirements)],
            cwd=self.repo_root,
            action="install-python-deps",
        )

    def install_dashboard_deps(self) -> RepairResult:
        """Install Wizard dashboard Node dependencies."""
        dashboard_root = self.repo_root / "wizard" / "dashboard"
        if not (dashboard_root / "package.json").exists():
            return RepairResult(
                success=False,
                action="install-dashboard-deps",
                error="wizard/dashboard/package.json not found",
            )

        npm_cmd = shutil.which("npm")
        if not npm_cmd:
            return RepairResult(
                success=False,
                action="install-dashboard-deps",
                error="npm not found",
            )

        return self._run_command(
            [npm_cmd, "install"],
            cwd=dashboard_root,
            action="install-dashboard-deps",
        )

    def build_dashboard(self) -> RepairResult:
        """Build Wizard dashboard assets."""
        dashboard_root = self.repo_root / "wizard" / "dashboard"
        if not (dashboard_root / "package.json").exists():
            return RepairResult(
                success=False,
                action="build-dashboard",
                error="wizard/dashboard/package.json not found",
            )

        npm_cmd = shutil.which("npm")
        if not npm_cmd:
            return RepairResult(
                success=False,
                action="build-dashboard",
                error="npm not found",
            )

        return self._run_command(
            [npm_cmd, "run", "build"],
            cwd=dashboard_root,
            action="build-dashboard",
        )

    def backup_target(self, target_key: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Create a tar.gz backup for a target path."""
        target_path = self.allowed_backup_targets.get(target_key)
        if not target_path:
            return {"success": False, "error": f"Unknown backup target: {target_key}"}

        if not target_path.exists():
            return {
                "success": False,
                "error": f"Target path does not exist: {target_path}",
            }

        temp_dir = self.repo_root / "memory" / "wizard" / "artifacts" / "tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        archive_name = f"{target_key}-{timestamp}.tar.gz"
        archive_path = temp_dir / archive_name

        try:
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(target_path, arcname=target_path.name)
            entry = self.artifact_store.add(
                archive_path,
                kind="backups",
                notes=notes or f"Backup of {target_key}",
            )
            archive_path.unlink(missing_ok=True)
            logger.info(f"[WIZ] Backup created for {target_key}: {entry.id}")
            return {"success": True, "entry": entry.to_dict()}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def restore_backup(self, artifact_id: str, target_key: str) -> Dict[str, Any]:
        """Restore a backup artifact to a target path."""
        target_path = self.allowed_backup_targets.get(target_key)
        if not target_path:
            return {"success": False, "error": f"Unknown restore target: {target_key}"}

        entry = self.artifact_store.get(artifact_id)
        if not entry:
            return {"success": False, "error": f"Backup not found: {artifact_id}"}
        if entry.kind != "backups":
            return {"success": False, "error": "Artifact is not a backup"}

        archive_path = self.artifact_store.path_for(entry)
        if not archive_path.exists():
            return {"success": False, "error": "Backup archive missing on disk"}

        try:
            self._safe_extract(archive_path, target_path.parent)
            logger.info(f"[WIZ] Restored backup {artifact_id} to {target_key}")
            return {"success": True, "restored_to": str(target_path)}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def _run_command(
        self, cmd: list[str], cwd: Path, action: str = ""
    ) -> RepairResult:
        action_name = action or "command"
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=900,
            )
            if result.returncode != 0:
                return RepairResult(
                    success=False,
                    action=action_name,
                    error=result.stderr.strip() or "Command failed",
                    output=result.stdout.strip(),
                )
            return RepairResult(
                success=True,
                action=action_name,
                message="Command completed",
                output=result.stdout.strip(),
            )
        except Exception as exc:
            return RepairResult(
                success=False,
                action=action_name,
                error=str(exc),
            )

    def _safe_extract(self, archive_path: Path, target_root: Path) -> None:
        with tarfile.open(archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                member_path = target_root / member.name
                if not str(member_path.resolve()).startswith(str(target_root.resolve())):
                    raise RuntimeError("Blocked path traversal in archive")
            tar.extractall(path=target_root)


_repair_service: Optional[RepairService] = None


def get_repair_service() -> RepairService:
    global _repair_service
    if _repair_service is None:
        _repair_service = RepairService(get_repo_root())
    return _repair_service
