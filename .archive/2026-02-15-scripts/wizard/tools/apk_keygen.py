#!/usr/bin/env python3
"""
APK Keygen Helper (Alpine)

Generates abuild keys and optionally installs the public key into /etc/apk/keys.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate abuild APK signing keys")
    parser.add_argument("--key-dir", default=str(Path.home() / ".abuild"))
    parser.add_argument("--install", action="store_true", help="Install public key into /etc/apk/keys")
    parser.add_argument("--name", default=os.environ.get("ABUILD_KEYNAME", "udos"))
    args = parser.parse_args()

    key_dir = Path(args.key_dir)
    key_dir.mkdir(parents=True, exist_ok=True)

    if not shutil.which("abuild-keygen"):
        raise SystemExit("abuild-keygen not found. Install abuild on Alpine.")

    env = os.environ.copy()
    env["HOME"] = str(Path.home())
    env["ABUILD_KEYNAME"] = args.name

    cmd = ["abuild-keygen", "-a"]
    if args.install:
        cmd.append("-i")

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise SystemExit(f"abuild-keygen failed: {result.stderr.strip()}")

    print("✅ abuild key generated")
    print(f"   key dir: {key_dir}")
    if args.install:
        print("   public key installed to /etc/apk/keys")


if __name__ == "__main__":
    import shutil
    main()
