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
from pathlib import Path
from typing import List, Dict

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


def run_provider_setup(provider_id: str, auto_yes: bool = False) -> bool:
    """Run setup for a specific provider."""
    print(f"\n{BLUE}━━━ Setting up {provider_id} ━━━{NC}\n")

    # Map provider IDs to setup commands
    setup_commands = {
        "github": ["gh", "auth", "login"],
        "ollama": None,  # Auto-detected
        "slack": ["slack", "auth"],
        "notion": None,  # Interactive browser flow
    }

    cmd = setup_commands.get(provider_id)
    if cmd is None:
        print(f"{YELLOW}⚠{NC} {provider_id} requires manual setup via dashboard")
        print(f"   Visit: http://localhost:8765/#config")
        return False

    # Confirm before running
    if not auto_yes:
        response = input(f"Run setup command for {provider_id}? (y/N): ")
        if response.lower() != "y":
            print(f"Skipped {provider_id}")
            return False

    # Run command
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print(f"{GREEN}✓{NC} {provider_id} setup complete")
            return True
        else:
            print(f"{YELLOW}⚠{NC} {provider_id} setup failed or incomplete")
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


def main():
    """Main entry point."""
    auto_yes = "--yes" in sys.argv or "-y" in sys.argv

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
