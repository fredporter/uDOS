"""SSH status/testing route module for config APIs."""

import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException

SSH_DIR = Path.home() / ".ssh"
DEFAULT_SSH_KEY_NAME = "id_ed25519_github"
SETUP_SCRIPT_PATH = Path(__file__).parent.parent.parent / "bin" / "setup_github_ssh.sh"


def create_config_ssh_routes() -> APIRouter:
    router = APIRouter(tags=["config-ssh"])

    @router.get("/ssh/status")
    async def get_ssh_status():
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

        if ssh_key_path.exists():
            try:
                result = subprocess.run(
                    ["ssh-keygen", "-l", "-f", str(ssh_key_path)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    parts = result.stdout.strip().split()
                    if len(parts) >= 4:
                        status["key_type"] = parts[-1].strip("()")
                        status["fingerprint"] = parts[1]
                        status["key_bits"] = parts[0]
            except Exception as exc:
                status["key_error"] = str(exc)

        return status

    @router.get("/ssh/public-key")
    async def get_ssh_public_key():
        ssh_pub_path = SSH_DIR / f"{DEFAULT_SSH_KEY_NAME}.pub"
        if not ssh_pub_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"SSH public key not found. Run setup script: {SETUP_SCRIPT_PATH}",
            )

        try:
            with open(ssh_pub_path, "r", encoding="utf-8") as handle:
                public_key = handle.read().strip()

            return {
                "public_key": public_key,
                "key_name": DEFAULT_SSH_KEY_NAME,
                "path": str(ssh_pub_path),
                "instructions": "Add this key to GitHub: https://github.com/settings/keys",
            }
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read public key: {str(exc)}",
            )

    @router.post("/ssh/test-connection")
    async def test_ssh_connection():
        ssh_key_path = SSH_DIR / DEFAULT_SSH_KEY_NAME
        if not ssh_key_path.exists():
            raise HTTPException(
                status_code=404,
                detail="SSH key not found. Run setup script first.",
            )

        try:
            result = subprocess.run(
                ["ssh", "-i", str(ssh_key_path), "-T", "git@github.com"],
                capture_output=True,
                text=True,
                timeout=10,
            )
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
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to test connection: {str(exc)}",
            )

    @router.get("/ssh/setup-instructions")
    async def get_ssh_setup_instructions():
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
