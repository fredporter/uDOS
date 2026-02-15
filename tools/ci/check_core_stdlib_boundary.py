#!/usr/bin/env python3
"""Enforce stdlib-only imports for core Python boundary paths.

Policy target is `core/py` when present. If that path does not exist yet,
this check exits cleanly so migration can happen incrementally.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def stdlib_modules() -> set[str]:
    names = set(getattr(sys, "stdlib_module_names", set()))
    # Compatibility safety for older Python runtimes.
    names.update({"typing_extensions"})
    return names


def is_allowed(module: str, stdlib: set[str]) -> bool:
    root = module.split(".", 1)[0]
    return root in stdlib


def collect_imports(path: Path) -> list[tuple[int, str]]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                # Relative import inside boundary path is acceptable.
                continue
            if node.module:
                imports.append((node.lineno, node.module))
    return imports


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    target = repo / "core" / "py"

    if not target.exists():
        print("[core-stdlib] SKIP: core/py does not exist yet.")
        return 0

    stdlib = stdlib_modules()
    violations: list[tuple[Path, int, str]] = []

    for py_file in sorted(target.rglob("*.py")):
        for lineno, module in collect_imports(py_file):
            if not is_allowed(module, stdlib):
                violations.append((py_file, lineno, module))

    if not violations:
        print("[core-stdlib] PASS: only stdlib imports found under core/py.")
        return 0

    print("[core-stdlib] FAIL: non-stdlib imports detected in core/py:")
    for path, line, module in violations:
        rel = path.relative_to(repo)
        print(f"  - {rel}:{line} imports '{module}'")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
