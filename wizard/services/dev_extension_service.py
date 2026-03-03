"""Dev Mode extension policy and GitHub integration service.

Wizard owns the runtime logic. The /dev workspace only carries the Dev Mode
framework, governance files, and templates that gate contributor features.
"""

from __future__ import annotations

import os
import secrets
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

from core.services.permission_handler import Permission
from core.services.release_profile_service import get_release_profile_service
from core.services.user_service import get_user_manager
from wizard.services.dev_mode_service import get_dev_mode_service
from wizard.services.logging_api import get_logger
from wizard.services.wizard_config import WizardConfig, resolve_wizard_config_path
from wizard.tools.github_dev import PluginFactory


class DevExtensionService:
    """Single service boundary for the permissioned Dev Mode extension."""

    REQUIRED_FILES: tuple[str, ...] = (
        "README.md",
        "AGENTS.md",
        "DEVLOG.md",
        "project.json",
        "tasks.md",
        "completed.json",
        "extension.json",
        "docs/README.md",
        "docs/DEV-MODE-POLICY.md",
        "docs/specs/DEV-WORKSPACE-SPEC.md",
        "docs/howto/GETTING-STARTED.md",
        "docs/howto/VIBE-Setup-Guide.md",
        "docs/features/GITHUB-INTEGRATION.md",
        "goblin/README.md",
    )
    LOCAL_ONLY_DIRS: tuple[str, ...] = ("files", "relecs", "dev-work", "testing")

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self.logger = get_logger("dev-extension-service")
        self.profile_service = get_release_profile_service()
        self.dev_mode_service = get_dev_mode_service()

    @property
    def dev_root(self) -> Path:
        return self.repo_root / "dev"

    @property
    def extension_manifest_path(self) -> Path:
        return self.dev_root / "extension.json"

    @property
    def wizard_config_path(self) -> Path:
        return resolve_wizard_config_path()

    def _wizard_config(self) -> WizardConfig:
        return WizardConfig.load(self.wizard_config_path)

    def _profile_enabled(self) -> bool:
        profile = self.profile_service.get_profile("dev")
        return bool(profile and profile.get("enabled"))

    def _permission_status(self) -> dict[str, bool]:
        manager = get_user_manager()
        return {
            "admin": manager.has_permission(Permission.ADMIN),
            "dev_mode": manager.has_permission(Permission.DEV_MODE),
        }

    def framework_status(self) -> dict[str, Any]:
        missing_files = [
            relative_path
            for relative_path in self.REQUIRED_FILES
            if not (self.dev_root / relative_path).exists()
        ]
        ignored = {
            name: {
                "path": str(self.dev_root / name),
                "present": (self.dev_root / name).exists(),
            }
            for name in self.LOCAL_ONLY_DIRS
        }
        manifest = self._read_extension_manifest()
        return {
            "workspace_alias": "@dev",
            "dev_root": str(self.dev_root),
            "dev_root_present": self.dev_root.exists(),
            "framework_manifest_path": str(self.extension_manifest_path),
            "framework_manifest_present": self.extension_manifest_path.exists(),
            "framework_manifest": manifest,
            "required_files": list(self.REQUIRED_FILES),
            "missing_files": missing_files,
            "framework_ready": self.dev_root.exists() and not missing_files,
            "local_only_dirs": ignored,
            "tracked_sync_paths": ["docs", "goblin"],
            "remote_framework_only": True,
        }

    def _read_extension_manifest(self) -> dict[str, Any]:
        if not self.extension_manifest_path.exists():
            return {}
        try:
            import json

            payload = json.loads(self.extension_manifest_path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def ensure_framework(self) -> Optional[str]:
        if not self.dev_root.exists():
            return "Dev extension workspace missing at /dev (`@dev`)."
        status = self.framework_status()
        if not status["framework_manifest_present"]:
            return "Dev extension manifest missing (/dev/extension.json)."
        if status["missing_files"]:
            joined = ", ".join(status["missing_files"])
            return f"Dev extension workspace missing required framework files: {joined}."
        return None

    def ensure_access(self, *, require_active: bool = True) -> Optional[str]:
        if not self._profile_enabled():
            return "Dev certified profile is not enabled."
        perms = self._permission_status()
        if not perms["admin"] or not perms["dev_mode"]:
            return "Admin and Dev Mode permissions are required."
        framework_error = self.ensure_framework()
        if framework_error:
            return framework_error
        if require_active:
            active_error = self.dev_mode_service.ensure_active()
            if active_error:
                return active_error
        return None

    def status(self) -> dict[str, Any]:
        config = self._wizard_config()
        return {
            "workspace_alias": "@dev",
            "profile_enabled": self._profile_enabled(),
            "permissions": self._permission_status(),
            "framework": self.framework_status(),
            "active": self.dev_mode_service.active,
            "github": {
                "allowed_repo": config.github_allowed_repo,
                "default_branch": config.github_default_branch,
                "push_enabled": config.github_push_enabled,
                "gh_available": shutil.which("gh") is not None,
            },
        }

    def github_status(self) -> dict[str, Any]:
        config = self._wizard_config()
        pat = self.get_pat_status()
        webhook = self.get_webhook_secret_status()
        gh_ready = shutil.which("gh") is not None
        gh_auth = self._gh_auth_status() if gh_ready else {"available": False, "authenticated": False, "detail": "gh CLI not found"}
        return {
            "workspace_alias": "@dev",
            "profile_enabled": self._profile_enabled(),
            "permissions": self._permission_status(),
            "active": self.dev_mode_service.active,
            "allowed_repo": config.github_allowed_repo,
            "default_branch": config.github_default_branch,
            "push_enabled": config.github_push_enabled,
            "pat": pat,
            "webhook": webhook,
            "gh_cli": gh_auth,
        }

    def _gh_auth_status(self) -> dict[str, Any]:
        proc = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {
            "available": True,
            "authenticated": proc.returncode == 0,
            "detail": (proc.stderr or proc.stdout or "").strip()[:1000],
        }

    def get_pat_status(self) -> dict[str, Any]:
        from wizard.services.secret_store import get_secret

        token = get_secret("github_token")
        configured = bool(token and len(token) > 10)
        masked = f"{token[:4]}...{token[-4:]}" if configured and len(token) > 8 else None
        return {"configured": configured, "masked": masked}

    def set_pat(self, token: str) -> dict[str, Any]:
        from wizard.services.secret_store import set_secret

        set_secret("github_token", token)
        return {"success": True, "message": "GitHub token saved"}

    def clear_pat(self) -> dict[str, Any]:
        from wizard.services.secret_store import set_secret

        set_secret("github_token", "")
        return {"success": True, "message": "GitHub token cleared"}

    def get_webhook_secret_status(self) -> dict[str, Any]:
        from wizard.services.secret_store import get_secret

        secret_value = get_secret("github_webhook_secret")
        return {"configured": bool(secret_value and len(secret_value) > 8)}

    def set_webhook_secret(self) -> dict[str, Any]:
        from wizard.services.secret_store import set_secret

        new_secret = secrets.token_hex(32)
        set_secret("github_webhook_secret", new_secret)
        return {
            "success": True,
            "secret": new_secret,
            "message": "Webhook secret generated and saved",
        }

    def _check_allowlist(self, repo: str) -> None:
        allowlist = os.environ.get("WIZARD_LIBRARY_REPO_ALLOWLIST", "").strip()
        if not allowlist:
            return
        allowed = [item.strip() for item in allowlist.split(",") if item.strip()]
        if any(
            repo == entry or repo.startswith(entry.rstrip("*")) or repo == entry.rstrip("*")
            for entry in allowed
        ):
            return
        raise PermissionError("Repo not allowed")

    def _factory(self) -> PluginFactory:
        return PluginFactory()

    def list_repos(self) -> list[dict[str, Any]]:
        access_error = self.ensure_access(require_active=True)
        if access_error:
            raise PermissionError(access_error)
        return self._factory().list_repos()

    def clone_repo(self, repo: str, branch: str = "main") -> dict[str, Any]:
        access_error = self.ensure_access(require_active=True)
        if access_error:
            raise PermissionError(access_error)
        self._check_allowlist(repo)
        cloned = self._factory().clone(repo, branch=branch)
        if not cloned:
            raise RuntimeError("Clone failed")
        return cloned.to_dict()

    def update_repo(self, name: str) -> dict[str, Any]:
        access_error = self.ensure_access(require_active=True)
        if access_error:
            raise PermissionError(access_error)
        ok = self._factory().update(name)
        if not ok:
            raise RuntimeError("Update failed")
        return {"success": True, "name": name}

    def delete_repo(self, name: str, remove_packages: bool = False) -> dict[str, Any]:
        access_error = self.ensure_access(require_active=True)
        if access_error:
            raise PermissionError(access_error)
        ok = self._factory().remove(name, remove_packages=remove_packages)
        if not ok:
            raise RuntimeError("Delete failed")
        return {"success": True, "name": name, "remove_packages": remove_packages}

    def build_repo(self, name: str, format: str = "tar.gz") -> dict[str, Any]:
        access_error = self.ensure_access(require_active=True)
        if access_error:
            raise PermissionError(access_error)
        result = self._factory().build(name, format=format)
        return {"success": result.success, "result": result.to_dict()}

    def list_packages(self) -> list[dict[str, Any]]:
        access_error = self.ensure_access(require_active=True)
        if access_error:
            raise PermissionError(access_error)
        return self._factory().list_packages()


_dev_extension_service: DevExtensionService | None = None


def get_dev_extension_service() -> DevExtensionService:
    global _dev_extension_service
    if _dev_extension_service is None:
        _dev_extension_service = DevExtensionService()
    return _dev_extension_service
