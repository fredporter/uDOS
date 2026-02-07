"""
Wizard MCP Gateway (scaffold)

Phase 2 bootstrap: this file will host the MCP protocol server that exposes
Wizard + uCODE tools to Vibe. For now it includes a minimal CLI for testing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from gateway import WizardGateway


def _print(obj) -> None:
    sys.stdout.write(json.dumps(obj, indent=2) + "\n")
    sys.stdout.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Wizard MCP Gateway (scaffold)")
    parser.add_argument("--health", action="store_true", help="Call /health")
    parser.add_argument("--config", action="store_true", help="Call /api/config")
    parser.add_argument("--providers", action="store_true", help="Call /api/providers")
    parser.add_argument("--ucode", type=str, help="Dispatch a uCODE command (allowlisted)")
    parser.add_argument("--ucode-command", type=str, help="Route raw uCODE input")
    parser.add_argument("--tools", action="store_true", help="List MCP tool names")
    args = parser.parse_args()

    client = WizardGateway()

    if args.health:
        _print(client.health())
        return 0
    if args.config:
        _print(client.config_get())
        return 0
    if args.providers:
        _print(client.providers_list())
        return 0
    if args.ucode:
        _print(client.ucode_dispatch(args.ucode))
        return 0
    if args.ucode_command:
        _print(client.ucode_dispatch(args.ucode_command))
        return 0
    if args.tools:
        tools_path = THIS_DIR.parent.parent / "api" / "wizard" / "tools" / "mcp-tools.md"
        if not tools_path.exists():
            _print({"count": 0, "tools": [], "error": f"Tool index not found: {tools_path}"})
            return 1
        tools: list[str] = []
        for line in tools_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("- `") and "`" in stripped[3:]:
                name = stripped.split("`", 2)[1]
                if name:
                    tools.append(name)
        _print({"count": len(tools), "tools": tools})
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
