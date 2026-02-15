"""
Configuration Management Routes
================================

Handle reading/writing configuration files locally.
Private configs (API keys, secrets) are only accessible on local machine.
Public repo contains templates only.

SSH Keys:
  - Managed separately from API keys
  - Stored in ~/.ssh/ (system standard location)
  - API provides status/verification, not key management
  - User runs setup script to generate keys
"""

import json
import os
import secrets
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from pydantic import BaseModel
from wizard.services.secret_store import (
    get_secret_store,
    SecretStoreError,
)
from wizard.routes.config_ssh_routes import create_config_ssh_routes
from wizard.routes.config_routes_helpers import ConfigRouteHelpers


def create_config_routes(auth_guard=None):
    """Create configuration management routes."""
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/config", tags=["config"], dependencies=dependencies
    )

    CONFIG_PATH = Path(__file__).parent.parent / "config"
    helpers = ConfigRouteHelpers(CONFIG_PATH)

    class _ConfigUpdate(BaseModel):
        updates: Dict[str, Any]

    @router.get("")
    async def get_wizard_config():
        """Return Wizard config as a simplified API (phase 1)."""
        return {
            "status": "ok",
            "config": helpers.load_wizard_config(),
        }

    @router.patch("")
    async def patch_wizard_config(payload: _ConfigUpdate):
        """Patch Wizard config (phase 1)."""
        current = helpers.load_wizard_config()
        updates = payload.updates or {}
        current.update(updates)
        helpers.save_wizard_config(current)
        return {
            "status": "ok",
            "config": current,
        }

    @router.get("/files")
    async def get_config_files():
        """List available config files with their status."""
        return {"files": helpers.list_config_files()}

    # ─────────────────────────────────────────────────────────────
    # Export/Import Routes (must come before /{file_id} to avoid conflicts)
    # ─────────────────────────────────────────────────────────────

    @router.post("/export")
    async def export_configs(body: Dict[str, Any]):
        """Export selected configs to a transferable file.

        Allows backing up or transferring settings to another device.

        Request body:
            {
                "file_ids": ["wizard", "github_keys", ...],  # Configs to export
                "include_secrets": false  # Whether to include API keys
            }

        Returns:
            {
                "success": true,
                "filename": "udos-config-export-2026-01-24T15-30-45Z.json",
                "path": "/path/to/file",
                "size": 1234,
                "timestamp": "2026-01-24T15:30:45Z",
                "exported_configs": ["wizard", "github_keys"],
                "warning": "⚠️ This file contains secrets. Keep it secure!"
            }
        """
        try:
            return helpers.export_configs(body)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to export configs: {str(e)}"
            )

    # Note: GET /export/list and /export/{filename} are handled by
    # wizard.routes.config_admin_routes.create_public_export_routes().
    # for local-only access without auth

    @router.get("/{file_id}")
    async def get_config(file_id: str):
        """Get configuration file content.

        Only works for actual config files (not examples).
        """
        return helpers.load_config_payload(file_id)

    @router.post("/{file_id}")
    async def save_config(file_id: str, body: Dict[str, Any]):
        """Save configuration file.

        Creates or updates the actual config file (not examples).
        Private files are never distributed in public repo.
        """
        try:
            return helpers.save_config_payload(file_id, body)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save config: {str(e)}"
            )

    @router.post("/{file_id}/reset")
    async def reset_config(file_id: str):
        """Reset config file to example/template version."""
        try:
            return helpers.reset_config(file_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to reset config: {str(e)}"
            )

    @router.get("/{file_id}/example")
    async def get_example_config(file_id: str):
        """Get example/template version of config file."""
        return helpers.get_example_or_template(file_id)

    # SSH routes are now modularized in wizard.routes.config_ssh_routes.
    router.include_router(create_config_ssh_routes())

    @router.post("/import")
    async def import_configs(file: UploadFile = File(...)):
        """Import configs from an export file.

        Validates and imports settings from a previously exported file.
        Does NOT automatically overwrite existing configs - returns what would be imported.

        Returns:
            {
                "success": true,
                "preview": {
                    "wizard": {...},
                    "github_keys": {...}
                },
                "conflicts": ["wizard"],  # Configs that would overwrite
                "timestamp": "2026-01-24T15:30:45Z"
            }
        """
        try:
            # Read upload file
            content = await file.read()
            import_data = json.loads(content.decode("utf-8"))
            return helpers.preview_import(import_data)

        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in upload file")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to read import file: {str(e)}"
            )

    @router.post("/import/apply")
    async def apply_import(body: Dict[str, Any]):
        """Apply previously validated import.

        Request body:
            {
                "file_ids": ["wizard", "github_keys", ...],
                "overwrite_conflicts": false
            }

        This is a two-step process to prevent accidental overwrites:
        1. POST /api/config/import (validate)
        2. POST /api/config/import/apply (confirm)
        """
        raise HTTPException(
            status_code=501,
            detail="Import apply requires upload file context. Use chunked import instead.",
        )

    @router.post("/import/chunked")
    async def import_configs_chunked(
        file: UploadFile = File(...), body: Dict[str, Any] = None
    ):
        """Import and apply configs from export file in one operation.

        Query params/body:
            overwrite_conflicts: bool - Whether to overwrite existing configs
            file_ids: list - Specific configs to import (optional, all by default)
        """
        try:
            # Read upload file
            content = await file.read()
            import_data = json.loads(content.decode("utf-8"))

            overwrite_conflicts = False
            if body:
                overwrite_conflicts = body.get("overwrite_conflicts", False)

            file_ids_to_import = None
            if body:
                file_ids_to_import = body.get("file_ids")
            return helpers.import_chunked(
                import_data,
                overwrite_conflicts=overwrite_conflicts,
                file_ids_to_import=file_ids_to_import,
            )

        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in upload file")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to import configs: {str(e)}"
            )

    # ========================================================================
    # Variable Management Endpoints
    # ========================================================================

    @router.get("/variables")
    async def list_variables():
        """List all environment variables (system, user, feature)."""
        try:
            from wizard.services.env_manager import get_env_manager

            env_mgr = get_env_manager()
            variables = env_mgr.list_all()

            return {
                "status": "success",
                "variables": [
                    {
                        "key": v.key,
                        "value": v.value,
                        "tier": v.tier,
                        "type": v.type,
                        "description": v.description,
                        "required": v.required,
                        "updated_at": v.updated_at
                    }
                    for v in variables
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list variables: {str(e)}")

    @router.get("/get/{key}")
    async def get_variable(key: str):
        """Get a specific variable by key."""
        try:
            from wizard.services.env_manager import get_env_manager

            env_mgr = get_env_manager()
            variable = env_mgr.get(key)

            if not variable:
                raise HTTPException(status_code=404, detail=f"Variable not found: {key}")

            return {
                "status": "success",
                "variable": {
                    "key": variable.key,
                    "value": variable.value,
                    "tier": variable.tier,
                    "type": variable.type,
                    "description": variable.description,
                    "required": variable.required,
                    "updated_at": variable.updated_at
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get variable: {str(e)}")

    @router.post("/set")
    async def set_variable(request: Dict[str, Any]):
        """Set a variable value with automatic tier routing and sync."""
        try:
            from wizard.services.env_manager import get_env_manager

            key = request.get("key")
            value = request.get("value")
            sync = request.get("sync", True)

            if not key:
                raise HTTPException(status_code=400, detail="Missing 'key' parameter")
            if value is None:
                raise HTTPException(status_code=400, detail="Missing 'value' parameter")

            env_mgr = get_env_manager()
            success = env_mgr.set(key, value, sync=sync)

            if not success:
                raise HTTPException(status_code=500, detail="Failed to set variable")

            return {
                "status": "success",
                "message": f"Variable {key} updated",
                "sync_enabled": sync
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to set variable: {str(e)}")

    @router.delete("/delete/{key}")
    async def delete_variable(key: str):
        """Delete a variable from its tier."""
        try:
            from wizard.services.env_manager import get_env_manager

            env_mgr = get_env_manager()
            success = env_mgr.delete(key)

            if not success:
                raise HTTPException(status_code=404, detail=f"Variable not found or could not be deleted: {key}")

            return {
                "status": "success",
                "message": f"Variable {key} deleted"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete variable: {str(e)}")

    @router.post("/sync")
    async def sync_all_variables():
        """Sync all variables across tiers (.env ↔ secrets ↔ config)."""
        try:
            from wizard.services.env_manager import get_env_manager

            env_mgr = get_env_manager()
            counts = env_mgr.sync_all()

            return {
                "status": "success",
                "message": "Variables synchronized",
                "counts": counts
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to sync variables: {str(e)}")

    @router.get("/export")
    async def export_config_backup():
        """Export configuration for backup (does not include secrets)."""
        try:
            from wizard.services.env_manager import get_env_manager

            env_mgr = get_env_manager()
            export_data = env_mgr.export_config()

            return {
                "status": "success",
                "data": export_data,
                "warning": "This export does NOT include encrypted secrets"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to export config: {str(e)}")

    @router.post("/secret/{key_id}/rotate")
    async def rotate_secret_entry(key_id: str, request: Request):
        """Rotate a secret store entry (auto-generates if no payload provided)."""
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        new_value = payload.get("new_value") or secrets.token_urlsafe(32)
        rotated_at = datetime.utcnow().isoformat()

        try:
            store = get_secret_store()
            store.unlock(os.environ.get("WIZARD_KEY", ""))
            store.rotate(key_id, new_value, rotated_at)
            return {
                "success": True,
                "key_id": key_id,
                "new_value": new_value,
                "rotated_at": rotated_at,
            }
        except SecretStoreError as exc:
            raise HTTPException(status_code=500, detail=str(exc))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to rotate secret: {exc}")

    return router
