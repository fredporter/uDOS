#!/usr/bin/env python3
"""Ensure contract commands are dispatchable in core dispatcher."""

from __future__ import annotations

import json
from pathlib import Path

from core.tui.dispatcher import CommandDispatcher

# These are handled directly by UCLI rather than dispatcher handlers.
DIRECT_UCLI = {"STATUS", "HELP"}


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    contract = json.loads((repo / "core" / "config" / "ucli_command_contract_v1_3_16.json").read_text())
    commands = set(contract.get("ucode", {}).get("commands", []))
    handlers = set(CommandDispatcher().handlers.keys())

    missing = sorted(cmd for cmd in commands if cmd not in handlers and cmd not in DIRECT_UCLI)
    if missing:
        print("[contract-dispatcher] FAIL")
        for cmd in missing:
            print(f"  - missing handler for contract command: {cmd}")
        return 1

    print("[contract-dispatcher] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
