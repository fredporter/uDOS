"""
Unified Settings Route (v1.1.0)
================================

Single all-in-one settings page for:
  1. Virtual environment (venv) management & detection
  2. Wizard API key & secret store configuration
  3. Extension & API installer integration
  4. Config auto-migration from v1.0.x formats

Replaces fragmented config management approach with
streamlined dashboard-first settings interface.
"""

import json
import os
import secrets
import subprocess
import sys
import venv
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root, get_memory_dir, get_wizard_venv_dir
from wizard.services.wizard_config import load_wizard_config_data, save_wizard_config_data
from core.services.integration_registry import get_wizard_secret_sync_map
from core.services.destructive_ops import remove_path
from wizard.services.secret_store import get_secret_store, SecretStoreError, SecretEntry

logger = get_logger("settings-unified")


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════


class VenvStatus(BaseModel):
    """Virtual environment status."""
    exists: bool
    path: str
    python_version: Optional[str] = None
    is_active: bool = False
    packages_installed: int = 0
    last_checked: str = None


class SecretConfig(BaseModel):
    """Secret/API key configuration."""
    key: str
    category: str  # "ai", "github", "oauth"
    masked_value: Optional[str] = None
    is_set: bool = False
    updated_at: Optional[str] = None


class ExtensionInstaller(BaseModel):
    """Extension installer status and configuration."""
    name: str
    version: str
    description: str
    enabled: bool = False
    required_secrets: List[str] = []
    installation_status: str  # "not-installed", "installing", "installed", "failed"
    installed_version: Optional[str] = None
    error_message: Optional[str] = None


class UnifiedSettings(BaseModel):
    """All-in-one settings object."""
    venv: VenvStatus
    secrets: Dict[str, List[SecretConfig]]
    extensions: List[ExtensionInstaller]
    config_version: str = "v1.1.0"
    wizard_settings: Dict[str, Any] = {}


# ═══════════════════════════════════════════════════════════════════════════
# VENV MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


def get_venv_path() -> Path:
    """Get the configured venv directory path."""
    return get_wizard_venv_dir()


def get_venv_status() -> VenvStatus:
    """Get current virtual environment status."""
    venv_path = get_venv_path()
    python_exec = venv_path / "bin" / "python"

    status = VenvStatus(
        exists=venv_path.exists(),
        path=str(venv_path),
        is_active=hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        ),
        last_checked=datetime.now().isoformat()
    )

    if status.exists and python_exec.exists():
        try:
            result = subprocess.run(
                [str(python_exec), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            status.python_version = result.stdout.strip()

            # Count installed packages
            result = subprocess.run(
                [str(python_exec), "-m", "pip", "list", "--quiet"],
                capture_output=True,
                text=True,
                timeout=10
            )
            status.packages_installed = len(result.stdout.strip().split('\n'))
        except Exception as e:
            logger.warning(f"[LOCAL] Failed to detect venv details: {e}")

    return status


def create_venv() -> Dict[str, Any]:
    """Create a new virtual environment."""
    venv_path = get_venv_path()

    if venv_path.exists():
        return {"error": "venv already exists", "path": str(venv_path)}

    try:
        logger.info(f"[LOCAL] Creating .venv at {venv_path}")
        venv.create(str(venv_path), with_pip=True, clear=False)

        status = get_venv_status()
        return {
            "status": "created",
            "venv": status.model_dump(),
            "next_step": "Install dependencies: pip install -r wizard/requirements.txt"
        }
    except Exception as e:
        logger.error(f"[LOCAL] Failed to create venv: {e}")
        return {"error": str(e)}


def delete_venv() -> Dict[str, Any]:
    """Delete the virtual environment."""
    venv_path = get_venv_path()

    if not venv_path.exists():
        return {"error": "venv does not exist"}

    try:
        logger.info(f"[LOCAL] Deleting .venv at {venv_path}")
        remove_path(venv_path)
        return {"status": "deleted"}
    except Exception as e:
        logger.error(f"[LOCAL] Failed to delete venv: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# SECRET/API KEY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


def get_secrets_config() -> Dict[str, List[SecretConfig]]:
    """Get all configured secrets organized by category."""
    categories = {
        "ai": ["mistral_api_key", "openrouter_api_key", "ollama_api_key"],
        "github": ["github_token", "github_webhook_secret"],
        "oauth": ["oauth_client_id", "oauth_client_secret"],
        "integrations": ["nounproject_api_key", "nounproject_api_secret"],
    }

    def _load_config_file(filename: str) -> Dict[str, Any]:
        repo_root = get_repo_root()
        config_path = repo_root / "wizard" / "config" / filename
        if not config_path.exists():
            return {}
        try:
            return json.loads(config_path.read_text())
        except Exception:
            return {}

    def _get_nested(data: Dict[str, Any], path: List[str]) -> Optional[Any]:
        current: Any = data
        for part in path:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    legacy_config = {
        "assistant": _load_config_file("assistant_keys.json"),
        "github": _load_config_file("github_keys.json"),
        "oauth": _load_config_file("oauth_providers.json"),
    }

    legacy_values: Dict[str, Any] = {
        "mistral_api_key": (
            _get_nested(legacy_config["assistant"], ["providers", "mistral", "key_id"])
            or legacy_config["assistant"].get("MISTRAL_API_KEY")
        ),
        "openrouter_api_key": (
            _get_nested(legacy_config["assistant"], ["providers", "openrouter", "key_id"])
            or legacy_config["assistant"].get("OPENROUTER_API_KEY")
        ),
        "ollama_api_key": (
            _get_nested(legacy_config["assistant"], ["providers", "ollama", "key_id"])
            or legacy_config["assistant"].get("OLLAMA_API_KEY")
        ),
        "github_token": (
            legacy_config["github"].get("token")
            or _get_nested(legacy_config["github"], ["tokens", "default", "key_id"])
            or _get_nested(legacy_config["github"], ["tokens", "default", "token"])
        ),
        "github_webhook_secret": (
            _get_nested(legacy_config["github"], ["webhooks", "secret_key_id"])
            or _get_nested(legacy_config["github"], ["webhooks", "secret"])
        ),
    }
    legacy_values["nounproject_api_key"] = os.getenv("NOUNPROJECT_API_KEY") or None
    legacy_values["nounproject_api_secret"] = os.getenv("NOUNPROJECT_API_SECRET") or None

    oauth_client_id = None
    oauth_client_secret = None
    if isinstance(legacy_config["oauth"], dict):
        for provider in legacy_config["oauth"].values():
            if not isinstance(provider, dict):
                continue
            oauth_client_id = oauth_client_id or provider.get("client_id")
            oauth_client_secret = oauth_client_secret or provider.get("client_secret")
    legacy_values["oauth_client_id"] = oauth_client_id
    legacy_values["oauth_client_secret"] = oauth_client_secret

    result = {}
    store = get_secret_store()

    try:
        store.unlock()
    except SecretStoreError:
        pass

    for category, keys in categories.items():
        result[category] = []
        for key in keys:
            try:
                entry = store.get_entry(key)
                is_set = entry is not None
                masked_value = ("●" * 8 + entry.value[-4:]) if is_set else None
                if not is_set:
                    legacy_value = legacy_values.get(key)
                    if legacy_value:
                        is_set = True
                        masked_value = "●" * 8 + str(legacy_value)[-4:]

                result[category].append(SecretConfig(
                    key=key,
                    category=category,
                    is_set=is_set,
                    masked_value=masked_value,
                    updated_at=entry.metadata.get("updated_at") if entry else None,
                ))
            except SecretStoreError:
                legacy_value = legacy_values.get(key)
                result[category].append(SecretConfig(
                    key=key,
                    category=category,
                    is_set=bool(legacy_value),
                    masked_value=("●" * 8 + str(legacy_value)[-4:]) if legacy_value else None,
                ))

    return result


def _write_env_var(env_path: Path, key: str, value: str) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if env_path.exists():
        lines = env_path.read_text().splitlines()
    updated = False
    new_lines = []
    for line in lines:
        if not line or line.strip().startswith("#") or "=" not in line:
            new_lines.append(line)
            continue
        k, _ = line.split("=", 1)
        if k.strip() == key:
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key}={value}")
    env_path.write_text("\n".join(new_lines) + "\n")


def _get_admin_key_id() -> str:
    repo_root = get_repo_root()
    wizard_config_path = repo_root / "wizard" / "config" / "wizard.json"
    if wizard_config_path.exists():
        try:
            config = json.loads(wizard_config_path.read_text())
            key_id = config.get("admin_api_key_id")
            if key_id:
                return key_id
        except Exception:
            pass
    return "wizard-admin-token"


def repair_secret_store() -> Dict[str, Any]:
    """Flush secret store tomb and regenerate Wizard keys."""
    repo_root = get_repo_root()
    env_path = repo_root / ".env"
    tomb_path = repo_root / "wizard" / "secrets.tomb"
    key_path = repo_root / "memory" / "bank" / "private" / "wizard_secret_store.key"
    key_path.parent.mkdir(parents=True, exist_ok=True)

    new_key = secrets.token_urlsafe(48)
    new_admin_token = secrets.token_urlsafe(48)

    # Update env and process
    _write_env_var(env_path, "WIZARD_KEY", new_key)
    _write_env_var(env_path, "WIZARD_ADMIN_TOKEN", new_admin_token)
    os.environ["WIZARD_KEY"] = new_key
    os.environ["WIZARD_ADMIN_TOKEN"] = new_admin_token

    # Persist key file for fallback unlock
    key_path.write_text(new_key)
    try:
        os.chmod(key_path, 0o600)
    except Exception:
        pass

    # Remove old tomb to flush secrets
    remove_path(tomb_path)

    # Reset secret store singleton
    if hasattr(get_secret_store, "_instance"):
        delattr(get_secret_store, "_instance")

    # Create fresh tomb with new admin token
    store = get_secret_store()
    store.unlock(new_key)
    entry = SecretEntry(
        key_id=_get_admin_key_id(),
        provider="wizard-admin",
        value=new_admin_token,
        created_at=datetime.utcnow().isoformat(),
        metadata={"source": "wizard-repair"},
    )
    store.set(entry)

    return {
        "status": "repaired",
        "admin_token": new_admin_token,
        "tomb_path": str(tomb_path),
        "key_path": str(key_path),
    }


def set_secret(key: str, value: str) -> Dict[str, Any]:
    """Set a secret/API key."""
    if not value:
        return {"error": "value required"}

    try:
        store = get_secret_store()
        try:
            store.unlock()
        except SecretStoreError as e:
            logger.error(f"[LOCAL] Failed to unlock secret store: {e}")
            return {"error": f"Secret store is locked: {str(e)}"}
        store.set_entry(key, value, metadata={"updated_at": datetime.now().isoformat()})
        # Persist env-only secrets when applicable
        if key in {"nounproject_api_key", "nounproject_api_secret"}:
            repo_root = get_repo_root()
            env_path = repo_root / ".env"
            env_key = (
                "NOUNPROJECT_API_KEY"
                if key == "nounproject_api_key"
                else "NOUNPROJECT_API_SECRET"
            )
            _write_env_var(env_path, env_key, value)
            os.environ[env_key] = value
        wizard_update = _sync_wizard_config_from_secret(key)
        logger.info(f"[LOCAL] Secret updated: {key}")
        return {"status": "set", "key": key, **wizard_update}
    except SecretStoreError as e:
        logger.error(f"[LOCAL] Failed to set secret {key}: {e}")
        return {"error": str(e)}


def _load_wizard_config() -> Dict[str, Any]:
    repo_root = get_repo_root()
    return load_wizard_config_data(path=repo_root / "wizard" / "config" / "wizard.json")


def _save_wizard_config(config: Dict[str, Any]) -> None:
    repo_root = get_repo_root()
    save_wizard_config_data(config, path=repo_root / "wizard" / "config" / "wizard.json")


def _enable_provider(config: Dict[str, Any], provider_id: str) -> None:
    enabled = config.get("enabled_providers") or []
    if provider_id not in enabled:
        enabled.append(provider_id)
    config["enabled_providers"] = enabled


def _sync_wizard_config_from_secret(key: str) -> Dict[str, Any]:
    mapping = get_wizard_secret_sync_map()

    if key not in mapping:
        return {"wizard_config_updated": False}

    config = _load_wizard_config()
    data = mapping[key]
    for provider_id in data.get("providers", []):
        _enable_provider(config, provider_id)
    for toggle in data.get("toggles", []):
        config[toggle] = True

    _save_wizard_config(config)
    return {
        "wizard_config_updated": True,
        "enabled_providers": config.get("enabled_providers", []),
    }


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSION INSTALLERS
# ═══════════════════════════════════════════════════════════════════════════


def get_available_extensions() -> List[ExtensionInstaller]:
    """Get list of available extensions from distribution/plugins/index.json."""
    repo_root = get_repo_root()
    index_path = repo_root / "distribution" / "plugins" / "index.json"

    if not index_path.exists():
        logger.warning("Plugin index not found: %s", index_path)
        return []

    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        plugins = data.get("plugins", {})
        extensions = []

        for plugin_id, plugin_data in plugins.items():
            extensions.append(ExtensionInstaller(
                name=plugin_data.get("id", plugin_id),
                version=plugin_data.get("version", "0.0.0"),
                description=plugin_data.get("description", ""),
                enabled=plugin_data.get("installed", False),
                required_secrets=plugin_data.get("dependencies", []),
                installation_status="installed" if plugin_data.get("installed") else "not-installed",
                installed_version=plugin_data.get("installed_version"),
                error_message=None,
            ))

        return extensions
    except Exception as exc:
        logger.error("Failed to load plugin index: %s", exc)
        return []


# ═══════════════════════════════════════════════════════════════════════════
# CONFIG AUTO-MIGRATION (v1.0.x → v1.1.0)
# ═══════════════════════════════════════════════════════════════════════════


def migrate_config_from_v1_0() -> Dict[str, Any]:
    """
    Auto-migrate config from v1.0.x fragmented format to v1.1.0 unified format.

    v1.0.x: 7 separate config files (assistant_keys.json, github_keys.json, etc.)
    v1.1.0: Unified secret store + single settings page
    """
    repo_root = get_repo_root()
    config_dir = repo_root / "wizard" / "config"
    migration_log = {
        "from_version": "1.0.x",
        "to_version": "1.1.0",
        "migrated_files": [],
        "skipped_files": [],
        "errors": []
    }

    # Map old config files to secret categories
    config_mapping = {
        "assistant_keys.json": ("ai", ["mistral_api_key", "openrouter_api_key"]),
        "github_keys.json": ("github", ["github_token", "github_webhook_secret"]),
        "oauth.json": ("oauth", ["oauth_client_id", "oauth_client_secret"]),
    }

    store = get_secret_store()

    for old_file, (category, keys) in config_mapping.items():
        file_path = config_dir / old_file
        if not file_path.exists():
            migration_log["skipped_files"].append(old_file)
            continue

        try:
            data = json.loads(file_path.read_text())
            for key in keys:
                if key in data and data[key]:
                    store.set_entry(
                        key,
                        data[key],
                        metadata={"migrated_from": old_file, "migrated_at": datetime.now().isoformat()}
                    )

            migration_log["migrated_files"].append(old_file)
            logger.info(f"[LOCAL] Migrated {old_file} to secret store")
        except Exception as e:
            migration_log["errors"].append({"file": old_file, "error": str(e)})
            logger.error(f"[LOCAL] Migration failed for {old_file}: {e}")

    return migration_log


# ═══════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════


def create_settings_unified_router(auth_guard=None):
    """Create unified settings API router."""
    router = APIRouter(prefix="/api/settings-unified", tags=["Settings (Unified v1.1.0)"])

    async def check_auth(request):
        """Verify authentication if guard is provided."""
        if auth_guard and callable(auth_guard):
            return await auth_guard(request)
        return True

    @router.get("/status")
    async def get_settings_status(request: Request = None):
        """Get complete unified settings status."""
        await check_auth(request)
        return {
            "venv": get_venv_status().model_dump(),
            "secrets": get_secrets_config(),
            "extensions": [ext.model_dump() for ext in get_available_extensions()],
            "timestamp": datetime.now().isoformat()
        }

    # VENV MANAGEMENT
    @router.get("/venv/status")
    async def venv_status(request: Request = None):
        """Get venv status."""
        await check_auth(request)
        return get_venv_status().model_dump()

    @router.post("/venv/create")
    async def venv_create(request: Request = None):
        """Create new virtual environment."""
        await check_auth(request)
        return create_venv()

    @router.post("/venv/delete")
    async def venv_delete(request: Request = None):
        """Delete virtual environment."""
        await check_auth(request)
        return delete_venv()

    # SECRET/API KEY MANAGEMENT
    @router.get("/secrets")
    async def get_secrets(request: Request = None):
        """Get all configured secrets (masked values only)."""
        await check_auth(request)
        return get_secrets_config()

    @router.get("/secrets/status")
    async def secrets_status(request: Request = None):
        """Check whether secret store is unlocked."""
        await check_auth(request)
        store = get_secret_store()
        try:
            store.unlock()
            return {"locked": False, "status": "unlocked"}
        except SecretStoreError as exc:
            logger.warning(f"[WIZ] Secret store unlock failed: {exc}")
            return {"locked": True, "error": str(exc), "can_repair": True}

    @router.post("/secrets/repair")
    async def secrets_repair(request: Request = None):
        """Repair secret store by flushing tomb and regenerating keys."""
        await check_auth(request)
        return repair_secret_store()

    @router.post("/secrets/{key}")
    async def set_secret_endpoint(key: str, value: str, request: Request = None):
        """Set a secret/API key."""
        await check_auth(request)
        return set_secret(key, value)

    # EXTENSIONS
    @router.get("/extensions")
    async def list_extensions(request: Request = None):
        """List available extensions for installation."""
        await check_auth(request)
        return [ext.model_dump() for ext in get_available_extensions()]

    # MIGRATION
    @router.post("/migrate-from-v1.0")
    async def migrate_config(request: Request = None):
        """Migrate config from v1.0.x to v1.1.0 format."""
        await check_auth(request)
        return migrate_config_from_v1_0()

    return router
