#!/usr/bin/env python3
"""Setup helper for TOYBOX upstream runtime storage + activation."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from wizard.services.path_utils import get_repo_root


SCRIPT_MAP = {
    "hethack": "library/hethack/setup.sh",
    "elite": "library/elite/setup.sh",
    "rpgbbs": "library/rpgbbs/setup.sh",
    "crawler3d": "library/crawler3d/setup.sh",
}


def run_script(repo_root: Path, profile: str, activate_dotenv: bool) -> int:
    rel = SCRIPT_MAP[profile]
    script = repo_root / rel
    if not script.exists():
        print(f"[toybox] missing setup script: {script}")
        return 1

    env = os.environ.copy()
    if activate_dotenv:
        env["ACTIVATE_DOTENV"] = "1"

    print(f"[toybox] running: {rel}")
    result = subprocess.run([str(script)], cwd=str(repo_root), env=env)
    return int(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install TOYBOX upstream runtimes into local Wizard-managed storage."
    )
    parser.add_argument(
        "profile",
        nargs="?",
        default="all",
        choices=["all", "hethack", "elite", "rpgbbs", "crawler3d"],
        help="Which TOYBOX profile to set up",
    )
    parser.add_argument(
        "--activate-dotenv",
        action="store_true",
        help="Also write TOYBOX_* vars into repo .env (not only memory/bank/private/toybox-runtime.env)",
    )
    args = parser.parse_args()

    repo_root = get_repo_root()
    profiles = list(SCRIPT_MAP.keys()) if args.profile == "all" else [args.profile]

    for profile in profiles:
        rc = run_script(repo_root, profile, activate_dotenv=args.activate_dotenv)
        if rc != 0:
            return rc

    activation = repo_root / "memory" / "bank" / "private" / "toybox-runtime.env"
    print("\n[toybox] setup complete")
    print(f"[toybox] activation file: {activation}")
    print(f"[toybox] activate in shell: source {activation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
