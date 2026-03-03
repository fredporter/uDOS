#!/usr/bin/env python3
"""Audit active core runtime surfaces for stdlib-only and Wizard separation."""

from __future__ import annotations

import ast
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_CORE_ROOTS = (
    REPO_ROOT / "core" / "commands",
    REPO_ROOT / "core" / "services",
    REPO_ROOT / "core" / "ulogic",
    REPO_ROOT / "core" / "workflows",
)

PROHIBITED_IMPORT_ROOTS = frozenset(
    {
        "wizard",
        "requests",
        "httpx",
        "aiohttp",
        "fastapi",
        "flask",
        "pydantic",
        "dotenv",
    }
)

ALLOWLIST = frozenset(
    {
        Path("core/services/packaging_manifest_models.py"),
        Path("core/services/unified_config_loader.py"),
        Path("core/services/vibe_setup_service.py"),
        Path("core/services/config_sync_service.py"),
        Path("core/services/provider_registry.py"),
        Path("core/services/ai_provider_handler.py"),
        Path("core/tui/ucode.py"),
    }
)


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in ACTIVE_CORE_ROOTS:
        if not root.exists():
            continue
        files.extend(path for path in root.rglob("*.py") if path.is_file())
    return sorted(set(files))


def _import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    return imports


def main() -> int:
    violations: list[str] = []
    allowlist_hits: list[str] = []

    for path in _iter_python_files():
        relative = path.relative_to(REPO_ROOT)
        imports = _import_roots(path) & PROHIBITED_IMPORT_ROOTS
        if not imports:
            continue
        if relative in ALLOWLIST:
            allowlist_hits.append(f"{relative} :: {', '.join(sorted(imports))}")
            continue
        violations.append(f"{relative} :: {', '.join(sorted(imports))}")

    if violations:
        print("Core stdlib contract violations detected:", file=sys.stderr)
        for item in violations:
            print(f"- {item}", file=sys.stderr)
        if allowlist_hits:
            print("", file=sys.stderr)
            print("Transitional allowlist entries:", file=sys.stderr)
            for item in allowlist_hits:
                print(f"- {item}", file=sys.stderr)
        return 1

    print("Core stdlib contract: PASS")
    if allowlist_hits:
        print("Transitional allowlist entries:")
        for item in allowlist_hits:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
