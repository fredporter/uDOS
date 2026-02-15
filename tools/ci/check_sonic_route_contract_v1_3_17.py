#!/usr/bin/env python3
"""Validate v1.3.17 Sonic route surface exists in Wizard router source files."""

from __future__ import annotations

import ast
from pathlib import Path


REQUIRED = {
    ("GET", "/api/platform/sonic/status"),
    ("POST", "/api/platform/sonic/build"),
    ("GET", "/api/platform/sonic/builds"),
    ("GET", "/api/platform/sonic/builds/{id}"),
    ("GET", "/api/platform/sonic/builds/{id}/artifacts"),
    ("GET", "/api/library/integration/sonic"),
    ("POST", "/api/library/integration/sonic/install"),
    ("POST", "/api/library/integration/sonic/enable"),
    ("POST", "/api/library/integration/sonic/disable"),
    ("DELETE", "/api/library/integration/sonic"),
    ("GET", "/api/sonic/health"),
    ("GET", "/api/sonic/devices"),
    ("GET", "/api/sonic/db/status"),
    ("POST", "/api/sonic/rescan"),
    ("POST", "/api/sonic/db/rebuild"),
    ("POST", "/api/sonic/rebuild"),
    ("GET", "/api/sonic/db/export"),
    ("GET", "/api/sonic/export"),
    ("POST", "/api/sonic/sync"),
}

METHOD_MAP = {
    "get": "GET",
    "post": "POST",
    "delete": "DELETE",
    "patch": "PATCH",
    "put": "PUT",
}


def gather_routes(path: Path, prefix: str = "") -> set[tuple[str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[tuple[str, str]] = set()

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            func = dec.func
            if not isinstance(func, ast.Attribute):
                continue
            method = METHOD_MAP.get(func.attr)
            if not method:
                continue
            if not dec.args:
                continue
            arg0 = dec.args[0]
            if not isinstance(arg0, ast.Constant) or not isinstance(arg0.value, str):
                continue
            route_path = f"{prefix}{arg0.value}"
            found.add((method, route_path))

    return found


def main() -> int:
    repo = Path(__file__).resolve().parents[2]

    available = set()
    available |= gather_routes(repo / "wizard" / "routes" / "platform_routes.py", prefix="/api/platform")
    available |= gather_routes(repo / "wizard" / "routes" / "library_routes.py", prefix="/api/library")
    available |= gather_routes(repo / "wizard" / "routes" / "sonic_plugin_routes.py", prefix="/api/sonic")

    missing = sorted(REQUIRED - available)
    if missing:
        print("[sonic-route-contract-v1.3.17] FAIL")
        for method, route in missing:
            print(f"  - missing {method} {route}")
        return 1

    print("[sonic-route-contract-v1.3.17] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
