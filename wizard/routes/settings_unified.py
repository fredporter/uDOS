"""
Unified Settings Route (v1.1.0)
================================

Single all-in-one settings page for:
  1. Virtual environment (.venv) management & detection
  2. Wizard API key & secret store configuration
  3. Extension & API installer integration
  4. Config auto-migration from v1.0.x formats

Replaces fragmented config management approach with
streamlined dashboard-first settings interface.
"""

import json
import os
import subprocess
import sys
import venv
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root, get_memory_dir
from wizard.services.secret_store import get_secret_store, SecretStoreError

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
    category: str  # "ai", "github", "notion", "oauth", "slack", "hubspot"
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
    """Get the .venv directory path."""
    return get_repo_root() / ".venv"


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
            "next_step": "Install dependencies: pip install -r requirements.txt"
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
        import shutil
        shutil.rmtree(str(venv_path))
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
        "notion": ["notion_api_key", "notion_workspace_id"],
        "oauth": ["oauth_client_id", "oauth_client_secret"],
        "slack": ["slack_bot_token", "slack_workspace_id"],
        "hubspot": ["hubspot_api_key"],
    }

    result = {}
    store = get_secret_store()

    for category, keys in categories.items():
        result[category] = []
        for key in keys:
            try:
                entry = store.get_entry(key)
                is_set = entry is not None
                masked_value = ("●" * 8 + entry.value[-4:]) if is_set else None

                result[category].append(SecretConfig(
                    key=key,
                    category=category,
                    is_set=is_set,
                    masked_value=masked_value,
                    updated_at=entry.metadata.get("updated_at") if is_set else None
                ))
            except SecretStoreError:
                result[category].append(SecretConfig(
                    key=key,
                    category=category,
                    is_set=False
                ))

    return result


def set_secret(key: str, value: str) -> Dict[str, Any]:
    """Set a secret/API key."""
    if not value:
        return {"error": "value required"}

    try:
        store = get_secret_store()
        store.set_entry(key, value, metadata={"updated_at": datetime.now().isoformat()})
        logger.info(f"[LOCAL] Secret updated: {key}")
        return {"status": "set", "key": key}
    except SecretStoreError as e:
        logger.error(f"[LOCAL] Failed to set secret {key}: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSION INSTALLERS
# ═══════════════════════════════════════════════════════════════════════════


def get_available_extensions() -> List[ExtensionInstaller]:
    """Get list of available extensions for installation."""
    # TODO: Load from distribution/plugins/index.json
    extensions = [
        ExtensionInstaller(
            name="github-cli",
            version="1.0.0",
            description="CLI-focused GitHub integration for sync, monitoring, and webhooks",
            required_secrets=["github_token"]
        ),
        ExtensionInstaller(
            name="mistral-vibe",
            version="2.0.0",
            description="Mistral AI local inference with voice interaction",
            required_secrets=["mistral_api_key"]
        ),
        ExtensionInstaller(
            name="mesh-core",
            version="1.5.0",
            description="Local mesh networking for device-to-device communication",
            required_secrets=[]
        ),
    ]
    return extensions


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
        "notion_keys.json": ("notion", ["notion_api_key", "notion_workspace_id"]),
        "oauth.json": ("oauth", ["oauth_client_id", "oauth_client_secret"]),
        "slack_keys.json": ("slack", ["slack_bot_token", "slack_workspace_id"]),
        "hubspot_keys.json": ("hubspot", ["hubspot_api_key"]),
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
        """Get .venv status."""
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
