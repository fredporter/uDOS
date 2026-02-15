#!/usr/bin/env python3
"""Guard core command profile against direct networking imports."""

from __future__ import annotations

import ast
from pathlib import Path

BANNED = {
    "requests",
    "urllib",
    "urllib3",
    "http",
    "socket",
    "websockets",
    "aiohttp",
    "ftplib",
    "smtplib",
    "imaplib",
    "poplib",
}

# Scope this check to the v1.3.16 core command profile implementation paths.
TARGETS = [
    "core/tui/dispatcher.py",
    "core/commands/health_handler.py",
    "core/commands/verify_handler.py",
    "core/commands/run_handler.py",
    "core/commands/draw_handler.py",
]


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    violations = []

    for rel in TARGETS:
        file_path = repo / rel
        if not file_path.exists():
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if mod.split(".", 1)[0] in BANNED:
                        violations.append((rel, node.lineno, mod))
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
                if mod.split(".", 1)[0] in BANNED:
                    violations.append((rel, node.lineno, mod))

    if violations:
        print("[core-no-network] FAIL")
        for rel, line, mod in violations:
            print(f"  - {rel}:{line} imports {mod}")
        return 1

    print("[core-no-network] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
