#!/usr/bin/env python3
"""
Provider Setup Checker
======================

Checks for flagged providers on startup and runs setup automations.
Called by Wizard Server startup or manually via TUI.
"""

import json
import os
import subprocess
import sys
import shutil
import urllib.request
import urllib.error
import threading
import time
import platform
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


def _read_env_os_type() -> Optional[str]:
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return None
    try:
        for line in env_path.read_text().splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "OS_TYPE":
                return value.strip().strip('"').strip("'").lower()
    except Exception:
        return None
    return None


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


def _validate_ollama() -> bool:
    """Validate that Ollama is running locally."""
    try:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        if shutil.which("curl"):
            return _run_check(f"curl -s {host}/api/tags")
        try:
            # Avoid requiring curl/CLI when OLLAMA_HOST is reachable.
            _ollama_api_request("/api/tags")
            return True
        except Exception:
            pass
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


def _ollama_api_request(path: str, payload: Optional[Dict] = None) -> Optional[Dict]:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    url = f"{host}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        method="POST" if data is not None else "GET",
        data=data,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _ollama_api_stream_pull(model: str) -> bool:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    url = f"{host}/api/pull"
    data = json.dumps({"name": model}).encode("utf-8")
    req = urllib.request.Request(
        url,
        method="POST",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            for raw in resp:
                line = raw.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if payload.get("error"):
                    print(f"{YELLOW}⚠{NC} {payload.get('error')}")
                    return False
                status = payload.get("status") or "pulling"
                total = payload.get("total")
                completed = payload.get("completed")
                if isinstance(total, (int, float)) and total:
                    pct = int((completed or 0) / total * 100)
                    print(f"  {status}… {pct}%")
                else:
                    print(f"  {status}…")
        return True
    except Exception as exc:
        print(f"{YELLOW}⚠{NC} Failed to pull via API: {exc}")
        return False


def _show_ollama_model_library(auto_yes: bool = False) -> bool:
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
        if shutil.which("ollama"):
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
        else:
            data = _ollama_api_request("/api/tags")
            models_data = (data or {}).get("models", [])
            if models_data:
                print(f"{GREEN}✓ INSTALLED MODELS (API):{NC}\n")
                for item in models_data:
                    name = item.get("name", "")
                    if name:
                        print(f"  {name}")
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
                    if shutil.which("ollama"):
                        result = subprocess.run(
                            ["ollama", "pull", choice],
                            check=False,
                        )
                        if result.returncode == 0:
                            print(f"\n{GREEN}✓{NC} {choice} installed successfully!")
                            return True
                    else:
                        if _ollama_api_stream_pull(choice):
                            print(f"\n{GREEN}✓{NC} {choice} pull started via API.")
                            return True
                except Exception as e:
                    print(f"{YELLOW}⚠{NC} Failed to pull {choice}: {e}")
                    return False
            else:
                print(f"{YELLOW}⚠{NC} Unknown model: {choice}")
                return False

    return True



def _run_with_spinner(cmd: str, label: str, timeout: int = 600) -> subprocess.CompletedProcess:
    spinner_running = True

    def _spinner_loop() -> None:
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while spinner_running:
            frame = frames[idx % len(frames)]
            sys.stdout.write(f"\r{frame} {label}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.12)
        sys.stdout.write("\r")
        sys.stdout.flush()

    spin_thread = threading.Thread(target=_spinner_loop, daemon=True)
    spin_thread.start()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
    finally:
        spinner_running = False
        time.sleep(0.02)
    return result


def _install_ollama_local() -> bool:
    os_type = _read_env_os_type()
    system = (os_type or platform.system()).lower()
    if system in ("linux", "ubuntu", "alpine"):
        confirm = input("Run automatic install now? (y/N): ").strip().lower()
        if confirm != "y":
            return False
        print(f"\n{BLUE}Installing Ollama for Linux...{NC}")
        result = _run_with_spinner(
            "curl -fsSL https://ollama.com/install.sh | sh",
            "Installing Ollama...",
            timeout=900,
        )
        if result.returncode != 0:
            print(f"{YELLOW}⚠{NC}  Install failed: {result.stderr.strip() or result.stdout.strip()}")
            return False
        if shutil.which("systemctl"):
            subprocess.run(
                ["systemctl", "start", "ollama"],
                capture_output=True,
                text=True,
                check=False,
            )
        return _validate_ollama()

    if system in ("darwin", "macos"):
        if shutil.which("brew"):
            confirm = input("Run brew install ollama now? (y/N): ").strip().lower()
            if confirm != "y":
                return False
            print(f"\n{BLUE}Installing Ollama via Homebrew...{NC}")
            result = _run_with_spinner(
                "brew install ollama",
                "Installing Ollama...",
                timeout=900,
            )
            if result.returncode != 0:
                print(f"{YELLOW}⚠{NC}  Install failed: {result.stderr.strip() or result.stdout.strip()}")
                return False
            try:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass
            time.sleep(1.0)
            return _validate_ollama()
        print(f"{YELLOW}⚠{NC}  Homebrew not found. Download Ollama for macOS from ollama.com/download")
        return False

    if system in ("windows", "win32"):
        print(f"{YELLOW}⚠{NC}  Windows install requires the official installer. Download from ollama.com/download")
        return False

    print(f"{YELLOW}⚠{NC}  Unsupported OS for auto-install: {system}")
    return False


def run_provider_setup(provider_id: str, auto_yes: bool = False) -> bool:
    """Run setup for a specific provider."""
    print(f"\n{BLUE}━━━ Setting up {provider_id} ━━━{NC}\n")

    if provider_id == "ollama":
        # Check if Ollama is installed
        if not shutil.which("ollama"):
            if _validate_ollama():
                host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
                print(f"{GREEN}✓{NC} Ollama API reachable at {host}\n")
                _show_ollama_model_library(auto_yes)
                return True
            sys.stderr.write(
                "ERROR: Ollama CLI not found and Ollama API unreachable. "
                "Install Ollama or set OLLAMA_HOST to a running server.\n"
            )
            print(f"{YELLOW}⚠{NC} ollama CLI not found")
            print("\nChoose setup type:")
            print("  1) Local Ollama (install CLI + run ollama serve)")
            print("  2) Remote Ollama (set OLLAMA_HOST)")
            print("  Enter to skip\n")
            choice = input("Select option [1/2]: ").strip()
            if choice == "1":
                print("\nLocal setup steps:")
                print("  Linux: automatic install will run (curl | sh)")
                print("  macOS: uses Homebrew if available")
                print("  Windows: opens download guidance")
                if _install_ollama_local():
                    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
                    print(f"{GREEN}✓{NC} Ollama API reachable at {host}\n")
                    _show_ollama_model_library(auto_yes)
                    return True
                recheck = input("\nRe-check now after install/start? (y/N): ").strip().lower()
                if recheck == "y":
                    if _validate_ollama():
                        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
                        print(f"{GREEN}✓{NC} Ollama API reachable at {host}\n")
                        _show_ollama_model_library(auto_yes)
                        return True
                    print(f"{YELLOW}⚠{NC} Ollama still not reachable. Try again after it is running.")
                return False
            if choice == "2":
                print("\nRemote setup steps:")
                print("  export OLLAMA_HOST=http://host:11434")
                print("  (Use the same shell that runs uCODE/TUI)")
                return False
            print(f"\n{YELLOW}⚠{NC}  Setup skipped. You can retry later.")
            return False

        # Check if running
        if not _validate_ollama():
            print(f"{YELLOW}⚠{NC} ollama server is not running")
            print("   Auto-starting ollama serve in background...")

            # Self-heal: auto-start ollama serve
            try:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True  # Detach from parent
                )
                print(f"{BLUE}→{NC} Waiting for ollama to start...")

                # Wait up to 10 seconds for ollama to become available
                for i in range(20):
                    time.sleep(0.5)
                    if _validate_ollama():
                        print(f"{GREEN}✓{NC} ollama server started!\n")
                        break
                else:
                    print(f"{YELLOW}⚠{NC} ollama didn't start in time")
                    print("   Try manually: ollama serve")
                    print("   Or install background service from https://ollama.ai")
                    return False
            except Exception as e:
                print(f"{YELLOW}⚠{NC} Failed to auto-start ollama: {e}")
                print("   Try manually: ollama serve")
                print("   Or install background service from https://ollama.ai")
                return False

        print(f"{GREEN}✓{NC} ollama server is running!\n")

        # Show model library
        _show_ollama_model_library(auto_yes)

        return True

    # Map provider IDs to setup commands
    setup_commands = {
        "github": ["gh", "auth", "login"],
        "ollama": None,  # Has dedicated setup function
    }

    cmd = setup_commands.get(provider_id)
    if cmd is None:
        print(f"{YELLOW}⚠{NC} {provider_id} requires manual setup via dashboard")
        print(f"   Visit: http://localhost:8765/#config")
        return False

    if _provider_is_configured(provider_id):
        if auto_yes:
            print(f"{YELLOW}⚠{NC} Existing setup detected; re-installing (--yes).")
            print(f"{BLUE}→{NC} Logging out of existing session...")
            _scrub_provider(provider_id)
        else:
            response = input(
                f"{provider_id} already configured. Scrub and reinstall? (y/N): "
            )
            if response.lower() != "y":
                print(f"Keeping existing setup for {provider_id}.")
                # Still try to auto-populate GitHub keys if available
                if provider_id == "github" and shutil.which("gh"):
                    print(f"{BLUE}→{NC} Refreshing GitHub configuration...")
                    token = _extract_github_token()
                    if token:
                        _populate_github_keys(token)
                return True
            print(f"{BLUE}→{NC} Logging out of existing session...")
            _scrub_provider(provider_id)

    # Confirm before running
    if not auto_yes:
        response = input(f"Run setup command for {provider_id}? (y/N): ")
        if response.lower() != "y":
            print(f"Skipped {provider_id}")
            return False

    # Run command
    try:
        print(f"\n{BLUE}━━━ Running {provider_id} authentication ━━━{NC}")
        print(f"Command: {' '.join(cmd)}\n")

        # For interactive commands like gh auth login, don't capture output
        if provider_id == "github":
            result = subprocess.run(cmd, check=False)
        else:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        # Validate that setup actually succeeded
        print(f"\n{BLUE}→{NC} Validating authentication...")
        setup_valid = False
        if result.returncode == 0:
            if provider_id == "github":
                # Validate GitHub auth
                setup_valid = _validate_github_auth()
                if setup_valid:
                    print(f"{GREEN}✓{NC} GitHub authentication verified")
            else:
                # For other providers, trust returncode
                setup_valid = True

        if setup_valid:
            # Auto-populate GitHub keys after successful gh auth login
            if provider_id == "github":
                print(f"{BLUE}→{NC} Extracting authentication token...")
                token = _extract_github_token()
                if token:
                    print(f"{BLUE}→{NC} Populating configuration files...")
                    _populate_github_keys(token)
                    print(f"\n{GREEN}✓{NC} {provider_id} setup complete")
                else:
                    print(f"{YELLOW}⚠{NC} Could not extract token from gh CLI")
                    print(f"   You may need to run: gh auth refresh")
            else:
                print(f"{GREEN}✓{NC} {provider_id} setup complete")

            return True
        else:
            print(f"{YELLOW}⚠{NC} {provider_id} setup did not complete successfully")
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
