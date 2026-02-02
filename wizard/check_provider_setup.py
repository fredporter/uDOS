#!/usr/bin/env python3
"""
Provider Setup Checker
======================

Checks for flagged providers on startup and runs setup automations.
Called by Wizard Server startup or manually via TUI.
"""

import json
import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

CONFIG_PATH = Path(__file__).parent / "config"
SETUP_FLAGS_FILE = CONFIG_PATH / "provider_setup_flags.json"


def load_flagged_providers() -> List[str]:
    """Load list of providers flagged for setup."""
    if SETUP_FLAGS_FILE.exists():
        with open(SETUP_FLAGS_FILE, "r") as f:
            data = json.load(f)
            return data.get("flagged", [])
    return []


def _load_config_file(file_name: str) -> Optional[Dict]:
    path = CONFIG_PATH / file_name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _get_nested(data: Dict, path: List[str]) -> Optional[str]:
    current = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _run_check(cmd: str) -> bool:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def _validate_github_auth() -> bool:
    """Validate that gh CLI is authenticated for github.com."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status", "-h", "github.com"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True
        output = f"{result.stdout}\n{result.stderr}".lower()
        if "logged in to github.com" in output:
            return True
        if "logged in to" in output and "github.com" in output:
            return True
        return False
    except Exception:
        return False


def _provider_is_configured(provider_id: str) -> bool:
    if provider_id == "github":
        if shutil.which("gh") and _validate_github_auth():
            return True
        config = _load_config_file("github_keys.json") or {}
        return bool(
            _get_nested(config, ["tokens", "default", "key_id"])
            or _get_nested(config, ["webhooks", "secret_key_id"])
        )

    if provider_id == "slack":
        if shutil.which("slack") and _run_check("slack auth test"):
            return True
        config = _load_config_file("slack_keys.json") or {}
        return bool(config.get("SLACK_BOT_TOKEN") or config.get("SLACK_WEBHOOK_URL"))

    if provider_id == "ollama":
        if _validate_ollama():
            return True
        config = _load_config_file("assistant_keys.json") or {}
        if config.get("OLLAMA_HOST"):
            return True
        return bool(
            _get_nested(config, ["providers", "ollama", "endpoint"])
            or _get_nested(config, ["providers", "ollama", "key_id"])
        )

    return False


def _scrub_provider(provider_id: str) -> None:
    if provider_id == "github" and shutil.which("gh"):
        try:
            subprocess.run(["gh", "auth", "logout", "-h", "github.com"], check=False)
        except Exception:
            pass
    elif provider_id == "slack" and shutil.which("slack"):
        try:
            subprocess.run(["slack", "auth", "logout"], check=False)
        except Exception:
            pass


def _extract_github_token() -> Optional[str]:
    """Extract GitHub token from gh CLI and save to github_keys.json."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            token = result.stdout.strip()
            if token and len(token) > 10:
                return token
    except Exception:
        pass
    return None


def _populate_github_keys(token: str) -> bool:
    """
    Populate github_keys.json with token and metadata from gh CLI.

    Args:
        token: GitHub personal access token

    Returns:
        True if successfully populated
    """
    try:
        # Get authenticated user info from gh CLI
        user_result = subprocess.run(
            ["gh", "api", "user"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        user_data = {}
        if user_result.returncode == 0:
            try:
                user_data = json.loads(user_result.stdout)
            except json.JSONDecodeError:
                pass

        # Build github_keys.json structure
        github_keys = {
            "profile": "default",
            "description": "GitHub CLI integration - auto-populated by Wizard setup",
            "tokens": {
                "default": {
                    "key_id": "github-personal-main",
                    "scopes": ["repo", "workflow", "admin:repo_hook", "user"],
                    "token": token,  # Store token in local-only config
                    "authenticated_user": user_data.get("login", "unknown"),
                }
            },
            "webhooks": {
                "secret_key_id": "github-webhook-secret"
            },
            "metadata": {
                "setup_date": datetime.now().isoformat(),
                "source": "gh-cli",
                "authenticated_user": user_data.get("login"),
                "user_id": user_data.get("id"),
            }
        }

        # Save to config
        config_path = CONFIG_PATH / "github_keys.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(github_keys, indent=2))

        print(f"{GREEN}✓{NC} GitHub keys populated from gh CLI")
        if user_data.get("login"):
            print(f"   Authenticated as: {user_data['login']}")
        return True

    except Exception as e:
        print(f"{YELLOW}⚠{NC} Failed to populate github_keys.json: {e}")
        return False


def _validate_slack_auth() -> bool:
    """Validate that Slack CLI is properly authenticated."""
    try:
        result = subprocess.run(
            ["slack", "auth", "test"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def _validate_ollama() -> bool:
    """Validate that Ollama is running locally."""
    try:
        if shutil.which("curl"):
            return _run_check("curl -s http://localhost:11434/api/tags")
        if shutil.which("ollama"):
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
    except Exception:
        return False
    return False


def run_provider_setup(provider_id: str, auto_yes: bool = False) -> bool:
    """Run setup for a specific provider."""
    print(f"\n{BLUE}━━━ Setting up {provider_id} ━━━{NC}\n")

    if provider_id == "ollama":
        if _provider_is_configured("ollama"):
            print(f"{GREEN}✓{NC} ollama setup complete")
            return True
        print(f"{YELLOW}⚠{NC} ollama requires manual setup via dashboard")
        print("   Visit: http://localhost:8765/#config")
        return False

    # Map provider IDs to setup commands
    setup_commands = {
        "github": ["gh", "auth", "login"],
        "ollama": None,  # Auto-detected
        "slack": ["slack", "login"],
        "notion": None,  # Interactive browser flow
    }

    cmd = setup_commands.get(provider_id)
    if cmd is None:
        print(f"{YELLOW}⚠{NC} {provider_id} requires manual setup via dashboard")
        print(f"   Visit: http://localhost:8765/#config")
        return False

    if _provider_is_configured(provider_id):
        if auto_yes:
            print(f"{YELLOW}⚠{NC} Existing setup detected; re-installing (--yes).")
            _scrub_provider(provider_id)
        else:
            response = input(
                f"{provider_id} already configured. Scrub and reinstall? (y/N): "
            )
            if response.lower() != "y":
                print(f"Keeping existing setup for {provider_id}.")
                # Still try to auto-populate GitHub keys if available
                if provider_id == "github" and shutil.which("gh"):
                    token = _extract_github_token()
                    if token:
                        _populate_github_keys(token)
                return True
            _scrub_provider(provider_id)

    # Confirm before running
    if not auto_yes:
        response = input(f"Run setup command for {provider_id}? (y/N): ")
        if response.lower() != "y":
            print(f"Skipped {provider_id}")
            return False

    # Run command
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        # Validate that setup actually succeeded
        setup_valid = False
        if result.returncode == 0:
            if provider_id == "github":
                # Validate GitHub auth
                setup_valid = _validate_github_auth()
            elif provider_id == "slack":
                # Validate Slack auth
                setup_valid = _validate_slack_auth()
            else:
                # For other providers, trust returncode
                setup_valid = True

        if setup_valid:
            print(f"{GREEN}✓{NC} {provider_id} setup complete")

            # Auto-populate GitHub keys after successful gh auth login
            if provider_id == "github":
                token = _extract_github_token()
                if token:
                    _populate_github_keys(token)
                else:
                    print(f"{YELLOW}⚠{NC} Could not extract token from gh CLI")

            return True
        else:
            print(f"{YELLOW}⚠{NC} {provider_id} setup did not complete successfully")
            if provider_id == "slack":
                output = f"{result.stdout}\n{result.stderr}".lower()
                if "missing_authorization" in output:
                    print("   Slack CLI is not authorized in that workspace.")
                    print("   Approve the Slack modal, then run: slack login")
                else:
                    print("   Please run: slack login")
            else:
                print(f"   Please run: {' '.join(cmd)} again")
            return False
    except FileNotFoundError:
        print(f"{YELLOW}⚠{NC} CLI not found: {cmd[0]}")
        print(f"   Install: brew install {cmd[0]}")
        return False
    except Exception as e:
        print(f"{YELLOW}⚠{NC} Setup error: {e}")
        return False


def mark_provider_completed(provider_id: str):
    """Mark provider as completed in flags file."""
    if SETUP_FLAGS_FILE.exists():
        with open(SETUP_FLAGS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"flagged": [], "completed": []}

    if provider_id in data["flagged"]:
        data["flagged"].remove(provider_id)
    if provider_id not in data["completed"]:
        data["completed"].append(provider_id)

    with open(SETUP_FLAGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _parse_provider_arg(argv: List[str]) -> Optional[str]:
    if "--provider" in argv:
        idx = argv.index("--provider")
        if idx + 1 < len(argv):
            return argv[idx + 1]
    return None


def main():
    """Main entry point."""
    auto_yes = "--yes" in sys.argv or "-y" in sys.argv
    provider_only = _parse_provider_arg(sys.argv)

    if provider_only:
        success = run_provider_setup(provider_only, auto_yes)
        if success:
            mark_provider_completed(provider_only)
            return 0
        return 1

    flagged = load_flagged_providers()
    if not flagged:
        print(f"{GREEN}✓{NC} No providers flagged for setup")
        return 0

    print(f"\n{BLUE}Providers flagged for setup:{NC}")
    for provider_id in flagged:
        print(f"  • {provider_id}")
    print()

    if not auto_yes:
        response = input("Run setup for these providers now? (y/N): ")
        if response.lower() != "y":
            print("Skipping provider setup. Run later with: CONFIG SETUP")
            return 0

    # Run setup for each provider
    for provider_id in flagged:
        success = run_provider_setup(provider_id, auto_yes)
        if success:
            mark_provider_completed(provider_id)

    print(f"\n{GREEN}━━━ Provider setup complete ━━━{NC}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
