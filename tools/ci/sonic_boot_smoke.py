#!/usr/bin/env python3
"""Sonic Stick boot smoke preflight (artifact + runtime availability checks)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.commands.sonic_handler import SonicHandler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", required=True)
    args = parser.parse_args()

    build_dir = Path(args.build_dir).expanduser().resolve()
    manifest_path = build_dir / "build-manifest.json"
    checksums_path = build_dir / "checksums.txt"

    if not manifest_path.exists() or not checksums_path.exists():
        print(f"[sonic-boot-smoke] FAIL: manifest/checksums missing in {build_dir}")
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[sonic-boot-smoke] FAIL: invalid manifest JSON: {exc}")
        return 1

    artifacts = manifest.get("artifacts") or []
    kinds = {Path(item.get("name", "")).suffix for item in artifacts}
    if ".img" not in kinds or ".iso" not in kinds:
        print("[sonic-boot-smoke] FAIL: build manifest must include .img and .iso artifacts")
        return 1

    for item in artifacts:
        rel = item.get("path")
        if not rel:
            print(f"[sonic-boot-smoke] FAIL: artifact missing path: {item}")
            return 1
        if not (build_dir / rel).exists():
            print(f"[sonic-boot-smoke] FAIL: artifact missing on disk: {rel}")
            return 1

    status = SonicHandler().handle("SONIC", ["STATUS"])
    if status.get("status") != "ok":
        print("[sonic-boot-smoke] FAIL: SONIC STATUS not healthy")
        print(status)
        return 1

    datasets = status.get("datasets") or {}
    if not datasets.get("available"):
        print("[sonic-boot-smoke] FAIL: sonic datasets not available")
        return 1

    print(f"[sonic-boot-smoke] PASS: {build_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
