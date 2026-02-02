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

    if provider_id == "hubspot":
        config = _load_config_file("hubspot_keys.json") or {}
        return bool(
            config.get("api_key")
            or config.get("private_app_access_token")
            or _get_nested(config, ["providers", "hubspot", "key_id"])
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


def _setup_hubspot() -> bool:
    """Interactive HubSpot Developer Platform CLI and API setup.

    Guides users through:
    1. Installing HubSpot CLI (@hubspot/cli)
    2. Authenticating with Personal Access Key
    3. OR manually configuring API token
    """
    print(f"{BLUE}━━━ HUBSPOT DEVELOPER PLATFORM SETUP ━━━{NC}\n")

    print("HubSpot offers two integration paths:")
    print("  1. CLI Workflow - Build and deploy apps (recommended for developers)")
    print("  2. API Token Only - Direct API access (simple integration)\n")

    choice = input(f"{YELLOW}?{NC} Choose setup type (1=CLI, 2=API Token, Enter=skip): ").strip()

    if choice == "1":
        return _setup_hubspot_cli()
    elif choice == "2":
        return _setup_hubspot_api()
    else:
        print(f"\n{YELLOW}⚠{NC}  Setup skipped. You can configure HubSpot later via the dashboard.")
        return False


def _setup_hubspot_cli() -> bool:
    """Interactive HubSpot CLI installation and authentication."""
    print(f"\n{BLUE}━━━ HUBSPOT CLI SETUP ━━━{NC}\n")

    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{YELLOW}⚠{NC}  npm not found. Install Node.js first: https://nodejs.org/")
        return False

    # Check if CLI is already installed
    try:
        result = subprocess.run(
            ["hs", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"{GREEN}✓{NC} HubSpot CLI already installed: {result.stdout.strip()}\n")
        else:
            raise FileNotFoundError
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("HubSpot CLI not found. Installing...\n")
        install = input(f"{YELLOW}?{NC} Install @hubspot/cli via npm? (y/N): ").strip().lower()
        
        if install != "y":
            print(f"{YELLOW}⚠{NC}  CLI installation skipped.")
            return False

        print(f"\n{BLUE}Installing @hubspot/cli (this may take 1-2 minutes)...{NC}")
        try:
            subprocess.run(
                ["npm", "install", "-g", "@hubspot/cli"],
                timeout=180,
                check=True
            )
            print(f"{GREEN}✓{NC} HubSpot CLI installed successfully\n")
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}⚠{NC}  Installation timed out. Try manually: npm install -g @hubspot/cli")
            return False
        except subprocess.CalledProcessError as e:
            print(f"{YELLOW}⚠{NC}  Installation failed: {e}")
            return False

    # Guide through authentication
    print(f"{BLUE}━━━ AUTHENTICATION GUIDE ━━━{NC}\n")
    print("To authenticate the HubSpot CLI:")
    print("  1. Run: hs init")
    print("  2. Follow browser prompt to generate Personal Access Key")
    print("  3. Copy and paste the key when prompted")
    print("  4. Set as default account when asked\n")

    print(f"{BLUE}Quick Start Commands:{NC}")
    print("  hs get-started     - Create a new HubSpot app project")
    print("  hs project dev     - Start local development server")
    print("  hs project upload  - Deploy to HubSpot")
    print("  hs account list    - Show authenticated accounts\n")

    print(f"📖 Full guide: https://developers.hubspot.com/docs/getting-started/quickstart\n")

    auto_auth = input(f"{YELLOW}?{NC} Run 'hs init' now? (y/N): ").strip().lower()
    if auto_auth == "y":
        try:
            subprocess.run(["hs", "init"], check=False)
            return True
        except Exception as e:
            print(f"{YELLOW}⚠{NC}  Interactive auth failed: {e}")
            return False

    print(f"{GREEN}✓{NC} HubSpot CLI ready. Run 'hs init' when ready to authenticate.")
    return True


def _setup_hubspot_api() -> bool:
    """Interactive HubSpot API token setup (legacy/simple integration)."""
    print(f"\n{BLUE}━━━ HUBSPOT API TOKEN SETUP ━━━{NC}\n")

    print("STEP 1: Create a HubSpot Private App")
    print("─" * 50)
    print("  1. Visit: https://developers.hubspot.com/apps")
    print("  2. Click 'Create app' button")
    print("  3. Enter app name (e.g., 'uDOS Integration')")
    print("  4. Click 'Create'\n")

    print("STEP 2: Configure App Permissions")
    print("─" * 50)
    print("  In the app dashboard, go to 'Scopes' tab and select:")
    print("    • crm.objects.contacts.read & write")
    print("    • crm.objects.deals.read & write")
    print("    • crm.objects.companies.read & write")
    print("    • crm.lists.read & write")
    print("    • automation.actions.create & execute")
    print("  Then click 'Save'\n")

    print("STEP 3: Get Your Private App Token")
    print("─" * 50)
    print("  1. In the app settings, go to 'Auth' tab")
    print("  2. Under 'Access tokens', copy your 'Private App Access Token'")
    print("  3. This token grants full API access\n")

    app_token = input(f"{YELLOW}?{NC} Paste your Private App Access Token (or press Enter to skip): ").strip()

    if not app_token:
        print(f"\n{YELLOW}⚠{NC}  Setup skipped. You can configure HubSpot later via the dashboard.")
        return False

    # Validate token format (HubSpot tokens start with 'pat-' or are long hex strings)
    if len(app_token) < 20:
        print(f"\n{YELLOW}⚠{NC}  Token seems too short. Please verify and try again.")
        return False

    # Save to hubspot_keys.json
    try:
        config_path = CONFIG_PATH / "hubspot_keys.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        hubspot_config = {
            "app_type": "developer_platform",
            "api_key": app_token,
            "private_app_access_token": app_token,
            "metadata": {
                "setup_date": datetime.now().isoformat(),
                "source": "tui_setup",
                "api_version": "v3",
                "platform": "developer_platform",
            }
        }

        config_path.write_text(json.dumps(hubspot_config, indent=2))
        print(f"\n{GREEN}✓{NC} HubSpot token saved to config")

        # Verify token by making a simple API call
        print(f"\n{BLUE}Verifying token...{NC}")
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {app_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                "https://api.hubapi.com/crm/v3/objects/contacts?limit=1",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                print(f"{GREEN}✓{NC} Token verified! API access confirmed.\n")
                return True
            elif response.status_code == 401:
                print(f"{YELLOW}⚠{NC}  Token is invalid or expired. Please check and try again.")
                config_path.unlink()  # Delete the invalid config
                return False
            else:
                print(f"{YELLOW}⚠{NC}  API verification returned: {response.status_code}")
                print("   Token was saved but couldn't verify. Try accessing via dashboard.")
                return True
        except requests.exceptions.RequestException as e:
            print(f"{YELLOW}⚠{NC}  Could not verify token (network issue): {str(e)}")
            print("   Token was saved. You can verify manually via the dashboard.")
            return True
        except ImportError:
            print(f"{YELLOW}⚠{NC}  requests library not available for verification")
            print("   Token was saved. You can verify via the dashboard.")
            return True

    except Exception as e:
        print(f"{YELLOW}⚠{NC}  Failed to save HubSpot config: {str(e)}")
        return False


def _show_ollama_model_library() -> bool:
    """Interactive Ollama model library browser and installer."""
    print(f"{BLUE}━━━ OLLAMA MODEL LIBRARY ━━━{NC}\n")

    # Popular models with recommendations
    models = [
        ("devstral-small-2", "10.7B", "Coding", "🟢 Mistral's lightweight coding assistant (8GB RAM)", True),
        ("mistral", "7.3B", "General", "⭐ Fast general purpose model (4GB RAM)", True),
        ("neural-chat", "13B", "Chat", "💬 Intel Neural Chat optimized (8GB RAM)", False),
        ("llama2", "7B", "General", "Meta's open foundation model (4GB RAM)", False),
        ("openchat", "7B", "Chat", "Lightweight conversation (4GB RAM)", False),
        ("zephyr", "7B", "General", "Fine-tuned Mistral (4GB RAM)", False),
        ("orca-mini", "3B", "General", "Tiny but capable (2GB RAM)", False),
        ("dolphin-mixtral", "46.7B", "Advanced", "Mixture of experts (24GB+ RAM)", False),
    ]

    print("POPULAR MODELS:\n")
    for i, (name, size, category, desc, recommend) in enumerate(models, 1):
        star = "⭐" if recommend else "  "
        print(f"  {star} {i:2d}. {name:<20s} ({size:>6s}) {category}")
        print(f"      {desc}\n")

    print("COMMANDS:")
    print("  • OLLAMA PULL <model>   - Download a model by name (e.g., 'ollama pull mistral')")
    print("  • OLLAMA LIST           - Show installed models")
    print("  • OLLAMA RUN <model>    - Start an interactive session\n")

    # Check installed models
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            installed = result.stdout.strip().split("\n")[1:]
            if installed and installed[0].strip():
                print(f"{GREEN}✓ INSTALLED MODELS:{NC}\n")
                for line in installed:
                    if line.strip():
                        print(f"  {line}")
                print()
    except Exception:
        pass

    # Offer to pull a model
    if not auto_yes:
        print(f"Want to download a model now?")
        choice = input("Enter model name or 'skip' (e.g., mistral): ").strip().lower()

        if choice and choice != "skip":
            if choice in [m[0] for m in models]:
                print(f"\nPulling {choice}...\n")
                try:
                    result = subprocess.run(
                        ["ollama", "pull", choice],
                        check=False,
                    )
                    if result.returncode == 0:
                        print(f"\n{GREEN}✓{NC} {choice} installed successfully!")
                        return True
                except Exception as e:
                    print(f"{YELLOW}⚠{NC} Failed to pull {choice}: {e}")
                    return False
            else:
                print(f"{YELLOW}⚠{NC} Unknown model: {choice}")
                return False

    return True


def run_provider_setup(provider_id: str, auto_yes: bool = False) -> bool:
    """Run setup for a specific provider."""
    print(f"\n{BLUE}━━━ Setting up {provider_id} ━━━{NC}\n")

    if provider_id == "hubspot":
        return _setup_hubspot()

    if provider_id == "ollama":
        # Check if Ollama is installed
        if not shutil.which("ollama"):
            print(f"{YELLOW}⚠{NC} ollama CLI not found")
            print("   Install from: https://ollama.ai")
            print("\n   macOS/Linux: brew install ollama")
            print("   Windows: Download from https://ollama.ai/download")
            return False

        # Check if running
        if not _validate_ollama():
            print(f"{YELLOW}⚠{NC} ollama server is not running")
            print("   Start it with: ollama serve")
            print("   Or install background service from https://ollama.ai")
            return False

        print(f"{GREEN}✓{NC} ollama server is running!\n")

        # Show model library
        _show_ollama_model_library()

        return True

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
