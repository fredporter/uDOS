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
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse


def create_config_routes(auth_guard=None):
    """Create configuration management routes."""
    router = APIRouter(prefix="/api/v1/config", tags=["config"])

    CONFIG_PATH = Path(__file__).parent.parent / "config"

    # Map config file IDs to actual filenames
    CONFIG_FILES = {
        "assistant_keys": "assistant_keys.json",
        "github_keys": "github_keys.json",
        "notion_keys": "notion_keys.json",
        "oauth": "oauth_providers.json",
        "slack_keys": "slack_keys.json",
        "wizard": "wizard.json",
    }

    # Proper capitalization for display labels
    LABEL_MAP = {
        "assistant_keys": "Assistant Keys",
        "github_keys": "GitHub Keys",
        "notion_keys": "Notion Keys",
        "oauth": "OAuth Providers",
        "slack_keys": "Slack Keys",
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

    return router
