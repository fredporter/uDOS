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
import subprocess
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from wizard.services.path_utils import get_repo_root, get_memory_dir
from wizard.services.secret_store import (
    get_secret_store,
    SecretEntry,
    SecretStoreError,
)


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


def create_admin_token_routes():
    router = APIRouter(prefix="/api/v1/admin-token", tags=["admin-token"])

    @router.post("/generate")
    async def generate_admin_token(request: Request):
        client_host = request.client.host if request.client else ""
        if client_host not in {"127.0.0.1", "::1", "localhost"}:
            raise HTTPException(status_code=403, detail="local requests only")

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

    return router


def create_config_routes(auth_guard=None):
    """Create configuration management routes."""
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(
        prefix="/api/v1/config", tags=["config"], dependencies=dependencies
    )

    CONFIG_PATH = Path(__file__).parent.parent / "config"

    # Map config file IDs to actual filenames
    CONFIG_FILES = {
        "assistant_keys": "assistant_keys.json",
        "github_keys": "github_keys.json",
        "notion_keys": "notion_keys.json",
        "oauth": "oauth_providers.json",
        "slack_keys": "slack_keys.json",
        "hubspot_keys": "hubspot_keys.json",
        "wizard": "wizard.json",
    }

    # Proper capitalization for display labels
    LABEL_MAP = {
        "assistant_keys": "Assistant Keys",
        "github_keys": "GitHub Keys",
        "notion_keys": "Notion Keys",
        "oauth": "OAuth Providers",
        "slack_keys": "Slack Keys",
        "hubspot_keys": "HubSpot Keys",
        "wizard": "Wizard",
    }

    @router.get("/files")
    async def get_config_files():
        """List available config files with their status."""
        files = []

        for file_id, filename in CONFIG_FILES.items():
            file_path = CONFIG_PATH / filename

            # Determine if file exists and is example/template
            if file_path.exists():
                with open(file_path, "r") as f:
                    try:
                        content = json.load(f)
                        files.append(
                            {
                                "id": file_id,
                                "label": LABEL_MAP.get(
                                    file_id,
                                    filename.replace("_", " ")
                                    .replace(".json", "")
                                    .title(),
                                ),
                                "filename": filename,
                                "exists": True,
                                "is_example": filename.endswith(".example.json"),
                                "is_template": filename.endswith(".template.json"),
                            }
                        )
                    except json.JSONDecodeError:
                        files.append(
                            {
                                "id": file_id,
                                "label": LABEL_MAP.get(
                                    file_id,
                                    filename.replace("_", " ")
                                    .replace(".json", "")
                                    .title(),
                                ),
                                "filename": filename,
                                "exists": True,
                                "is_example": False,
                                "is_template": False,
                                "error": "Invalid JSON",
                            }
                        )
            else:
                # Check for .example or .template versions
                example_path = CONFIG_PATH / filename.replace(".json", ".example.json")
                template_path = CONFIG_PATH / filename.replace(
                    ".json", ".template.json"
                )

                if example_path.exists():
                    files.append(
                        {
                            "id": file_id,
                            "label": LABEL_MAP.get(
                                file_id,
                                filename.replace("_", " ").replace(".json", "").title(),
                            ),
                            "filename": filename,
                            "exists": False,
                            "is_example": True,
                            "is_template": False,
                            "actual_file": filename.replace(".json", ".example.json"),
                        }
                    )
                elif template_path.exists():
                    files.append(
                        {
                            "id": file_id,
                            "label": LABEL_MAP.get(
                                file_id,
                                filename.replace("_", " ").replace(".json", "").title(),
                            ),
                            "filename": filename,
                            "exists": False,
                            "is_example": False,
                            "is_template": True,
                            "actual_file": filename.replace(".json", ".template.json"),
                        }
                    )
                else:
                    files.append(
                        {
                            "id": file_id,
                            "label": LABEL_MAP.get(
                                file_id,
                                filename.replace("_", " ").replace(".json", "").title(),
                            ),
                            "filename": filename,
                            "exists": False,
                            "is_example": False,
                            "is_template": False,
                            "actual_file": None,
                        }
                    )

        return {"files": files}

    @router.get("/{file_id}")
    async def get_config(file_id: str):
        """Get configuration file content.

        Only works for actual config files (not examples).
        """
        if file_id not in CONFIG_FILES:
            raise HTTPException(
                status_code=400, detail=f"Unknown config file: {file_id}"
            )

        filename = CONFIG_FILES[file_id]
        file_path = CONFIG_PATH / filename

        # Try actual file first
        if file_path.exists():
            with open(file_path, "r") as f:
                try:
                    content = json.load(f)
                    if file_id == "wizard":
                        content.setdefault("file_locations", {})
                        content["file_locations"].setdefault("memory_root", "memory")
                        content["file_locations"].setdefault("repo_root", "auto")
                        content["file_locations"]["repo_root_actual"] = str(
                            get_repo_root()
                        )
                        content["file_locations"]["memory_root_actual"] = str(
                            get_memory_dir()
                        )
                    return {
                        "id": file_id,
                        "filename": filename,
                        "content": content,
                        "is_example": False,
                        "is_template": False,
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500, detail=f"Invalid JSON in {filename}: {str(e)}"
                    )

        # Try example version
        example_path = CONFIG_PATH / filename.replace(".json", ".example.json")
        if example_path.exists():
            with open(example_path, "r") as f:
                try:
                    content = json.load(f)
                    if file_id == "wizard":
                        content.setdefault("file_locations", {})
                        content["file_locations"].setdefault("memory_root", "memory")
                        content["file_locations"].setdefault("repo_root", "auto")
                        content["file_locations"]["repo_root_actual"] = str(
                            get_repo_root()
                        )
                        content["file_locations"]["memory_root_actual"] = str(
                            get_memory_dir()
                        )
                    return {
                        "id": file_id,
                        "filename": filename,
                        "content": content,
                        "is_example": True,
                        "is_template": False,
                        "message": "Using example file. Save to create actual config.",
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid JSON in {example_path.name}: {str(e)}",
                    )

        # Try template version
        template_path = CONFIG_PATH / filename.replace(".json", ".template.json")
        if template_path.exists():
            with open(template_path, "r") as f:
                try:
                    content = json.load(f)
                    return {
                        "id": file_id,
                        "filename": filename,
                        "content": content,
                        "is_example": False,
                        "is_template": True,
                        "message": "Using template file. Save to create actual config.",
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid JSON in {template_path.name}: {str(e)}",
                    )

        raise HTTPException(status_code=404, detail=f"Config file not found: {file_id}")

    @router.post("/{file_id}")
    async def save_config(file_id: str, body: Dict[str, Any]):
        """Save configuration file.

        Creates or updates the actual config file (not examples).
        Private files are never distributed in public repo.
        """
        if file_id not in CONFIG_FILES:
            raise HTTPException(
                status_code=400, detail=f"Unknown config file: {file_id}"
            )

        try:
            filename = CONFIG_FILES[file_id]
            file_path = CONFIG_PATH / filename

            # Extract content from request body
            content = body.get("content", {})

            # Validate JSON
            if not isinstance(content, dict):
                raise HTTPException(
                    status_code=400, detail="Config content must be a JSON object"
                )

            # Write file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(content, f, indent=2)

            return {
                "success": True,
                "message": f"Saved {filename}",
                "file": filename,
                "path": str(file_path),
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save config: {str(e)}"
            )

    @router.post("/{file_id}/reset")
    async def reset_config(file_id: str):
        """Reset config file to example/template version."""
        if file_id not in CONFIG_FILES:
            raise HTTPException(
                status_code=400, detail=f"Unknown config file: {file_id}"
            )

        try:
            filename = CONFIG_FILES[file_id]
            file_path = CONFIG_PATH / filename

            # Delete actual config if it exists
            if file_path.exists():
                file_path.unlink()
                return {
                    "success": True,
                    "message": f"Reset {filename} to example/template",
                }
            else:
                raise HTTPException(
                    status_code=404, detail=f"No config file to reset: {filename}"
                )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to reset config: {str(e)}"
            )

    @router.get("/{file_id}/example")
    async def get_example_config(file_id: str):
        """Get example/template version of config file."""
        if file_id not in CONFIG_FILES:
            raise HTTPException(
                status_code=400, detail=f"Unknown config file: {file_id}"
            )

        filename = CONFIG_FILES[file_id]

        # Try example first
        example_path = CONFIG_PATH / filename.replace(".json", ".example.json")
        if example_path.exists():
            with open(example_path, "r") as f:
                try:
                    content = json.load(f)
                    return {
                        "id": file_id,
                        "filename": filename,
                        "example_file": example_path.name,
                        "content": content,
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500, detail=f"Invalid JSON: {str(e)}"
                    )

        # Try template
        template_path = CONFIG_PATH / filename.replace(".json", ".template.json")
        if template_path.exists():
            with open(template_path, "r") as f:
                try:
                    content = json.load(f)
                    return {
                        "id": file_id,
                        "filename": filename,
                        "template_file": template_path.name,
                        "content": content,
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500, detail=f"Invalid JSON: {str(e)}"
                    )

        raise HTTPException(
            status_code=404, detail=f"No example/template found for {filename}"
        )

    # ===== SSH KEY MANAGEMENT =====
    # SSH keys are stored in ~/.ssh/ (system standard location)
    # API provides status/verification, not key management itself

    SSH_DIR = Path.home() / ".ssh"
    DEFAULT_SSH_KEY_NAME = "id_ed25519_github"
    SETUP_SCRIPT_PATH = (
        Path(__file__).parent.parent.parent / "bin" / "setup_github_ssh.sh"
    )

    @router.get("/ssh/status")
    async def get_ssh_status():
        """Check SSH key status and provide setup instructions."""
        ssh_key_path = SSH_DIR / DEFAULT_SSH_KEY_NAME
        ssh_pub_path = SSH_DIR / f"{DEFAULT_SSH_KEY_NAME}.pub"

        status = {
            "ssh_dir": str(SSH_DIR),
            "key_name": DEFAULT_SSH_KEY_NAME,
            "key_path": str(ssh_key_path),
            "pub_key_path": str(ssh_pub_path),
            "key_exists": ssh_key_path.exists(),
            "pub_key_exists": ssh_pub_path.exists(),
            "setup_script": (
                str(SETUP_SCRIPT_PATH) if SETUP_SCRIPT_PATH.exists() else None
            ),
        }

        # If key exists, get fingerprint and type
        if ssh_key_path.exists():
            try:
                result = subprocess.run(
                    ["ssh-keygen", "-l", "-f", str(ssh_key_path)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    # Parse: 4096 SHA256:XXXXX user@host (RSA)
                    parts = result.stdout.strip().split()
                    if len(parts) >= 4:
                        status["key_type"] = parts[-1].strip("()")
                        status["fingerprint"] = parts[1]
                        status["key_bits"] = parts[0]
            except Exception as e:
                status["key_error"] = str(e)

        return status

    @router.get("/ssh/public-key")
    async def get_ssh_public_key():
        """Get the public SSH key content for GitHub."""
        ssh_pub_path = SSH_DIR / f"{DEFAULT_SSH_KEY_NAME}.pub"

        if not ssh_pub_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"SSH public key not found. Run setup script: {SETUP_SCRIPT_PATH}",
            )

        try:
            with open(ssh_pub_path, "r") as f:
                public_key = f.read().strip()

            return {
                "public_key": public_key,
                "key_name": DEFAULT_SSH_KEY_NAME,
                "path": str(ssh_pub_path),
                "instructions": "Add this key to GitHub: https://github.com/settings/keys",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read public key: {str(e)}",
            )

    @router.post("/ssh/test-connection")
    async def test_ssh_connection():
        """Test SSH connection to GitHub."""
        ssh_key_path = SSH_DIR / DEFAULT_SSH_KEY_NAME

        if not ssh_key_path.exists():
            raise HTTPException(
                status_code=404,
                detail="SSH key not found. Run setup script first.",
            )

        try:
            # Test SSH connection to GitHub
            result = subprocess.run(
                ["ssh", "-i", str(ssh_key_path), "-T", "git@github.com"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # GitHub returns "successfully authenticated" on success
            success = (
                "successfully authenticated" in result.stdout or result.returncode == 1
            )

            return {
                "status": "connected" if success else "failed",
                "output": result.stdout + result.stderr,
                "success": success,
                "instructions": (
                    "Make sure your public key is added to GitHub: https://github.com/settings/keys"
                    if not success
                    else None
                ),
            }
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=408,
                detail="SSH connection test timed out",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to test connection: {str(e)}",
            )

    @router.get("/ssh/setup-instructions")
    async def get_ssh_setup_instructions():
        """Get comprehensive SSH setup instructions."""
        return {
            "title": "GitHub SSH Setup Instructions",
            "ssh_dir": str(SSH_DIR),
            "key_name": DEFAULT_SSH_KEY_NAME,
            "setup_script": (
                str(SETUP_SCRIPT_PATH) if SETUP_SCRIPT_PATH.exists() else None
            ),
            "steps": [
                {
                    "step": 1,
                    "title": "Run Setup Script",
                    "command": f"bash {SETUP_SCRIPT_PATH}",
                    "description": "This script will generate SSH keys with user interaction",
                },
                {
                    "step": 2,
                    "title": "Confirm Email",
                    "description": "Provide your GitHub email (used as key comment)",
                },
                {
                    "step": 3,
                    "title": "Choose Key Type",
                    "options": [
                        "ed25519 (recommended, faster)",
                        "rsa (wider compatibility)",
                    ],
                    "description": "Ed25519 is recommended for modern systems",
                },
                {
                    "step": 4,
                    "title": "Copy Public Key",
                    "command": f"cat {SSH_DIR}/{DEFAULT_SSH_KEY_NAME}.pub",
                    "description": "The script will display your public key",
                },
                {
                    "step": 5,
                    "title": "Add to GitHub",
                    "url": "https://github.com/settings/keys",
                    "description": "Paste the public key into GitHub settings",
                },
                {
                    "step": 6,
                    "title": "Test Connection",
                    "command": "ssh -T git@github.com",
                    "description": "Verify the SSH connection works",
                },
            ],
            "script_options": {
                "interactive": f"bash {SETUP_SCRIPT_PATH}",
                "auto": f"bash {SETUP_SCRIPT_PATH} --auto",
                "status": f"bash {SETUP_SCRIPT_PATH} --status",
                "rsa": f"bash {SETUP_SCRIPT_PATH} --type rsa",
                "help": f"bash {SETUP_SCRIPT_PATH} --help",
            },
            "security_notes": [
                "Private keys are stored in ~/.ssh/ (never committed to git)",
                "Public keys only (safe to share)",
                "Keys are local-machine only",
                "Backup your ~/.ssh/ directory",
                "Protect your private key with file permissions (700)",
            ],
        }

    # ===== IMPORT/EXPORT SETTINGS =====
    # Transfer settings between devices

    EXPORT_DIR = Path(__file__).parent.parent.parent / "memory" / "config_exports"

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
            file_ids = body.get("file_ids", [])
            include_secrets = body.get("include_secrets", False)

            if not file_ids:
                raise HTTPException(
                    status_code=400, detail="No config files specified for export"
                )

            # Validate file_ids
            invalid_ids = [fid for fid in file_ids if fid not in CONFIG_FILES]
            if invalid_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid config file IDs: {', '.join(invalid_ids)}",
                )

            # Create export directory
            EXPORT_DIR.mkdir(parents=True, exist_ok=True)

            # Collect configs
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat() + "Z",
                "exported_from": "uDOS Wizard Server",
                "version": "1.0",
                "include_secrets": include_secrets,
                "configs": {},
            }

            has_secrets = False

            for file_id in file_ids:
                filename = CONFIG_FILES[file_id]
                file_path = CONFIG_PATH / filename

                # Try actual file first
                content = None
                if file_path.exists():
                    try:
                        with open(file_path, "r") as f:
                            content = json.load(f)
                    except json.JSONDecodeError:
                        pass

                if content is None:
                    # Try example
                    example_path = CONFIG_PATH / filename.replace(
                        ".json", ".example.json"
                    )
                    if example_path.exists():
                        try:
                            with open(example_path, "r") as f:
                                content = json.load(f)
                        except json.JSONDecodeError:
                            pass

                if content is None:
                    # Try template
                    template_path = CONFIG_PATH / filename.replace(
                        ".json", ".template.json"
                    )
                    if template_path.exists():
                        try:
                            with open(template_path, "r") as f:
                                content = json.load(f)
                        except json.JSONDecodeError:
                            pass

                if content:
                    # Filter secrets if not included
                    if not include_secrets and file_id != "wizard":
                        has_secrets = True
                        # Keep structure but redact values
                        content = {k: "***REDACTED***" for k in content.keys()}

                    export_data["configs"][file_id] = {
                        "filename": filename,
                        "content": content,
                    }

            if not export_data["configs"]:
                raise HTTPException(
                    status_code=404, detail="No config files found to export"
                )

            # Write export file
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
            export_filename = f"udos-config-export-{timestamp}.json"
            export_path = EXPORT_DIR / export_filename

            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2)

            warning = None
            if has_secrets or include_secrets:
                warning = "⚠️ This file contains secrets or redacted values. Keep it secure and never commit to git!"

            return {
                "success": True,
                "filename": export_filename,
                "path": str(export_path),
                "size": export_path.stat().st_size,
                "timestamp": export_data["export_timestamp"],
                "exported_configs": list(export_data["configs"].keys()),
                "include_secrets": include_secrets,
                "warning": warning,
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to export configs: {str(e)}"
            )

    @router.get("/export/list")
    async def list_exports():
        """List available export files."""
        if not EXPORT_DIR.exists():
            return {"exports": []}

        exports = []
        for export_file in sorted(
            EXPORT_DIR.glob("udos-config-export-*.json"), reverse=True
        ):
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
    async def download_export(filename: str):
        """Download an export file.

        Safety check: only allows downloading from export directory.
        """
        # Validate filename to prevent path traversal
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

            # Validate export file structure
            if "configs" not in import_data:
                raise ValueError("Invalid export file: missing 'configs' field")

            if not isinstance(import_data["configs"], dict):
                raise ValueError("Invalid export file: 'configs' must be an object")

            # Check for conflicts
            conflicts = []
            preview = {}

            for file_id, config_info in import_data["configs"].items():
                if file_id not in CONFIG_FILES:
                    continue  # Skip unknown configs

                filename = CONFIG_FILES[file_id]
                file_path = CONFIG_PATH / filename

                # Check if file exists (conflict)
                if file_path.exists():
                    conflicts.append(file_id)

                # Add to preview
                preview[file_id] = {
                    "filename": config_info.get("filename", filename),
                    "has_content": "content" in config_info
                    and bool(config_info["content"]),
                    "is_redacted": all(
                        v == "***REDACTED***"
                        for v in config_info.get("content", {}).values()
                        if isinstance(v, str)
                    ),
                }

            return {
                "success": True,
                "preview": preview,
                "conflicts": conflicts,
                "timestamp": import_data.get("export_timestamp"),
                "exported_from": import_data.get("exported_from"),
                "message": (
                    "Preview: Use POST /api/v1/config/import/apply to import these configs"
                ),
            }

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
        1. POST /api/v1/config/import (validate)
        2. POST /api/v1/config/import/apply (confirm)
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

            # Validate export file structure
            if "configs" not in import_data:
                raise ValueError("Invalid export file: missing 'configs' field")

            overwrite_conflicts = False
            if body:
                overwrite_conflicts = body.get("overwrite_conflicts", False)

            file_ids_to_import = None
            if body:
                file_ids_to_import = body.get("file_ids")

            # Import configs
            imported = []
            skipped = []
            errors = []

            for file_id, config_info in import_data["configs"].items():
                if file_id not in CONFIG_FILES:
                    continue  # Skip unknown configs

                # Check filter
                if file_ids_to_import and file_id not in file_ids_to_import:
                    continue

                filename = CONFIG_FILES[file_id]
                file_path = CONFIG_PATH / filename
                content_to_write = config_info.get("content", {})

                # Check for redacted values
                is_redacted = all(
                    v == "***REDACTED***"
                    for v in content_to_write.values()
                    if isinstance(v, str)
                )

                if is_redacted:
                    skipped.append(
                        {
                            "file_id": file_id,
                            "reason": "Config was redacted during export. Use full export to transfer secrets.",
                        }
                    )
                    continue

                # Check for conflicts
                if file_path.exists() and not overwrite_conflicts:
                    skipped.append(
                        {
                            "file_id": file_id,
                            "reason": "Config already exists. Use overwrite_conflicts=true to replace.",
                        }
                    )
                    continue

                try:
                    # Write config
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, "w") as f:
                        json.dump(content_to_write, f, indent=2)

                    imported.append(file_id)
                except Exception as e:
                    errors.append({"file_id": file_id, "error": str(e)})

            return {
                "success": len(errors) == 0,
                "imported": imported,
                "skipped": skipped,
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": (
                    f"Imported {len(imported)} config(s)"
                    if imported
                    else "No configs imported"
                ),
            }

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

    return router


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
