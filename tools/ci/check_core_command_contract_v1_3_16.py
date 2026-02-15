#!/usr/bin/env python3
"""Validate core command contract policy for v1.3.16."""

from __future__ import annotations

import json
import re
from pathlib import Path


CMD_RE = re.compile(r"^[A-Z][A-Z0-9]*$")
MAX_LEN = 6


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "core" / "config" / "ucli_command_contract_v1_3_16.json"
    if not path.exists():
        print(f"[contract-v1.3.16] FAIL: missing {path}")
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    commands = data.get("ucode", {}).get("commands", [])
    aliases = data.get("ucode", {}).get("deprecated_aliases", {})

    bad = []
    seen = set()
    for cmd in commands:
        if cmd in seen:
            bad.append(f"duplicate command: {cmd}")
        seen.add(cmd)
        if not isinstance(cmd, str) or not cmd.strip():
            bad.append(f"invalid command entry: {cmd!r}")
            continue
        if not CMD_RE.match(cmd):
            bad.append(f"not uppercase canonical: {cmd}")
        if len(cmd) > MAX_LEN:
            bad.append(f"too long (> {MAX_LEN}): {cmd}")

    if aliases:
        bad.append("deprecated_aliases must be empty (no shims policy)")

    if bad:
        print("[contract-v1.3.16] FAIL")
        for issue in bad:
            print(f"  - {issue}")
        return 1

    print("[contract-v1.3.16] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
