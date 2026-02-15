"""Admin-token and public export route modules for config APIs."""

import json
import os
import secrets
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from wizard.services.path_utils import get_repo_root
from wizard.services.secret_store import (
    SecretEntry,
    SecretStoreError,
    get_secret_store,
)

LOCAL_CLIENTS = {"127.0.0.1", "::1", "localhost"}
EXPORT_DIR = Path(__file__).parent.parent.parent / "memory" / "config_exports"


def _ensure_local_request(request: Request) -> None:
    client_host = request.client.host if request.client else ""
    if client_host not in LOCAL_CLIENTS:
        raise HTTPException(status_code=403, detail="local requests only")


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


def create_admin_token_routes() -> APIRouter:
    router = APIRouter(prefix="/api/admin-token", tags=["admin-token"])

    @router.post("/generate")
    async def generate_admin_token(request: Request):
        _ensure_local_request(request)

        repo_root = get_repo_root()
        env_path = repo_root / ".env"
        token = secrets.token_urlsafe(32)

        wizard_config_path = repo_root / "wizard" / "config" / "wizard.json"
        key_id = "wizard-admin-token"
        if wizard_config_path.exists():
            try:
                config = json.loads(wizard_config_path.read_text())
                key_id = config.get("admin_api_key_id") or key_id
            except Exception:
                pass

        wizard_key = os.getenv("WIZARD_KEY")
        key_created = False
        if not wizard_key:
            wizard_key = secrets.token_urlsafe(32)
            key_created = True
            _write_env_var(env_path, "WIZARD_KEY", wizard_key)
            os.environ["WIZARD_KEY"] = wizard_key

        _write_env_var(env_path, "WIZARD_ADMIN_TOKEN", token)
        os.environ["WIZARD_ADMIN_TOKEN"] = token

        stored = False
        try:
            store = get_secret_store()
            store.unlock(wizard_key)
            entry = SecretEntry(
                key_id=key_id,
                provider="wizard_admin",
                value=token,
                created_at=datetime.utcnow().isoformat(),
                metadata={"source": "wizard-dashboard"},
            )
            store.set(entry)
            stored = True
        except SecretStoreError:
            stored = False

        return {
            "status": "success",
            "token": token,
            "stored_in_secret_store": stored,
            "env_path": str(env_path),
            "key_created": key_created,
        }

    @router.get("/status")
    async def get_admin_token_status(request: Request):
        _ensure_local_request(request)

        repo_root = get_repo_root()
        env_path = repo_root / ".env"
        env_data = {}

        if env_path.exists():
            try:
                for line in env_path.read_text().splitlines():
                    if not line or line.strip().startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key:
                        env_data[key] = value
            except Exception as exc:
                return {
                    "status": "error",
                    "message": f"Failed to read .env: {str(exc)}",
                    "env": {},
                }

        return {
            "status": "success",
            "env": env_data,
            "has_admin_token": "WIZARD_ADMIN_TOKEN" in env_data,
            "has_wizard_key": "WIZARD_KEY" in env_data,
        }

    return router


def create_public_export_routes() -> APIRouter:
    """Create public export download routes (no auth required for local clients)."""
    router = APIRouter(prefix="/api/config", tags=["config"])

    @router.get("/export/list")
    async def list_exports(request: Request):
        _ensure_local_request(request)

        exports = []
        if EXPORT_DIR.exists():
            for export_file in EXPORT_DIR.glob("udos-config-export-*.json"):
                try:
                    stat = export_file.stat()
                    exports.append(
                        {
                            "filename": export_file.name,
                            "path": str(export_file),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                            + "Z",
                        }
                    )
                except Exception:
                    pass

        return {"exports": exports}

    @router.get("/export/{filename}")
    async def download_export(filename: str, request: Request):
        _ensure_local_request(request)

        if not filename.startswith("udos-config-export-") or not filename.endswith(
            ".json"
        ):
            raise HTTPException(status_code=400, detail="Invalid export filename")
        if ".." in filename:
            raise HTTPException(status_code=400, detail="Invalid path")

        export_path = EXPORT_DIR / filename
        if not export_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Export file not found: {filename}"
            )

        return FileResponse(
            path=export_path,
            filename=filename,
            media_type="application/json",
        )

    return router
