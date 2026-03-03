#!/usr/bin/env python3
"""Provider setup helper for Wizard.

Supports the active v1.5 provider surfaces:
- github
- logic_assist
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys

from core.services.logic_assist_setup import run_logic_assist_setup
from wizard.services.logic_assist_service import get_logic_assist_service

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

CONFIG_PATH = Path(__file__).parent / "config"
SETUP_FLAGS_FILE = CONFIG_PATH / "provider_setup_flags.json"
REPO_ROOT = Path(__file__).resolve().parents[1]


def load_flagged_providers() -> list[str]:
    """Load providers flagged for setup."""
    if not SETUP_FLAGS_FILE.exists():
        return []
    try:
        data = json.loads(SETUP_FLAGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    flagged = data.get("flagged", [])
    return flagged if isinstance(flagged, list) else []


def _load_flags() -> dict[str, object]:
    if not SETUP_FLAGS_FILE.exists():
        return {"flagged": [], "completed": [], "timestamp": None}
    try:
        data = json.loads(SETUP_FLAGS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"flagged": [], "completed": [], "timestamp": None}
    except Exception:
        return {"flagged": [], "completed": [], "timestamp": None}


def _save_flags(flags: dict[str, object]) -> None:
    flags["timestamp"] = datetime.now(UTC).isoformat()
    SETUP_FLAGS_FILE.write_text(json.dumps(flags, indent=2), encoding="utf-8")


def _validate_github_auth() -> bool:
    try:
        result = subprocess.run(
            ["gh", "auth", "status", "-h", "github.com"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return False
    if result.returncode == 0:
        return True
    output = f"{result.stdout}\n{result.stderr}".lower()
    return "logged in to github.com" in output


def _logic_assist_ready() -> bool:
    status = get_logic_assist_service(REPO_ROOT).get_status()["local"]
    return bool(status.get("ready"))


def _logic_assist_summary() -> dict[str, object]:
    status = get_logic_assist_service(REPO_ROOT).get_status()["local"]
    return {
        "ready": bool(status.get("ready")),
        "issue": status.get("issue"),
        "model": status.get("model"),
        "model_path": status.get("model_path"),
        "package_available": bool(status.get("package_available")),
        "model_present": bool(status.get("model_present")),
    }


def _provider_is_configured(provider_id: str) -> bool:
    if provider_id == "github":
        return bool(shutil.which("gh") and _validate_github_auth())
    if provider_id == "logic_assist":
        summary = _logic_assist_summary()
        return bool(summary["package_available"]) or bool(summary["model_path"])
    return False


def mark_provider_completed(provider_id: str) -> None:
    flags = _load_flags()
    flagged = list(flags.get("flagged") or [])
    completed = list(flags.get("completed") or [])
    if provider_id in flagged:
        flagged.remove(provider_id)
    if provider_id not in completed:
        completed.append(provider_id)
    flags["flagged"] = flagged
    flags["completed"] = completed
    _save_flags(flags)


def _parse_provider_arg(argv: list[str]) -> str | None:
    if "--provider" not in argv:
        return None
    idx = argv.index("--provider")
    if idx + 1 >= len(argv):
        return None
    return argv[idx + 1].strip().lower() or None


def _run_github_setup(auto_yes: bool) -> bool:
    if _validate_github_auth():
        print(f"{GREEN}✓{NC} github already authenticated")
        return True

    if not shutil.which("gh"):
        print(f"{YELLOW}⚠{NC} gh CLI not installed")
        print("   Install GitHub CLI first, then rerun setup.")
        return False

    if not auto_yes:
        response = input("Run 'gh auth login -h github.com' now? (y/N): ").strip().lower()
        if response != "y":
            print("Skipped github setup.")
            return False

    print(f"\n{BLUE}━━━ Setting up github ━━━{NC}\n")
    result = subprocess.run(["gh", "auth", "login", "-h", "github.com"], check=False)
    if result.returncode != 0:
        print(f"{YELLOW}⚠{NC} github setup did not complete")
        return False
    if _validate_github_auth():
        print(f"{GREEN}✓{NC} github authentication verified")
        return True
    print(f"{YELLOW}⚠{NC} github authentication still incomplete")
    return False


def _run_logic_assist_setup(auto_yes: bool) -> bool:
    summary = _logic_assist_summary()
    if summary["ready"]:
        print(f"{GREEN}✓{NC} logic_assist local runtime ready")
        return True

    if not auto_yes:
        response = input("Prepare local logic-assist tooling now? (y/N): ").strip().lower()
        if response != "y":
            print("Skipped logic_assist setup.")
            return False

    print(f"\n{BLUE}━━━ Setting up logic_assist ━━━{NC}\n")
    result = run_logic_assist_setup(REPO_ROOT)

    for step in result.get("steps", []):
        print(f"  • {step}")
    for warning in result.get("warnings", []):
        print(f"  {YELLOW}⚠{NC} {warning}")

    summary = _logic_assist_summary()
    if summary["ready"]:
        print(f"{GREEN}✓{NC} logic_assist local runtime ready")
        return True

    if result.get("status") == "success":
        print(f"{GREEN}✓{NC} logic_assist tooling prepared")
        if summary.get("model_path"):
            print(f"   Model path: {summary['model_path']}")
        if summary.get("issue"):
            print(f"   Remaining action: {summary['issue']}")
        return True

    print(f"{YELLOW}⚠{NC} logic_assist setup incomplete")
    if summary.get("issue"):
        print(f"   Issue: {summary['issue']}")
    return False


def run_provider_setup(provider_id: str, auto_yes: bool = False) -> bool:
    """Run setup for a supported provider."""
    normalized = (provider_id or "").strip().lower()
    if normalized == "github":
        return _run_github_setup(auto_yes)
    if normalized == "logic_assist":
        return _run_logic_assist_setup(auto_yes)

    print(f"{YELLOW}⚠{NC} Unsupported provider for v1.5 setup: {normalized}")
    print("   Supported providers: github, logic_assist")
    return False


def main() -> int:
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
        response = input("Run setup for these providers now? (y/N): ").strip().lower()
        if response != "y":
            print("Skipping provider setup.")
            return 0

    for provider_id in flagged:
        success = run_provider_setup(provider_id, auto_yes)
        if success:
            mark_provider_completed(provider_id)

    print(f"\n{GREEN}━━━ Provider setup complete ━━━{NC}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
