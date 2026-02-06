#!/usr/bin/env python3
"""Home Assistant gateway config sanity check."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    bridge_path = repo_root / "library" / "home-assistant" / "bridge.json"
    if not bridge_path.exists():
        print("bridge.json not found")
        return 1
    try:
        payload = json.loads(bridge_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"bridge.json invalid: {exc}")
        return 1

    required = ["gateway", "routes", "features", "configuration"]
    missing = [key for key in required if key not in payload]
    if missing:
        print(f"bridge.json missing keys: {', '.join(missing)}")
        return 1

    print("bridge.json OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
